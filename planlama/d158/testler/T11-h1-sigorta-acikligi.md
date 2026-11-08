# T11 · H1 servis kapağı: sigorta kutusu açıklığı

Kâğıt T11 / 13 · Lale 1,58 m · sürüm 08.11.2026

| Tarih | Ölçen | Yazan | Kontrol eden | Alet markası/modeli |
|---|---|---|---|---|
| | | | | |

## Amaç

Satın alınan 6 yollu sigorta kutusunu ölçmek ve eteğin arkasındaki H1 servis kapağı açıklığından (64 × 50 mm) **hangi sigortaların
kapak açılınca çekilip takılabildiğini** saymak.

## Neden önemli

Sigortalar etek üst plakasındaki H1 kapağının altında. Modelde kutu tahmini bir zarf (105 × 60 mm), açıklık 64 × 50 mm. Kutu 1 × 6
dizilişliyse uçtaki iki sigorta kapağın altında kalır, 2 × 3 dizilişte altısı da açıkta (`Y3-kontrol.md:41-42`). Karar: açıklık aynı kalır,
kutu alınınca ölçülür, kapak altında kalan uç yuvalar yedeğe ayrılır; sık değişecek F1, F3, F4, F5 ortadaki dört yuvaya (`kararlar:114-115`,
`elektrik.md:345-347`). Bu kâğıt o ölçümdür. Açıkta dört yuva yoksa karar yeniden açılır.

### Doğruladığı varsayım

| Değer | Kaynak | Durum |
|---|---|---|
| Sigorta kutusu 6 yollu | `elektrik.md:290` | Tasarım |
| Kutu zarfı 105 × 60 × 35 mm, merkez (x 0, z −203), bağlantı delikleri x ±47, z −213 | `arayuz.py:655` | **Tahmini zarf** (gerçek kutu yok) |
| H1 açıklığı x −32…32, z −228…−178 (64 × 50 mm), köşe yarıçapı 8 mm; açıklığın merkezi kutu merkezinin üstünde (x 0, z −203) | `arayuz.py:973`, `kararlar:114` | Karar 29.10 |
| 1 × 6 dizilişte uçtaki 2 yuva kapak altında, 2 × 3'te 6'sı açıkta | `Y3-kontrol.md:41-42` | Tahmini kutuyla hesap (1,65 m modeli) |
| Uç iki yuva yedek (F2 15 A ve boş yuva); F1, F3, F4, F5 ortadaki dört yuvada | `elektrik.md:345-347` | Karar 29.10 |
| Kutu üstü ile etek plakası arası 45 mm (sigorta pensesi için yeterli) | `M6-montaj-sirasi.md:228` | 125 cm modelinde ölçüldü; 1,58 m'de yeniden ölçülmedi |

## Gereken alet

- Kumpas (0,05 mm), çelik cetvel, kalem
- **Karton şablon:** sert kartona 64 × 50 mm, köşeleri 8 mm yarıçaplı bir pencere kes; pencerenin merkezini ve uzun kenar doğrultusunu işaretle.
  Şablonun kenarlarını kutudan en az 30 mm taşacak kadar büyük bırak.
- Şablonu yükseltmek için 4 eşit takoz (tahta, kitap ya da karton yığını): kutunun yanına konur, üstü kutu üstünden **45 mm** yukarıda
  (`M6-montaj-sirasi.md:228`; gerçek etek plakasının yüksekliği)
- Kutuyla gelen sigorta pensesi (yoksa küçük plastik pense), sigorta seti (standart ve mini bıçak, `elektrik.md:341-344`)
- Basılmış etek ve H1 kapağı varsa onlar (adım 6)

## Güvenlik

- Ölçüm tezgâhta, **kablosuz yeni kutuyla** yapılır. Kutu robotta takılı ve kabloluysa: önce akünün XT60'ını ayır ve ana 30 A sigortayı çıkar;
  enerji varken sigorta çekilmez, kutuya metal alet sokulmaz (akü kısa devrede çok yüksek akım verir).
- Saat, yüzük, bileklik çıkar. Maket bıçağıyla şablon keserken kesme altlığı kullan, bıçağı kendine doğru çekme.

## Yöntem

1. Kutunun marka/modelini, yuva sayısını ve sigorta tipini (standart / mini bıçak) yaz. Fotoğrafını çek (`T11-kutu-1.jpg`).
2. **Diziliş:** ☐ 1 × 6 ☐ 2 × 3 ☐ başka (çiz). Yuvaları numarala: uzun kenar boyunca soldan sağa 1, 2, 3 …; iki sıra varsa üst sıra önce.
3. **Dış ölçü:** kutunun en büyük boyu (uzun kenar, modelde x), eni (modelde z) ve yüksekliği (taban yüzünden kapaksız en üst noktaya), kumpasla.
   Bağlantı deliklerinin sayısını, çapını ve **merkezden merkeze aralığını** yaz; deliklerin kutu dış kenarlarına uzaklığını da yaz
   (tasarım ajanı taban deliklerini buna göre koyar).
4. **Şablon denemesi:** modelde açıklığın merkezi kutunun merkezinin tam üstünde (x 0, z −203; `arayuz.py:655`, `arayuz.py:973`). Kutunun dış
   çerçevesinin merkezini kalemle bul (iki köşegen). Her yuvaya bir sigorta tak. Şablonu kutunun üstüne değil, kutunun yanındaki **takozların üstüne** koy:
   şablon kutu üstünden 45 mm yukarıda durur (gerçek düzende pense ve el bu yükseklikteki açıklıktan iner). Pencere merkezi kutu merkezinde,
   pencerenin 64 mm'lik kenarı kutunun uzun kenarına paralel. (Varsayım: gerçek kutu da dış çerçevesinin merkezi bu noktaya gelecek biçimde
   bağlanır; delikleri farklıysa tasarım ajanı taban deliklerini buna göre yeniden koyar.)
