"""Y0f: Lale'nin MuJoCo fizik dünyası (sahte ESP32'nin ikinci dünya arka ucu).

Bu modül YALNIZ fiziktir: robot modeli (`model/lale.xml`, CAD'den üretilir) + sahne (2B haritadan duvar / kutu / kolon,
ayrıca rampa ve eşik). Firmware davranışı (protokol, bekçi, güç, rampa sınırları) burada DEĞİL, `sahte_esp32.cekirdek`'tedir;
`fizik_esp32.FizikEsp32` ikisini bağlar.

Motor modeli (her fizik adımında, teker başına; parametreler `fizik_parametreleri.json`):
    sürülüyor (EN HIGH ve bara gerilimli):  tau = tau_durma * (u * k_V - w / w0)     u = PWM oranı (-1..1), k_V = V_aku / 12
    boşta (EN LOW ya da bara yok):           tau = 0  (eklemin Coulomb sürtünmesi her zaman var)
  u = 0 iken EN HIGH = kısa devre freni (tau = -tau_durma * w / w0), main motorlar.cpp teker_yaz yorumu.
Servolar: MuJoCo konum eyleyicisi (kp, kv, tork sınırı); bara gerilimsizken eyleyici kapanır, eklemde yalnız sürtünme kalır.

Çerçeve: dünya x, y = 2B haritanın x, y (m), z yukarı. Robot çerçevesi +x ileri, +y robotun kendi solu.
Bu modül `mujoco` ve `numpy` ister; ikisi de yoksa `FIZIK_VAR` False olur (testler atlanır, 2B dünya etkilenmez).
"""

import json
import math
import os

try:
    import mujoco
    import numpy as np
    FIZIK_VAR = True
    FIZIK_HATA = None
except ImportError as _h:      # 2B dünya ve 58 test bağımlılıksız kalır
    mujoco = None
    np = None
    FIZIK_VAR = False
    FIZIK_HATA = str(_h)

BURASI = os.path.dirname(os.path.abspath(__file__))
MODEL_XML = os.path.join(BURASI, "model", "lale.xml")
AG = os.path.join(BURASI, "model", "ag")
SAHNELER = os.path.join(BURASI, "sahneler")
TEKERLER = ("teker_on_sol", "teker_arka_sol", "teker_on_sag", "teker_arka_sag")
SERVOLAR = ("sag_omuz", "sag_omuz_yan", "sag_dirsek", "sag_bilek", "kafa_pan",
            "sol_omuz", "sol_omuz_yan", "sol_dirsek", "sol_bilek", "kafa_tilt")


def parametreler(degis=None):
    """fizik_parametreleri.json değerleri {ad: değer}; `degis` ile duyarlılık koşusu için üzerine yazılır."""
    with open(os.path.join(BURASI, "fizik_parametreleri.json"), encoding="utf-8") as f:
        p = {k: v["deger"] for k, v in json.load(f)["parametreler"].items()}
    for k, v in (degis or {}).items():
        if k not in p:
            raise KeyError("bilinmeyen fizik parametresi: %s" % k)
        p[k] = v
    return p


def sahne_oku(ad):
    yol = ad if os.path.isabs(ad) else os.path.join(SAHNELER, ad if ad.endswith(".json") else ad + ".json")
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


def _q_yaw(a):
    return (math.cos(a / 2), 0.0, 0.0, math.sin(a / 2))


def _q_carp(a, b):
    w1, x1, y1, z1 = a
    w2, x2, y2, z2 = b
    return (w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2, w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2, w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2)


def _g(x):
    return "%.6g" % x


def _v(v):
    return " ".join(_g(x) for x in v)


