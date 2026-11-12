/* Lale 3B montaj rehberi. Veri: veri/rehber-veri.js (window.REHBER_VERI), mesh: veri/robot-glb.js (window.REHBER_GLB, base64 GLB).
   İkisi de tasarim/freecad/rehber/rehber_veri.py ile üretilir; elle düzenleme. Klasik betik (file:// altında da çalışsın diye);
   three.js 0.160 index.html'de vendor/three-0.160.0-paket.min.js'ten (klasik betik, internetsiz) RehberBaslat'a verilir.
   F10a (P10.1): seçim vurgusu (tıklanan parça + aynı kalemin kopyaları, panel satırından da), öncekiler opak / saydam / gizli,
   patlat + panel sırasıyla satır satır tak, "robotun neresi" küçük görünümü, yeni parçalara sıkı kadraj.
   F10d (P10.4): alt adımlar. Kaynak adım verisindeki sira_grup (F10c adım içi sırası): "alt" sayısı olan adımda her grup bir alt
   adımdır (31.1 … 31.n; 31 = 31.0 genel bakış, bütün yeni parçalar). Adres ?adim=31.3 ya da #31.3; ←/→ alt adımlar arasında da
   yürür. Masa grubu (tezgah anahtarı): yalnız o birimin parçaları; "bag" grubu birimi ub yönünden robota bağlar. Panel ve sıralı
   takma aynı sırayı (st.sira) izler; ısıl gömme ev sahibiyle (p.h) uçar. */
