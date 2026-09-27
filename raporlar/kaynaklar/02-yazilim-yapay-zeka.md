---
title: "Kanıt: Yazılım ve yapay zekâ"
created: 2026-09-26
---

> Claude Opus alt ajan raporu, 26 Eylül 2026, olduğu gibi. Rakamlar ajanın beyanıdır; "(t)", "tahmini", "doğrulanmadı" işaretleri korunmuştur.

# Tekerlekli insansı robot: yazılım ve yapay zekâ araştırması (Eylül 2026)

## Önce, işin gidişatını değiştiren beş bulgu
1. **Türkçe uyandırma kelimesi için hazır, ücretsiz bir çözüm yok.** Porcupine'in desteklediği diller arasında Türkçe yok; Türkçe yalnızca ticari müşterilere, duruma göre veriliyor. openWakeWord ise resmî olarak yalnızca İngilizce destekliyor. Fuar için en sağlam çözüm **bas-konuş düğmesi ya da dokunmatik sensör, yanında LED halka**. Yedek olarak "hey jarvis" gibi İngilizce bir hazır model de kullanılabilir.
2. **Pi 5 üzerinde yerel Whisper, Türkçede 2 saniyenin altına inemiyor.** Pi 5'te `small` modeli gerçek zamandan yavaş, `base` modeli ancak gerçek zaman hızında ve Türkçe doğruluğu zayıf. Common Voice Türkçe testinde Whisper small'un kelime hata oranı yaklaşık %16. Bu yüzden konuşma tanıma bulutta yapılmalı.
3. **Fuar Wi-Fi'ı en büyük tek risk.** Bulut hattı için ayrı bir 4.5G/5G mobil erişim noktası şart. Ayrıca çevrimdışı bir "yedek mod" gerekli: Vosk'un küçük Türkçe modeli (vosk-model-small-tr) ile birkaç sabit komut tanınır, cevaplar Piper ile yerelde seslendirilir.
4. **Donanım fiyatları arttı.** Jetson Orin Nano Super 22 Temmuz 2026'dan beri 249 $ değil **399 $**. Pi 5 8GB **125 $** oldu. AI HAT+ üretici sayfasında "70 $'dan başlayan" fiyatla görünüyor. Türkiye fiyatları ithalat nedeniyle bunların üstünde olacaktır.
5. **Görüntü tarafında en ucuz ve en etkileyici özellik bulut VLM ("ne görüyorsun?").** Tahminen 5–10 saatlik iş. En pahalı ve hukuken en riskli özellik ise yüz tanıma, yani kişiyi kimliğiyle ayırt etmek.

## Senaryo A: Yalnız ses
| Bileşen | Araç | Yerel/Bulut | Maliyet | Zorluk (1-5) |
|---|---|---|---|---|
| Mikrofon | ReSpeaker XVF3800 veya Lite (yankı iptali, gürültü bastırma, yön bulma) | Donanım | Tek seferlik | 2 |
| Tetik | Düğme + LED; istenirse openWakeWord (İngilizce kelime) | Yerel | 0 | 1 |
| Konuşma tanıma | Deepgram Nova-3 (Türkçe var, akışlı) veya Google | Bulut | ~0,0077 $/dk akışlı (başlangıçta 200 $ kredi) | 2 |
| Dil modeli | Gemini 3.8 Flash (0,75/3,75 $ / 1M token, ücretsiz katman var) veya Claude Haiku 4.5 (1/5 $) | Bulut | Konuşma başına ~0,005 $ (tahmini) | 2 |
| Metinden sese | Google Chirp 3 HD tr-TR (30 $ / 1M karakter) veya ücretsiz Piper (tr_TR dfki/fahrettin/fettah, orta kalite) | Bulut / Yerel | ~0,013 $/konuşma veya 0 | 2 |
| Alternatif | Gemini Live (ses girişi ~0,005 $/dk, ses çıkışı ~0,018 $/dk) veya gpt-realtime-2.1-mini | Bulut | Aşağıya bakın | 3 |
| Çevrimdışı yedek | Vosk small-tr + Piper | Yerel | 0 | 2 |
| Ana bilgisayar | Pi 5 8GB | — | ~125 $ | 1 |

