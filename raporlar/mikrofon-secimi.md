# Robot için gürültü bastırmalı mikrofon seçimi (Pi 5, açık alan + sanayi)

> Kaynak: vault raporu (26 Ekim 2026, araştırma ajanı; Efe seçimi yaptı: XVF3800 dizi + yönlü mikrofon, ikisi de alınacak). Alt ajan raporu olduğu gibi. Rakamlar ajanın beyanı; "tahmini", "doğrulanmadı", "[ESKİ]" işaretleri korundu. Satın alma kararı Efe'de. Seçim sonrası TÜBİTAK 2209-B bütçe satırları (3.500 + 1.800 TL) ve İP1/risk metni güncellenecek.

**Önce güvenlik:** Rapordaki hiçbir pakette kötü amaç şüphesi bulmadım. Tek uyarı: `pywebrtc-audio` olgun değil (19 yıldız, 4 commit, sürüm yok) [K15]. Onun yerine sistemde zaten olan PipeWire `module-echo-cancel` [K14] ya da LiveKit APM kullanılmalı (Apache-2.0, 16.10.2026 sürümü) [K16].

## 1. Sonuç
Birinci tercihim **XVF3800 çipli 4 mikrofonlu USB dizi** (Seeed reSpeaker XVF3800, kasalı). Yankı iptali (AEC), sinir ağı tabanlı gürültü bastırma (NS), hüzme oluşturma (beamforming) ve geliş yönü bulma (DOA) donanımda çalışıyor. Pi'ye UAC2 ile sürücüsüz bağlanıyor. 6 kanallı yazılım sürümü ham mikrofon kanallarını da verdiği için TÜBİTAK'taki "işlenmiş / ham" karşılaştırmasına doğrudan veri çıkarır [K1][K2].
İkinci tercih ucuz bir yönlü mikrofon, USB ses kartı, kürk kılıf ve yazılımda yankı iptali. Bu zaten bütçedeki karşılaştırma kolu. Konferans hoparlörleri (Jabra, Anker) robot için uygun değil: hoparlörleri fabrika gürültüsüne göre zayıf, Linux desteği belgelenmemiş.
XVF3800'ün Pi 5'te açık bir hatası var: sıcak yeniden başlatmadan sonra ses bozuluyor. Satın almadan önce bu hata ve güç beslemesi doğrulanmalı (aşağıdaki liste).

