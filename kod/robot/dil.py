# Ne yapıyor: kullanıcının sorusuna cevap üretir. Tüm üreticiler aynı arayüzü kullanır: cevapla(soru, bolge=None) -> Cevap.
# bolge: robotun şu an bulunduğu bölge (robot/konum); yer tariflerinde bölgeye özel tarif ve işaret yönü seçilir.
# KuralTabanli internetsiz çalışır: önce içerik paketinde arar, sonra selam/teşekkür gibi kalıplara bakar.
# BulutDilModeli Gemini ya da Anthropic ile sohbet eder (son N tur hafızada); sorun olursa KuralTabanli'ye düşer.

import os
from collections import deque
from dataclasses import dataclass

from robot.icerik import ifade_geciyor_mu, kelimeler

BILMIYORUM = "Bunu bilmiyorum, sizi bir görevliye yönlendireyim."
EN_FAZLA_TOKEN = 200          # 1-2 cümle için yeter
GECMIS_TUR = 6                # sohbet hafızası: son kaç soru-cevap turu hatırlansın (ayar: dil.gecmis_tur)
BULUT_ZAMAN_ASIMI = 15.0      # saniye; internet yavaşsa robot sonsuza kadar beklemesin


@dataclass
class Cevap:
    metin: str
    jest: str | None = None   # ESP32'ye gidecek jest adı (selam, isaret, evet; kod/jestler/ ile aynı) ya da None
    konu: str | None = None   # günlük için: eşleşen içerik başlığı, "kalıp:..." ya da None (bilmiyorum)
    puan: int = 0             # günlük için: içerik eşleşme puanı (kalıpta 0)
    yon: str | None = None    # işaret jestinin yönü (sol, sag, ileri, arka) ya da None (yönsüz, eski biçim)


class SohbetGecmisi:
    """Son N soru-cevap turu. Bulut modeline mesaj geçmişi olarak gider; kural tabanlıda yalnız kayıttır."""

    def __init__(self, tur=GECMIS_TUR):
        self.turlar = deque(maxlen=max(int(tur), 0))   # dolunca en eski tur kendiliğinden düşer

    def ekle(self, soru, cevap):
        self.turlar.append((soru, cevap))

    def mesajlar(self):
        """[{"role": "user", ...}, {"role": "assistant", ...}, ...] biçiminde, eskiden yeniye."""
        liste = []
        for soru, cevap in self.turlar:
            liste.append({"role": "user", "content": soru})
            liste.append({"role": "assistant", "content": cevap})
        return liste