## Senaryo B: Ses + görüntü (A'ya eklenenler)
| Bileşen | Araç | Yerel/Bulut | Maliyet | Zorluk |
|---|---|---|---|---|
| Kamera | Pi Camera Module 3 veya USB kamera | Donanım | Tek seferlik | 1 |
| Yüz algılama ve kafa takibi | MediaPipe Face Detection + pan-tilt PID | Yerel (Pi 5 CPU'da ~54 FPS) | 0 | 3 |
| Kişi/nesne algılama | YOLO26n/YOLO11n, NCNN formatında | Yerel (~15 FPS; ONNX ile ~7–8) | 0 | 3 |
| El/poz algılama | MediaPipe Pose (Pi 5'te ~6 FPS) | Yerel | 0 | 3 |
| "Ne görüyorsun?" | Tek kare → Gemini Flash / Claude görüntü girişi | Bulut | Soru başına ~0,001–0,003 $ (tahmini) | 1 |
| Yüz tanıma (önerilmiyor) | face_recognition (dlib) veya InsightFace | Yerel | InsightFace'in hazır modelleri **yalnız ticari olmayan araştırma** lisanslı | 4 + hukuk |
| Hızlandırıcı (gerekirse) | AI HAT+ 13 TOPS (Hailo-8L): YOLOv8n ~30 FPS | Yerel | 70 $'dan başlıyor | 4 |
| Jetson Orin Nano Super | YOLO11n TensorRT FP16 ~4,5 ms | Yerel | 399 $ | 4 (JetPack/CUDA kurulumu zor) |

## Mimari
```
            [Mikrofon dizisi]   [Kamera] (yalnız B)
                   |                 |
 [Düğme/LED]-->  Raspberry Pi 5 (Python asyncio, tek süreç)
                 ├─ ses_hatti:   tetik → akışlı STT → LLM (akışlı) → TTS → hoparlör
                 ├─ gorus (B):   MediaPipe yüz → kafa açısı hedefi; talep üzerine VLM karesi
                 ├─ davranis:    durum makinesi (BEKLE / DİNLE / DÜŞÜN / KONUŞ / JEST)
                 └─ seri protokol (USB-UART, 115200, satır tabanlı JSON)
                          |
                 ESP32 (alt kontrolcü)
                 ├─ 2x DC motor + enkoder → PID (50–100 Hz)
                 ├─ PCA9685 → kol/kafa servoları (kayıtlı jest kareleri)
                 ├─ 500 ms komut gelmezse motorları DURDUR (watchdog)
                 └─ Bluetooth gamepad / ESP-NOW ile teleop (Pi çökse de çalışır)
   Donanım acil stop anahtarı + servo ve mantık devreleri için ayrı güç (ortak toprak)
```

**ROS 2 kullanılmalı mı?** Bence hayır. Bu ekip için doğru olan düz Python + ESP32 ve seri haberleşme. ROS 2'nin öğrenme eğrisi dik. Üstelik değerini asıl gösterdiği yer Nav2 + SLAM, ve bu iş lidar, iyi odometri, URDF/TF ağacı ister. Nav2 + SLAM tahminen 150–300 saat ekler, fuar robotuna ise gerekmiyor. Teleop ve basit davranışlar yeterli. İleride otonom gezinme istenirse Jazzy seçilmeli (Ubuntu 24.04, uzun süreli destek sürümü). O durumda ekibin SolidWorks becerisi URDF dışa aktarımında işe yarar.

**Kollar:** Ters kinematik gereksiz. Jest kütüphanesi yeterli: el sallama, işaret etme, selam gibi hareketler zaman damgalı servo açıları olarak kaydedilip oynatılır. Bu yaklaşık 20–30 saat sürer, IK ise bunun katlarını ister.

## Toplam tepki süresi (<2 sn) nasıl yakalanır
Tahmini bütçe: konuşmanın bittiğini algılama (endpoint) 0,3–0,5 s, akışlı STT'nin son sonucu 0,2–0,4 s, LLM ilk token 0,3–0,8 s, TTS ilk ses 0,1–0,3 s, Türkiye'den ağ gecikmesi 0,1–0,2 s. Toplamda **~1,2–2,0 s**. Bunu tutturmanın yolları:
- Her aşama akışlı çalışmalı.
- LLM'nin ilk cümlesi biter bitmez TTS'e verilmeli, yani aşamalar üst üste binmeli.
- Sistem istemi kısa tutulmalı, cevap 1–2 cümleyle sınırlanmalı.
- Beklerken dolgu ses ya da "hmm" jesti kullanılmalı; algılanan süreyi kısaltır.

Gerçek zamanlı ses API'leri (Gemini Live, OpenAI Realtime) bir ağ turunu azaltır, ancak gürültüde sunucu tarafı konuşma algılaması (VAD) yanlış tetiklenir. Fuarda otomatik VAD kapatılıp tur düğmeyle yönetilmeli.

**Gürültü ve yankı:** Fuar ortamında en etkili önlemler şunlar:
- Yankı iptalli mikrofon dizisi.
- Robot konuşurken mikrofonu kapatmak (yarım dupleks, en basit barge-in çözümü).
- Konuşmacıyı 30–50 cm'ye çağıran fiziksel tasarım.
- Motor gürültüsünün mikrofondan yalıtılması.

## KVKK
Yüz tanıma biyometrik veridir, yani **özel nitelikli kişisel veri**. 7499 sayılı Kanun'la 1 Haziran 2024'ten itibaren işleme şartları genişledi, ama bir fuar robotu için pratikte geçerli dayanak hâlâ **açık rıza**. Açık rıza özgür iradeyle ve bilgilendirilerek verilmeli. Kurul 2026/921 sayılı ilke kararında mesai takibinde biyometri kullanımını açık rızayla bile sınırladı; bu, orantılılık ilkesinin ne kadar sıkı uygulandığını gösteriyor.

Önerim:
- Yüz **algılama** yapılmalı, kimlik tespiti değil; görüntü diske kaydedilmemeli.
- Robotun üzerinde ve stantta **aydınlatma metni** bulunmalı: "Kamera kullanılır, kayıt yapılmaz."
- Bulut VLM'e yalnız kişi düğmeye basınca tek kare gönderilmeli. Bu yurt dışına aktarım sayılır, aydınlatma metninde belirtilmeli.
- Üniversitenin KVKK birimine danışılmalı. Ben avukat değilim.

## A ve B karşılaştırması
| Ölçüt | A: Yalnız ses | B: Ses + görüntü (tam) |
|---|---|---|
| Geliştirme süresi (tahmini, YZ destekli) | ~150–220 saat | ~270–410 saat |
| Öğrenme eğrisi | Orta: ses aygıtları, asyncio | Yüksek: ek olarak eşzamanlılık, CPU/ısı, kamera kalibrasyonu |
| En çok takılınan yer | Ses kartı ve ALSA ayarları, gürültü, Wi-Fi | Yukarıdakiler + kafa takibinde salınım (PID ayarı), FPS düşüşü, Pi'nin ısınıp yavaşlaması |
| Fuar etkisi | Konuşur ama "bakmaz" | Göz teması ve "ne görüyorsun" etkisi çok yüksek |
| Donanım | Pi 5 yeterli | Hafif B için Pi 5 yeterli; YOLO ve poz birlikte gerekirse AI HAT+ |
| Hukuk | Ses kaydı için aydınlatma yeterli | Kimlik tespiti yapılırsa açık rıza + özel nitelikli veri yükü |

**Yapay zekâ kodlama asistanı nerede hızlandırır, nerede yetmez?** Asistanlar API bağlantı kodunu, durum makinesini, seri protokolü ve PID iskeletini hızlıca yazar; bu kısımlarda tahminen 2–3 kat kazanç sağlar. Şunları yapamazlar:
- Servo akım çekişinin Pi'yi yeniden başlatması (brownout; en sık görülen arıza).
- Kablo ve toprak hataları.
- USB ses aygıtı numaralarının değişmesi.
- PID'in gerçek robot üzerinde ayarlanması.
- Motor elektriksel gürültüsünün mikrofona sızması.
- Fuar akustiğinde gecikme ayarı.

Bu kısımlar ölçmeyi ve denemeyi gerektirir; ekibin mekanik ve montaj gücü tam burada işe yarar.

## Aylık işletme maliyeti (tahmini)
**Varsayımlar:** Fuar günü 6 saat, 60 etkileşim. Etkileşim başına 3 tur; kullanıcı turu 5 s, robot turu 10 s (~150 karakter).

| Hat | Etkileşim başına | Fuar günü | Ay (4 demo günü + ~300 geliştirme etkileşimi ≈ 540 etkileşim) |
|---|---|---|---|
| Ardışık bulut (Deepgram + Gemini Flash + Chirp 3 HD) | ~0,02 $ | ~1,2 $ | ~11 $ |
| Aynısı, TTS olarak Piper | ~0,007 $ | ~0,4 $ | ~4 $ |
| Gemini Live | ~0,015–0,03 $ | ~1–2 $ | ~8–16 $ |
| gpt-realtime-2.1 / mini | ~0,06–0,11 $ / ~0,02–0,05 $ (dk başına kaynaklı tahmin) | ~3,6–6,6 $ / ~1,2–3 $ | ~30–60 $ / ~11–27 $ |
| B ek maliyeti: VLM | ~0,002 $/soru | <0,1 $ | <1 $ |

Gemini'nin ücretsiz katmanı geliştirme aşamasının maliyetini neredeyse sıfıra indirebilir. Ancak ücretsiz katmandaki veriler model eğitiminde kullanılabilir, bu yüzden demo sırasında ücretli katman tercih edilmeli. İşletme maliyeti ayda **10–20 $ düzeyinde**; asıl maliyet donanım.

## Önerim
**Önce A, sonra "hafif B", tam B hiç değil.**
1. **1. aşama:** Ses hattı (düğme tetik, Deepgram, Gemini Flash veya Haiku, Chirp 3 HD), ESP32 sürüşü, teleop ve jest kütüphanesi. Fuara bu hâliyle bile çıkılabilir.
2. **2. aşama (eklenti modül):** MediaPipe ile yüz algılayıp kafayı kişiye çevirmek ve düğmeyle tetiklenen bulut VLM. Pi 5 CPU'su bunu kaldırır, ek kart gerekmez. Tahminen +60–90 saat, etkisi çok yüksek.
3. **Yapılmamalı:** Yüz tanıma (KVKK yükü ve lisans sorunu, fuarda kazancı az), Nav2/SLAM, Jetson.

Gerekçe: Ekibin gücü mekanikte. Görüntünün "canlılık" hissi kafa takibinden ve VLM'den geliyor, kimlik tanımadan değil. Modüler yapı sayesinde 2. aşama yetişmezse 1. aşama tek başına çalışan bir ürün olarak kalır.

## Kaynaklar
- Whisper / Pi 5: https://bmdpat.com/blog/raspberry-pi-5-local-voice-ai-2026 · https://dl.acm.org/doi/10.1145/3769102.3774244
- Whisper Türkçe: https://huggingface.co/selimc/whisper-large-v3-turbo-turkish · https://github.com/openai/whisper/discussions/1762
- Jetson + whisper.cpp: https://thomasthelliez.com/blog/run-whisper-cpp-with-cuda-on-jetson-orin-nano-super/ · https://github.com/NVIDIA-AI-IOT/whisper_trt
- Uyandırma kelimesi: https://github.com/dscripka/openWakeWord · https://picovoice.ai/docs/faq/porcupine/
- Vosk: https://alphacephei.com/vosk/models
- Deepgram Türkçe: https://deepgram.com/learn/deepgram-expands-nova-3-with-italian-turkish-norwegian-and-indonesian-support · https://deepgram.com/pricing
- Fiyatlar: https://developers.openai.com/api/docs/pricing · https://ai.google.dev/gemini-api/docs/pricing · https://platform.claude.com/docs/en/about-claude/pricing · https://www.layer3labs.io/guides/openai-realtime-api-pricing
- Gemini Live dilleri: https://ai.google.dev/gemini-api/docs/live-api/capabilities
- Metinden sese: https://github.com/rhasspy/piper/blob/master/VOICES.md · https://docs.cloud.google.com/text-to-speech/docs/chirp3-hd · https://elevenlabs.io/docs/overview/models
- Gecikme bütçesi: https://livekit.com/blog/voice-agent-architecture-stt-llm-tts-pipelines-explained · https://thepromptbench.com/voice-and-realtime/latency-budgets-for-realtime-voice/
- Mikrofon: https://thepihut.com/products/respeaker-xmos-xvf3800-ai-powered-4-mic-array-for-clear-voice-even-in-noise
- YOLO: https://docs.ultralytics.com/guides/raspberry-pi · https://www.ultralytics.com/blog/ultralytics-yolo11-on-nvidia-jetson-orin-nano-super-fast-and-efficient · https://www.myaihardware.com/compare-article/jetson-orin-nano-super-vs-raspberry-pi-5-hailo
- MediaPipe: https://github.com/youssefmedhat4/dms-face · https://lb.lax.hackaday.io/project/203704-gesturebot/log/242569-mediapipe-pose-detection-real-time-performance-analysis
- InsightFace lisansı: https://github.com/deepinsight/insightface/blob/master/python-package/README.md
- Donanım fiyatları: https://www.cnx-software.com/2026/07/22/nvidia-increases-the-price-of-jetson-modules-and-devkits-by-up-to-101/ · https://www.raspberrypi.com/news/more-memory-driven-price-rises/ · https://www.raspberrypi.com/products/ai-hat/
- Yerel LLM: https://www.stratosphereips.org/blog/2025/6/5/how-well-do-llms-perform-on-a-raspberry-pi-5 · https://www.muratkarakaya.net/2026/01/turkce-icin-ucretsiz-ve-guclu-bir.html
  - Not: Pi 5'te 1–3B modeller 5–20 token/sn üretiyor ve Türkçeleri zayıf; sohbet için önermiyorum.
- KVKK: https://www.erdem-erdem.av.tr/bilgi-bankasi/kisisel-verilerin-korunmasi-kanununda-neler-degisti · https://www.kvkk.gov.tr/Icerik/8762/mesai-takibi-amaciyla-biyometrik-veri-islenmesi-hakkinda-kisisel-verileri-koruma-kurulunun-29-04-2026-tarihli-ve-2026-921-sayili-ilke-kararina-iliskin-kamuoyu-duyurusu
- ROS 2 ve seri haberleşme: https://github.com/joshnewans/serial_motor_demo · https://dev.to/admantium/robotic-projects-reasons-for-switching-from-ros2-to-ros1-4ka9

**Kesinlik notu:** Saat tahminleri, etkileşim başına maliyetler ve gecikme bütçesi benim tahminlerim; kaynaklardaki birim fiyatlardan hesaplandı. FPS ve fiyat rakamları kaynaklardan alındı. Vault'ta hiçbir dosya değiştirmedim.