(function () {
  "use strict";
  const VERI = window.REHBER_VERI;
  const ADIM = VERI ? VERI.adimlar : [];
  const N = ADIM.length;
  // ---------------------------------------------------------------- F10d: alt adım yardımcıları (veri: sira_grup, alt)
  const KONUM = [];                                   // gezinme sırası: [adım, alt adım]
  ADIM.forEach((a) => { KONUM.push([a.i, 0]); for (let j = 1; j <= (a.alt || 0); j++) KONUM.push([a.i, j]); });
  function konumNo(s, j) { for (let i = 0; i < KONUM.length; i++) if (KONUM[i][0] === s && KONUM[i][1] === j) return i; return 0; }
  const _gh = {};
  function grupHarita(s) {                            // parça / şema -> grup sırası (0'dan), bağlayan grup: anahtar -> sıra
    if (_gh[s]) return _gh[s];
    const st = ADIM[s], h = { p: {}, sema: {}, bag: {}, satir: {} };
    (st.sira_grup || []).forEach((g, n) => {
      g.satir.forEach((k) => {
        h.satir[k] = n;
        const [t, i] = k.split(":"); const r = (t === "p" ? st.parcalar : st.baglantilar)[+i];
        if (r) r.ids.forEach((id) => { h.p[id] = n; });
      });
      (g.sema || []).forEach((i) => { h.sema[i] = n; });
      (g.ref || []).forEach((id) => { h.p[id] = n; });   // gösterim parçası (satırı yok)
      if (g.bag) h.bag[g.bag] = n;
    });
    _gh[s] = h;
    return h;
  }
  function adresOku(x) {                              // "31.3" -> [31, 3]; "31" -> [31, 0]
    const m = /^\s*(\d+)(?:\.(\d+))?\s*$/.exec(String(x == null ? "" : x));
    if (!m) return null;
    const s = Math.max(0, Math.min(N - 1, +m[1]));
    return [s, Math.max(0, Math.min((ADIM[s] && ADIM[s].alt) || 0, m[2] ? +m[2] : 0))];
  }
  function adres(s, j) { return j ? s + "." + j : String(s); }
  const $ = (id) => document.getElementById(id);
  const P = new URLSearchParams(location.search);
  const CEKIM = P.get("cekim") === "1";               // ekran görüntüsü kipi: animasyon yok, sabit kamera
  const SAHNE = P.get("sahne") === "1";               // F7b: yalnız 3B görünüm (yazdırılabilir sürümün görüntüsü; panel, üst ve alt şerit gizli)
  if (SAHNE) document.documentElement.classList.add("yalniz-sahne");
  const TUR_AD = (VERI && VERI.tur_ad) || {};
  const MODUL_AD = (VERI && VERI.modul_ad) || {};
  const SEMA = (VERI && VERI.semalar) || [];          // F7b: gösterim şemaları (lale158/kablo_yolu_ekran.py); parça değil

  // ---------------------------------------------------------------- güvenli yerel kayıt (hata verirse sessizce düşer)
  const KAYIT = "lale-rehber-v1";
  function oku() { try { return JSON.parse(localStorage.getItem(KAYIT) || "{}") || {}; } catch (e) { return {}; } }
  function yaz(k, v) { try { const d = oku(); d[k] = v; localStorage.setItem(KAYIT, JSON.stringify(d)); } catch (e) { /* yok say */ } }

  // ---------------------------------------------------------------- renkler
  const SINIF = {
    baski: ["#f0932b", "Baskı (PETG)"], cf: ["#3d5a80", "Baskı (PETG-CF)"], profil: ["#16a085", "Sigma profil"],
    satin: ["#2f86d4", "Satın alınan"], lazer: ["#8e44ad", "Lazer kesim"], imalat: ["#d35400", "İmalat"],
    baglanti: ["#d4ac0d", "Bağlantı elemanı"], kablo: ["#c0392b", "Kablo yolu"],
    ref: ["#95a5a6", "Gösterim"], onceki: ["#b5b5b0", "Önceki adımlar"],
    secili: ["#7cfc00", "Seçili"]                      // F10a: seçim vurgusu (sınıf ve kablo renklerinde olmayan açık yeşil)
  };
  const VURGU_ANA = "#7cfc00", VURGU_KOPYA = "#cdf7a6", KONUM_RENK = "#ffb000";
  // F10e (P10.4b): renk kipi. "gercek" (varsayılan): o adımın (alt adımın) yeni parçaları CAD rengiyle (veri: parcalar[].gr, kaynak
  // tasarim/freecad/rehber/rehber_gorunum.py: modül FCStd "Renk" özelliği + modülün gorsel betiğindeki RENK tablosu); "sinif": bugünkü
  // sınıf renkleri (lejant). Önceki adımlar iki kipte de gri. Bağlandığı yer (veri: sira_grup[].ev / adimlar[].ev) EV_RENK: gerçek
  // renklerden, sınıf renklerinden, seçim yeşilinden ve kehribardan en uzak ton (CIELAB ΔE ≥ 47, F10e günlüğü). Zeminle karşıtlığı
  // KENAR_ESIK'in altında kalan yeni parçaya kenar çizgisi (iki temada; zemin --sahne).
  const EV_RENK = "#ff3fa4", KENAR_ESIK = 3.0, ONCEKI_ESIK = 1.5;
  const KENAR = { light: "#26282c", dark: "#e8e8e8" };
  function _lin(c) { c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }
  function parlaklik(hex) {
    const h = String(hex).replace("#", ""); const r = parseInt(h.slice(0, 2), 16), g = parseInt(h.slice(2, 4), 16), b = parseInt(h.slice(4, 6), 16);
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b);
  }
  function karsitlik(a, b) { const x = parlaklik(a), y = parlaklik(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); }
  function tema() {
    const t = document.documentElement.dataset.theme;
    if (t) return t;
    return matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  window.RehberBaslat = function (L) {
    if (!L || !L.THREE) { $("yukleniyor").textContent = "three.js yüklenemedi: vendor/three-0.160.0-paket.min.js gerekli."; return; }
    const THREE = L.THREE;
    if (!VERI || !window.REHBER_GLB) { $("yukleniyor").textContent = "Veri bulunamadı: veri/rehber-veri.js ve veri/robot-glb.js gerekli."; return; }
    const tuval = $("tuval"), sahneEl = $("sahne"), miniEl = $("mini");
    const renderer = new THREE.WebGLRenderer({ canvas: tuval, antialias: true, preserveDrawingBuffer: CEKIM });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    const sahne = new THREE.Scene();
    const kamera = new THREE.PerspectiveCamera(35, 1, 5, 20000);
    const kontrol = new L.OrbitControls(kamera, tuval);
    kontrol.enableDamping = false;
    kontrol.addEventListener("change", ciz);
    sahne.add(new THREE.HemisphereLight(0xffffff, 0x8a8a80, 1.6));
    const isik = new THREE.DirectionalLight(0xffffff, 1.6); isik.position.set(600, 1400, 900); sahne.add(isik);
    const isik2 = new THREE.DirectionalLight(0xffffff, 0.6); isik2.position.set(-800, 300, -600); sahne.add(isik2);
    const zemin = new THREE.GridHelper(1400, 28, 0x999999, 0xbbbbbb); zemin.material.transparent = true; zemin.material.opacity = 0.35;
    sahne.add(zemin);

    const mat = {};
    function malzeme(renk, opak) {                   // opak: yok / false = 1, true = 0,35 (önceki kablolar), sayı = o opaklık
      const a = opak === true ? 0.35 : (typeof opak === "number" ? opak : 1);
      const k = renk + "|" + a;
      if (!mat[k]) {
        mat[k] = new THREE.MeshStandardMaterial({ color: renk, metalness: 0.05, roughness: 0.75, side: THREE.DoubleSide,
          transparent: a < 1, opacity: a, depthWrite: a >= 1 });
      }
      return mat[k];
    }
    // seçim vurgusu: tıklanan parça parlak, aynı kalemin kopyaları açık ton; ikisinin de önde duran parçaların arkasından görünen
    // silueti (derinlik testi kapalı yarı saydam kopya). Malzeme yalnız seçim süresince değişir; uygula() asıl malzemeyi
    // userData.mat0'da tutar, temizlenince o geri konur.
    const VURGU = {
      ana: new THREE.MeshStandardMaterial({ color: VURGU_ANA, emissive: "#3f8f00", emissiveIntensity: 0.6, metalness: 0.05, roughness: 0.5,
        side: THREE.DoubleSide }),
      kopya: new THREE.MeshStandardMaterial({ color: VURGU_KOPYA, emissive: "#2b5a10", emissiveIntensity: 0.35, metalness: 0.05,
        roughness: 0.6, side: THREE.DoubleSide }),
      xray: new THREE.MeshBasicMaterial({ color: VURGU_ANA, transparent: true, opacity: 0.3, depthTest: false, depthWrite: false,
        side: THREE.DoubleSide })
    };
    let zeminHex = "#eceae4";
    function sahneRengi() {
      const cs = getComputedStyle(document.documentElement);
      const c = cs.getPropertyValue("--sahne").trim() || "#eceae4";
      zeminHex = c;
      sahne.background = new THREE.Color(c);
      SINIF.onceki[0] = tema() === "dark" ? "#5d6168" : "#b5b5b0";
      zemin.material.color = new THREE.Color(tema() === "dark" ? 0x555555 : 0xaaaaaa);
      MINI.sahne.background = new THREE.Color(cs.getPropertyValue("--card").trim() || "#ffffff");
      MINI.soluk.color = new THREE.Color(tema() === "dark" ? "#9aa0a8" : "#6b7078");
      MINI.yakin.color = MINI.soluk.color;
    }

    // ---------------------------------------------------------------- "robotun neresi" küçük görünümü (aynı tuvalde ikinci görüş alanı)
    const MINI = {
      sahne: new THREE.Scene(), kamera: new THREE.PerspectiveCamera(30, 0.75, 10, 40000), kutu: new THREE.Box3(), hazir: false,
      soluk: new THREE.MeshStandardMaterial({ color: "#6b7078", transparent: true, opacity: 0.2, depthWrite: false, side: THREE.DoubleSide }),
      yakin: new THREE.MeshStandardMaterial({ color: "#6b7078", transparent: true, opacity: 0.5, depthWrite: false, side: THREE.DoubleSide }),
      // vurgu saydam geçişte, soluk robottan sonra çizilir (renderOrder 10; soluklar derinlik yazmaz): içeride kalan parça da
      // soluk katmanların altında kaybolmaz, kendi içinde derinlik doğru kalır
      vurgu: new THREE.MeshStandardMaterial({ color: KONUM_RENK, emissive: "#6a4000", emissiveIntensity: 0.5, metalness: 0.05, roughness: 0.6,
        side: THREE.DoubleSide, transparent: true, opacity: 1, depthWrite: true }),
      hk: new THREE.Box3(), yon: new THREE.Vector3(0.85, 0.62, 1.25)
    };
    MINI.nokta = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), MINI.vurgu);   // yarıçap 1, ölçekle ~3,5 px (kalıp; sahnede değil)
    MINI.noktalar = []; MINI.hlist = [];
    MINI.sahne.add(new THREE.HemisphereLight(0xffffff, 0x8a8a80, 1.8));
    const mIsik = new THREE.DirectionalLight(0xffffff, 1.4); mIsik.position.set(600, 1400, 900); MINI.sahne.add(mIsik);
    // yazdırılabilir sürümün görüntüsünde (?sahne=1) de açık: kâğıtta döndürme yok, bağlamı küçük görünüm verir
    let miniAcik = SAHNE ? P.get("mini") !== "0" : (P.get("mini") === "1" || (P.get("mini") !== "0" && oku().mini !== false));

    // ---------------------------------------------------------------- GLB
    const ikili = Uint8Array.from(atob(window.REHBER_GLB), (c) => c.charCodeAt(0)).buffer;
    const PAR = {};                                   // id -> { v: veri, obj, taban (Vector3), mini (klon), mkutu }
    VERI.parcalar.forEach((p) => { PAR[p.id] = { v: p }; });
    let yuklu = false;
    new L.GLTFLoader().parse(ikili, "", (gltf) => {
      const kirisim = new Map();
      gltf.scene.traverse((o) => {
        if (!o.isMesh) return;
        const kayit = PAR[o.name] || PAR[o.parent && o.parent.name];
        if (!kayit) return;
        let g = kirisim.get(o.geometry.uuid);
        if (!g) { g = L.toCreasedNormals(o.geometry, Math.PI / 6); kirisim.set(o.geometry.uuid, g); }
        o.geometry = g;
        kayit.obj = o;
        kayit.taban = o.position.clone();
        o.userData.id = kayit.v.id;
      });
      sahne.add(gltf.scene);
      gltf.scene.updateMatrixWorld(true);
      for (const id in PAR) {                         // küçük görünüm: bitmiş robotun klonu (geometri ortak)
        const k = PAR[id]; if (!k.obj) continue;
        const m = new THREE.Mesh(k.obj.geometry, MINI.soluk);
        m.matrixAutoUpdate = false; m.matrix.copy(k.obj.matrixWorld);
        MINI.sahne.add(m); k.mini = m;
      }
      semaKur();
      MINI.sahne.updateMatrixWorld(true);
      for (const id in PAR) { const k = PAR[id]; if (k.mini) { k.mkutu = new THREE.Box3().setFromObject(k.mini); MINI.kutu.union(k.mkutu); } }
      SEMA_MINI.forEach((m, i) => { if (m) { m.userData.mkutu = new THREE.Box3().setFromObject(m); MINI.kutu.union(m.userData.mkutu); } });
      MINI.hazir = true;
      $("yukleniyor").hidden = true;
      yuklu = true;
      sahneRengi();
      miniGoster(miniAcik, true);
      const b0 = baslangic(); git(b0[0], false, b0[1]);
      if (P.get("patlat") === "1") { patlat(); const t = parseInt(P.get("tak"), 10); for (let i = 0; i < (t || 0); i++) tak(); }
    }, (h) => { $("yukleniyor").textContent = "GLB okunamadı: " + h; console.error(h); });

    // ---------------------------------------------------------------- gösterim şemaları (F7b): çoklu doğru parçası -> ince tüp
    const SEMA_OBJ = [], SEMA_MINI = [];
    function semaKur() {
      SEMA.forEach((s, i) => {
        if (!s.pts || s.pts.length < 2) return;
        const yol = new THREE.CurvePath();
        for (let k = 1; k < s.pts.length; k++) {
          const a = new THREE.Vector3(...s.pts[k - 1]), b = new THREE.Vector3(...s.pts[k]);
          if (a.distanceTo(b) > 1e-6) yol.add(new THREE.LineCurve3(a, b));
        }
        const g = new THREE.TubeGeometry(yol, Math.max(24, s.pts.length * 12), 2.5, 6, false);
        const o = new THREE.Mesh(g, malzeme(s.renk));
        o.userData.sema = i;
        o.visible = false;
        sahne.add(o);
        SEMA_OBJ[i] = o;
        const m = new THREE.Mesh(g, MINI.soluk); MINI.sahne.add(m); SEMA_MINI[i] = m;
      });
    }
    function semaDurum(i, adim, j) {                 // "gizli" | "simdi" | "onceki" | "hedef"
      const s = SEMA[i];
      if (adim === 0) return "hedef";
      if (j === undefined) j = adim === su ? ss : 0;
      // F10d düzeltme 1 (kontrol B-3): masa alt adımında robot yok; başka adımların kablo yolları havada çizilmesin
      if (j && ADIM[adim].alt && ADIM[adim].sira_grup[j - 1].tezgah && s.a !== adim) return "gizli";
      if (j && ADIM[adim].alt && s.a === adim) {     // F10d: şema kendi alt adımında yeni, sonra önceki
        const G = ADIM[adim].sira_grup, n = grupHarita(adim).sema[i];
        if (n == null) return "gizli";
        if (G[j - 1].tezgah) return n === j - 1 ? "simdi" : "gizli";
        return n < j - 1 ? "onceki" : (n === j - 1 ? "simdi" : "gizli");
      }
      if (ADIM[adim].tezgah) return s.a === adim ? "simdi" : "gizli";
      if (s.a > adim) return "gizli";
      return s.a === adim ? "simdi" : "onceki";
    }

    // ---------------------------------------------------------------- adım durumu
    let su = 0, ss = 0, anim = null;                 // ss: alt adım (0 = adımın genel bakışı)
    const ONCEKI = ["opak", "saydam", "gizli"];
    let onceki = ONCEKI.indexOf(P.get("onceki")) >= 0 ? P.get("onceki") : (ONCEKI.indexOf(oku().onceki) >= 0 ? oku().onceki : "opak");
    function baslangic() {                           // [adım, alt adım]
      const q = adresOku(P.get("adim"));
      if (q) return q;
      const h = adresOku((location.hash || "").slice(1));
      if (h) return h;
      const k = oku().adim, j = oku().alt;
      return typeof k === "number" && k >= 0 && k < N ? [k, Math.max(0, Math.min(ADIM[k].alt || 0, typeof j === "number" ? j : 0))] : [0, 0];
    }

    function durum0(p, s) {                          // adım düzeyi: "gizli" | "simdi" | "alt" (alt montaj bağlanıyor) | "onceki"
      const st = ADIM[s];
      if (s === 0) return "hedef";
      if (st.tezgah) {
        if (p.t !== st.tezgah || p.a > s) return "gizli";
        return p.a === s ? "simdi" : "onceki";
      }
      if (p.b > s) return "gizli";
      if (p.b === s) return p.a === s ? "simdi" : "alt";
      return "onceki";
    }
    function durum(p, s, j) {                        // F10d: alt adımda grup sırasına göre
      if (j === undefined) j = s === su ? ss : 0;
      const st = ADIM[s];
      const d0 = durum0(p, s);
      if (!j || !st.alt || s === 0) return d0;
      const G = st.sira_grup, g = G[j - 1], gh = grupHarita(s);
      const pg = p.a === s ? gh.p[p.id] : undefined;
      if (g.tezgah) {                                // masa: yalnız bu birimin buraya kadarki parçaları
        if (pg == null || G[pg].tezgah !== g.tezgah || pg > j - 1) return "gizli";
        return pg === j - 1 ? "simdi" : "onceki";
      }
      if (p.a !== s) return d0 === "alt" ? (j === 1 ? "alt" : "onceki") : d0;
      if (pg == null) return d0;
      const key = G[pg].tezgah;
      if (key && gh.bag[key] != null) {              // masa birimi: bağlandığı alt adımda "alt", sonra önceki
        const bi = gh.bag[key];
        return j - 1 < bi ? "gizli" : (j - 1 === bi ? "alt" : "onceki");
      }
      return pg < j - 1 ? "onceki" : (pg === j - 1 ? "simdi" : "gizli");
    }
    function altGrup(s, j) { if (j === undefined) j = s === su ? ss : 0; return j && ADIM[s].alt ? ADIM[s].sira_grup[j - 1] : null; }

    function sinif(p) { return SINIF[p.r] ? p.r : "satin"; }
    // F10e: renk kipi (C tuşu / düğme; ?renk=sinif|gercek; yerel kayıt). Kablo yolu parçaları (p.renk) iki kipte de kablo rengiyle.
    let renkKip = P.get("renk") === "sinif" || P.get("renk") === "gercek" ? P.get("renk") : (oku().renk === "sinif" ? "sinif" : "gercek");
    function parcaRengi(p) { return p.renk || (renkKip === "gercek" && p.gr ? p.gr : SINIF[sinif(p)][0]); }
    function satirRengi(x, bag) {                      // panel satırı: gerçek kipte satırın ilk parçasının rengi
      const id = x.ids && x.ids[0], p = id && PAR[id] && PAR[id].v;
      if (renkKip === "gercek" && p && p.gr) return p.renk || p.gr;
      return bag ? SINIF.baglanti[0] : (SINIF[x.r] || SINIF.satin)[0];
    }
    function evListe(s, j) {                         // F10e: bağlandığı yer (veri; alt adımda grubun, genel bakışta adımın)
      const ag = altGrup(s, j);
      return new Set((ag ? ag.ev : ADIM[s].ev) || []);
    }
    // kenar çizgisi: geometri başına bir EdgesGeometry (30°), nesneye çocuk olarak (uçuşta parçayla gider)
    const kenarGeo = new Map(), kenarMat = {};
    function kenarKoy(o, renk) {
      let e = o.userData.kenar;
      if (!renk) { if (e) e.visible = false; return; }
      if (!e) {
        let g = kenarGeo.get(o.geometry.uuid);
        if (!g) { g = new THREE.EdgesGeometry(o.geometry, 30); kenarGeo.set(o.geometry.uuid, g); }
        e = new THREE.LineSegments(g, null); e.raycast = function () {}; e.userData.kenarMi = true;
        o.add(e); o.userData.kenar = e;
      }
      if (!kenarMat[renk]) kenarMat[renk] = new THREE.LineBasicMaterial({ color: renk });
      e.material = kenarMat[renk]; e.visible = true;
    }
    // F10e düzeltme 1 (kontrol bulgu 1, 2): saydam katmanların arkasındaki yeni bağlantı elemanı. Saydam çizilen parçalar (alt adımın
    // saydam listesi) çift yüzlü ve derinlik yazmaz; arkalarındaki opak cıvata / ısıl gömme her yüzde soluklaşır (ölçüm: katmanların
    // geçirdiği ≈ %10). Açık temada çelik açık zeminden yine ayrılıyordu, koyu temada zemine karışıp 0–3 px kalıyordu (34.3–34.6,
    // 35.1, 35.2 bindirme cıvataları; 31.3 p0762 iki temada). Çözüm rengi değiştirmez: parça aynı renkte, opaklık 1, derinlik yazarak
    // saydam geçişte saydam katmanlardan sonra çizilir (renderOrder 10; küçük görünümdeki vurgunun yöntemi). Opak parçaların arkasında
    // kalan yeri yine gizli (derinlik testi açık); saydam katmanın arkasında kalan yeri tam renkte görünür. Kenarı da ondan sonra.
    const ustMat = {};
    function ustteOf(m) {
      const k = m.color.getHexString();
      if (!ustMat[k]) ustMat[k] = new THREE.MeshStandardMaterial({ color: m.color.clone(), metalness: 0.05, roughness: 0.75, side: THREE.DoubleSide,
        transparent: true, opacity: 1, depthWrite: true });
      return ustMat[k];
    }
    function ustteKoy(o) {
      o.material = o.userData.mat0 = o.userData.mat1 = ustteOf(o.material);
      o.renderOrder = 10; o.userData.ustte = true;
      const e = o.userData.kenar;
      if (e && e.visible) {
        const k = "#" + e.material.color.getHexString() + "|u";
        if (!kenarMat[k]) kenarMat[k] = new THREE.LineBasicMaterial({ color: e.material.color.clone(), transparent: true, opacity: 1 });
        e.material = kenarMat[k]; e.renderOrder = 11;
      }
    }

    // bir nesnenin yerel sınır kutusunun 8 köşesi, dünya koordinatında (kadraj; kutunun kendisi parçayı kapsar)
    function koseler(o, ek, hedef) {
      const g = o.geometry; if (!g.boundingBox) g.computeBoundingBox();
      const b = g.boundingBox;
      for (let i = 0; i < 8; i++) {
        const v = new THREE.Vector3(i & 1 ? b.max.x : b.min.x, i & 2 ? b.max.y : b.min.y, i & 4 ? b.max.z : b.min.z).applyMatrix4(o.matrixWorld);
        if (ek) v.add(ek);
        hedef.push(v);
      }
    }

    let sonUc = [], sonSay = {}, sonEv = [];

    // ---------------------------------------------------------------- F10e: bağlantı elemanı işaretleri (ekranda sabit boyutlu halka)
    // Konumun yeni bağlantı elemanları (durum "simdi"): işaret noktası veride (parcalar[].ip: cıvata başı üst merkezi, öbürleri kutu
    // merkezi; parça uçarken / patlakken onunla gider). Ekranda ISARET.R px'ten yakın işaretler tek halkada kümelenir, halkada adet
    // (×n) yazar; kümelerin adetleri toplamı = yeni bağlantı elemanı sayısı. Panel satırı (ya da parça) seçilince o satırın işaretleri
    // seçim renginde. SVG katmanı tuvalin üstünde (yazdırma karesinde de görünür), tıklamayı engellemez.
    const ISARET = { acik: P.get("isaret") === "0" ? false : (P.get("isaret") === "1" ? true : oku().isaret !== false), liste: [], R: 22, kume: [] };
    const isaretEl = $("isaret");
    const _ip = new THREE.Vector3();
    function isaretKur(uc) {
      ISARET.liste = [];
      uc.forEach((x) => {
        const p = x.k.v;
        if (x.d !== "simdi" || p.r !== "baglanti" || !p.ip) return;
        ISARET.liste.push({ id: p.id, k: x.k, ip: new THREE.Vector3(p.ip[0], p.ip[1], p.ip[2]) });
      });
    }
    function isaretCiz() {
      if (!isaretEl) return;
      if (!ISARET.acik || !ISARET.liste.length) { if (isaretEl.innerHTML) isaretEl.innerHTML = ""; ISARET.kume = []; return; }
      const c = tuval.getBoundingClientRect(), W = c.width, H = c.height;
      const sec = secim ? new Set(secim.ids) : null;
      const kume = [];
      ISARET.liste.forEach((m) => {
        const o = m.k.obj; if (!o || !o.visible) return;
        _ip.copy(m.ip).add(o.position).sub(m.k.taban);
        _v.copy(_ip).applyMatrix4(kamera.matrixWorldInverse);
        if (_v.z > -kamera.near) return;
        _ip.project(kamera);
        const x = (_ip.x + 1) / 2 * W, y = (1 - _ip.y) / 2 * H;
        if (x < 0 || y < 0 || x > W || y > H) return;
        let k = null;
        for (const q of kume) if (Math.hypot(q.x - x, q.y - y) < ISARET.R) { k = q; break; }
        if (!k) { k = { x: x, y: y, ids: [] }; kume.push(k); }
        k.ids.push(m.id);
      });
      ISARET.kume = kume;
      isaretEl.setAttribute("viewBox", "0 0 " + Math.round(W) + " " + Math.round(H));
      isaretEl.innerHTML = kume.map((k) => {
        const s = sec && k.ids.some((i) => sec.has(i));
        const x = k.x.toFixed(1), y = k.y.toFixed(1);
        return "<g class='isr" + (s ? " secili" : "") + "'><circle class='d' cx='" + x + "' cy='" + y + "' r='9'/><circle class='i' cx='" + x +
          "' cy='" + y + "' r='9'/>" + (k.ids.length > 1 ? "<text x='" + (k.x + 11).toFixed(1) + "' y='" + (k.y - 8).toFixed(1) + "'>×" +
          k.ids.length + "</text>" : "") + "</g>";
      }).join("");
    }
    function isaretGoster(a) {
      ISARET.acik = a;
      if (!SAHNE) yaz("isaret", a);
      const d = $("isaret-dugme"); if (d) d.classList.toggle("acik", a);
      lejant(sonSay, su); ciz();
    }

    // ---------------------------------------------------------------- F10e: kare başlığı (karenin hangi adım / alt adım ve bakış yönü
    // olduğu karenin kendisinden okunsun: benzer kare çiftleri 34.3 / 34.5, 34.4 / 34.6, 49.3 / 49.4). Bakış yönü kamera vektöründen
    // (robot: +x sağ, +y yukarı, +z ön).
    // Yalnız yazdırma / PDF karesinde (?sahne=1): etkileşimli sayfada aynı ad ve numara sahnenin yanındaki panel başlığında; araç
    // çubuğunun altında ayrıca başlık bandı güvenli alanı daraltıyor, yeni parçalar küçülüyordu (F10d görünürlüğü: 33.5, 33.7, 36.1'de
    // cıvata / ısıl gömme 30 px eşiğinin altına indi)
    function kareBaslik(s) {
      const e = $("kare-baslik"); if (!e) return;
      if (s === 0 || !SAHNE) { e.hidden = true; return; }
      const ag = altGrup(s), st = ADIM[s];
      const y = kameraYonu();
      const ad = ag ? ag.ad : st.baslik;
      e.innerHTML = "<b>" + esc(adres(s, ss)) + "</b> " + esc(ad) + " <span class='bakis'>· bakış: " + esc(bakisMetin(y)) + "</span>";
      e.hidden = false;
    }
    function bakisMetin(y) {                          // "sağ-ön-üstten", "sol-arkadan"
      const t = [];
      if (y.x > 0.3) t.push("sağ"); else if (y.x < -0.3) t.push("sol");
      if (y.z > 0.3) t.push("ön"); else if (y.z < -0.3) t.push("arka");
      if (y.y > 0.45) t.push("üst"); else if (y.y < -0.3) t.push("alt");
      if (!t.length) return "yandan";
      const son = t[t.length - 1];
      t[t.length - 1] = son + ({ "sağ": "dan", "sol": "dan", "ön": "den", "arka": "dan", "üst": "ten", "alt": "tan" })[son];
      return t.join("-");
    }

    function uygula(s, ucus) {
      const gizle = onceki === "gizli", saydam = onceki === "saydam";
      const kutu = new THREE.Box3(), gorunur = new THREE.Box3(), altKutu = new THREE.Box3();
      const uc = [];
      const sinifSay = {};
      const yeni = { simdi: [], alt: [], hedef: [] }, eksik = [];   // kontrol: bu adımda yeni görünenler (duruma göre), mesh'i olmayanlar
      const nokta = [], gNokta = [];                  // kadraj: yeni parçaların / görünenlerin kutu köşeleri (son konumda)
      let altVar = false;
      const ev = evListe(s);                          // F10e: bağlandığı yer
      const tm = tema(), kenarRenk = KENAR[tm === "dark" ? "dark" : "light"];
      sonEv = [];
      for (const id in PAR) {
        const k = PAR[id]; const p = k.v; const o = k.obj;
        if (!o) { eksik.push(p.id); continue; }
        const d = durum(p, s);
        o.position.copy(k.taban);
        o.userData.d = d;
        o.userData.ev = false;
        o.renderOrder = 0; o.userData.ustte = false; if (o.userData.kenar) o.userData.kenar.renderOrder = 0;
        const evMi = ev.has(p.id);
        if (d === "gizli" || (d === "onceki" && gizle && !p.renk && !evMi)) { o.visible = false; kenarKoy(o, null); continue; }
        o.visible = true;
        if (yeni[d]) yeni[d].push(p.id);
        o.updateMatrixWorld(true);
        const b = new THREE.Box3().setFromObject(o);
        gorunur.union(b);
        if (d === "onceki") {
          // F10e: bağlandığı önceki parça ayrı tonda (öncekiler saydam kipteyse o da saydam)
          o.material = p.renk ? malzeme(p.renk, saydam ? 0.2 : true) : malzeme(evMi ? EV_RENK : SINIF.onceki[0], saydam ? 0.18 : 1);
          o.userData.mat0 = o.material;
          o.userData.ev = evMi && !p.renk;
          if (o.userData.ev) sonEv.push(p.id);
          kenarKoy(o, null);
          continue;
        }
        const c = parcaRengi(p);
        o.material = malzeme(c);
        o.userData.mat0 = o.userData.mat1 = o.material;
        // kenar: bağlandığı yer bu adımda yeniyse (masa tabanı) ev tonunda; değilse zeminle karşıtlığı eşiğin altındaysa tema renginde
        if (evMi && !p.renk) { kenarKoy(o, EV_RENK); o.userData.ev = true; sonEv.push(p.id); }
        // F10e: önceki adımların grisine çok yakın gerçek renk (ör. alüminyum horn, çelik cıvata) de kenar alır: tezgâh karelerinde
        // yeni parça öncekilerden ayrılsın (önceki grisiyle karşıtlık < ONCEKI_ESIK)
        else kenarKoy(o, karsitlik(c, zeminHex) < KENAR_ESIK || karsitlik(c, SINIF.onceki[0]) < ONCEKI_ESIK ? kenarRenk : null);
        sinifSay[p.renk ? "kablo" : (renkKip === "gercek" ? "gercek" : sinif(p))] = 1;
        kutu.union(b);
        koseler(o, null, nokta);
        if (d === "alt") { altVar = true; altKutu.union(b); }
        uc.push({ k: k, d: d });
      }
      const semaYeni = [];
      SEMA_OBJ.forEach((o, i) => {
        if (!o) return;
        const d = semaDurum(i, s);
        o.userData.d = d;
        o.visible = d !== "gizli";
        if (!o.visible) return;
        o.material = malzeme(SEMA[i].renk, d === "onceki" ? (saydam ? 0.2 : true) : 1);
        o.userData.mat0 = o.userData.mat1 = o.material;
        const b = new THREE.Box3().setFromObject(o);
        gorunur.union(b);
        if (d === "simdi" || d === "hedef") { kutu.union(b); koseler(o, null, nokta); }
        if (d === "simdi") { semaYeni.push(i); sinifSay.kablo = 1; }
      });
      // F10e: konumun yeni parçalarının hepsi bağlantı elemanıysa (ör. 31.5, 31.10, 36.3) kadraj bağlandığı parçaları da kapsar: yalnız
      // cıvatalara sıkı kadraj yerini göstermiyordu (F10d "kadraj yakın"); cıvataların yeri işaret halkalarıyla seçilir
      if (uc.length && sonEv.length && uc.every((x) => x.k.v.r === "baglanti")) {
        sonEv.forEach((id) => { const o = PAR[id] && PAR[id].obj; if (o && o.visible) koseler(o, null, nokta); });
      }
      if (!nokta.length && !gorunur.isEmpty()) {
        for (let i = 0; i < 8; i++) gNokta.push(new THREE.Vector3(i & 1 ? gorunur.max.x : gorunur.min.x, i & 2 ? gorunur.max.y : gorunur.min.y,
          i & 4 ? gorunur.max.z : gorunur.min.z));
      }
      // uçuş vektörleri (F10d: "bag" alt adımında birim grubun ub yönünden gelir; ısıl gömme ev sahibiyle birlikte uçar)
      const altBoy = altVar ? Math.max(120, altKutu.getSize(new THREE.Vector3()).length() * 0.8) : 0;
      const ag = altGrup(s);
      const ubG = ag && ag.bag && ag.ub ? ag.ub : null;
      uc.forEach((x) => {
        const p = x.k.v;
        const ub = ubG || p.ub;
        if (x.d === "alt" && ub) x.ofs = new THREE.Vector3(ub[0], ub[1], ub[2]).multiplyScalar(altBoy);
        else if (x.d === "simdi" && p.d > 0 && !p.renk) x.ofs = new THREE.Vector3(p.u[0], p.u[1], p.u[2]).multiplyScalar(p.d);
        else x.ofs = null;
        x.gec = (p.r === "baglanti") ? 0.45 : 0;
      });
      const um = new Map(); uc.forEach((x) => um.set(x.k.v.id, x));
      uc.forEach((x) => {
        const h = x.k.v.h && um.get(x.k.v.h);
        if (h && h.d === x.d) { x.ofs = h.ofs ? h.ofs.clone() : null; x.gec = h.gec; }
      });
      const sdl = ag ? ag.saydam : ADIM[s].saydam;    // F10d: alt adımın (yoksa adımın) saydam çizdiği önceki parçalar
      if (sdl && sdl.length) {                       // içerisi görünsün diye
        const sd = new Set(sdl);
        for (const id in PAR) {
          const o = PAR[id].obj;
          // F10d düzeltme 1: bu alt adımda gelen parça saydam listedeyse (içindeki ısıl gömme / parça görünsün diye) 0,4 opaklık;
          // önceki parçalar 0,25. İkisi de < 0,5: görünürlük ölçümünde arkasını örtmez (RehberTest.gorunurluk)
          const yeniMi = o && (o.userData.d === "simdi" || o.userData.d === "alt");
          if (o && o.visible && sd.has(id)) {
            o.material = o.userData.mat0 = o.userData.mat1 = saydamOf(o.material, yeniMi ? 0.4 : 0.25);
            // F10e: saydam çizilen yeni parçanın görünen rengi zeminle karışır (ör. 35.3 kara taşıyıcı açık temada bulanık kalıyordu):
            // kenar her zaman, iki tema renginden parçanın kendi rengiyle karşıtlığı yüksek olanı (ev kenarı korunur)
            if (yeniMi && !o.userData.ev) {
              const c = "#" + o.material.color.getHexString();
              kenarKoy(o, karsitlik(c, KENAR.light) >= karsitlik(c, KENAR.dark) ? KENAR.light : KENAR.dark);
            }
          }
        }
        // F10e düzeltme 1: saydam katmanların arkasındaki yeni bağlantı elemanları saydam geçişte üstte (ustteKoy). ?ustte=0: kapalı
        // (yalnız önce / sonra ölçümü için)
        if (P.get("ustte") !== "0") uc.forEach((x) => {
          const o = x.k.obj, m = o.material;
          if (x.k.v.r === "baglanti" && !sd.has(x.k.v.id) && !(m.transparent && m.opacity < 1)) ustteKoy(o);
        });
      }
      sonUc = uc; sonSay = sinifSay;
      isaretKur(uc);
      kareBaslik(s);
      if (sira && sira.adim === s && sira.alt === ss) siraKonum();
      vurguUygula(true);
      lejant(sinifSay, s);
      if (miniAdim !== adres(s, ss)) miniGuncelle(s);
      if (ucus && !CEKIM) baslatUcus(uc); else ciz();
      return { kutu: kutu.isEmpty() ? gorunur : kutu, gorunur: gorunur, yeni: yeni, eksik: eksik, sema: semaYeni,
        nokta: nokta.length ? nokta : gNokta };
    }

    function canlandir(hareket, T, bitince) {         // hareket: [{ o, a (başlangıç), b (bitiş), gec (0..1) }]
      if (anim) cancelAnimationFrame(anim);
      const t0 = performance.now();
      const adim = (t) => {
        const f = Math.min(1, (t - t0) / T);
        hareket.forEach((x) => {
          const g = Math.min(1, Math.max(0, (f - (x.gec || 0)) / (1 - (x.gec || 0) - 0.0001)));
          const e = 1 - Math.pow(1 - g, 3);
          x.o.position.lerpVectors(x.a, x.b, e);
        });
        render();
        anim = f < 1 ? requestAnimationFrame(adim) : null;
        if (!anim && bitince) bitince();
      };
      hareket.forEach((x) => x.o.position.copy(x.a));
      anim = requestAnimationFrame(adim);
    }

    function baslatUcus(uc) {                         // adım açılınca / R: adımın bütün parçaları birlikte yerine uçar
      const h = [];
      uc.forEach((x) => { if (x.ofs) h.push({ o: x.k.obj, a: x.k.taban.clone().add(x.ofs), b: x.k.taban, gec: x.gec }); });
      canlandir(h, 1300);
    }

    // ---------------------------------------------------------------- patlat + sıralı tak (F10a)
    // patlat: adımın parçaları uçuş başlangıcında (taban + u·d) bekler, uçuş yönü olmayanlar (kablo, şema) gizlenir.
    // tak (Boşluk): panel sırasıyla bir satır yerine gider (önce bağlanan alt montaj, sonra parçalar, sonra bağlantı elemanları,
    // en son şemalar); takılan satır seçili gösterilir. Shift+Boşluk son satırı geri çıkarır. ↻ uçuş (R) hepsini birlikte oynatır.
    let sira = null;                                  // { adim, satir: [{ ad, ids, sema, tur, i }], n: takılan satır sayısı }
    function siraKur() {
      const st = ADIM[su];
      const var_ = new Set(sonUc.map((x) => x.k.v.id));
      const satir = [];
      const ag = altGrup(su);
      const alt = sonUc.filter((x) => x.d === "alt").map((x) => x.k.v.id);
      if (alt.length) {
        const kod = ADIM.filter((a) => a.baglanir === su).map((a) => a.i + ". " + a.kod).join(", ");
        satir.push({ ad: ag && ag.bag ? ag.ad : "Alt montaj" + (kod ? " (" + kod + ")" : ""), ids: alt, sema: [] });
      }
      const pb = {};                                  // F10c: adım verisinde "sira" (p:i / b:i) varsa satırlar o sırayla
      // F10d: ısıl gömme satırı (onceden) ev sahibiyle yerine gelir: sıralı takmada satır kalır (panel sırası = takma sırası), parçaları
      // ev sahibinin satırıyla birlikte konumlanır (siraKonum)
      st.parcalar.forEach((x, i) => { pb["p:" + i] = { ad: x.ad, ids: x.ids.filter((id) => var_.has(id)), sema: [], tur: "p", i: i, adet: x.adet }; });
      st.baglantilar.forEach((x, i) => { pb["b:" + i] = { ad: x.kod, ids: x.ids.filter((id) => var_.has(id)), sema: [], tur: "b", i: i, adet: x.adet,
        onceden: !!x.onceden }; });
      (ag ? ag.satir : (st.sira || Object.keys(pb))).forEach((k) => { if (pb[k]) satir.push(pb[k]); });
      const sm = [];
      SEMA_OBJ.forEach((o, i) => { if (o && o.userData.d === "simdi") sm.push(i); });
      if (sm.length) satir.push({ ad: "Kablo şemaları", ids: [], sema: sm });
      return satir.filter((x) => x.ids.length || x.sema.length);
    }
    function ucHarita() { const m = new Map(); sonUc.forEach((x) => m.set(x.k.v.id, x)); return m; }
    // takılmamış satırlar patlak konumda / gizli, takılanlar yerinde. Saydam kipte bu adımda daha önce takılan satırlar da
    // (ör. kabuk) saydamlaşır; o an takılan satır ve bekleyenler opak kalır: içeri giren parça kabuğun arkasında kaybolmaz.
    function saydamOf(m, a) { return malzeme("#" + m.color.getHexString(), a || 0.25); }
    function siraKonum() {
      const m = ucHarita();
      const sd = onceki === "saydam";
      const taban = (o, j) => {
        const b = o.userData.mat1 || o.material;
        o.material = o.userData.mat0 = sd && j < sira.n - 1 ? saydamOf(b) : b;
      };
      const satirNo = {};
      sira.satir.forEach((r, j) => r.ids.forEach((id) => { satirNo[id] = j; }));
      sira.satir.forEach((r, j) => {
        r.ids.forEach((id) => {
          const x = m.get(id); if (!x) return;
          const h = x.k.v.h, jj = h != null && satirNo[h] != null ? satirNo[h] : j;   // F10d: ısıl gömme ev sahibinin satırıyla
          const takili = jj < sira.n;
          const o = x.k.obj;
          o.position.copy(x.k.taban);
          if (!takili) { if (x.ofs) o.position.add(x.ofs); else o.visible = false; }
          else o.visible = true;
          taban(o, jj);
        });
        r.sema.forEach((i) => { SEMA_OBJ[i].visible = j < sira.n; taban(SEMA_OBJ[i], j); });
      });
    }
    function patlat() {
      if (!yuklu || su === 0) return;
      if (sira) { sira = null; secimTemizle(); uygula(su, false); siraDugme(); return; }      // topla: hepsi yerinde
      if (anim) { cancelAnimationFrame(anim); anim = null; }
      const k = uygula(su, false);
      // kadraj: yerindeki ve patlak konumdaki köşeler birlikte (matrixWorld uygula()'dan beri son konumda)
      const nk = k.nokta.slice();
      sonUc.forEach((x) => { if (x.ofs) koseler(x.k.obj, x.ofs, nk); });
      // siki: yerindeki köşeler (bütün satırlar takılınca bu kadraja dönülür, F10a düzeltme 1 / B-4); patlak: iki konum birlikte
      sira = { adim: su, alt: ss, satir: siraKur(), n: 0, siki: k.nokta, patlak: nk, gorunur: k.gorunur };
      siraKonum();
      kameraYerlestir({ nokta: nk, gorunur: k.gorunur });
      secimTemizle();
      siraDugme();
      ciz();
    }
    function tak() {
      if (!yuklu || su === 0) return;
      if (!sira) { patlat(); return; }
      if (sira.n >= sira.satir.length) return;
      if (anim) { cancelAnimationFrame(anim); anim = null; }
      const r = sira.satir[sira.n]; sira.n++;
      siraKonum();                                    // önceki satırlar yerinde (saydam kipte saydam), bu satır görünür
      const m = ucHarita(); const h = [];
      const bu = new Set(r.ids);
      sonUc.forEach((x) => { if (x.k.v.h && bu.has(x.k.v.h)) bu.add(x.k.v.id); });   // ev sahibiyle gelen ısıl gömmeler
      bu.forEach((id) => {
        const x = m.get(id); if (!x) return;
        if (x.k.v.h && !bu.has(x.k.v.h) && r.ids.indexOf(id) >= 0 && r.onceden) return;   // ev sahibi daha önce takıldı: yerinde
        if (x.ofs) h.push({ o: x.k.obj, a: x.k.taban.clone().add(x.ofs), b: x.k.taban, gec: 0 });
      });
      secimYap({ ids: r.ids, sema: r.sema, hepsi: true, satir: r.tur ? { adim: su, tur: r.tur, i: r.i } : null });
      etiketYaz("<b>" + esc(r.ad) + "</b>" + (r.adet > 1 ? " ×" + r.adet : "") + "<br><span class='not'>Sıra " + sira.n + " / " +
        sira.satir.length + " · Boşluk: sıradaki, Shift+Boşluk: geri</span>");
      siraDugme();
      // B-4: son satır yerine oturunca kamera patlak kutudan yeni parçalara sıkı kadraja döner (V'nin verdiği kadraj)
      const s0 = sira;
      const bitti = sira.n >= sira.satir.length ? () => { if (sira === s0 && su === s0.adim) kameraYerlestir({ nokta: s0.siki, gorunur: s0.gorunur }); } : null;
      if (h.length && !CEKIM) canlandir(h, 900, bitti); else { h.forEach((x) => x.o.position.copy(x.b)); ciz(); if (bitti) bitti(); }
    }
    function geriAl() {
      if (!sira || sira.n === 0) return;
      if (anim) { cancelAnimationFrame(anim); anim = null; }
      const tamdi = sira.n >= sira.satir.length;
      sira.n--;
      siraKonum();
      secimTemizle();
      siraDugme();
      if (tamdi) kameraYerlestir({ nokta: sira.patlak, gorunur: sira.gorunur });   // geri çıkan satır patlak konumda kadrajda kalsın
      ciz();
    }
    function siraDugme() {
      const p = $("patlat"), t = $("tak");
      if (!p || !t) return;
      p.innerHTML = sira ? "⇲ <span class='yazi'>topla</span>" : "⇱ <span class='yazi'>patlat</span>";
      p.classList.toggle("acik", !!sira);
      t.innerHTML = "▶ <span class='yazi'>tak</span>" + (sira ? " " + sira.n + "/" + sira.satir.length : "");
      t.disabled = su === 0 || !!(sira && sira.n >= sira.satir.length);
      p.disabled = su === 0;
    }

    // ---------------------------------------------------------------- kadraj (F10a: yeni parçalara sıkı)
    // Yeni parçaların kutu köşeleri, araç çubuğu / lejant / küçük görünüm dışında kalan alana sığdırılır: kamera yönü sabit
    // (ön-sağ-üst; B1 / B1a alttan; "kamera": "arka" arkadan), uzaklık ve hedef yinelemeli bulunur. Küçük görünüm sağ sütunu ya da
    // alt şeridi kaplar; ikisinden hangisi daha büyük görüntü veriyorsa o seçilir. Bağlam küçük görünümde.
    function guvenliAlanlar() {
      const c = tuval.getBoundingClientRect(); const W = Math.max(1, c.width), H = Math.max(1, c.height);
      let ust = 0, alt = 0, sag = 0, altMini = 0;
      const ar = document.querySelector(".sahne-arac"), lj = $("lejant");   // gizli öğenin offsetParent'ı yok (?sahne=1 araç çubuğu)
      if (ar && ar.offsetParent) ust = Math.max(0, ar.getBoundingClientRect().bottom - c.top + 4);
      const kb = $("kare-baslik");                    // F10e: kare başlığı araç çubuğunun altında (yazdırma karesinde en üstte)
      if (kb && !kb.hidden && kb.offsetParent) ust = Math.max(ust, kb.getBoundingClientRect().bottom - c.top + 4);
      if (lj && !lj.hidden && lj.offsetParent) alt = Math.max(0, c.bottom - lj.getBoundingClientRect().top + 4);
      if (miniAcik && !miniEl.hidden) {
        const m = miniEl.getBoundingClientRect();
        sag = Math.max(0, c.right - m.left + 4); altMini = Math.max(0, c.bottom - m.top + 4);
      }
      const pay = 0.03;
      const ndc = (x0, y0, x1, y1) => ({ x0: x0 / W * 2 - 1 + pay, x1: x1 / W * 2 - 1 - pay, y0: 1 - y1 / H * 2 + pay, y1: 1 - y0 / H * 2 - pay });
      const a = [ndc(0, ust, W - sag, H - alt)];
      if (sag > 0) a.push(ndc(0, ust, W, H - Math.max(alt, altMini)));
      return a.filter((x) => x.x1 - x.x0 > 0.2 && x.y1 - x.y0 > 0.2);
    }
    const _v = new THREE.Vector3(), _sag = new THREE.Vector3(), _yuk = new THREE.Vector3();
    function konumla(hedef, yon, D) {
      kamera.position.copy(hedef).addScaledVector(yon, D);
      kamera.near = Math.max(1, D / 100); kamera.far = D * 20 + 4000;
      kamera.up.set(0, 1, 0); kamera.lookAt(hedef);
      kamera.updateProjectionMatrix(); kamera.updateMatrixWorld(true);
    }
    function olc(noktalar) {
      let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
      for (const p of noktalar) {
        _v.copy(p).applyMatrix4(kamera.matrixWorldInverse);
        if (_v.z > -kamera.near) return null;         // kameranın arkasında
        _v.applyMatrix4(kamera.projectionMatrix);
        if (_v.x < x0) x0 = _v.x; if (_v.x > x1) x1 = _v.x; if (_v.y < y0) y0 = _v.y; if (_v.y > y1) y1 = _v.y;
      }
      return { x0, x1, y0, y1 };
    }
    function sigdir(noktalar, yon, alan) {
      const kutu = new THREE.Box3().setFromPoints(noktalar);
      const hedef = kutu.getCenter(new THREE.Vector3());
      const th = Math.tan(kamera.fov * Math.PI / 360);
      const Dmin = 45 / th;                           // en yakın: hedef derinliğinde ~90 mm yükseklik
      let D = Math.max(Dmin, kutu.getSize(new THREE.Vector3()).length() / th);
      let e = null, k = 1;
      for (let it = 0; it < 30; it++) {
        konumla(hedef, yon, D);
        e = olc(noktalar);
        if (!e) { D *= 1.6; continue; }
        k = Math.max((e.x1 - e.x0) / (alan.x1 - alan.x0), (e.y1 - e.y0) / (alan.y1 - alan.y0), 1e-6);
        const hh = D * th, hw = hh * kamera.aspect;
        _sag.setFromMatrixColumn(kamera.matrixWorld, 0); _yuk.setFromMatrixColumn(kamera.matrixWorld, 1);
        const dx = (e.x0 + e.x1) / 2 - (alan.x0 + alan.x1) / 2, dy = (e.y0 + e.y1) / 2 - (alan.y0 + alan.y1) / 2;
        const sigiyor = e.x0 >= alan.x0 - 1e-3 && e.x1 <= alan.x1 + 1e-3 && e.y0 >= alan.y0 - 1e-3 && e.y1 <= alan.y1 + 1e-3;
        if (sigiyor && k > 0.985 && Math.abs(dx) < 0.01 && Math.abs(dy) < 0.01) break;
        if (sigiyor && D <= Dmin + 1e-6 && Math.abs(dx) < 0.01 && Math.abs(dy) < 0.01) break;
        hedef.addScaledVector(_sag, dx * hw).addScaledVector(_yuk, dy * hh);
        D = Math.max(Dmin, D * (it < 20 ? k : Math.max(k, 1) * 1.01));
      }
      for (let n = 0; n < 20; n++) {                  // güvence: hiçbir köşe alanın dışında kalmasın
        konumla(hedef, yon, D); e = olc(noktalar);
        if (e && e.x0 >= alan.x0 - 1e-3 && e.x1 <= alan.x1 + 1e-3 && e.y0 >= alan.y0 - 1e-3 && e.y1 <= alan.y1 + 1e-3) break;
        D *= 1.04;
      }
      return { hedef: hedef, D: D };
    }
    let sonKutu = null;
    function kameraYonu() {
      const st = ADIM[su];
      const yon = new THREE.Vector3(0.85, 0.62, 1.25);
      const alttan = st && (st.kod === "B1" || st.kod === "B1a");
      if (alttan) yon.set(0.9, -0.55, 1.2);
      if (st && st.kamera === "arka") yon.set(0.85, 0.62, -1.25);   // rehber_metin "kamera": yeni parçalar arkada (F5 kapaklar)
      if (st && Array.isArray(st.kamera)) yon.set(st.kamera[0], st.kamera[1], st.kamera[2]);   // F10d: adım kamerası (vektör)
      const ag = st && altGrup(su);                  // F10d: alt adımın kendi kamerası
      if (ag && ag.kamera === "arka") yon.set(0.85, 0.62, -1.25);
      else if (ag && Array.isArray(ag.kamera)) yon.set(ag.kamera[0], ag.kamera[1], ag.kamera[2]);
      return yon.normalize();
    }
    function kameraYerlestir(k) {
      let nokta = k.nokta && k.nokta.length ? k.nokta : null;
      if (!nokta) {
        nokta = [];
        const b = new THREE.Box3(new THREE.Vector3(-300, 0, -300), new THREE.Vector3(300, 1300, 300));
        for (let i = 0; i < 8; i++) nokta.push(new THREE.Vector3(i & 1 ? b.max.x : b.min.x, i & 2 ? b.max.y : b.min.y, i & 4 ? b.max.z : b.min.z));
      }
      const yon = kameraYonu();
      let en = null, ai = 0;
      guvenliAlanlar().forEach((alan, i) => { const r = sigdir(nokta, yon, alan); if (!en || r.D < en.D) { en = r; ai = i; } });
      if (!en) en = sigdir(nokta, yon, { x0: -0.95, x1: 0.95, y0: -0.95, y1: 0.95 });
      konumla(en.hedef, yon, en.D);
      kontrol.target.copy(en.hedef);
      kontrol.update();
      k.kadraj = { D: Math.round(en.D), alan: ai === 0 ? "sag-sutun" : "alt-serit", nokta: nokta.length };
      sonKutu = k;
      ciz();
    }

    let gitSay = 0;
    function git(s, ucus, j) {
      s = Math.max(0, Math.min(N - 1, s));
      j = Math.max(0, Math.min(ADIM[s].alt || 0, j || 0));
      su = s; ss = j;
      sira = null; secim = null;
      yaz("adim", s); yaz("alt", j);
      // F10d düzeltme 1 (kontrol B-10): adres gezinmeyi izlesin. Sayfa ?adim= ile açıldıysa gezindikçe sorgudaki adim de güncellenir
      // (yenilemede sorgu hash'ten önce okunur; eskiden bayat kalıyordu). İlk açılışta sorgu olduğu gibi kalır.
      try {
        const q = new URLSearchParams(location.search);
        if (gitSay++ > 0 && q.has("adim")) q.set("adim", adres(s, j));
        const qs = q.toString().replace(/%2C/g, ",");
        history.replaceState(null, "", location.pathname + (qs ? "?" + qs : "") + "#" + adres(s, j));
      } catch (e) { /* file:// */ }
      panel(s);
      const k = uygula(s, ucus !== false);
      kameraYerlestir(k);
      const no = konumNo(s, j);
      $("geri").disabled = no === 0; $("ileri").disabled = no === KONUM.length - 1;
      $("secim").value = adres(s, j);
      $("cubuk").style.width = (100 * no / Math.max(1, KONUM.length - 1)) + "%";
      $("sayac").textContent = "Adım " + s + " / " + (N - 1) + (ADIM[s].alt ? " · alt adım " + (j ? j + " / " + ADIM[s].alt : "genel bakış") : "");
      $("etiket").hidden = true;
      siraDugme();
      if (CEKIM) {
        // rehber_uret.py kontrolü --dump-dom ile okur: adım başına yeni görünen parça kimlikleri ve mesh'i bulunmayan parçalar
        const kv = $("kontrol-veri");
        if (kv) kv.textContent = JSON.stringify({ adim: s, alt_adim: j, kod: ADIM[s].kod, simdi: k.yeni.simdi.sort(), alt: k.yeni.alt.sort(),
          hedef: k.yeni.hedef.length, eksik: k.eksik, sema: k.sema, kadraj: k.kadraj });
        requestAnimationFrame(() => {
          ciz();
          // F7b: telefon kontrolü (rehber_uret.py --telefon): yatay taşma = belge genişliği - pencere genişliği
          const de = document.documentElement;
          de.dataset.genislik = String(window.innerWidth);
          de.dataset.tasma = String(Math.max(de.scrollWidth, document.body.scrollWidth) - de.clientWidth);
          document.body.dataset.hazir = "1";
        });
      }
    }

    // ---------------------------------------------------------------- çizim (ana görünüm + küçük görünüm aynı tuvalde)
    const _boy = new THREE.Vector2();
    function miniDikdortgen() {
      const c = tuval.getBoundingClientRect(), m = miniEl.getBoundingClientRect();
      return { x: m.left - c.left, y: c.bottom - m.bottom, w: m.width, h: m.height };
    }
    function render() {
      renderer.getSize(_boy);
      renderer.setScissorTest(false);
      renderer.setViewport(0, 0, _boy.x, _boy.y);
      renderer.render(sahne, kamera);
      isaretCiz();
      if (miniAcik && MINI.hazir && !miniEl.hidden) {
        const r = miniDikdortgen();
        if (r.w > 4 && r.h > 4) {
          renderer.setScissorTest(true);
          renderer.setScissor(r.x, r.y, r.w, r.h); renderer.setViewport(r.x, r.y, r.w, r.h);
          renderer.render(MINI.sahne, MINI.kamera);
          renderer.setScissorTest(false);
          renderer.setViewport(0, 0, _boy.x, _boy.y);
        }
      }
    }
    let bekleyen = false;
    function ciz() {
      if (anim || bekleyen) return;
      bekleyen = true;
      requestAnimationFrame(() => { bekleyen = false; render(); });
    }
    function boyut() {
      const r = tuval.parentElement.getBoundingClientRect();
      renderer.setSize(Math.max(1, r.width), Math.max(1, r.height), false);
      kamera.aspect = r.width / Math.max(1, r.height);
      kamera.updateProjectionMatrix();
      miniKamera();
      // F10a düzeltme 1 (B-1): setSize tuvalin çizim tamponunu temizler. ResizeObserver boyamadan hemen önce koşar; çizimi bir
      // sonraki kareye (ciz -> rAF) bırakmak bir karelik boş tuval sunar. Başsız --screenshot görüntüyü almadan hemen önce pencereyi
      // yeniden boyutlandırdığı için bu boş kare yazdırma görüntüsüne giriyordu. Aynı karede eşzamanlı çiz.
      render();
    }

    // ---------------------------------------------------------------- küçük görünüm: bütün robot soluk, bu adımın parçaları vurgulu
    let miniAdim = -1;
    function miniGuncelle(s) {
      if (!MINI.hazir) return;
      miniAdim = adres(s, ss);
      const st = ADIM[s];
      const ag = altGrup(s);
      MINI.hk.makeEmpty(); MINI.hlist = [];
      for (const id in PAR) {
        const k = PAR[id]; if (!k.mini) continue;
        const p = k.v; let m = MINI.soluk;
        if (s === 0) m = MINI.vurgu;
        else if (ag) { const d = durum(p, s); if (d === "simdi" || d === "alt") m = MINI.vurgu; else if (ag.tezgah && d === "onceki") m = MINI.yakin; }
        else if (st.tezgah) { if (p.t === st.tezgah) m = p.a === s ? MINI.vurgu : (p.a < s ? MINI.yakin : MINI.soluk); }
        else { const d = durum(p, s); if (d === "simdi" || d === "alt") m = MINI.vurgu; }
        k.mini.material = m; k.mini.renderOrder = m === MINI.vurgu ? 10 : 0;
        if (m === MINI.vurgu) { MINI.hk.union(k.mkutu); if (s > 0) MINI.hlist.push(k.mkutu); }
      }
      SEMA_MINI.forEach((m, i) => {
        if (!m) return;
        const v = s === 0 || semaDurum(i, s) === "simdi";
        m.material = v ? MINI.vurgu : MINI.soluk; m.renderOrder = v ? 10 : 0;
        if (v && m.userData.mkutu) MINI.hk.union(m.userData.mkutu);
      });
      MINI.yon.copy(kameraYonu());
      miniYer(s);
      miniKamera();
    }
    // F10e düzeltme 1 (kontrol bulgu 4): küçük görünümün altında yeni parçaların yeri: taraf (vurgulu kutunun ortası; robotun sağı
    // +x, önü +z) ve vurgulu kutunun yükseklik aralığı (y, mm, 10'a yuvarlı). Benzer kare çiftleri (34.3 / 34.5, 34.4 / 34.6, 49.3 / 49.4) aynı bakıştan
    // çizildiği için 3B karede ayrılmıyordu; etiket küçük görünüm kutusunun içinde, sahneyi küçültmez (güvenli alan değişmez).
    function miniYer(s) {
      const e = $("mini-yer"); if (!e) return;
      if (s === 0 || MINI.hk.isEmpty()) { e.hidden = true; return; }
      const c = MINI.hk.getCenter(new THREE.Vector3()), t = [];
      if (c.x > 40) t.push("sağ"); else if (c.x < -40) t.push("sol"); else t.push("orta");
      if (c.z > 60) t.push("ön"); else if (c.z < -60) t.push("arka");
      const y0 = Math.round(MINI.hk.min.y / 10) * 10, y1 = Math.round(MINI.hk.max.y / 10) * 10;
      e.textContent = t.join("-") + " · y " + y0 + "–" + y1;
      e.title = "Bu adımın parçaları: robotun " + t.join("-") + " tarafı, yerden yükseklik " + y0 + "–" + y1 + " mm";
      e.hidden = false;
    }
    function miniKamera() {
      if (!MINI.hazir || MINI.kutu.isEmpty()) return;
      const r = miniEl.getBoundingClientRect();
      const asp = r.height > 0 ? r.width / r.height : 0.75;
      MINI.kamera.aspect = asp;
      const merkez = MINI.kutu.getCenter(new THREE.Vector3());
      const yar = MINI.kutu.getSize(new THREE.Vector3()).length() / 2;
      const D = yar / Math.sin(MINI.kamera.fov * Math.PI / 360) / Math.min(1, asp) * 0.92;
      MINI.kamera.position.copy(merkez).addScaledVector(MINI.yon, D);
      MINI.kamera.near = D / 50; MINI.kamera.far = D * 4;
      MINI.kamera.lookAt(merkez);
      MINI.kamera.updateProjectionMatrix(); MINI.kamera.updateMatrixWorld(true);
      // halka: vurgulu parçaların küçük görünümdeki yeri (küçük parçalar da bulunabilsin)
      const hal = $("mini-hal");
      if (!hal) return;
      if (MINI.hk.isEmpty() || su === 0 || r.width < 5) { hal.hidden = true; MINI.noktalar.forEach((m) => { m.visible = false; }); return; }   // alt adım: aynı kural
      let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
      for (let i = 0; i < 8; i++) {
        const b = MINI.hk; _v.set(i & 1 ? b.max.x : b.min.x, i & 2 ? b.max.y : b.min.y, i & 4 ? b.max.z : b.min.z).project(MINI.kamera);
        x0 = Math.min(x0, _v.x); x1 = Math.max(x1, _v.x); y0 = Math.min(y0, _v.y); y1 = Math.max(y1, _v.y);
      }
      const px = (x) => (x + 1) / 2 * r.width, py = (y) => (1 - y) / 2 * r.height;
      // küçük parça (horn, burç) küçük görünümde 6 px'ten küçük kalıyorsa yerinde vurgu renginde bir nokta çizilir
      miniNoktalar(r);
      const w = Math.max(16, (x1 - x0) / 2 * r.width + 8), h = Math.max(16, (y1 - y0) / 2 * r.height + 8);
      const cx = px((x0 + x1) / 2), cy = py((y0 + y1) / 2);
      hal.style.left = Math.round(cx - w / 2) + "px"; hal.style.top = Math.round(cy - h / 2) + "px";
      hal.style.width = Math.round(w) + "px"; hal.style.height = Math.round(h) + "px";
      hal.hidden = false;
    }
    function miniNoktalar(r) {
      const th = Math.tan(MINI.kamera.fov * Math.PI / 360), H = Math.max(1, r.height);
      const yer = [], c = new THREE.Vector3(), s = new THREE.Vector3();
      let n = 0;
      for (const b of MINI.hlist) {
        b.getCenter(c);
        const dd = c.distanceTo(MINI.kamera.position);
        const pxBoy = b.getSize(s).length() / (2 * dd * th) * H;
        if (pxBoy >= 6) continue;
        _v.copy(c).project(MINI.kamera);
        if (yer.some((q) => Math.abs(q[0] - _v.x) * r.width < 8 && Math.abs(q[1] - _v.y) * H < 8)) continue;   // üst üste binen nokta
        yer.push([_v.x, _v.y]);
        let m = MINI.noktalar[n];
        if (!m) { m = new THREE.Mesh(MINI.nokta.geometry, MINI.vurgu); m.renderOrder = 11; MINI.sahne.add(m); MINI.noktalar[n] = m; }
        m.position.copy(c); m.scale.setScalar(3.5 * 2 * dd * th / H); m.visible = true; m.updateMatrixWorld(true);
        n++;
      }
      for (let i = n; i < MINI.noktalar.length; i++) MINI.noktalar[i].visible = false;
    }
    function miniGoster(acik, ilk) {
      miniAcik = acik;
      miniEl.hidden = !miniAcik;
      sahneEl.classList.toggle("mini-acik", miniAcik);
      const d = $("mini-dugme"); if (d) d.classList.toggle("acik", miniAcik);
      if (!ilk && !SAHNE) yaz("mini", miniAcik);
      if (miniAcik) { miniGuncelle(su); }
      ciz();
    }

    // ---------------------------------------------------------------- seçim vurgusu (F10a)
    let secim = null;                                 // { ids, ana, sema, hepsi, satir: { adim, tur, i } }
    const secNesne = [];
    function vurguKaldir() {
      secNesne.forEach((o) => {
        if (o.userData.mat0) o.material = o.userData.mat0;
        if (o.userData.xray) { o.remove(o.userData.xray); o.userData.xray = null; }
      });
      secNesne.length = 0;
    }
    function vurguUygula(sessiz) {
      vurguKaldir();
      document.querySelectorAll("#panel .secili").forEach((e) => e.classList.remove("secili"));
      if (secim) {
        const isle = (o, ana) => {
          if (!o || !o.visible) return;
          o.material = ana ? VURGU.ana : VURGU.kopya;
          const x = new THREE.Mesh(o.geometry, VURGU.xray);
          x.renderOrder = 10; x.raycast = function () {};
          o.add(x); o.userData.xray = x;
          secNesne.push(o);
        };
        secim.ids.forEach((id) => isle(PAR[id] && PAR[id].obj, secim.hepsi || id === secim.ana));
        (secim.sema || []).forEach((i) => isle(SEMA_OBJ[i], true));
        if (secim.satir && secim.satir.adim === su) {
          const e = document.querySelector("#panel [data-satir='" + secim.satir.tur + ":" + secim.satir.i + "']");
          if (e) e.classList.add("secili");
        }
        (secim.ids.length === 1 ? secim.ids : []).forEach((id) => {
          const e = document.querySelector("#kablo [data-kid='" + id + "']"); if (e) e.classList.add("secili");
        });
        (secim.sema || []).forEach((i) => { const e = document.querySelector("#kablo [data-sema='" + i + "']"); if (e) e.classList.add("secili"); });
      }
      if (!sessiz) { lejant(sonSay, su); ciz(); }
    }
    function secimYap(s) { secim = s; vurguUygula(); }
    function secimTemizle() { if (!secim) { $("etiket").hidden = true; return; } secim = null; vurguUygula(); $("etiket").hidden = true; }
    function etiketYaz(h) { const et = $("etiket"); et.innerHTML = h; et.hidden = false; }

    function satirBul(id) {                           // parçanın panel satırı: kendi adımında (önceki adımdan seçilse de)
      const p = PAR[id].v;
      const st = ADIM[p.a]; if (!st) return null;
      const ara = [["p", st.parcalar], ["b", st.baglantilar]];
      for (const [tur, liste] of ara) {
        const i = liste.findIndex((x) => x.ids && x.ids.indexOf(id) >= 0);
        if (i >= 0) return { adim: p.a, tur: tur, i: i, ids: liste[i].ids, ad: tur === "p" ? liste[i].ad : liste[i].kod, adet: liste[i].adet };
      }
      return null;
    }
    const ray = new THREE.Raycaster(); let basla = null;
    function isabet(cx, cy) {                         // ekran noktasındaki parça / şema; saydam kipte önce bu adımın parçaları
      const r = tuval.getBoundingClientRect();
      ray.setFromCamera(new THREE.Vector2(((cx - r.left) / r.width) * 2 - 1, -((cy - r.top) / r.height) * 2 + 1), kamera);
      const h = ray.intersectObjects(sahne.children, true).filter((x) => x.object.visible && (x.object.userData.id || x.object.userData.sema != null));
      if (!h.length) return null;
      let x = h[0];
      if (onceki === "saydam") { const y = h.find((z) => z.object.userData.d !== "onceki"); if (y) x = y; }
      return x.object.userData.id ? { id: x.object.userData.id } : { sema: x.object.userData.sema };
    }
    function parcaSec(id) {
      const st = satirBul(id);
      const ids = st ? st.ids.filter((i) => PAR[i] && PAR[i].obj && PAR[i].obj.visible) : [id];
      secimYap({ ids: ids.indexOf(id) >= 0 ? ids : [id], ana: id, sema: [], satir: st ? { adim: st.adim, tur: st.tur, i: st.i } : null });
      const p = PAR[id].v;
      const kopya = secim.ids.length - 1;
      etiketYaz("<b>" + esc(p.ad) + "</b><br><span class='not'>" + esc(p.kod) + " · " + esc(MODUL_AD[p.modul] || p.modul) + " · adım " +
        p.a + " (" + esc(ADIM[p.a].kod) + ")" + (kopya > 0 ? "<br>Aynı kalemden " + kopya + " kopya daha açık tonla vurgulu" : "") +
        "</span>");
    }
    function semaSec(i) {
      secimYap({ ids: [], sema: [i], hepsi: true, satir: null });
      etiketYaz("<b>" + esc(SEMA[i].ad) + "</b><br><span class='not'>Kablo şeması · adım " + SEMA[i].a + " (" + esc(ADIM[SEMA[i].a].kod) + ")" +
        (SEMA[i].boy_mm ? " · ~" + Math.round(SEMA[i].boy_mm) + " mm" : "") + "</span>");
    }
    tuval.addEventListener("pointerdown", (e) => { basla = [e.clientX, e.clientY]; });
    tuval.addEventListener("pointerup", (e) => {
      if (!basla || Math.hypot(e.clientX - basla[0], e.clientY - basla[1]) > 5) return;
      const h = isabet(e.clientX, e.clientY);
      if (!h) { secimTemizle(); return; }
      if (h.sema != null) semaSec(h.sema); else parcaSec(h.id);
    });

    // ---------------------------------------------------------------- panel
    function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]); }
    function md(s) { return esc(s).replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>").replace(/`([^`]+)`/g, "<code>$1</code>"); }

    // F10d: panel tablosu = sıralı takma sırası. Adımda "sira" varsa parçalar ve bağlantı elemanları tek tabloda, grup başlıklarıyla,
    // st.sira sırasıyla (data-satir korunur); alt adımda yalnız o grubun satırları. sira yoksa parçalar sonra bağlantılar (siraKur ile aynı).
    function satirHtml(st, k) {
      const [t, i] = k.split(":"); const x = (t === "p" ? st.parcalar : st.baglantilar)[+i]; if (!x) return "";
      if (t === "p") return "<tr data-satir='" + k + "'><td><i class='sw' style='background:" + satirRengi(x, false) + "'></i>" + esc(x.ad) +
        "<div class='t'>" + esc(TUR_AD[x.tur] || x.tur) + (x.malzeme && x.malzeme !== "-" ? " · " + esc(x.malzeme) : "") + "</div></td><td class='n'>×" + x.adet + "</td></tr>";
      return "<tr data-satir='" + k + "'><td><i class='sw' style='background:" + satirRengi(x, true) + "'></i>" + esc(x.kod) + "<div class='t'>" +
        (x.onceden ? "Bağlantı elemanı · baskıdan sonra takılı (hazırlık), parçasıyla gelir; burada yalnız sayılır" : "Bağlantı elemanı") +
        "</div></td><td class='n'>×" + x.adet + "</td></tr>";
    }
    function altListe(s) {                           // alt adım bağlantıları (genel bakış dahil)
      const st = ADIM[s]; if (!st.alt) return "";
      const li = ["<li class='" + (ss === 0 ? "su" : "") + "'><a href='#" + s + "' data-git='" + s + "'>" + s + " · genel bakış</a></li>"];
      st.sira_grup.forEach((g, n) => {
        li.push("<li class='" + (ss === n + 1 ? "su" : "") + "'><a href='#" + s + "." + (n + 1) + "' data-git='" + s + "." + (n + 1) + "'>" + s + "." + (n + 1) +
          " · " + esc(g.ad) + "</a></li>");
      });
      return "<div class='altlar'><b>Alt adımlar</b> <span class='not'>(← / → ile sırayla)</span><ol>" + li.join("") + "</ol></div>";
    }
    function panel(s) {
      const st = ADIM[s];
      const ag = altGrup(s);
      const roz = ["<span class='rozet kod'>" + esc(st.kod) + (ag ? "." + ss : "") + "</span>", "<span class='rozet'>" + esc(st.faz) + "</span>"];
      if (st.tezgah || (ag && ag.tezgah)) roz.push("<span class='rozet tezgah'>Tezgâh: masada yap</span>");
      if (st.kablolama) roz.push("<span class='rozet kapi'>Kablolama kapısı: kabuktan önce dur</span>");
      if (st.no && st.no !== "0") roz.push("<span class='rozet'>M6 no " + esc(st.no) + "</span>");
      if (st.alt) roz.push("<span class='rozet'>" + (ag ? "alt adım " + ss + " / " + st.alt : st.alt + " alt adım") + "</span>");
      $("rozetler").innerHTML = roz.join("");
      $("adim-baslik").textContent = ag ? s + "." + ss + " · " + ag.ad : s + ". " + st.baslik;
      $("adim-is").innerHTML = ag ? "<span class='not'>Adım " + s + ": " + esc(st.baslik) + "</span><br>" + md(ag.is_ || "") : md(st.is_);
      $("altlar").innerHTML = altListe(s);
      // notlar (rehber_metin.py not_: doğrulanmamış bilgiler, uyarılar)
      const nt = st.not_ || [];
      $("notlar").innerHTML = nt.length ? "<div class='notlar'><b>Notlar</b><ul>" + nt.map((t) => "<li>" + md(t) + "</li>").join("") +
        "</ul></div>" : "";
      // KPI
      const satirlar = ag ? ag.satir : (st.sira || null);
      const say = (t) => (satirlar ? satirlar.filter((k) => k[0] === t).map((k) => (t === "p" ? st.parcalar : st.baglantilar)[+k.slice(2)])
        : (t === "p" ? st.parcalar : st.baglantilar)).reduce((a, b) => a + (b ? b.adet : 0), 0);
      const nb = say("b"), np = say("p");
      $("kpi").innerHTML = [
        ["~" + st.sure_dk + " dk", "süre" + (st.sure_tahmini ? " (tahmini)" : "") + (ag ? ", bütün adım" : "")],
        [st.alet ? md(st.alet) : "—", "alet"],
        [np, "parça"], [nb, "bağlantı elemanı"]
      ].map((x) => "<div class='kpi'><b>" + x[0] + "</b><span>" + x[1] + "</span></div>").join("");
      // parçalar (F10a: satıra tıklayınca modelde vurgu; data-satir = tür:sıra)
      const bag = st.baglanir != null ? "<p class='not'>Bu alt montaj " + st.baglanir + ". adımda (" + esc(ADIM[st.baglanir].kod) +
        ") robota bağlanır.</p>" : "";
      const altlar = [];
      if (!st.tezgah && s > 0) ADIM.forEach((a) => { if (a.baglanir === s) altlar.push(a); });
      const altNot = altlar.length ? "<p class='not'>Robota gelen alt montaj: " + altlar.map((a) => a.i + ". " + esc(a.kod)).join(", ") + "</p>" : "";
      const bagNot = ag && ag.bag ? "<p class='not'>Bu alt adımda masada hazırlanan birim robota bağlanır (" +
        esc(st.sira_grup.filter((g) => g.tezgah === ag.bag).map((g) => g.ad).join(", ")) + ").</p>" : "";
      if (satirlar) {                                 // F10d: tek tablo, takma sırasıyla
        const gr = [];
        if (ag) gr.push(ag.satir.map((k) => satirHtml(st, k)).join(""));
        else st.sira_grup.forEach((g, n) => {
          if (!g.satir.length) return;
          gr.push("<tr class='grup'><td colspan='2'>" + (st.alt ? s + "." + (n + 1) + " · " : (n + 1) + ". ") + esc(g.ad) + "</td></tr>" +
            g.satir.map((k) => satirHtml(st, k)).join(""));
        });
        $("parcalar").innerHTML = (gr.join("") ? "<table class='secilir'>" + gr.join("") + "</table>" :
          "<p class='bos'>Bu alt adımda yeni parça yok.</p>") + bagNot + bag + altNot;
        $("baglantilar").innerHTML = "<p class='not'>Bağlantı elemanları takma sırasıyla yukarıdaki tabloda.</p>" +
          (st.baglanti_md ? "<p class='not'>Bağlantı: " + md(st.baglanti_md) + "</p>" : "");
      } else {
        $("parcalar").innerHTML = (st.parcalar.length ? "<table class='secilir'>" + st.parcalar.map((x, i) => satirHtml(st, "p:" + i)).join("") +
          "</table>" : "<p class='bos'>" + (s === 0 ? "Hedef: bitmiş robot (" + VERI.parcalar.length + " parça)." : "Bu adımda yeni parça yok.") + "</p>") + bag + altNot;
        $("baglantilar").innerHTML = (st.baglantilar.length ? "<table class='secilir'>" + st.baglantilar.map((x, i) => satirHtml(st, "b:" + i)).join("") +
          "</table>" : "<p class='bos'>Yok.</p>") + (st.baglanti_md ? "<p class='not'>Bağlantı: " + md(st.baglanti_md) + "</p>" : "");
      }
      // kontrol listesi
      const kk = (oku().kontrol || {})[st.kod] || [];
      $("kontrol").innerHTML = st.kontrol.length ? st.kontrol.map((t, i) =>
        "<li class='" + (kk[i] ? "tamam" : "") + "'><input type='checkbox' data-i='" + i + "'" + (kk[i] ? " checked" : "") + "><span>" + md(t) + "</span></li>").join("")
        : "<li class='bos'>Bu adım için kontrol listesi henüz yazılmadı (erişim notuna bak).</li>";
      // kablo kancası (kablo parçası ve şema satırına tıklayınca modelde vurgu)
      const kab = st.kablo.map((t) => "<li>" + md(t) + "</li>");
      VERI.parcalar.forEach((p) => {
        if (p.renk && p.a === s) kab.push("<li class='secilir' data-kid='" + esc(p.id) + "'><i class='sw' style='background:" + p.renk + "'></i>" + esc(p.ad) + "</li>");
      });
      SEMA.forEach((x, i) => {
        if (x.a === s) kab.push("<li class='secilir' data-sema='" + i + "'><i class='sw' style='background:" + x.renk + "'></i>" + esc(x.ad) + " <span class='t'>(şema)</span></li>");
      });
      $("kablo").innerHTML = kab.length ? kab.join("") : "<li class='bos'>Bu adımda özel kablo işi yok.</li>";
      $("erisim").innerHTML = st.erisim ? md(st.erisim) : "—";
      $("panel").scrollTop = 0;
    }
    $("kontrol").addEventListener("change", (e) => {
      const i = +e.target.dataset.i; if (isNaN(i)) return;
      const d = oku().kontrol || {}; const kod = ADIM[su].kod;
      d[kod] = d[kod] || []; d[kod][i] = e.target.checked; yaz("kontrol", d);
      e.target.parentElement.classList.toggle("tamam", e.target.checked);
    });
    $("panel").addEventListener("click", (e) => {
      if (!yuklu) return;
      const ga = e.target.closest("[data-git]");
      if (ga) { e.preventDefault(); const q = adresOku(ga.dataset.git); if (q) git(q[0], true, q[1]); return; }
      const tr = e.target.closest("[data-satir]");
      if (tr) {
        const [tur, i] = tr.dataset.satir.split(":"); const st = ADIM[su];
        const x = (tur === "p" ? st.parcalar : st.baglantilar)[+i]; if (!x) return;
        if (secim && secim.satir && secim.satir.adim === su && secim.satir.tur === tur && secim.satir.i === +i && !secim.ana) { secimTemizle(); return; }
        secimYap({ ids: x.ids.slice(), hepsi: true, sema: [], satir: { adim: su, tur: tur, i: +i } });
        const gor = secNesne.length;
        etiketYaz("<b>" + esc(tur === "p" ? x.ad : x.kod) + "</b> ×" + x.adet + "<br><span class='not'>" + (gor ? gor + " parça vurgulu" :
          "Bu görünümde gizli") + " · Esc: temizle</span>");
        return;
      }
      const li = e.target.closest("#kablo [data-kid], #kablo [data-sema]");
      if (li) {
        if (li.dataset.sema != null) semaSec(+li.dataset.sema);
        else if (PAR[li.dataset.kid]) parcaSec(li.dataset.kid);
      }
    });

    function lejant(say, s) {
      const k = Object.keys(say);
      const h = [];
      k.forEach((c) => {
        if (c === "gercek") {                         // F10e: gerçek renk kipi: bu konumun yeni parçalarının renklerinden en çok 4'ü
          const rr = [];
          sonUc.forEach((x) => { const p = x.k.v; if (!p.renk) { const r = parcaRengi(p); if (rr.indexOf(r) < 0) rr.push(r); } });
          const g = rr.slice(0, 4);
          h.push("<span><i style='background:" + (g.length > 1 ? "linear-gradient(90deg," + g.join(",") + ")" : (g[0] || "#999")) +
            "'></i>Bu adımın parçaları (gerçek renk)</span>");
        } else h.push("<span><i style='background:" + SINIF[c][0] + "'></i>" + SINIF[c][1] + "</span>");
      });
      if (sonEv.length) h.push("<span><i style='background:" + EV_RENK + "'></i>Bağlandığı yer</span>");
      if (s > 0) h.push("<span><i style='background:" + SINIF.onceki[0] + "'></i>" + SINIF.onceki[1] + "</span>");
      if (ISARET.acik && ISARET.liste.length) h.push("<span><i class='hl'></i>Bağlantı elemanı yeri (×n: küme)</span>");
      if (secim && secNesne.length) h.push("<span><i style='background:" + SINIF.secili[0] + "'></i>" + SINIF.secili[1] + "</span>");
      $("lejant").innerHTML = h.join("");
      $("lejant").hidden = !h.length;
    }
    function renkKipAyarla(k, kaydet) {
      renkKip = k;
      if (kaydet && !SAHNE) yaz("renk", k);
      const d = $("renk-dugme");
      if (d) { d.classList.toggle("acik", k === "gercek"); d.innerHTML = "◑ <span class='yazi'>" + (k === "gercek" ? "gerçek renk" : "sınıf rengi") + "</span>"; }
      if (yuklu) { panel(su); uygula(su, false); }
    }

    // ---------------------------------------------------------------- öncekiler: opak / saydam / gizli
    function oncekiAyarla(d, kaydet) {
      onceki = d;
      document.querySelectorAll("input[name='onceki']").forEach((r) => { r.checked = r.value === d; });
      if (kaydet) yaz("onceki", d);
      if (yuklu) uygula(su, false);
    }
    oncekiAyarla(onceki, false);
    document.querySelectorAll("input[name='onceki']").forEach((r) => r.addEventListener("change", (e) => {
      if (e.target.checked) oncekiAyarla(e.target.value, true);
      e.target.blur();
    }));

    // ---------------------------------------------------------------- gezinme ve kısayollar
    $("secim").innerHTML = KONUM.map(([s, j]) => {
      const a = ADIM[s];
      return j ? "<option value='" + s + "." + j + "'>  " + s + "." + j + " · " + esc(a.sira_grup[j - 1].ad) + "</option>"
        : "<option value='" + s + "'>" + s + " · " + esc(a.kod) + " · " + esc(a.baslik) + "</option>";
    }).join("");
    $("secim").addEventListener("change", (e) => { const q = adresOku(e.target.value); if (q) git(q[0], true, q[1]); });
    function yuru(dx) {                               // F10d: ←/→ alt adımlar dahil sıradaki / önceki konum
      const i = konumNo(su, ss) + dx;
      if (i < 0 || i >= KONUM.length) return;
      git(KONUM[i][0], true, KONUM[i][1]);
    }
    const dugme = (id, f) => { const b = $(id); if (b) b.addEventListener("click", () => { f(); b.blur(); }); };
    dugme("geri", () => yuru(-1));
    dugme("ileri", () => yuru(1));
    dugme("tekrar", () => { sira = null; secimTemizle(); uygula(su, true); siraDugme(); });
    dugme("sifirla", () => kameraYerlestir(uygula(su, false)));
    dugme("patlat", patlat);
    dugme("tak", tak);
    dugme("mini-dugme", () => miniGoster(!miniAcik));
    dugme("mini-kapat", () => miniGoster(false));
    dugme("renk-dugme", () => renkKipAyarla(renkKip === "gercek" ? "sinif" : "gercek", true));      // F10e
    dugme("isaret-dugme", () => isaretGoster(!ISARET.acik));
    renkKipAyarla(renkKip, false);
    { const d = $("isaret-dugme"); if (d) d.classList.toggle("acik", ISARET.acik); }
    document.addEventListener("keydown", (e) => {
      if (e.target.tagName === "SELECT" || e.target.tagName === "INPUT" || e.ctrlKey || e.metaKey || e.altKey) return;
      const k = e.key;
      if (k === "ArrowRight" || k === "PageDown") { yuru(1); e.preventDefault(); }
      else if (k === "ArrowLeft" || k === "PageUp") { yuru(-1); e.preventDefault(); }
      else if (k === "r" || k === "R") { sira = null; secimTemizle(); uygula(su, true); siraDugme(); }
      else if (k === "v" || k === "V") kameraYerlestir(uygula(su, false));
      else if (k === "t" || k === "T") temaDegis();
      else if (k === "o" || k === "O" || k === "ö" || k === "Ö") oncekiAyarla(ONCEKI[(ONCEKI.indexOf(onceki) + 1) % 3], true);
      else if (k === "p" || k === "P") patlat();
      else if (k === " " || k === "Spacebar") { if (e.shiftKey) geriAl(); else tak(); e.preventDefault(); }
      else if (k === "m" || k === "M") miniGoster(!miniAcik);
      else if (k === "c" || k === "C") renkKipAyarla(renkKip === "gercek" ? "sinif" : "gercek", true);   // F10e: renk kipi
      else if (k === "i" || k === "I" || k === "ı" || k === "İ") isaretGoster(!ISARET.acik);            // F10e: işaretler
      else if (k === "Escape") secimTemizle();
    });
    let dok = null;                                   // panel / üst şeritte yatay kaydırma = adım değiştir
    document.addEventListener("touchstart", (e) => { if (e.target === tuval || e.touches.length !== 1) { dok = null; return; } dok = [e.touches[0].clientX, e.touches[0].clientY]; }, { passive: true });
    document.addEventListener("touchend", (e) => {
      if (!dok) return; const t = e.changedTouches[0]; const dx = t.clientX - dok[0], dy = t.clientY - dok[1]; dok = null;
      if (Math.abs(dx) > 70 && Math.abs(dy) < 45) yuru(dx < 0 ? 1 : -1);
    }, { passive: true });

    function temaDegis() {
      const sira_ = [undefined, "dark", "light"];
      const simdi = document.documentElement.dataset.theme;
      const yeni = sira_[(sira_.indexOf(simdi) + 1) % 3];
      if (yeni) document.documentElement.dataset.theme = yeni; else delete document.documentElement.dataset.theme;
      yaz("tema", yeni || null);
      sahneRengi(); uygula(su, false);
    }
    dugme("tema", temaDegis);
    matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { sahneRengi(); uygula(su, false); });
    new ResizeObserver(boyut).observe(tuval.parentElement);
    boyut();

    // ---------------------------------------------------------------- sınama kancası (planlama/d158/F10a-dogrula.py okur; davranışı değiştirmez)
    window.RehberTest = {
      THREE: THREE, kamera: kamera, tuval: tuval, PAR: PAR, SEMA_OBJ: SEMA_OBJ,
      hazir: () => yuklu, su: () => su, anim: () => !!anim, onceki: () => onceki, miniAcik: () => miniAcik,
      sira: () => (sira ? { n: sira.n, toplam: sira.satir.length } : null),
      kadraj: () => (sonKutu ? sonKutu.kadraj : null),
      vurgu() {                                       // sahnede vurgu malzemesi taşıyan görünür mesh sayısı (ana / kopya)
        let ana = 0, kopya = 0; const ids = [];
        sahne.traverse((o) => {
          if (!o.isMesh || !o.visible) return;
          if (o.material === VURGU.ana) ana++; else if (o.material === VURGU.kopya) kopya++; else return;
          ids.push(o.userData.id || ("sema" + o.userData.sema));
        });
        return { sayi: ana + kopya, ana: ana, kopya: kopya, ids: ids.sort(), satir: secim && secim.satir };
      },
      tikNoktasi(hedef) {                             // hedef parça / şemanın, tıklanınca onu veren bir ekran noktası (istemci px)
        const o = typeof hedef === "string" ? (PAR[hedef] && PAR[hedef].obj) : SEMA_OBJ[hedef.sema];
        if (!o || !o.visible) return null;
        const c = tuval.getBoundingClientRect(), pos = o.geometry.attributes.position, n = Math.floor(pos.count / 3);
        const adim = Math.max(1, Math.floor(n / 600)), v = new THREE.Vector3();
        for (let t = 0; t < n; t += adim) {
          v.set(0, 0, 0);
          for (let j = 0; j < 3; j++) v.add(new THREE.Vector3().fromBufferAttribute(pos, t * 3 + j));
          v.multiplyScalar(1 / 3).applyMatrix4(o.matrixWorld).project(kamera);
          if (Math.abs(v.x) > 0.98 || Math.abs(v.y) > 0.98 || v.z > 1) continue;
          const x = c.left + (v.x + 1) / 2 * c.width, y = c.top + (1 - v.y) / 2 * c.height;
          if (document.elementFromPoint(x, y) !== tuval) continue;
          const h = isabet(x, y);
          if (h && ((typeof hedef === "string" && h.id === hedef) || (typeof hedef !== "string" && h.sema === hedef.sema))) return { x: x, y: y };
        }
        return null;
      },
      bosNokta() {
        const c = tuval.getBoundingClientRect();
        for (let j = 1; j < 24; j++) for (let i = 1; i < 32; i++) {
          const x = c.left + c.width * i / 32, y = c.top + c.height * j / 24;
          if (document.elementFromPoint(x, y) !== tuval) continue;
          if (!isabet(x, y)) return { x: x, y: y };
        }
        return null;
      },
      miniOlc() {                                     // küçük görünüm: çizilen piksel ve vurgu rengindeki piksel sayısı
        if (!miniAcik || miniEl.hidden) return { acik: false };
        render();
        const gl = renderer.getContext(), pr = renderer.getPixelRatio(), r = miniDikdortgen();
        const x = Math.round(r.x * pr), y = Math.round(r.y * pr), w = Math.round(r.w * pr), h = Math.round(r.h * pr);
        const buf = new Uint8Array(w * h * 4);
        gl.readPixels(x, y, w, h, gl.RGBA, gl.UNSIGNED_BYTE, buf);
        const bg = MINI.sahne.background; const br = bg.r * 255, bgg = bg.g * 255, bb = bg.b * 255;
        let dolu = 0, vurgu = 0;
        for (let i = 0; i < buf.length; i += 4) {
          const R = buf[i], G = buf[i + 1], B = buf[i + 2];
          if (Math.abs(R - br) + Math.abs(G - bgg) + Math.abs(B - bb) > 24) dolu++;
          if (R > 120 && R - B > 70 && G > 0.4 * R && G < 0.9 * R) vurgu++;
        }
        const m = miniEl.getBoundingClientRect();
        return { acik: true, w: w, h: h, dolu: dolu, vurgu: vurgu, kutu: { sol: m.left, ust: m.top, sag: m.right, alt: m.bottom } };
      },
      patlat: patlat, tak: tak, geriAl: geriAl, oncekiAyarla: (d) => oncekiAyarla(d, false), miniGoster: (a) => miniGoster(a, true),
      // F10d: alt adım gezinmesi ve ölçümler (planlama/d158/F10d-dogrula.py, F10a-dogrula.py)
      konum: () => [su, ss], konumlar: () => KONUM.slice(), git: (s, j) => git(s, false, j || 0),
      panelSira: () => Array.prototype.map.call(document.querySelectorAll("#parcalar [data-satir], #baglantilar [data-satir]"), (e) => e.dataset.satir),
      takmaSira: () => { const r = siraKur(); return r.filter((x) => x.tur).map((x) => x.tur + ":" + x.i); },
      // yeni parçaların (simdi + alt) ve yeni şemaların kamera görüntüsündeki piksel sayısı (kimlik tamponu, güvenli alan).
      // F10d düzeltme 1 (kontrol B-1, B-7, B-8): iki geçiş. (1) opak geçiş: saydam çizilen her şey (opaklık < 0,5; eski ya da bu alt
      // adımın saydam listesindeki yeni parça) arkasını örtmez, yok sayılır; opak yeni parçalar burada sayılır. (2) saydam çizilen her yeni
      // parça tek başına opak parçalarla birlikte çizilir, opak örtücülerin önündeki pikselleriyle sayılır. yalnız: parça tek başına çizilince (engelsiz izdüşüm) piksel.
      // Isıl gömme dahil her yeni parça ölçülür. sema: görünen şemalar ve durumları (masa karesinde yabancı kablo denetimi).
      gorunurluk(op) {
        op = op || {};
        const W = renderer.domElement.width, H = renderer.domElement.height, pr = renderer.getPixelRatio();
        const rt = new THREE.WebGLRenderTarget(W, H);
        const kayit = [], cizgi = [];
        sahne.traverse((o) => { if (o.isMesh) kayit.push([o, o.material, o.visible]); });
        // F10e: kenar çizgileri kimlik tamponuna girmesin (renkleri kimlik kodu gibi okunurdu); ölçülen şey F10d'deki gibi mesh pikseli
        sahne.traverse((o) => { if (o.userData && o.userData.kenarMi) { cizgi.push([o, o.visible]); o.visible = false; } });
        const bg = sahne.background; sahne.background = new THREE.Color(0, 0, 0); const zg = zemin.visible; zemin.visible = false;
        const anahtar = (o) => o.userData.id || (o.userData.sema != null ? "sema" + o.userData.sema : null);
        const yeni = {}, sdy = new Set(), semaGor = [];
        const kod = {}, kodOf = new Map();
        let n = 1;
        kayit.forEach(([o, m, v]) => {
          const k = anahtar(o);
          if (!v || !k) return;
          const c = n++; kod[c] = k; kodOf.set(o, c);
          if (o.userData.d === "simdi" || o.userData.d === "alt") { yeni[k] = 0; if (m && m.transparent && m.opacity < 0.5) sdy.add(k); }
          if (o.userData.sema != null) semaGor.push({ i: o.userData.sema, d: o.userData.d });
          o.material = new THREE.MeshBasicMaterial({ side: THREE.DoubleSide,
            color: new THREE.Color().setRGB((c & 255) / 255, ((c >> 8) & 255) / 255, ((c >> 16) & 255) / 255, THREE.LinearSRGBColorSpace) });
        });
        const al = guvenliAlanlar()[0] || { x0: -1, x1: 1, y0: -1, y1: 1 };
        const x0 = Math.floor((al.x0 + 1) / 2 * W), x1 = Math.ceil((al.x1 + 1) / 2 * W), y0 = Math.floor((al.y0 + 1) / 2 * H), y1 = Math.ceil((al.y1 + 1) / 2 * H);
        const buf = new Uint8Array(W * H * 4);
        const opak = (o, m) => !(m && m.transparent && m.opacity < 0.5);
        function gec(gor) {                           // gor(o, asıl malzeme) -> çizilsin mi; döner: anahtar -> piksel
          kayit.forEach(([o, m, v]) => { o.visible = !!(v && kodOf.has(o) && gor(o, m)); });
          renderer.setRenderTarget(rt); renderer.setViewport(0, 0, W, H); renderer.render(sahne, kamera); renderer.setRenderTarget(null);
          renderer.readRenderTargetPixels(rt, 0, 0, W, H, buf);
          const say = {};
          for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) {
            const i = (y * W + x) * 4, c = buf[i] | (buf[i + 1] << 8) | (buf[i + 2] << 16);
            const k = kod[c]; if (k) say[k] = (say[k] || 0) + 1;
          }
          return say;
        }
        const A = gec(opak);
        // saydam yeni parça tek tek: opak parçalarla birlikte yalnız o çizilir (başka saydam parça da arkasını örtmez)
        for (const k in yeni) yeni[k] = (sdy.has(k) ? gec((o, m) => opak(o, m) || anahtar(o) === k)[k] : A[k]) || 0;
        const yalniz = {};
        if (op.yalniz !== false) for (const k in yeni) { const r = gec((o) => anahtar(o) === k); yalniz[k] = r[k] || 0; }
        kayit.forEach(([o, m, v]) => { if (o.material !== m) o.material.dispose(); o.material = m; o.visible = v; });
        cizgi.forEach(([o, v]) => { o.visible = v; });
        sahne.background = bg; zemin.visible = zg; rt.dispose();
        const karede = {};                            // kutu köşeleri kamerada güvenli alanın içinde mi
        for (const k in yeni) {
          const o = k.startsWith("sema") ? SEMA_OBJ[+k.slice(4)] : PAR[k].obj, pts = []; koseler(o, null, pts);
          karede[k] = pts.every((v) => { v.project(kamera); return v.x >= al.x0 - 0.02 && v.x <= al.x1 + 0.02 && v.y >= al.y0 - 0.02 && v.y <= al.y1 + 0.02 && v.z < 1; });
        }
        ciz();
        return { piksel: yeni, yalniz: yalniz, saydam: Array.from(sdy), sema: semaGor, karede: karede, oran: pr, W: W, H: H };
      },
      // F10e: okurun gördüğü piksel. Kare gerçek malzeme, saydamlık, kenar çizgisi ve zeminle, sayfanın kendi tuvaline (ekrandaki çizimle
      // aynı yol: sRGB çıktı, tuvalin kenar yumuşatması) çizilip okunur; her yeni parça (simdi + alt) tek tek gizlenip yeniden çizilir,
      // güvenli alanda rengi değişen piksel (|ΔR| + |ΔG| + |ΔB| > esik) sayılır. Saydam katmanın arkasındaki parça, katmanın geçirdiği
      // kadar fark verir (örtücü sayılmaz ama soluklaştırır).
      // F10e düzeltme 1 (kontrol bulgu 2): önceki sürüm sahne dışı bir render target'a çiziyordu. three r160 XR olmayan render target'a
      // çıktıyı doğrusal (LinearSRGB) yazar, hedefin colorSpace seçeneği çıktıyı değiştirmez; farklar ekrandakinden büyük çıkıyordu
      // (31.3 p0762: render target 40 px, ekran 0 px). Artık ölçüm ekrana giden çizimin kendisi.
      gorunurlukFark(op) {
        op = op || {};
        const esik = op.esik || 24;
        const W = renderer.domElement.width, H = renderer.domElement.height;
        const al = guvenliAlanlar()[0] || { x0: -1, x1: 1, y0: -1, y1: 1 };
        const x0 = Math.floor((al.x0 + 1) / 2 * W), x1 = Math.ceil((al.x1 + 1) / 2 * W), y0 = Math.floor((al.y0 + 1) / 2 * H), y1 = Math.ceil((al.y1 + 1) / 2 * H);
        const gl = renderer.getContext();
        const ciz1 = (buf) => { renderer.setRenderTarget(null); renderer.setScissorTest(false); renderer.setViewport(0, 0, _boy.x, _boy.y);
          renderer.render(sahne, kamera); gl.readPixels(0, 0, W, H, gl.RGBA, gl.UNSIGNED_BYTE, buf); };
        renderer.getSize(_boy);
        const a = new Uint8Array(W * H * 4), b = new Uint8Array(W * H * 4);
        ciz1(a);
        const hedef = op.ids || Object.keys(PAR).filter((id) => PAR[id].obj && PAR[id].obj.visible && (PAR[id].obj.userData.d === "simdi" || PAR[id].obj.userData.d === "alt"));
        const out = {};
        hedef.forEach((id) => {
          const o = PAR[id] && PAR[id].obj; if (!o || !o.visible) { out[id] = 0; return; }
          o.visible = false; ciz1(b); o.visible = true;
          let n = 0;
          for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) {
            const i = (y * W + x) * 4;
            if (Math.abs(a[i] - b[i]) + Math.abs(a[i + 1] - b[i + 1]) + Math.abs(a[i + 2] - b[i + 2]) > esik) n++;
          }
          out[id] = n;
        });
        render();
        return { piksel: out, esik: esik, W: W, H: H, yol: "tuval" };
      },
      // F10e: görünen parçaların malzeme rengi (sRGB hex), durumu, opaklığı, kenar çizgisi ve ev işareti; zemin rengi; renk kipi
      renkler() {
        const out = {};
        for (const id in PAR) {
          const o = PAR[id].obj; if (!o || !o.visible) continue;
          const m = o.userData.mat0 || o.material, e = o.userData.kenar;
          out[id] = { d: o.userData.d, renk: "#" + m.color.getHexString(), opak: m.transparent ? m.opacity : 1, ev: !!o.userData.ev,
            kenar: e && e.visible ? "#" + e.material.color.getHexString() : null };
        }
        return { kip: renkKip, tema: tema(), zemin: zeminHex, ev_renk: EV_RENK, kenar_esik: KENAR_ESIK, parca: out, ev: sonEv.slice() };
      },
      renkKip: (k) => { if (k) renkKipAyarla(k, false); return renkKip; },
      isaretler() {                                   // F10e: işaret kümeleri (ekran px, tuvale göre) ve kapsadıkları bağlantı elemanları
        render();
        const c = tuval.getBoundingClientRect();
        return { acik: ISARET.acik, liste: ISARET.liste.map((m) => m.id), kume: ISARET.kume.map((k) => ({ x: k.x, y: k.y, n: k.ids.length, ids: k.ids.slice(),
          secili: !!(secim && k.ids.some((i) => secim.ids.indexOf(i) >= 0)) })), tuval: { w: c.width, h: c.height }, alan: guvenliAlanlar()[0] || null,
          dom: isaretEl ? isaretEl.querySelectorAll("g.isr").length : 0, dom_secili: isaretEl ? isaretEl.querySelectorAll("g.isr.secili").length : 0 };
      },
      isaretGoster: (a) => isaretGoster(a),
      kareBaslik: () => { const e = $("kare-baslik"); return e && !e.hidden ? e.textContent : null; }
    };
  };

  // tema kaydı: sayfa açılır açılmaz uygula
  const t = oku().tema;
  if (t === "dark" || t === "light") document.documentElement.dataset.theme = t;
  if (new URLSearchParams(location.search).get("tema")) document.documentElement.dataset.theme = new URLSearchParams(location.search).get("tema");
})();