class KuralTabanli:
    """Her zaman çalışan, internetsiz cevap üretici (varsayılan)."""

    def __init__(self, paket, robot_adi="Robot", gecmis_tur=GECMIS_TUR):
        self.paket = paket
        self.robot_adi = robot_adi
        self.kaliplar = self._kaliplari_kur()
        self.gecmis = SohbetGecmisi(gecmis_tur)

    def _kaliplari_kur(self):
        # (soruda geçen ifadeler, cevap, jest). Sıra önemli: ilk tutan kazanır.
        konular = ", ".join(self.paket.konu_basliklari()[:3])
        return [
            (["kimsin", "adın ne", "adın"], f"Ben {self.robot_adi}, {self.paket.rol}.", "selam"),
            (["neler yapabilir", "ne yapabilir", "yardım"],
             f"Bana şu konularda soru sorabilirsiniz: {konular}.", None),
            (["nasılsın", "naber"], "İyiyim, teşekkür ederim. Size nasıl yardımcı olabilirim?", None),
            (["teşekkür", "sağ ol", "sağol", "eyvallah", "mersi"], "Rica ederim, her zaman!", None),
            (["hoşça kal", "görüşürüz", "güle güle", "bay bay", "iyi günler"],
             "Hoşça kalın, iyi günler!", "selam"),  # selam jesti zaten el sallama
            (["merhaba", "selam", "günaydın", "iyi akşamlar"], self.paket.selamlama, "selam"),
        ]

    def kalip_bul(self, soru):
        soru_kelimeleri = kelimeler(soru)
        for ifadeler, cevap, jest in self.kaliplar:
            if any(ifade_geciyor_mu(i, soru_kelimeleri) for i in ifadeler):
                return Cevap(cevap, jest, "kalıp:" + ifadeler[0])
        return None

    def cevapla(self, soru, bolge=None):
        cevap = self.cevap_bul(soru, bolge)
        self.gecmis.ekle(soru, cevap.metin)     # kural tabanlı geçmişi kullanmaz, yalnız kaydeder
        return cevap

    def cevap_bul(self, soru, bolge=None):
        """Geçmişe yazmadan cevabı bulur (bulut modeli jest/konu için de bunu kullanır)."""
        # 1) İçerik paketinde eşleşme varsa onu söyle ("merhaba, kantin nerede?" -> kantin tarifi;
        #    robotun bölgesine özel tarif varsa o, yoksa genel tarif)
        eslesme = self.paket.ara(soru)
        if eslesme:
            k = eslesme.kayit
            return Cevap(k.tarif_sec(bolge), k.jest, k.baslik, eslesme.puan, k.yon_sec(bolge))
        # 2) Selam, teşekkür, vedalaşma gibi kalıplar
        kalip = self.kalip_bul(soru)
        if kalip:
            return kalip
        # 3) Hiçbiri değilse kibarca görevliye yönlendir
        return Cevap(BILMIYORUM)


def sistem_istemi(paket, robot_adi, soru, bolge=None):
    """Bulut modeline giden talimat: sohbet eden, kısa cevap veren, içerik paketine öncelik veren
    karşılama robotu. Bölge biliniyorsa "Robot şu an: <bölge>" eklenir. Sonuna içerik paketinden bu soruya
    en uygun 3 bilgi (yerlerde robotun bölgesine göre tarif) eklenir."""
    satirlar = [
        f"Sen {robot_adi} adında, {paket.kurum} için çalışan bir karşılama robotusun ({paket.rol}).",
        "Ziyaretçilerle sesli sohbet ediyorsun: Türkçe, sıcak ve doğal konuş; her cevap en fazla 1-2 kısa cümle.",
        "Cevabın sesli okunacak: madde işareti, emoji, parantez ve kısaltma kullanma.",
        "Kurumla ilgili sorularda önce aşağıdaki bilgilere dayan. Orada olmayan bir olguyu (tarih, saat, yer, "
        "isim, numara, kural) asla uydurma; 'bunu bilmiyorum, görevliye sorabilirsiniz' de.",
        "Selamlaşma, hal hatır, senin hakkındaki sorular ve gündelik sohbette doğal biçimde sohbete devam et; "
        "önceki konuşmayı hatırla ve ziyaretçiye yardımcı olmaya çalış.",
        f"Bildiğin konular: {', '.join(paket.konu_basliklari())}.",
    ]
    if bolge:
        satirlar.append(f"Robot şu an: {bolge}. Yer tariflerini buradan başlayarak ver.")
    baglam = paket.en_iyiler(soru, 3)
    if baglam:
        satirlar.append("Kullanabileceğin bilgiler ('...' bilinmeyen demektir, onu söyleme):")
        for e in baglam:
            satirlar.append(f"- {e.kayit.baslik}: {e.kayit.tarif_sec(bolge)}")
    return "\n".join(satirlar)