def sahne_xml(harita=None, sahne=None, p=None):
    """Sahne geom'ları (MJCF metni). harita: sahte_esp32.harita.Harita ya da None; sahne: 3B ekler (rampa, eşik).

    Sahne geom'larının sürtünmesi 0: MuJoCo temas sürtünmesini iki geom'un BÜYÜĞÜ olarak alır, böylece temas katsayısı
    robot tarafındaki değerdir (teker: teker_zemin_surtunme, gövde: govde_zemin_surtunme)."""
    p = p or parametreler()
    kal, yuk, ic_kal = p["duvar_kalinligi_m"], p["duvar_yuksekligi_m"], p["ic_duvar_kalinligi_m"]
    s = ['<light name="isik" pos="0 0 6" dir="0 0 -1" diffuse="0.8 0.8 0.8" directional="true"/>',
         '<geom name="zemin_duz" type="plane" size="0 0 0.05" material="m_zemin" contype="1" conaffinity="2" group="0" friction="0 0 0"/>']
    n = 0
    if harita is not None:
        w, h = harita.genislik, harita.yukseklik
        cevre = []
        if harita.veri.get("cevre_duvari", True):
            cevre = [(0, 0, w, 0), (w, 0, w, h), (w, h, 0, h), (0, h, 0, 0)]
        for (x1, y1, x2, y2) in harita.parcalar:
            boy = math.hypot(x2 - x1, y2 - y1)
            if boy < 1e-9:
                continue
            a = math.atan2(y2 - y1, x2 - x1)
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            if (x1, y1, x2, y2) in cevre:            # çevre duvarı dışa kalınlaşır: iç yüz haritadaki çizgide
                mx, my = (cx - w / 2), (cy - h / 2)
                nx, ny = -math.sin(a), math.cos(a)
                if nx * mx + ny * my < 0:
                    nx, ny = -nx, -ny
                cx, cy = cx + nx * kal / 2, cy + ny * kal / 2
                boy += 2 * kal
                k = kal
            else:                                     # iç duvar / kutu kenarı: çizgiye ortalı ince levha (2B'de kalınlıksız)
                k = ic_kal
            q = _q_yaw(a)
            s.append('<geom name="engel_duvar_%d" type="box" pos="%s" size="%s" quat="%s" material="m_duvar" '
                     'contype="1" conaffinity="2" group="0" friction="0 0 0"/>' % (n, _v((cx, cy, yuk / 2)), _v((boy / 2, k / 2, yuk / 2)), _v(q)))
            n += 1
        for i, (cx, cy, r) in enumerate(harita.daireler):
            s.append('<geom name="engel_kolon_%d" type="cylinder" pos="%s" size="%s %s" material="m_duvar" '
                     'contype="1" conaffinity="2" group="0" friction="0 0 0"/>' % (i, _v((cx, cy, yuk / 2)), _g(r), _g(yuk / 2)))
    for i, r in enumerate((sahne or {}).get("rampalar", [])):
        th = math.radians(r["egim_derece"])
        L, gen, H = r["uzunluk_m"], r["genislik_m"], r["uzunluk_m"] * math.tan(math.radians(r["egim_derece"]))
        kal_r = 0.05
        a = math.radians(r.get("aci_derece", 0.0))
        ca, sa = math.cos(a), math.sin(a)
        # rampa çerçevesi: x çıkış yönü; üst yüz (0,0) -> (L, H)
        eg = L / math.cos(th)
        # levha merkezi = üst yüz ortası (L/2, H/2) - normal (-sin, cos) * kalınlık / 2
        ux, uz = L / 2 + math.sin(th) * kal_r / 2, H / 2 - math.cos(th) * kal_r / 2
        q = _q_carp(_q_yaw(a), (math.cos(-th / 2), 0.0, math.sin(-th / 2), 0.0))
        X, Y = r["x"] + ca * ux, r["y"] + sa * ux
        s.append('<geom name="zemin_rampa_%d" type="box" pos="%s" size="%s" quat="%s" material="m_rampa" '
                 'contype="1" conaffinity="2" group="0" friction="0 0 0"/>' % (i, _v((X, Y, uz)), _v((eg / 2, gen / 2, kal_r / 2)), _v(q)))
        P = r.get("ust_uzunluk_m", 0.0)
        if P > 0:
            X, Y = r["x"] + ca * (L + P / 2), r["y"] + sa * (L + P / 2)
            s.append('<geom name="zemin_platform_%d" type="box" pos="%s" size="%s" quat="%s" material="m_rampa" '
                     'contype="1" conaffinity="2" group="0" friction="0 0 0"/>' % (i, _v((X, Y, H / 2)), _v((P / 2, gen / 2, H / 2)), _v(_q_yaw(a))))
    for i, e in enumerate((sahne or {}).get("esikler", [])):
        a = math.radians(e.get("aci_derece", 0.0))
        hh = e["yukseklik_mm"] / 1000.0
        d = e.get("derinlik_m", 0.6)
        ca, sa = math.cos(a), math.sin(a)
        X, Y = e["x"] + ca * d / 2, e["y"] + sa * d / 2
        s.append('<geom name="zemin_esik_%d" type="box" pos="%s" size="%s" quat="%s" material="m_rampa" '
                 'contype="1" conaffinity="2" group="0" friction="0 0 0"/>' % (i, _v((X, Y, hh / 2)), _v((d / 2, e["genislik_m"] / 2, hh / 2)), _v(_q_yaw(a))))
    for i, k in enumerate((sahne or {}).get("kutular", [])):
        s.append('<geom name="engel_kutu3b_%d" type="box" pos="%s" size="%s" quat="%s" material="m_duvar" '
                 'contype="1" conaffinity="2" group="0" friction="0 0 0"/>' % (i, _v((k["x"], k["y"], k["z"])), _v(k["yari"]),
                                                          _v(_q_yaw(math.radians(k.get("aci_derece", 0))))))
    return "\n    ".join(s)


