> Kaynak: Efe'nin vault'undaki araştırma raporu (27 Ekim 2026), üç Sonnet 5.5 araştırmacı raporu + Kimi incelemesinin sentezi. Fiyatlar ve ölçümler o güne ait; satıcı/sağlayıcı sayfalarından teyit edin.

# Lale'nin yapay zekâ beyni: çok modlu model, benzer projeler, görüntü hattı (2026-10-27)

## Kısa sonuç
**Efe kararı (2026-10-27, bu rapordan sonra): yerel model kullanılmayacak, dil/görüntü modeli API üzerinden.** Aşağıdaki cihaz üstü model tablosu bu kararın gerekçesi olarak kalır (ölçümler), uygulanmaz.

1. **Beyin bulutta, refleksler cihazda.** Pi 5'te görüntü de işleyen bir dil modeli konuşma hızında çalışmıyor: en iyi belgeli ölçüm Gemma 4 E2B (LiteRT-LM) ile saniyede 9 token ve ilk token 7-8 s; Gemma 3n E2B ~6 token/s; Moondream 2B'de görüntü kodlama tek başına ~29 s. 2,5 s hedefi cihazda tutmuyor. Bulutta Gemini 3.1 Flash-Lite ya da Claude Haiku 5.5 görüntü dahil yılda ~5-10 $ (günde 100 tur, %20'si görüntülü varsayımıyla); bütçe 3.000 TL.
2. **Claude modelleri görüntü işliyor** (Haiku 5.5 / Sonnet 5.5 / Opus 5.5 resim girişi alır); "Claude olmaz" varsayımı doğru değil. Gemini Flash-Lite daha ucuz ve ses girişi de var; ikisi de aday. Karar 50 soruluk Türkçe testle (20'si görüntülü) verilir.
3. **Cihazda kalanlar:** VAD (Silero ya da mevcut webrtcvad), Vosk STT, Piper TTS, yüz/kişi algılama (YuNet ya da MediaPipe, Pi 5 CPU, lores akış), ArUco ve yer tanıma (mevcut konum paketi), kural tabanlı yedek cevap. İnternet kesilince kural tabanlı + "şu an göremiyorum" (Efe kararıyla yerel dil modeli yedeği de yok).
4. **Hızlandırıcı şimdi alınmaz.** AI HAT+ (Hailo-8, 26 TOPS, ~6.600 TL) yalnız yüz takibi CPU'da yetmezse; AI HAT+ 2 (Hailo-10H, 200 $) LLM/VLM çalıştırıyor ama ölçülen LLM hızı CPU'dan düşük, VLM süre ölçümü yok.
5. **Feyz alınacak proje: Pollen `reachy_mini_conversation_app`** (Apache-2.0): LLM jestleri araç çağrısıyla üretiyor (`move_head`, `play_emotion`, `camera`), Silero VAD ile araya girme (barge-in), konuşurken baş sallama katmanı. Bizim BEKLE→DİNLE→DÜŞÜN→JEST→KONUŞ yapısına doğrudan uyuyor.
6. **Türkçe uyandırma sözü çözümsüz:** openWakeWord yalnız İngilizce (kendi "Lale" modeli eğitilebilir, Türkçe sentetik veri kalitesi belirsiz), Porcupine'de Türkçe yok. VAD ile başlamak (mevcut) doğru karar.

## A. Çok modlu model seçenekleri

### Cihaz üstü (Pi 5, 8 GB)
| Model | Türkçe | Pi 5 ölçümü | Karar |
|---|---|---|---|
| Gemma 3 1B (metin) | 140+ dil iddiası | ~10 token/s, 1,1 GB (Ollama Q4) | yerel metin yedeği olabilir |
| Gemma 3 4B (görüntülü) | 140+ dil | ~5 token/s (QAT), görüntü ölçümü yok | hayal |
| Gemma 3n E2B / E4B (ses+görüntü) | 140+ dil; ses girişi dilleri belirsiz | ~6 / ~2,5 token/s, çok modlu ölçüm yok | sınırda / hayal |
| Gemma 4 E2B (LiteRT-LM, Apache-2.0) | belirsiz | decode 9 token/s, ilk token 7,8 s (16 GB'ta), görüntü destekli | cihazdaki en umut verici, yine de 2,5 s'yi aşar |
| SmolVLM2 | yalnız İngilizce | Pi ölçümü yok | elenir |
| Moondream 2 | belirsiz | görüntü kodlama ~29 s | hayal |
| Qwen2.5/3-VL 3B | doğrulanmadı | metin 5 token/s, VLM ölçümü yok | muhtemelen hayal |

### Bulut ($/1M token, 27.10.2026)
| Model | Giriş | Çıkış | Not |
|---|---|---|---|
| Gemini 2.5 Flash-Lite | 0,10 | 0,40 | en ucuz |
| Gemini 3.1 Flash-Lite | 0,25 | 1,50 | öneri adayı |
| Gemini 3.x Flash | 0,75 (1 Oca 2027: 1,50) | 3,75 (7,50) | fiyat artışı |
| Claude Haiku 5.5 | 0,10 | 0,50 | görüntü var, öneri adayı |
| Claude Sonnet 5.5 / Opus 5.5 | 2 / 4 | 10 / 20 | kalite yüksek, bu iş için pahalı |
| Kimi K2.6 / K3.1 Pro | 0,95 / 2,00 | 4,00 / 10,00 | Türkçe ölçümü yok, Moonshot ucunda yavaş (K2.6 ~36 token/s, ilk token ~2,6 s), K3.1 23 Ekim'de çıktı |

Gemini ücretsiz katmanında Google içerikleri ürün geliştirmede kullanabiliyor → ziyaretçi görüntüsü gidecekse ücretli katman (KVKK). Bulut gecikmesi ve Türkçe kalitesi için güvenilir bağımsız ölçüm bulunamadı; deneyle ölçülecek.

## B. Benzer açık kaynak projeler (yıldız / son push / lisans, GitHub API 27.10.2026)
| Proje | Ne öğreniriz |
|---|---|
| [Reachy Mini](https://github.com/pollen-robotics/reachy_mini) 1597 / 2026-10-27 / Apache-2.0 | SDK'da YuNet (ONNX) yüz takibi daemon'u; uygulamaları HF Spaces ile dağıtma |
| [reachy_mini_conversation_app](https://github.com/pollen-robotics/reachy_mini_conversation_app) 338 / 2026-10-26 / Apache-2.0 | araç çağrısıyla jest/yön, Silero VAD 400 ms, konuşurken ses %25'e düşüp barge-in, profil başına araç beyaz listesi |
| [Stack-chan](https://github.com/stack-chan/stack-chan) 1822 / Apache-2.0 | animasyonlu yüz düzenleyici, tarayıcı simülatörü, MOD galerisi (içerik yönetimi) |
| [Open Duck Mini](https://github.com/apirrone/Open_Duck_Mini) 4537 / Apache-2.0 | sevimlilik, ONNX'i Pi'de çalıştırma; konuşma yok |
| [huggingface/speech-to-speech](https://github.com/huggingface/speech-to-speech) 13578 / Apache-2.0 | VAD→STT→LLM→TTS modüler boru hattı (bizim sağlayıcı arayüzleriyle aynı fikir) |
| [xiaozhi-esp32](https://github.com/78/xiaozhi-esp32) 32057 / MIT | ESP32'de MCP ile cihaz araçlarını açma deseni |
| [Jetson NanoLLM](https://github.com/dusty-nv/NanoLLM) [eski] | araya girilebilir sesli sohbet + canlı VLM; Jetson gerekir |
| [llm_voice_chatbot_rpi](https://github.com/zhoupingjay/llm_voice_chatbot_rpi) [eski] | tam çevrimdışı Pi hattı örneği |

Doğrulanamayan: Misty deposu 404; Türkiye/Teknofest'ten açık kaynak karşılama robotu bulunamadı.

**Mimari dersler:** (1) JEST ve KONUŞ ardışık değil paralel katman olsun (konuşurken baş sallama). (2) Çift VAD: yerel hızlı tepki + tur kararı; barge-in. (3) LLM serbest metin yerine araç çağrısı: kayıtlı jest listesi = araç listesi, kural tabanlı yedekte sınırlı sözlük. (4) Kamera tek süreçte yakalanıp paylaşılır. (5) Araç beyaz listesi.

**Alınabilir parçalar:** Silero VAD (LICENSE dosyası MIT; README rozeti CC BY-NC der, çelişki), MediaPipe (Apache-2.0), YuNet (OpenCV), Vosk (zaten), Piper: yeni depo `piper1-gpl` **GPL-3.0** (eski sürümler MIT) → kodu dağıtırsak lisans etkisi, not alındı.

**Literatür (TÜBİTAK'a aday):** Mauliana vd. 2025 (DOI 10.3389/frobt.2025.1585589; RAG+LLM yanıt 6-15 s, ASR hataları turu düşürüyor), Herath vd. 2025 (DOI 10.1038/s41598-025-04274-z; ChatGPT'li Pepper, yavaş yanıt eleştirisi), Galatolo & Winkle 2025 (DOI 10.3389/frobt.2025.1581024; küçük model + jest başı, Jetson'da 8B int4 ~5,5 token/s), INDI, MDPI Computers DOI 10.3390/computers15090582 (düşük maliyetli LLM kampüs rehber robotu; tam metin okunmadı, en yakın rakip/atıf adayı).

## C. Pi 5 görüntü hattı
- Picamera2 ile tek yakalama iş parçacığı, `main` (ArUco / bulut VLM karesi) + `lores` (yüz/kişi) akışı; en son kare kilitli tek yuvada, tüketiciler kendi hızında okur, kuyruk birikmez.
- Yüz algılama: OpenCV YuNet ya da MediaPipe BlazeFace, CPU. Pi 5 FPS ölçümü kaynaklarda yok → **ilk iş kendimiz ölçeriz.** Kişi/poz gerekirse YOLO11n ONNX ~6,8 FPS, YOLO26n NCNN ~67 ms (Ultralytics rehberi).
- Mesafe: yüz kutusu boyundan kalibrasyonla (ya da ToF); histerezis (gir 2 m / çık 3 m gibi) + N ardışık kare.
- Kalabalıkta muhatap: **XVF3800 DoA veriyor** (`xvf_host AEC_AZIMUTH_VALUES`, 4 azimut); VAD aktifken DoA açısına en yakın yüz kutusu seçilir, kafa oraya döner.
- "Ne görüyorsun": kare küçült, JPEG, buluta; internet yoksa "göremiyorum".
- KVKK: yüz tanıma yok, kayıt yok, kare diskte tutulmaz; bulut VLM'e kare gidiyorsa levhada yazılır, sağlayıcının veri politikası doğrulanır (hukuki görüş değil).
- Ölçülecek 3 metrik: yakalama→servo gecikmesi ve FPS (tüm tüketiciler açıkken); yanlış selamlama / kaçırma oranı; "ne görüyorsun"dan ilk sese süre.

## D. Önerilen yol ve ilk hafta deneyleri
**Asıl:** Vosk yerel → metin + (gerekirse) 1 JPEG → Gemini 3.1 Flash-Lite ya da Haiku 5.5 (akışlı; Piper ilk cümleyi hemen okur) → jest/yön araç çağrısıyla. **Yedek:** yalnız kural tabanlı (mevcut); görüntüye "göremiyorum". Yerel model yok (Efe). **Donanım:** şimdilik Pi 5 CPU; robota kendi interneti (USB 4G / hotspot).

Deneyler: (1) 50 Türkçe soru (20 görüntülü), Flash-Lite vs Haiku 5.5: konuşma bitişi → ilk ses süresi, doğruluk, uydurma; (2) Wi-Fi kesme testi: yedeğe düşme süresi, zaman aşımı (~1,5 s); (3) Pi 5 CPU'da YuNet/BlazeFace FPS ve kafa takibi gecikmesi. (Gemma 4 E2B cihaz deneyi Efe kararıyla düştü.)

## Riskler / bilinmeyenler
Gemma 4 ve Gemini 3.x çok yeni, Türkçe ölçümü yok; Gemini Flash fiyatı 1 Ocak 2027'de artıyor; görüntü başına token sayısı doğrulanmadı; Hailo hız verileri çelişkili; Reachy uygulaması README'den okundu, kod okunmadı; XVF3800 Pi 5'te sıcak yeniden başlatma hatası (mikrofon raporu).

## Kaynaklar
Gemini fiyat https://ai.google.dev/gemini-api/docs/pricing · Anthropic fiyat https://platform.claude.com/docs/en/about-claude/pricing · Google blog Pi 5 Gemma 4 (2026-08-11) https://developers.googleblog.com/mastering-edge-ai-on-raspberry-pi-with-litert-and-gemma/ · LiteRT-LM Gemma 4 https://developers.google.com/edge/litert-lm/models/gemma-4.md.txt · Gemma 3n https://ai.google.dev/gemma/docs/gemma-3n · Gemma 3 Pi 5 benchmark https://www.kunalganglani.com/blog/gemma-3-raspberry-pi-5-benchmark.md · SmolVLM2 https://huggingface.co/HuggingFaceTB/SmolVLM2-2.2B-Instruct · AI HAT+ 2 LLM https://www.hardware-corner.net/local-llms-raspberry-pi-ai-hat-plus-2/ · AI HAT+ 2 inceleme https://www.cnx-software.com/2026/01/20/raspberry-pi-ai-hat-2-review-a-40-tops-ai-accelerator-tested-with-computer-vision-llm-and-vlm-workloads/ · RPi AI belgesi https://www.raspberrypi.com/documentation/computers/ai.html · Robotistan AI HAT https://www.robotistan.com/raspberry-pi-ai-hat · Ultralytics Pi rehberi https://docs.ultralytics.com/guides/raspberry-pi · Moondream Pi forum https://forum.dexterindustries.com/t/moondream-vision-language-assistant-on-gopigo3-robot-kilted-dave/10750 · XMOS XVF3800 DoA https://www.xmos.com/documentation/XM-014888-PC/html/modules/fwk_xvf/doc/user_guide/03_using_the_host_application.html · Seeed XVF3800 https://wiki.seeedstudio.com/respeaker_xvf3800_introduction/ · Picamera2 capture https://tessl.io/registry/tessl/pypi-picamera2/files/docs/capture.md · Reachy yüz takibi https://huggingface.co/docs/reachy_mini/examples/head_tracking.md · Silero VAD https://github.com/snakers4/silero-vad · openWakeWord https://github.com/dscripka/openWakeWord · Porcupine diller https://picovoice.ai/docs/porcupine/ · Piper GPL https://github.com/OHF-Voice/piper1-gpl · Cetvel https://arxiv.org/abs/2508.16431 · TurkBench https://arxiv.org/html/2601.07020v2 · Kimi K3.1 Pro https://simonwillison.net/2026/Oct/23/kimi-k31-pro/ · Kimi fiyat https://benchlm.ai/moonshot/api-pricing · Kimi hız https://artificialanalysis.ai/models/comparisons/kimi-k3-vs-kimi-k2-6