class BulutDilModeli:
    """Sağlayıcıyı ayardan seçer: "gemini" ya da "anthropic". Çalışamazsa KuralTabanli'ye düşer."""

    ANAHTAR_DEGISKENI = {"gemini": "GEMINI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}

    def __init__(self, saglayici, model, paket, robot_adi="Robot", istemci=None, gecmis_tur=GECMIS_TUR):
        self.saglayici = saglayici
        self.model = model
        self.paket = paket
        self.robot_adi = robot_adi
        self.yedek = KuralTabanli(paket, robot_adi, gecmis_tur)
        self.gecmis = SohbetGecmisi(gecmis_tur)
        # Testlerde sahte istemci verilir; gerçekte burada kurulur (olmazsa None)
        self.istemci = istemci if istemci is not None else self._istemci_kur()

    @property
    def calisiyor(self):
        return self.istemci is not None

    def _istemci_kur(self):
        degisken = self.ANAHTAR_DEGISKENI.get(self.saglayici)
        if degisken is None:
            print(f"[dil] Bilinmeyen sağlayıcı '{self.saglayici}'; kural tabanlı cevaplara düşüyorum.")
            return None
        anahtar = os.environ.get(degisken)
        if not anahtar:
            print(f"[dil] {degisken} ortam değişkeni yok; kural tabanlı cevaplara düşüyorum.")
            return None
        try:
            if self.saglayici == "gemini":
                from google import genai
                return genai.Client(api_key=anahtar)
            import anthropic
            return anthropic.Anthropic(api_key=anahtar, timeout=BULUT_ZAMAN_ASIMI)
        except ImportError:
            paket_adi = "google-genai" if self.saglayici == "gemini" else "anthropic"
            print(f"[dil] '{paket_adi}' paketi kurulu değil (pip install {paket_adi}); "
                  "kural tabanlı cevaplara düşüyorum.")
            return None

    def _sor(self, soru, bolge=None):
        istem = sistem_istemi(self.paket, self.robot_adi, soru, bolge)
        mesajlar = self.gecmis.mesajlar() + [{"role": "user", "content": soru}]   # sohbet hafızası + yeni soru
        if self.saglayici == "gemini":
            yanit = self.istemci.models.generate_content(
                model=self.model, contents=gemini_icerigi(mesajlar),
                config={"system_instruction": istem, "max_output_tokens": EN_FAZLA_TOKEN})
            return yanit.text
        yanit = self.istemci.messages.create(
            model=self.model, max_tokens=EN_FAZLA_TOKEN, system=istem, messages=mesajlar)
        return yanit.content[0].text

    def cevapla(self, soru, bolge=None):
        cevap = self._cevap_uret(soru, bolge)
        self.gecmis.ekle(soru, cevap.metin)     # bir sonraki soruda modele geçmiş olarak gider
        return cevap

    def _cevap_uret(self, soru, bolge=None):
        # İçerik eşleşmesi: jest, yön ve konu buradan; bulut çalışmazsa cevabın kendisi de buradan
        yedek = self.yedek.cevap_bul(soru, bolge)
        if not self.calisiyor:
            return yedek
        try:
            metin = (self._sor(soru, bolge) or "").strip()
        except Exception as hata:   # ağ, kota, anahtar hatası... robot susmasın
            print(f"[dil] Bulut hatası ({hata}); kural tabanlı cevap veriyorum.")
            return yedek
        if not metin:
            return yedek
        # Eşleşme olmasa da (yedek "bilmiyorum" dese de) bulutun sohbet cevabı söylenir
        return Cevap(metin, yedek.jest, yedek.konu, yedek.puan, yedek.yon)


def gemini_icerigi(mesajlar):
    """Gemini mesaj biçimi: rol 'assistant' yerine 'model', metin 'parts' içinde."""
    return [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
            for m in mesajlar]


def dil_sec(saglayici, paket, robot_adi="Robot", gemini_model="", anthropic_model="claude-haiku-5-5",
            gecmis_tur=GECMIS_TUR):
    """Ayardaki sağlayıcı adına göre cevap üreticiyi kurar."""
    if saglayici in ("gemini", "anthropic"):
        model = gemini_model if saglayici == "gemini" else anthropic_model
        return BulutDilModeli(saglayici, model, paket, robot_adi, gecmis_tur=gecmis_tur)
    if saglayici != "kural":
        print(f"[dil] Bilinmeyen sağlayıcı '{saglayici}'; kural tabanlı kullanıyorum.")
    return KuralTabanli(paket, robot_adi, gecmis_tur)