5. Şablonun tam üstünden (yandan değil) bak. Her yuva için yaz: sigortanın üstten görünen başı **tamamen** pencerenin içinde mi; içindeyse
   başın pencere kenarına en yakın mesafesi (mm, cetvelle). Sonra şablonu kaldırmadan sigortayı pensle tut ve çek: pense pencere kenarına
   değmeden çıkıyor mu? Sigortayı geri tak.
6. **Gerçek kapakla (varsa):** etek ve H1 kapağı basıldıysa kutuyu yerine bağla (kablosuz), kapağı aç, her sigortayı pensle çek ve tak.
   Kutu üstü ile etek plakası arasındaki yüksekliği yaz.

## Kayıt tablosu

Kutu: ______________________  Diziliş: ☐ 1 × 6 ☐ 2 × 3 ☐ başka   Sigorta tipi: ☐ standart ☐ mini

Dış ölçü: uzun kenar ______ mm × en ______ mm × yükseklik ______ mm   Bağlantı deliği: ______ adet, Ø ______ mm, aralık ______ mm

Deliklerin kenarlara uzaklığı: ____________________   Kutu üstü – etek plakası (adım 6): ______ mm

| Yuva | Pencerede tamamen mi (şablon) | Pencere kenarına en yakın (mm) | Pense ile çıktı mı (şablon) | Gerçek kapakla çıktı mı |
|---|---|---|---|---|
| 1 | ☐ evet ☐ hayır | | ☐ evet ☐ hayır | ☐ evet ☐ hayır ☐ yapılmadı |
| 2 | ☐ evet ☐ hayır | | ☐ evet ☐ hayır | ☐ evet ☐ hayır ☐ yapılmadı |
| 3 | ☐ evet ☐ hayır | | ☐ evet ☐ hayır | ☐ evet ☐ hayır ☐ yapılmadı |
| 4 | ☐ evet ☐ hayır | | ☐ evet ☐ hayır | ☐ evet ☐ hayır ☐ yapılmadı |
| 5 | ☐ evet ☐ hayır | | ☐ evet ☐ hayır | ☐ evet ☐ hayır ☐ yapılmadı |
| 6 | ☐ evet ☐ hayır | | ☐ evet ☐ hayır | ☐ evet ☐ hayır ☐ yapılmadı |

Açıkta (pencerede tamamen + kenara ≥ 3 mm + pense ile çıktı) yuva sayısı: ______   Bu yuvalar: ______

## Geçer / kalır sınırı

Bir yuva "açıkta" sayılır: sigorta başı şablon penceresinin tamamen içinde, pencere kenarına **en az 3 mm** (varsayım: pense çenesi için yer)
ve pense kenara değmeden sigortayı çıkarıyor. Gerçek kapakla deneme yapıldıysa o sonuç esastır.

| Ölçüt | GEÇER | Kaynak |
|---|---|---|
| Açıkta yuva sayısı | **≥ 4** (F1, F3, F4, F5 için) | `elektrik.md:345-347`, `kararlar:114-115` |
| Kutu dış ölçüsü (uzun kenar × en × yükseklik) | **≤ 105 × 60 × 35 mm** | `arayuz.py:655` (tahmini zarf) |
| Bağlantı delikleri | modelle aynı: **iki delik, aralık 94 ± 0,5 mm** (x ±47) | `arayuz.py:655`; ±0,5 mm **varsayım** (taban deliği boşluğu) |

Sonuç:
- Üçü de sağlanırsa **GEÇER**.
- Açıkta yuva ≥ 4 ama dış ölçü zarftan büyük ya da delikler farklıysa **KOŞULLU**: kapak kararı geçerli, ama model kutunun gerçek
  ölçüsüyle yeniden kontrol edilmeli (taban delikleri, kapak cıvata boss'ları, acil stop ve ana anahtar yakınlığı).
- Açıkta yuva < 4 ise **KALIR**.

## Sınır aşılırsa

- **KALIR (açıkta yuva < 4):** `karar-kuyrugu.md` **K8** (H1 sigorta erişimi, "kapandı") yeniden açılmak üzere **Ahmet Yorulmaz**'a gider.
  Kaynaktaki seçenekler: kutuyu açıklığın altına başka biçimde ortalamak ya da dolgu şeridi dikişlerini kaydırıp açıklığı ±44'e çıkarmak
  (kabuk yeniden; `Y3-kontrol.md:107-108`). Hangisi olursa olsun sigortalar yerleşmeden kutu kablolanmaz.
- **KOŞULLU:** ölçüler ve fotoğraf tasarım ajanına verilir; `arayuz.py:655` `sigorta_kutusu` zarfı gerçek ölçüyle güncellenir, taban ve kabuk
  yeniden kontrol edilir.
- **Her sonuçta:** hangi sigortanın hangi yuvaya gireceği (uç yuvalar yedek, F1, F3, F4, F5 açıktaki yuvalara) kutunun yanına etiketle
  yazılır ve `elektrik.md` sigorta listesine (`elektrik.md:327-347`) işlenmek üzere tasarım ajanına verilir.

## Sonuç

☐ GEÇER  ☐ KOŞULLU  ☐ KALIR    Açıkta yuva: ______ / 6   Dış ölçü: ______ × ______ × ______ mm

Ölçen imza: ____________  Kontrol eden imza: ____________

Kaynak dosyalar için kısaltma tablosu: [00-genel.md](00-genel.md).