## 2. Donanım karşılaştırması (fiyatlar 24-26.10.2026; 1 USD = 49,58 TL, 1 EUR = 55,73 TL, 20.10.2026 [K24])
| Aday | Mik. sayısı / donanımda işlem | Pi 5'te bağlantı | Hoparlör çıkışı | Fiyat, satıcı, stok | Bilinen sorun |
|---|---|---|---|---|---|
| **XVF3800 USB 4-Mic Array** (2025) | 4 / AEC, DNN-NS, beamforming, DOA, VAD | UAC2, sürücü yok; 16 kHz 6 kanal ya da 48 kHz 2 kanal yazılım sürümü [K1] | 3,5 mm + JST, "5 W'lık amfili hoparlör destekler" [K1] | Kasalı 65,88 € ≈ 3.670 TL, RobotShop EU, ön sipariş [K3]; A$112,88, Pakronics, stokta 40 adet [K4]; Türk satıcıda bulamadım | Sıcak yeniden başlatmada ses bozuluyor; Pi 5'te de doğrulanmış (#20). USB'de G/Ç hatası (#26, Pi 4). 21 açık konu var [K2] |
| reSpeaker **Flex** XVF3800 (2026, çevresel ya da doğrusal) | Aynı çip. Mikrofon kartı 20 cm FPC kabloyla ayrı duruyor; doğrusal sürüm öne bakıyor, arkadan geleni bastırıyor [K5] | UAC2 [K5] | Var | Çevresel $57,94 ≈ 2.870 TL, RobotShop, "yakında stokta" [K6] | XIAO'lu sürüm I2S yazılımıyla gelir, USB ses aygıtı olarak görünmez [K1] |
| ReSpeaker Lite (XU316) | 2 / AEC, NS, girişim bastırma. Wiki'de beamforming ya da DOA yazmıyor [K7] | UAC2 (en az 2.0.5 sürümü) [K7] | Var | $29,12 ≈ 1.445 TL, RobotShop, stokta [K8] | Yalnız 2 mikrofon var, 85 dB'lik ortamda yetersiz kalabilir (tahmini) |
| USB Mic Array v2.0 (XVF3000) | 4 / AEC, NS, beamforming, DOA, VAD [K9] | UAC1, en çok 16 kHz [K9] | 3,5 mm | 6.624,22 TL (KDV dahil), Robotistan, **tükendi** [K10] | 2018 kartı; örnek betikler Python 2.7 [K9] [ESKİ] |
| 2-Mics Pi HAT | 2 / donanımda işlem yok (wiki'de AEC ya da NS geçmiyor) [K11] | I2S HAT; wiki'de Pi 5 geçmiyor [K11] | Var | 1.215,01 TL, Robotistan, **tükendi** [K12] | Yankı iptali tamamen yazılıma kalır |
| miniDSP UMA-8 v2 | 7 / AEC, NS, beamforming, DOA [K13] | UAC2, sürücü yok [K13] | Yok | İndirimli 156,16 € (liste 188,95 €), SoundImports, tükendi, 30.10.2026'da bekleniyor [K13] | Ayar arayüzü yalnız Windows/Mac'te |
| Jabra Speak2 40 | 4 / AEC, NS; IP64; algılama mesafesi 2,3 m [K17] | Teknik sayfada Linux yok | 50 mm, tepe 83 dB SPL (0,5 m'de) [K17] | Türkiye fiyatını doğrulayamadım (Teknosa sayfası açılmadı) | Bu ses düzeyi 80 dB'lik fabrikada yetersiz (tahmini) |
| Anker PowerConf S330 | 4 / NS; AEC yazılı değil [K18] | **5 V / 2 A istiyor** [K19]; Pi 5 USB portlarına toplam 0,6-1,6 A veriyor [K20] | 3 W | $99,99, soundcore.com [K18]; Türkiye fiyatı doğrulanmadı | Yazılım güncellemesi yalnız PC'deki AnkerWork ile [K19] |
| Yönlü mikrofon + USB ses kartı | 1 kardioid shotgun (Boya BY-MM1), işlem yok | UAC (ses kartına bağlı; doğrulanmadı) | Ayrı | 1.334,11 TL, n11, epey.com'dan [K21] | Yönlü mikrofon rüzgâra omniden 20 dB'e kadar daha duyarlı [K22] |

## 3. Rüzgâr önlemleri
| Önlem | Etkisi | Kaynak |
|---|---|---|
| Diziyi kafanın içine, büyük durgun hava hacmine gömmek | Her mikrofona ayrı kılıf yerine tek büyük sepet önerilir. Durgun hava hacmi ne kadar büyükse koruma o kadar iyi | [K22]; [K23] [ESKİ] |
| Köpük | Dizi için yapılmış köpük dolgulu kılıf: 13 mph rüzgârda ~9 dB, 20 mph'de 16 dB'den fazla azaltma. Tek başına köpük sınırlı kalır | [K25] [ESKİ]; [K23] [ESKİ] |
| Kürk kılıf ("deadcat") | Orta kuvvette rüzgârda iyi koruma sağlar | [K22] |
| Omni kapsül | MEMS dizileri omni olduğu için rüzgârda yönlü mikrofona göre avantajlı | [K22] |
| Dizinin rüzgârdaki davranışı | Rüzgâr türbülansı her mikrofonda ayrı oluştuğu için kanallar arasında ilişkisizdir. Uzamsal filtre bu gürültüyü 5 kattan fazla büyütebiliyor. Kuvvetli rüzgârda beamforming kazancı tersine dönebilir | [K26] [ESKİ] |
| Yüksek geçiren filtre (HPF) | En alt basları kesmek rüzgâr gürültüsünü etkili biçimde azaltır. Pratikte ~100-150 Hz (tahmini). webrtc APM'de HPF seçeneği var | [K27] [ESKİ]; [K16] |

## 4. Yazılım: Pi 5'te 2,5 s gecikme hedefi
- **Önerdiğim zincir:** XVF3800'ün ASR kanalı → HPF → Silero VAD → konuşma tanıma (STT). Silero'nun kendi iddiası: CPU'da 30 ms'lik parça başına 1 ms'den az; Pi'de ölçülmedi [K28].
- **Donanımdaki işlemin üstüne ikinci bir sinir ağı gürültü bastırması eklemiyorum.** Tek kanallı iyileştirmenin bıraktığı bozulmalar tanımayı kötüleştirebiliyor [K29] [ESKİ].
- **DeepFilterNet:** dizüstü i5'te gerçek zaman çarpanı 0,04 [K30] [ESKİ]. Pi 5 için ölçüm bulamadım (doğrulanmadı). Döngüye girmesin, yalnız çevrimdışı karşılaştırmada kullanılsın.
- **RNNoise:** BSD lisanslı, 48 kHz. ARM'deki performansı belgelenmemiş [K31].
- **Yerel yedek STT:** Pi 5'te Whisper tiny 10 s'lik sesi 2-3 s'de yazıya döküyor [K32]. Kısa komutlarda sığar, uzun cümlede bütçeyi aşar.
- **Gecikme bütçesi (tahmini):** VAD'ın konuşma sonu bekleme süresi 0,5-0,7 s + bulut STT 0,3-0,8 s + dil modeli ilk yanıt ve TTS ~1 s. Toplam ≈ 2-2,5 s. Ön işlemenin payı 50 ms'yi geçmemeli.

## 5. Öneri ve bütçe
1. **Birinci tercih:** XVF3800 USB dizisi, kasalı, XIAO'suz.
   - Ürün ≈ 3.670 TL. Kargo ve gümrükle birlikte **≈ 5.500 TL (tahmini)**.
   - 30 € gümrük muafiyeti 2026'da kaldırıldı [K33].
   - Kafaya gömmek gerekirse aynı çipli Flex doğrusal sürüm (XIAO'suz -L4-0) değerlendirilebilir.
2. **İkinci tercih / karşılaştırma kolu:** yönlü mikrofon + USB ses kartı + kürk kılıf. Ses kartı ve kılıf fiyatı doğrulanmadı; toplam **≈ 2.000 TL (tahmini)**.
3. **Toplam ≈ 7.500 TL.** Taslaktaki iki kalem 3.500 + 1.800 TL'ydi; fark +2.200 TL. 16.000 TL'lik toplam sabit kalacaksa bu fark başka bir kalemden düşülmeli.
4. **Bütçe satırları (TÜBİTAK metninde marka adı yasak):**
   - "Donanımsal yankı iptalli ve gürültü bastırmalı 4 mikrofonlu USB mikrofon dizisi + rüzgâr koruyucu — makine/teçhizat — 5.500 TL"
   - "Yönlü mikrofon, USB ses kartı ve kürk rüzgâr kılıfı (karşılaştırma kolu) — makine/teçhizat — 2.000 TL"

**Satın almadan önce doğrulanacaklar:**
- XIAO'suz USB sürümü alınmalı [K1].
- Yazılım sürümü 2.1.0 ve 6 kanallı dosya erişilebilir olmalı [K1].
- Pi 5 + Bookworm'da sıcak yeniden başlatma testi; topluluğun önerdiği `xvf_host REBOOT 1` geçici çözümü denenmeli (bakımcılar doğrulamadı) [K2].
- Pi 5 için 5 V 5 A güç kaynağı. Olmazsa USB portlarına toplam 600 mA kalır [K20]. Dizinin akım tüketimi belgelenmemiş, ölçülmeli.
- Robot hoparlörü dizinin çıkışından beslenmeli ki AEC referans sinyalini alabilsin. Araya harici amfi girince AEC'nin çalıştığı doğrulanmadı.
- Satıcı Türkiye'ye gönderiyor mu, yoksa üniversite yerel tedarikçiden teklif mi alacak?

## 6. Riskler ve bilinmeyenler
- XVF3800'de USB bağlantı sorunları açık duruyor (#20, #26, #32) ve bakımcı yanıtı yok [K2]. Yedek kart, tek kart fiyatı (≈ 5.500 TL) kadar ek bütçe ister.
- Türk pazar yerleri (akakçe, hepsiburada, trendyol, teknosa) erişimimi engelledi. Konferans hoparlörlerinin TL fiyatları doğrulanmadı.
- Robot konuşurken mikrofon kapalı olacağı için AEC'nin rolü daha çok robotun sözünü kesme (barge-in) ve yankı kuyruğu için. Ama ileride kesmeye izin verilirse şart olur.

## Kaynaklar
- K1 [Seeed XVF3800 wiki, 10.11.2025 güncel](https://wiki.seeedstudio.com/respeaker_xvf3800_introduction/)
- K2 [GitHub XVF3800 issues; #20](https://github.com/respeaker/reSpeaker_XVF3800_USB_4MIC_ARRAY/issues/20) · [#26](https://github.com/respeaker/reSpeaker_XVF3800_USB_4MIC_ARRAY/issues/26) (2026)
- K3 [RobotShop EU](https://eu.robotshop.com/products/respeaker-xmos-xvf3800-w-case-ai-powered-4-mic-array-for-clear-voice-in-noise)
- K4 [Pakronics](https://pakronics.com.au/products/respeaker-xvf3800-usb-4-mic-array-with-aec-agc-beamforming-doa-noise-suppression-360-far-field-voice-processing-for-xiao-esp32s3-raspberry-pi-jetson-device-ss101991441)
- K5 [Flex wiki, 26.03.2026](https://wiki.seeedstudio.com/respeaker_flex_introduction/)
- K6 [RobotShop Flex](https://www.robotshop.com/products/respeaker-flex-xvf3800-circular-4-ai-powered-microphone-array-for-robotics-embedded-applications)
- K7 [Lite wiki](https://wiki.seeedstudio.com/reSpeaker_usb_v3/)
- K8 [RobotShop Lite](https://www.robotshop.com/products/respeaker-lite-usb-2-mic-array-with-onboard-ai-audio-processing-algorithms)
- K9 [Mic Array v2.0 wiki](https://wiki.seeedstudio.com/ReSpeaker_Mic_Array_v2.0/)
- K10 [Robotistan v2.0](https://www.robotistan.com/respeaker-mic-array-v20)
- K11 [2-Mics HAT wiki](https://wiki.seeedstudio.com/ReSpeaker_2_Mics_Pi_HAT_Raspberry/)
- K12 [Robotistan HAT](https://www.robotistan.com/respeaker-2-mikrofonlu-pi-hat)
- K13 [SoundImports UMA-8](https://www.soundimports.eu/it/minidsp-uma-8.html)
- K14 [PipeWire echo-cancel](https://docs.pipewire.org/page_module_echo_cancel.html)
- K15 [pywebrtc-audio](https://github.com/strands-labs/pywebrtc-audio)
- K16 [LiveKit APM](https://docs.livekit.io/reference/python/livekit/rtc/apm.html) · [PyPI](https://pypi.org/project/livekit/)
- K17 [Jabra Speak2 40 teknik sayfası, 14.07.2026](https://www.jabra.com/_/media/Jabra_VXi_Product-Documentation/Jabra-Speak2-40/Datasheets/RevC/EN-US--Speak2-40-Datasheet-20260714.pdf)
- K18 [soundcore S330](https://www.soundcore.com/products/a3308011)
- K19 [S330 kılavuzu](https://lp.ankerjapan.com/hubfs/aoos/manual/A3308Manual.pdf)
- K20 [Raspberry Pi USB PD teknik notu, 05.03.2026](https://pip-assets.raspberrypi.com/categories/685-app-notes-guides-whitepapers/documents/RP-009856-WP-1-USB%20Power%20delivery%20on%20Raspberry%20Pi%205.pdf)
- K21 [epey BY-MM1](https://www.epey.com/mikrofon/boya-by-mm1.html)
- K22 [Schoeps rüzgâr koruması](https://schoeps.de/en/knowledge/knowledge-base/things-to-know/effective-wind-protection.html)
- K23 [Sound on Sound, 2007](https://www.soundonsound.com/sound-advice/q-what-should-consider-when-recording-outside)
- K24 [hisse.net kur, 20.10.2026](https://www.hisse.net/haber/20-ekim-sali-doviz-fiyatlari-dolar-ve-euroda-son-durum-102977)
- K25 [BYU tezi, 2005](https://scholarsarchive.byu.edu/etd/611)
- K26 [Qualcomm US8391507B2, 2013](https://patents.google.com/patent/US8391507B2/en)
- K27 [Shure, 2012](https://www.shure.com/en-us/insights/shure-tech-tip-methods-to-minimize-wind-noise)
- K28 [Silero VAD](https://github.com/snakers4/silero-vad)
- K29 [Iwamoto vd., 2022](https://arxiv.org/abs/2201.06685)
- K30 [DeepFilterNet2, 2022](https://arxiv.org/abs/2205.05474)
- K31 [RNNoise](https://github.com/xiph/rnnoise)
- K32 [fast.io, 24.06.2026](https://fast.io/resources/openclaw-raspberry-pi-speech-recognition-offline-voice-agent/)
- K33 [Webrazzi, 07.01.2026](https://webrazzi.com/2026/01/07/yurt-disi-alisverislerde-gumruk-muafiyeti-kaldirildi-30-euro-limiti-tarihe-karisti/)