VARLIK = """
    <texture name="t_zemin" type="2d" builtin="checker" rgb1="0.82 0.82 0.8" rgb2="0.7 0.7 0.68" width="512" height="512"/>
    <material name="m_zemin" texture="t_zemin" texrepeat="1 1" texuniform="true"/>
    <material name="m_duvar" rgba="0.55 0.6 0.68 0.55"/>
    <material name="m_rampa" rgba="0.75 0.55 0.35 1"/>
    <texture name="gok" type="skybox" builtin="gradient" rgb1="0.9 0.93 0.97" rgb2="0.6 0.65 0.72" width="256" height="256"/>
"""


def model_kur(harita=None, sahne=None, p=None, varyant=None):
    if not FIZIK_VAR:
        raise RuntimeError("fizik bağımlılığı yok (mujoco): %s" % FIZIK_HATA)
    with open(MODEL_XML, encoding="utf-8") as f:
        x = f.read()
    if varyant and varyant.get("on_teker"):              # VARSAYIM (varyantlar.py); V0'da bu dal yok
        import varyantlar
        x = varyantlar.on_teker_xml(x, varyant["on_teker"])
    x = x.replace("__AG__", AG.replace("\\", "/"))
    x = x.replace("<!--SAHNE-->", sahne_xml(harita, sahne, p))
    x = x.replace("<asset>", "<asset>" + VARLIK, 1)
    return mujoco.MjModel.from_xml_string(x)


