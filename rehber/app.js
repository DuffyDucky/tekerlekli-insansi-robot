/* Lale 3B montaj rehberi. Veri: veri/rehber-veri.js (window.REHBER_VERI), mesh: veri/robot-glb.js (window.REHBER_GLB, base64 GLB).
   İkisi de tasarim/freecad/rehber/rehber_veri.py ile üretilir; elle düzenleme. Klasik betik (file:// altında da çalışsın diye);
   three.js 0.160 index.html'de vendor/three-0.160.0-paket.min.js'ten (klasik betik, internetsiz) RehberBaslat'a verilir.
   F10a (P10.1): seçim vurgusu (tıklanan parça + aynı kalemin kopyaları, panel satırından da), öncekiler opak / saydam / gizli,
   patlat + panel sırasıyla satır satır tak, "robotun neresi" küçük görünümü, yeni parçalara sıkı kadraj. */
(function () {
  "use strict";
  const VERI = window.REHBER_VERI;
  const ADIM = VERI ? VERI.adimlar : [];
  const N = ADIM.length;
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
    function sahneRengi() {
      const cs = getComputedStyle(document.documentElement);
      const c = cs.getPropertyValue("--sahne").trim() || "#eceae4";
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
      git(baslangic(), false);
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
    function semaDurum(s, adim) {                    // "gizli" | "simdi" | "onceki" | "hedef"
      if (adim === 0) return "hedef";
      if (ADIM[adim].tezgah) return s.a === adim ? "simdi" : "gizli";
      if (s.a > adim) return "gizli";
      return s.a === adim ? "simdi" : "onceki";
    }

    // ---------------------------------------------------------------- adım durumu
    let su = 0, anim = null;
    const ONCEKI = ["opak", "saydam", "gizli"];
    let onceki = ONCEKI.indexOf(P.get("onceki")) >= 0 ? P.get("onceki") : (ONCEKI.indexOf(oku().onceki) >= 0 ? oku().onceki : "opak");
    function baslangic() {
      const q = parseInt(P.get("adim"), 10);
      if (!isNaN(q)) return Math.max(0, Math.min(N - 1, q));
      const h = parseInt((location.hash || "").slice(1), 10);
      if (!isNaN(h)) return Math.max(0, Math.min(N - 1, h));
      const k = oku().adim;
      return typeof k === "number" && k >= 0 && k < N ? k : 0;
    }

    function durum(p, s) {                           // "gizli" | "simdi" | "alt" (alt montaj bağlanıyor) | "onceki"
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

    function sinif(p) { return SINIF[p.r] ? p.r : "satin"; }

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

    let sonUc = [], sonSay = {};
    function uygula(s, ucus) {
      const gizle = onceki === "gizli", saydam = onceki === "saydam";
      const kutu = new THREE.Box3(), gorunur = new THREE.Box3(), altKutu = new THREE.Box3();
      const uc = [];
      const sinifSay = {};
      const yeni = { simdi: [], alt: [], hedef: [] }, eksik = [];   // kontrol: bu adımda yeni görünenler (duruma göre), mesh'i olmayanlar
      const nokta = [], gNokta = [];                  // kadraj: yeni parçaların / görünenlerin kutu köşeleri (son konumda)
      let altVar = false;
      for (const id in PAR) {
        const k = PAR[id]; const p = k.v; const o = k.obj;
        if (!o) { eksik.push(p.id); continue; }
        const d = durum(p, s);
        o.position.copy(k.taban);
        o.userData.d = d;
        if (d === "gizli" || (d === "onceki" && gizle && !p.renk)) { o.visible = false; continue; }
        o.visible = true;
        if (yeni[d]) yeni[d].push(p.id);
        o.updateMatrixWorld(true);
        const b = new THREE.Box3().setFromObject(o);
        gorunur.union(b);
        if (d === "onceki") {
          o.material = p.renk ? malzeme(p.renk, saydam ? 0.2 : true) : malzeme(SINIF.onceki[0], saydam ? 0.18 : 1);
          o.userData.mat0 = o.material;
          continue;
        }
        const c = p.renk || SINIF[sinif(p)][0];
        o.material = malzeme(c);
        o.userData.mat0 = o.userData.mat1 = o.material;
        sinifSay[p.renk ? "kablo" : sinif(p)] = 1;
        kutu.union(b);
        koseler(o, null, nokta);
        if (d === "alt") { altVar = true; altKutu.union(b); }
        uc.push({ k: k, d: d });
      }
      const semaYeni = [];
      SEMA_OBJ.forEach((o, i) => {
        if (!o) return;
        const d = semaDurum(SEMA[i], s);
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
      if (!nokta.length && !gorunur.isEmpty()) {
        for (let i = 0; i < 8; i++) gNokta.push(new THREE.Vector3(i & 1 ? gorunur.max.x : gorunur.min.x, i & 2 ? gorunur.max.y : gorunur.min.y,
          i & 4 ? gorunur.max.z : gorunur.min.z));
      }
      // uçuş vektörleri
      const altBoy = altVar ? Math.max(120, altKutu.getSize(new THREE.Vector3()).length() * 0.8) : 0;
      uc.forEach((x) => {
        const p = x.k.v;
        if (x.d === "alt" && p.ub) x.ofs = new THREE.Vector3(p.ub[0], p.ub[1], p.ub[2]).multiplyScalar(altBoy);
        else if (x.d === "simdi" && p.d > 0 && !p.renk) x.ofs = new THREE.Vector3(p.u[0], p.u[1], p.u[2]).multiplyScalar(p.d);
        else x.ofs = null;
        x.gec = (p.r === "baglanti") ? 0.45 : 0;
      });
      sonUc = uc; sonSay = sinifSay;
      if (sira && sira.adim === s) siraKonum();
      vurguUygula(true);
      lejant(sinifSay, s);
      if (miniAdim !== s) miniGuncelle(s);
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
      const alt = sonUc.filter((x) => x.d === "alt").map((x) => x.k.v.id);
      if (alt.length) {
        const kod = ADIM.filter((a) => a.baglanir === su).map((a) => a.i + ". " + a.kod).join(", ");
        satir.push({ ad: "Alt montaj" + (kod ? " (" + kod + ")" : ""), ids: alt, sema: [] });
      }
      st.parcalar.forEach((x, i) => satir.push({ ad: x.ad, ids: x.ids.filter((id) => var_.has(id)), sema: [], tur: "p", i: i, adet: x.adet }));
      st.baglantilar.forEach((x, i) => satir.push({ ad: x.kod, ids: x.ids.filter((id) => var_.has(id)), sema: [], tur: "b", i: i, adet: x.adet }));
      const sm = [];
      SEMA_OBJ.forEach((o, i) => { if (o && o.userData.d === "simdi") sm.push(i); });
      if (sm.length) satir.push({ ad: "Kablo şemaları", ids: [], sema: sm });
      return satir.filter((x) => x.ids.length || x.sema.length);
    }
    function ucHarita() { const m = new Map(); sonUc.forEach((x) => m.set(x.k.v.id, x)); return m; }
    // takılmamış satırlar patlak konumda / gizli, takılanlar yerinde. Saydam kipte bu adımda daha önce takılan satırlar da
    // (ör. kabuk) saydamlaşır; o an takılan satır ve bekleyenler opak kalır: içeri giren parça kabuğun arkasında kaybolmaz.
    function saydamOf(m) { return malzeme("#" + m.color.getHexString(), 0.25); }
    function siraKonum() {
      const m = ucHarita();
      const sd = onceki === "saydam";
      const taban = (o, j) => {
        const b = o.userData.mat1 || o.material;
        o.material = o.userData.mat0 = sd && j < sira.n - 1 ? saydamOf(b) : b;
      };
      sira.satir.forEach((r, j) => {
        const takili = j < sira.n;
        r.ids.forEach((id) => {
          const x = m.get(id); if (!x) return;
          const o = x.k.obj;
          o.position.copy(x.k.taban);
          if (!takili) { if (x.ofs) o.position.add(x.ofs); else o.visible = false; }
          else o.visible = true;
          taban(o, j);
        });
        r.sema.forEach((i) => { SEMA_OBJ[i].visible = takili; taban(SEMA_OBJ[i], j); });
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
      sira = { adim: su, satir: siraKur(), n: 0, siki: k.nokta, patlak: nk, gorunur: k.gorunur };
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
      r.ids.forEach((id) => {
        const x = m.get(id); if (!x) return;
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

    function git(s, ucus) {
      s = Math.max(0, Math.min(N - 1, s));
      su = s;
      sira = null; secim = null;
      yaz("adim", s);
      try { history.replaceState(null, "", "#" + s); } catch (e) { /* file:// */ }
      panel(s);
      const k = uygula(s, ucus !== false);
      kameraYerlestir(k);
      $("geri").disabled = s === 0; $("ileri").disabled = s === N - 1;
      $("secim").value = String(s);
      $("cubuk").style.width = (100 * s / (N - 1)) + "%";
      $("sayac").textContent = "Adım " + s + " / " + (N - 1);
      $("etiket").hidden = true;
      siraDugme();
      if (CEKIM) {
        // rehber_uret.py kontrolü --dump-dom ile okur: adım başına yeni görünen parça kimlikleri ve mesh'i bulunmayan parçalar
        const kv = $("kontrol-veri");
        if (kv) kv.textContent = JSON.stringify({ adim: s, kod: ADIM[s].kod, simdi: k.yeni.simdi.sort(), alt: k.yeni.alt.sort(),
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
      miniAdim = s;
      const st = ADIM[s];
      MINI.hk.makeEmpty(); MINI.hlist = [];
      for (const id in PAR) {
        const k = PAR[id]; if (!k.mini) continue;
        const p = k.v; let m = MINI.soluk;
        if (s === 0) m = MINI.vurgu;
        else if (st.tezgah) { if (p.t === st.tezgah) m = p.a === s ? MINI.vurgu : (p.a < s ? MINI.yakin : MINI.soluk); }
        else { const d = durum(p, s); if (d === "simdi" || d === "alt") m = MINI.vurgu; }
        k.mini.material = m; k.mini.renderOrder = m === MINI.vurgu ? 10 : 0;
        if (m === MINI.vurgu) { MINI.hk.union(k.mkutu); if (s > 0) MINI.hlist.push(k.mkutu); }
      }
      SEMA_MINI.forEach((m, i) => {
        if (!m) return;
        const v = s === 0 || semaDurum(SEMA[i], s) === "simdi";
        m.material = v ? MINI.vurgu : MINI.soluk; m.renderOrder = v ? 10 : 0;
        if (v && m.userData.mkutu) MINI.hk.union(m.userData.mkutu);
      });
      MINI.yon.copy(kameraYonu());
      miniKamera();
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
      if (MINI.hk.isEmpty() || su === 0 || r.width < 5) { hal.hidden = true; MINI.noktalar.forEach((m) => { m.visible = false; }); return; }
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

    function panel(s) {
      const st = ADIM[s];
      const roz = ["<span class='rozet kod'>" + esc(st.kod) + "</span>", "<span class='rozet'>" + esc(st.faz) + "</span>"];
      if (st.tezgah) roz.push("<span class='rozet tezgah'>Tezgâh: masada yap</span>");
      if (st.kablolama) roz.push("<span class='rozet kapi'>Kablolama kapısı: kabuktan önce dur</span>");
      if (st.no && st.no !== "0") roz.push("<span class='rozet'>M6 no " + esc(st.no) + "</span>");
      $("rozetler").innerHTML = roz.join("");
      $("adim-baslik").textContent = s + ". " + st.baslik;
      $("adim-is").innerHTML = md(st.is_);
      // notlar (rehber_metin.py not_: doğrulanmamış bilgiler, uyarılar)
      const nt = st.not_ || [];
      $("notlar").innerHTML = nt.length ? "<div class='notlar'><b>Notlar</b><ul>" + nt.map((t) => "<li>" + md(t) + "</li>").join("") +
        "</ul></div>" : "";
      // KPI
      const nb = st.baglantilar.reduce((a, b) => a + b.adet, 0), np = st.parcalar.reduce((a, b) => a + b.adet, 0);
      $("kpi").innerHTML = [
        ["~" + st.sure_dk + " dk", "süre" + (st.sure_tahmini ? " (tahmini)" : "")],
        [st.alet ? md(st.alet) : "—", "alet"],
        [np, "parça"], [nb, "bağlantı elemanı"]
      ].map((x) => "<div class='kpi'><b>" + x[0] + "</b><span>" + x[1] + "</span></div>").join("");
      // parçalar (F10a: satıra tıklayınca modelde vurgu; data-satir = tür:sıra)
      const bag = st.baglanir != null ? "<p class='not'>Bu alt montaj " + st.baglanir + ". adımda (" + esc(ADIM[st.baglanir].kod) +
        ") robota bağlanır.</p>" : "";
      const altlar = [];
      if (!st.tezgah && s > 0) ADIM.forEach((a) => { if (a.baglanir === s) altlar.push(a); });
      const altNot = altlar.length ? "<p class='not'>Robota gelen alt montaj: " + altlar.map((a) => a.i + ". " + esc(a.kod)).join(", ") + "</p>" : "";
      $("parcalar").innerHTML = (st.parcalar.length ? "<table class='secilir'>" + st.parcalar.map((x, i) =>
        "<tr data-satir='p:" + i + "'><td><i class='sw' style='background:" + (SINIF[x.r] || SINIF.satin)[0] +
        "'></i>" + esc(x.ad) + "<div class='t'>" + esc(TUR_AD[x.tur] || x.tur) + (x.malzeme && x.malzeme !== "-" ? " · " + esc(x.malzeme) : "") + "</div></td><td class='n'>×" + x.adet + "</td></tr>").join("") +
        "</table>" : "<p class='bos'>" + (s === 0 ? "Hedef: bitmiş robot (" + VERI.parcalar.length + " parça)." : "Bu adımda yeni parça yok.") + "</p>") + bag + altNot;
      // bağlantılar
      $("baglantilar").innerHTML = (st.baglantilar.length ? "<table class='secilir'>" + st.baglantilar.map((x, i) =>
        "<tr data-satir='b:" + i + "'><td>" + esc(x.kod) + (x.onceden ? "<div class='t'>Baskıdan sonra takılı (hazırlık); burada yalnız sayılır</div>" : "") +
        "</td><td class='n'>×" + x.adet + "</td></tr>").join("") + "</table>" : "<p class='bos'>Yok.</p>") +
        (st.baglanti_md ? "<p class='not'>Bağlantı: " + md(st.baglanti_md) + "</p>" : "");
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
      if (s > 0) k.push("onceki");
      if (secim && secNesne.length) k.push("secili");
      $("lejant").innerHTML = k.map((c) => "<span><i style='background:" + SINIF[c][0] + "'></i>" + SINIF[c][1] + "</span>").join("");
      $("lejant").hidden = !k.length;
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
    $("secim").innerHTML = ADIM.map((a) => "<option value='" + a.i + "'>" + a.i + " · " + esc(a.kod) + " · " + esc(a.baslik) + "</option>").join("");
    $("secim").addEventListener("change", (e) => git(+e.target.value));
    const dugme = (id, f) => { const b = $(id); if (b) b.addEventListener("click", () => { f(); b.blur(); }); };
    dugme("geri", () => git(su - 1));
    dugme("ileri", () => git(su + 1));
    dugme("tekrar", () => { sira = null; secimTemizle(); uygula(su, true); siraDugme(); });
    dugme("sifirla", () => kameraYerlestir(uygula(su, false)));
    dugme("patlat", patlat);
    dugme("tak", tak);
    dugme("mini-dugme", () => miniGoster(!miniAcik));
    dugme("mini-kapat", () => miniGoster(false));
    document.addEventListener("keydown", (e) => {
      if (e.target.tagName === "SELECT" || e.target.tagName === "INPUT" || e.ctrlKey || e.metaKey || e.altKey) return;
      const k = e.key;
      if (k === "ArrowRight" || k === "PageDown") { git(su + 1); e.preventDefault(); }
      else if (k === "ArrowLeft" || k === "PageUp") { git(su - 1); e.preventDefault(); }
      else if (k === "r" || k === "R") { sira = null; secimTemizle(); uygula(su, true); siraDugme(); }
      else if (k === "v" || k === "V") kameraYerlestir(uygula(su, false));
      else if (k === "t" || k === "T") temaDegis();
      else if (k === "o" || k === "O" || k === "ö" || k === "Ö") oncekiAyarla(ONCEKI[(ONCEKI.indexOf(onceki) + 1) % 3], true);
      else if (k === "p" || k === "P") patlat();
      else if (k === " " || k === "Spacebar") { if (e.shiftKey) geriAl(); else tak(); e.preventDefault(); }
      else if (k === "m" || k === "M") miniGoster(!miniAcik);
      else if (k === "Escape") secimTemizle();
    });
    let dok = null;                                   // panel / üst şeritte yatay kaydırma = adım değiştir
    document.addEventListener("touchstart", (e) => { if (e.target === tuval || e.touches.length !== 1) { dok = null; return; } dok = [e.touches[0].clientX, e.touches[0].clientY]; }, { passive: true });
    document.addEventListener("touchend", (e) => {
      if (!dok) return; const t = e.changedTouches[0]; const dx = t.clientX - dok[0], dy = t.clientY - dok[1]; dok = null;
      if (Math.abs(dx) > 70 && Math.abs(dy) < 45) git(su + (dx < 0 ? 1 : -1));
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
      patlat: patlat, tak: tak, geriAl: geriAl, oncekiAyarla: (d) => oncekiAyarla(d, false), miniGoster: (a) => miniGoster(a, true)
    };
  };

  // tema kaydı: sayfa açılır açılmaz uygula
  const t = oku().tema;
  if (t === "dark" || t === "light") document.documentElement.dataset.theme = t;
  if (new URLSearchParams(location.search).get("tema")) document.documentElement.dataset.theme = new URLSearchParams(location.search).get("tema");
})();
