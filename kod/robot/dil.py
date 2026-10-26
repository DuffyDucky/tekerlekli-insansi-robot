# Ne yapıyor: kullanıcının sorusuna cevap üretir. Tüm üreticiler aynı arayüzü kullanır: cevapla(soru) -> Cevap.
# KuralTabanli internetsiz çalışır: önce içerik paketinde arar, sonra selam/teşekkür gibi kalıplara bakar.
# BulutDilModeli Gemini ya da Anthropic'e sorar; paket/anahtar yoksa ya da hata olursa KuralTabanli'ye düşer.

import os
from dataclasses import dataclass

from robot.icerik import ifade_geciyor_mu, kelimeler

BILMIYORUM = "Bunu bilmiyorum, sizi bir görevliye yönlendireyim."
EN_FAZLA_TOKEN = 200          # 1-2 cümle için yeter
BULUT_ZAMAN_ASIMI = 15.0      # saniye; internet yavaşsa robot sonsuza kadar beklemesin


@dataclass
class Cevap:
    metin: str
    jest: str | None = None   # ESP32'ye gidecek jest adı (selam, isaret, el_salla) ya da None


class KuralTabanli:
    """Her zaman çalışan, internetsiz cevap üretici (varsayılan)."""

    def __init__(self, paket, robot_adi="Robot"):
        self.paket = paket
        self.robot_adi = robot_adi
        self.kaliplar = self._kaliplari_kur()

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
             "Hoşça kalın, iyi günler!", "el_salla"),
            (["merhaba", "selam", "günaydın", "iyi akşamlar"], self.paket.selamlama, "selam"),
        ]

    def kalip_bul(self, soru):
        soru_kelimeleri = kelimeler(soru)
        for ifadeler, cevap, jest in self.kaliplar:
            if any(ifade_geciyor_mu(i, soru_kelimeleri) for i in ifadeler):
                return Cevap(cevap, jest)
        return None

    def cevapla(self, soru):
        # 1) İçerik paketinde eşleşme varsa onu söyle ("merhaba, kantin nerede?" -> kantin tarifi)
        eslesme = self.paket.ara(soru)
        if eslesme:
            return Cevap(eslesme.kayit.cevap, eslesme.kayit.jest)
        # 2) Selam, teşekkür, vedalaşma gibi kalıplar
        kalip = self.kalip_bul(soru)
        if kalip:
            return kalip
        # 3) Hiçbiri değilse kibarca görevliye yönlendir
        return Cevap(BILMIYORUM)


def sistem_istemi(paket, robot_adi, soru):
    """Bulut modeline giden kısa talimat + içerik paketinden en iyi 3 eşleşme."""
    satirlar = [
        f"Sen {robot_adi} adında bir robotsun; {paket.kurum} için {paket.rol} olarak çalışıyorsun.",
        "Ziyaretçiye Türkçe, kibar ve en fazla 1-2 kısa cümleyle cevap ver.",
        "Bilmediğin bir şeyi uydurma; emin değilsen görevliye yönlendir.",
    ]
    baglam = paket.en_iyiler(soru, 3)
    if baglam:
        satirlar.append("Kullanabileceğin bilgiler ('...' bilinmeyen demektir, onu söyleme):")
        for e in baglam:
            satirlar.append(f"- {e.kayit.baslik}: {e.kayit.cevap}")
    return "\n".join(satirlar)


class BulutDilModeli:
    """Sağlayıcıyı ayardan seçer: "gemini" ya da "anthropic". Çalışamazsa KuralTabanli'ye düşer."""

    ANAHTAR_DEGISKENI = {"gemini": "GEMINI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}

    def __init__(self, saglayici, model, paket, robot_adi="Robot", istemci=None):
        self.saglayici = saglayici
        self.model = model
        self.paket = paket
        self.robot_adi = robot_adi
        self.yedek = KuralTabanli(paket, robot_adi)
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

    def _sor(self, soru):
        istem = sistem_istemi(self.paket, self.robot_adi, soru)
        if self.saglayici == "gemini":
            yanit = self.istemci.models.generate_content(
                model=self.model, contents=soru,
                config={"system_instruction": istem, "max_output_tokens": EN_FAZLA_TOKEN})
            return yanit.text
        yanit = self.istemci.messages.create(
            model=self.model, max_tokens=EN_FAZLA_TOKEN, system=istem,
            messages=[{"role": "user", "content": soru}])
        return yanit.content[0].text

    def cevapla(self, soru):
        if not self.calisiyor:
            return self.yedek.cevapla(soru)
        try:
            metin = (self._sor(soru) or "").strip()
        except Exception as hata:   # ağ, kota, anahtar hatası... robot susmasın
            print(f"[dil] Bulut hatası ({hata}); kural tabanlı cevap veriyorum.")
            return self.yedek.cevapla(soru)
        if not metin:
            return self.yedek.cevapla(soru)
        # Jest bulutta seçilmez; içerik paketindeki eşleşmeden ya da kalıplardan alınır
        return Cevap(metin, self.yedek.cevapla(soru).jest)


def dil_sec(saglayici, paket, robot_adi="Robot", gemini_model="", anthropic_model="claude-haiku-5-5"):
    """Ayardaki sağlayıcı adına göre cevap üreticiyi kurar."""
    if saglayici in ("gemini", "anthropic"):
        model = gemini_model if saglayici == "gemini" else anthropic_model
        return BulutDilModeli(saglayici, model, paket, robot_adi)
    if saglayici != "kural":
        print(f"[dil] Bilinmeyen sağlayıcı '{saglayici}'; kural tabanlı kullanıyorum.")
    return KuralTabanli(paket, robot_adi)