class FizikDunya:
    """Robot + sahne. Zaman `adim(dt)` ile ilerler (deterministik; duvar saati yok)."""

    def __init__(self, harita=None, sahne=None, konum=(0.0, 0.0, 0.0), degis=None, varyant=None):
        self.p = parametreler(degis)
        self.harita = harita
        self.sahne = sahne
        self.varyant = varyant
        self.m = model_kur(harita, sahne, self.p, varyant)
        self.d = mujoco.MjData(self.m)
        m = self.m
        ad = lambda t, n: mujoco.mj_name2id(m, t, n)
        J, B, G, A, S = (mujoco.mjtObj.mjOBJ_JOINT, mujoco.mjtObj.mjOBJ_BODY, mujoco.mjtObj.mjOBJ_GEOM,
                         mujoco.mjtObj.mjOBJ_ACTUATOR, mujoco.mjtObj.mjOBJ_SITE)
        self.taban = ad(B, "taban")
        self.teker_dof = [m.jnt_dofadr[ad(J, t)] for t in TEKERLER]
        self.teker_qpos = [m.jnt_qposadr[ad(J, t)] for t in TEKERLER]
        self.teker_geom = [ad(G, "c_" + t) for t in TEKERLER]
        self.motor = [ad(A, "motor_" + t) for t in TEKERLER]
        self.servo_act = {s: ad(A, "servo_" + s) for s in SERVOLAR}
        self.servo_jnt = {s: ad(J, s) for s in SERVOLAR}
        self.servo_dof = {s: m.jnt_dofadr[self.servo_jnt[s]] for s in SERVOLAR}
        self.servo_qpos = {s: m.jnt_qposadr[self.servo_jnt[s]] for s in SERVOLAR}
        self._servo_kazanc = {s: (m.actuator_gainprm[i, 0], m.actuator_biasprm[i, 1], m.actuator_biasprm[i, 2])
                              for s, i in self.servo_act.items()}
        self.servo_guclu = True
        self.sonar_site = {k: ad(S, "sonar_" + k) for k in ("sol", "orta", "sag")}
        self.zemin_geom = set()
        self.engel_geom = set()
        for g in range(m.ngeom):
            n = mujoco.mj_id2name(m, G, g) or ""
            if n.startswith("zemin_"):
                self.zemin_geom.add(g)
            elif n.startswith("engel_"):
                self.engel_geom.add(g)
        self.robot_geom = {g for g in range(m.ngeom) if m.geom_bodyid[g] != 0 and m.geom_contype[g] == 2}
        # parametre uygulaması (derlenmiş modele; yeniden derleme gerekmez)
        for g in self.teker_geom:
            m.geom_friction[g, 0] = self.p["teker_zemin_surtunme"]
        for g in self.robot_geom - set(self.teker_geom):
            m.geom_friction[g, 0] = self.p["govde_zemin_surtunme"]
        # teker ekleminde Coulomb sürtünmesi = dişli sürtünmesi + yuvarlanma direnci (crr x statik teker yükü x r; yük
        # değişimi izlenmez: TAHMİN). Yuvarlanma direnci MuJoCo temasında yok (condim 3), bu yüzden eklemde.
        r_teker = float(m.geom_size[self.teker_geom[0], 0])
        n_teker = float(sum(m.body_mass)) * 9.81 / 4.0
        self.teker_surtunme = self.p["motor_disli_surtunme_Nm"] + self.p["yuvarlanma_direnci_katsayisi"] * n_teker * r_teker
        for dof in self.teker_dof:
            m.dof_frictionloss[dof] = self.teker_surtunme
            m.dof_armature[dof] = self.p["motor_yansiyan_atalet_kgm2"]
        # VARSAYIM V4 (varyantlar.py): ön tekerler tahriksiz sarhoş: motor / dişli yok, yalnız yuvarlanma direnci
        self.tahriksiz = set()
        # VARSAYIM V3 / V4: ön "makara" menteşeleri; açısı her adımda 0'a döner (küre kendi merkezi çevresinde simetrik,
        # temas geometrisi değişmez; teker ekseni yatay kalır = hep alttaki makara, hızı korunur). V0'da liste boş.
        self.makara_qpos = []
        if varyant and varyant.get("on_teker"):
            self.makara_qpos = [m.jnt_qposadr[ad(J, "makara_on_" + y)] for y in ("sol", "sag")]
        if varyant and varyant.get("on_teker") == "sarhos":
            self.tahriksiz = {0, 2}
            for i in self.tahriksiz:
                m.dof_frictionloss[self.teker_dof[i]] = self.teker_surtunme - self.p["motor_disli_surtunme_Nm"]
                m.dof_armature[self.teker_dof[i]] = 0.0
        m.geom_solref[:, 0] = self.p["temas_solref_s"]
        m.opt.timestep = self.p["zaman_adimi_s"]
        self.tau_durma = self.p["motor_durma_torku_Nm"]
        self.w0 = self.p["motor_bos_hiz_dev_dk"] * 2 * math.pi / 60.0
        self.k_V = 1.0
        self.zaman_s = 0.0
        self.adim_kaydi = None               # ölçüm: her fizik adımından sonra adim_kaydi(self)
        self.son_tork = [0.0] * 4
        self.en_cok_tork = [0.0] * 4
        self.konum_ayarla(*konum)

    # ------------------------------------------------------------ durum
    def gerilim(self, v_aku):
        self.k_V = (v_aku / self.p["motor_anma_gerilimi_V"]) if self.p["motor_gerilimle_olcekle"] else 1.0

    def konum_ayarla(self, x, y, aci_rad, z=0.0):
        d = self.d
        d.qpos[0:3] = (x, y, z)
        d.qpos[3:7] = _q_yaw(aci_rad)
        d.qvel[0:6] = 0.0
        for dof in self.teker_dof:
            d.qvel[dof] = 0.0
        mujoco.mj_forward(self.m, d)

    def servo_hedef(self, hedef_rad):
        """{servo adı: eklem açısı rad} (eklem çerçevesi: servo açısı - ofset)."""
        for s, a in hedef_rad.items():
            self.d.ctrl[self.servo_act[s]] = a

    def servo_eklem_ayarla(self, aci_rad):
        """Ölçüm kurulumu: eklemleri doğrudan koy (hedefle birlikte)."""
        for s, a in aci_rad.items():
            self.d.qpos[self.servo_qpos[s]] = a
            self.d.ctrl[self.servo_act[s]] = a
        mujoco.mj_forward(self.m, self.d)

    def servo_guc(self, acik):
        if acik == self.servo_guclu:
            return
        self.servo_guclu = acik
        for s, i in self.servo_act.items():
            g, b1, b2 = self._servo_kazanc[s]
            self.m.actuator_gainprm[i, 0] = g if acik else 0.0
            self.m.actuator_biasprm[i, 1] = b1 if acik else 0.0
            self.m.actuator_biasprm[i, 2] = b2 if acik else 0.0
            self.m.dof_frictionloss[self.servo_dof[s]] = 0.0 if acik else self.p["servo_gucsuz_surtunme_Nm"]

    # ------------------------------------------------------------ zaman
    def adim(self, dt_s, u_sol=0.0, u_sag=0.0, suruluyor=False, dis_kuvvet=None):
        """dt_s boyunca ilerle. suruluyor False = motorlar boşta (EN LOW / bara yok)."""
        n = max(1, int(round(dt_s / self.m.opt.timestep)))
        d = self.d
        for _ in range(n):
            for i, dof in enumerate(self.teker_dof):
                if suruluyor and i not in self.tahriksiz:
                    u = u_sol if i < 2 else u_sag
                    t = self.tau_durma * (u * self.k_V - d.qvel[dof] / self.w0)
                else:
                    t = 0.0
                d.ctrl[self.motor[i]] = t
                self.son_tork[i] = t
                if abs(t) > self.en_cok_tork[i]:
                    self.en_cok_tork[i] = abs(t)
            if dis_kuvvet is not None:
                dis_kuvvet(self)
            mujoco.mj_step(self.m, d)
            for a in self.makara_qpos:
                d.qpos[a] = 0.0
            self.zaman_s += self.m.opt.timestep
            if self.adim_kaydi is not None:
                self.adim_kaydi(self)

    # ------------------------------------------------------------ okuma
    def teker_acilari(self):
        return [float(self.d.qpos[a]) for a in self.teker_qpos]

    def teker_hizlari(self):
        return [float(self.d.qvel[a]) for a in self.teker_dof]

    def poz(self):
        """(x, y, z, yaw, pitch, roll) rad; pitch + = burun aşağı (öne eğilme), roll + = sola yatma."""
        q = self.d.xquat[self.taban]
        w, x, y, z = q
        yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
        pitch = math.asin(max(-1.0, min(1.0, 2 * (w * y - z * x))))
        roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
        p = self.d.xpos[self.taban]
        return float(p[0]), float(p[1]), float(p[2]), yaw, pitch, roll

    def egim(self):
        """Taban dikeyinin dünya dikeyinden sapması (rad)."""
        R = self.d.xmat[self.taban].reshape(3, 3)
        return math.acos(max(-1.0, min(1.0, float(R[2, 2]))))

    def hiz(self):
        """(v ileri m/s, w yaw rad/s) robot çerçevesinde (taban orijininin hızı)."""
        # serbest eklem: qvel[0:3] dünya çerçevesinde taban orijininin doğrusal hızı, qvel[3:6] yerel açısal hız
        # (mj_objectVelocity yerel kipte gövdenin ana atalet eksenlerini kullanır; burada istenen taban çerçevesi)
        R = self.d.xmat[self.taban].reshape(3, 3)
        vd = self.d.qvel[0:3]
        wd = R @ self.d.qvel[3:6]
        return float(R[:, 0] @ vd), float(wd[2])

    def am(self):
        return [float(v) for v in self.d.subtree_com[self.taban]]

    def teker_yukleri(self):
        """Teker başına zemin normal kuvveti (N); 0 = teker havada."""
        F = [0.0] * 4
        f6 = np.zeros(6)
        for i in range(self.d.ncon):
            c = self.d.contact[i]
            for k, g in enumerate(self.teker_geom):
                if (c.geom1 == g or c.geom2 == g):
                    mujoco.mj_contactForce(self.m, self.d, i, f6)
                    F[k] += float(f6[0])
        return F

    def temas_engel(self):
        """Robotun bir engele (duvar / kutu / kolon) değip değmediği."""
        for i in range(self.d.ncon):
            c = self.d.contact[i]
            if (c.geom1 in self.engel_geom and c.geom2 in self.robot_geom) or \
               (c.geom2 in self.engel_geom and c.geom1 in self.robot_geom):
                return True
        return False

    def govde_zemine_degiyor(self):
        """Tekerler dışında robotun bir parçası zemine / rampaya / eşiğe değiyor mu (takılma, devrilme)."""
        tk = set(self.teker_geom)
        for i in range(self.d.ncon):
            c = self.d.contact[i]
            a, b = c.geom1, c.geom2
            if (a in self.zemin_geom and b in self.robot_geom - tk) or (b in self.zemin_geom and a in self.robot_geom - tk):
                return True
        return False

    def isin(self, bas, yon, en_cok):
        """Sahneye ışın: (uzaklık m, geliş açısı rad) ya da None. Robotun kendi geom'ları sayılmaz (grup 0 = sahne)."""
        gid = np.zeros(1, dtype=np.int32)
        grup = np.array([1, 0, 0, 0, 0, 0], dtype=np.uint8)
        y = np.asarray(yon, dtype=float)
        t = mujoco.mj_ray(self.m, self.d, np.asarray(bas, dtype=float), y, grup, 1, -1, gid)
        if t < 0 or t > en_cok:
            return None
        g = int(gid[0])
        h = np.asarray(bas) + y * t
        n = self._normal(g, h)
        gelis = math.acos(min(1.0, abs(float(np.dot(n, y)))))
        return float(t), gelis

    def _normal(self, g, h):
        m, d = self.m, self.d
        R = d.geom_xmat[g].reshape(3, 3)
        p = R.T @ (h - d.geom_xpos[g])
        tur = m.geom_type[g]
        if tur == mujoco.mjtGeom.mjGEOM_PLANE:
            return R[:, 2]
        if tur == mujoco.mjtGeom.mjGEOM_BOX:
            s = m.geom_size[g]
            k = int(np.argmax(np.abs(p) / s))
            n = np.zeros(3)
            n[k] = 1.0 if p[k] >= 0 else -1.0
            return R @ n
        if tur == mujoco.mjtGeom.mjGEOM_CYLINDER:
            s = m.geom_size[g]
            if abs(p[2]) >= s[1] - 1e-6:
                return R[:, 2] * (1.0 if p[2] > 0 else -1.0)
            n = np.array([p[0], p[1], 0.0])
            return R @ (n / (np.linalg.norm(n) or 1.0))
        return np.array([0.0, 0.0, 1.0])

    def sonar_cercevesi(self, ad):
        i = self.sonar_site[ad]
        return self.d.site_xpos[i].copy(), self.d.site_xmat[i].reshape(3, 3).copy()
