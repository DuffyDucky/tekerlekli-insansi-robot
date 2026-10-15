/* Lale 3B montaj rehberi. Veri: veri/rehber-veri.js (window.REHBER_VERI), mesh: veri/robot-glb.js (window.REHBER_GLB, base64 GLB).
   İkisi de tasarim/freecad/rehber/rehber_veri.py ile üretilir; elle düzenleme. Klasik betik (file:// altında da çalışsın diye);
   three.js index.html'deki modül betiği tarafından RehberBaslat'a verilir. */
(function () {
  "use strict";
  const VERI = window.REHBER_VERI;
  const ADIM = VERI ? VERI.adimlar : [];
  const N = ADIM.length;
  const $ = (id) => document.getElementById(id);
  const P = new URLSearchParams(location.search);
  const CEKIM = P.get("cekim") === "1";               // ekran görüntüsü kipi: animasyon yok, sabit kamera

  // ---------------------------------------------------------------- güvenli yerel kayıt (hata verirse sessizce düşer)
  const KAYIT = "lale-rehber-v1";
  function oku() { try { return JSON.parse(localStorage.getItem(KAYIT) || "{}") || {}; } catch (e) { return {}; } }
  function yaz(k, v) { try { const d = oku(); d[k] = v; localStorage.setItem(KAYIT, JSON.stringify(d)); } catch (e) { /* yok say */ } }

  // ---------------------------------------------------------------- renkler
  const SINIF = {
    baski: ["#f0932b", "Baskı (PETG)"], cf: ["#3d5a80", "Baskı (PETG-CF)"], profil: ["#16a085", "Sigma profil"],
    satin: ["#2f86d4", "Satın alınan"], lazer: ["#8e44ad", "Lazer kesim"], imalat: ["#d35400", "İmalat"],
    baglanti: ["#d4ac0d", "Bağlantı elemanı"], m6: ["#e5383b", "M6 CAD sonrası değişecek"], kablo: ["#c0392b", "Kablo yolu"],
    ref: ["#95a5a6", "Gösterim"], onceki: ["#b5b5b0", "Önceki adımlar"]
  };
  function tema() {
    const t = document.documentElement.dataset.theme;
    if (t) return t;
    return matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  window.RehberBaslat = function (L) {
    const THREE = L.THREE;
    if (!VERI || !window.REHBER_GLB) { $("yukleniyor").textContent = "Veri bulunamadı: veri/rehber-veri.js ve veri/robot-glb.js gerekli."; return; }
    const tuval = $("tuval");
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
    function malzeme(renk, saydam) {
      const k = renk + (saydam ? "s" : "");
      if (!mat[k]) {
        mat[k] = new THREE.MeshStandardMaterial({ color: renk, metalness: 0.05, roughness: 0.75, side: THREE.DoubleSide,
          transparent: !!saydam, opacity: saydam ? 0.35 : 1, depthWrite: !saydam });
      }
      return mat[k];
    }
    function sahneRengi() {
      const c = getComputedStyle(document.documentElement).getPropertyValue("--sahne").trim() || "#eceae4";
      sahne.background = new THREE.Color(c);
      SINIF.onceki[0] = tema() === "dark" ? "#5d6168" : "#b5b5b0";
      zemin.material.color = new THREE.Color(tema() === "dark" ? 0x555555 : 0xaaaaaa);
    }

    // ---------------------------------------------------------------- GLB
    const ikili = Uint8Array.from(atob(window.REHBER_GLB), (c) => c.charCodeAt(0)).buffer;
    const PAR = {};                                   // id -> { veri, obj, taban (Vector3) }
    VERI.parcalar.forEach((p) => { PAR[p.id] = { v: p }; });
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
      $("yukleniyor").hidden = true;
      sahneRengi();
      git(baslangic(), false);
    }, (h) => { $("yukleniyor").textContent = "GLB okunamadı: " + h; console.error(h); });

    // ---------------------------------------------------------------- adım durumu
    let su = 0, anim = null;
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

    function sinif(p) { return p.m6 ? "m6" : p.r; }

    function uygula(s, ucus) {
      const gizle = $("onceki-gizle").checked;
      const kutu = new THREE.Box3(), gorunur = new THREE.Box3(), altKutu = new THREE.Box3();
      const uc = [];
      const sinifSay = {};
      let altVar = false;
      for (const id in PAR) {
        const k = PAR[id]; const p = k.v; const o = k.obj;
        if (!o) continue;
        const d = durum(p, s);
        o.position.copy(k.taban);
        if (d === "gizli" || (d === "onceki" && gizle && !p.renk)) { o.visible = false; continue; }
        o.visible = true;
        o.updateMatrixWorld(true);
        const b = new THREE.Box3().setFromObject(o);
        gorunur.union(b);
        if (d === "onceki") {
          o.material = p.renk ? malzeme(p.renk, true) : malzeme(SINIF.onceki[0]);
          continue;
        }
        const c = p.renk || SINIF[sinif(p)][0];
        o.material = malzeme(c);
        sinifSay[p.renk ? "kablo" : sinif(p)] = 1;
        kutu.union(b);
        if (d === "alt") { altVar = true; altKutu.union(b); }
        uc.push({ k: k, d: d });
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
      lejant(sinifSay, s);
      if (ucus && !CEKIM) baslatUcus(uc); else ciz();
      return { kutu: kutu.isEmpty() ? gorunur : kutu, gorunur: gorunur };
    }

    function baslatUcus(uc) {
      const T = 1300, t0 = performance.now();
      if (anim) cancelAnimationFrame(anim);
      const adim = (t) => {
        const f = Math.min(1, (t - t0) / T);
        uc.forEach((x) => {
          if (!x.ofs) return;
          const g = Math.min(1, Math.max(0, (f - x.gec) / (1 - x.gec - 0.0001)));
          const e = 1 - Math.pow(1 - g, 3);
          x.k.obj.position.copy(x.k.taban).addScaledVector(x.ofs, 1 - e);
        });
        renderer.render(sahne, kamera);
        anim = f < 1 ? requestAnimationFrame(adim) : null;
      };
      uc.forEach((x) => { if (x.ofs) x.k.obj.position.copy(x.k.taban).add(x.ofs); });
      anim = requestAnimationFrame(adim);
    }

    let sonKutu = null;
    function kameraYerlestir(k) {
      const kutu = k.kutu.isEmpty() ? new THREE.Box3(new THREE.Vector3(-300, 0, -300), new THREE.Vector3(300, 1300, 300)) : k.kutu.clone();
      // bağlam: hedef kutu çok küçükse görünen parçaların bir kısmını da kadraja al
      const r0 = kutu.getSize(new THREE.Vector3()).length() / 2;
      const merkez = kutu.getCenter(new THREE.Vector3());
      const r = Math.max(60, r0 * 0.95);
      const st = ADIM[su];
      let yon = new THREE.Vector3(0.85, 0.62, 1.25);
      const alttan = st && (st.kod === "B1" || st.kod === "B1a");
      if (alttan) yon.set(0.9, -0.55, 1.2);
      yon.normalize();
      const fov = kamera.fov * Math.PI / 180;
      const asp = Math.max(0.5, Math.min(1, kamera.aspect));
      const uzak = r / Math.sin(fov / 2) / asp;
      kamera.position.copy(merkez).addScaledVector(yon, uzak);
      kamera.near = Math.max(1, uzak / 100); kamera.far = uzak * 20; kamera.updateProjectionMatrix();
      kontrol.target.copy(merkez);
      kontrol.update();
      sonKutu = k;
    }

    function git(s, ucus) {
      s = Math.max(0, Math.min(N - 1, s));
      su = s;
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
      if (CEKIM) requestAnimationFrame(() => { ciz(); document.body.dataset.hazir = "1"; });
    }

    // ---------------------------------------------------------------- çizim
    let bekleyen = false;
    function ciz() {
      if (anim || bekleyen) return;
      bekleyen = true;
      requestAnimationFrame(() => { bekleyen = false; renderer.render(sahne, kamera); });
    }
    function boyut() {
      const r = tuval.parentElement.getBoundingClientRect();
      renderer.setSize(Math.max(1, r.width), Math.max(1, r.height), false);
      kamera.aspect = r.width / Math.max(1, r.height);
      kamera.updateProjectionMatrix();
      ciz();
    }
    new ResizeObserver(boyut).observe(tuval.parentElement);
    boyut();

    // ---------------------------------------------------------------- tıklayınca parça adı
    const ray = new THREE.Raycaster(); let basla = null;
    tuval.addEventListener("pointerdown", (e) => { basla = [e.clientX, e.clientY]; });
    tuval.addEventListener("pointerup", (e) => {
      if (!basla || Math.hypot(e.clientX - basla[0], e.clientY - basla[1]) > 5) return;
      const r = tuval.getBoundingClientRect();
      ray.setFromCamera(new THREE.Vector2(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1), kamera);
      const hit = ray.intersectObjects(sahne.children, true).find((h) => h.object.visible && h.object.userData.id);
      const et = $("etiket");
      if (!hit) { et.hidden = true; return; }
      const p = PAR[hit.object.userData.id].v;
      et.innerHTML = "<b>" + esc(p.ad) + "</b><br><span class='not'>" + esc(p.kod) + " · " + esc(p.modul) + " · adım " +
        p.a + " (" + esc(ADIM[p.a].kod) + ")" + (p.m6 ? " · <span style='color:var(--no)'>M6 " + p.m6 + "</span>" : "") + "</span>";
      et.hidden = false;
    });

    // ---------------------------------------------------------------- panel
    function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]); }
    function md(s) { return esc(s).replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>").replace(/`([^`]+)`/g, "<code>$1</code>"); }
    const TUR_SINIF = { Baski: "baski", Satin: "satin", Lazer: "lazer", Imalat: "imalat" };

    function panel(s) {
      const st = ADIM[s];
      const roz = ["<span class='rozet kod'>" + esc(st.kod) + "</span>", "<span class='rozet'>" + esc(st.faz) + "</span>"];
      if (st.tezgah) roz.push("<span class='rozet tezgah'>Tezgâh: masada yap</span>");
      if (st.kablolama) roz.push("<span class='rozet kapi'>Kablolama kapısı: kabuktan önce dur</span>");
      if (st.no && st.no !== "0") roz.push("<span class='rozet'>M6 no " + esc(st.no) + "</span>");
      $("rozetler").innerHTML = roz.join("");
      $("adim-baslik").textContent = s + ". " + st.baslik;
      $("adim-is").innerHTML = md(st.is_);
      // M6 uyarısı
      $("m6-uyari").innerHTML = st.m6.length ? "<div class='uyari'><b>M6 CAD sonrası değişecek</b><ul>" +
        st.m6.map((m) => "<li>" + m.adet + " bağlantı: " + esc(m.not_) + "</li>").join("") + "</ul></div>" : "";
      // KPI
      const nb = st.baglantilar.reduce((a, b) => a + b.adet, 0), np = st.parcalar.reduce((a, b) => a + b.adet, 0);
      $("kpi").innerHTML = [
        ["~" + st.sure_dk + " dk", "süre" + (st.sure_tahmini ? " (tahmini)" : "")],
        [st.alet ? md(st.alet) : "—", "alet"],
        [np, "parça"], [nb, "bağlantı elemanı"]
      ].map((x) => "<div class='kpi'><b>" + x[0] + "</b><span>" + x[1] + "</span></div>").join("");
      // parçalar
      const bag = st.baglanir != null ? "<p class='not'>Bu alt montaj " + st.baglanir + ". adımda (" + esc(ADIM[st.baglanir].kod) +
        ") robota bağlanır.</p>" : "";
      const altlar = [];
      if (!st.tezgah && s > 0) ADIM.forEach((a) => { if (a.baglanir === s) altlar.push(a); });
      const altNot = altlar.length ? "<p class='not'>Robota gelen alt montaj: " + altlar.map((a) => a.i + ". " + esc(a.kod)).join(", ") + "</p>" : "";
      $("parcalar").innerHTML = (st.parcalar.length ? "<table>" + st.parcalar.map((x) =>
        "<tr><td><i class='sw' style='background:" + (SINIF[x.r] || SINIF.satin)[0] +
        "'></i>" + esc(x.ad) + "<div class='t'>" + esc(x.tur) + (x.malzeme ? " · " + esc(x.malzeme) : "") + "</div></td><td class='n'>×" + x.adet + "</td></tr>").join("") +
        "</table>" : "<p class='bos'>" + (s === 0 ? "Hedef: bitmiş robot (" + VERI.parcalar.length + " parça)." : "Bu adımda yeni parça yok.") + "</p>") + bag + altNot;
      // bağlantılar
      $("baglantilar").innerHTML = (st.baglantilar.length ? "<table>" + st.baglantilar.map((x) =>
        "<tr class='" + (x.m6 ? "m6" : "") + "'><td>" + esc(x.kod) + (x.m6 ? "<div class='t'>" + x.m6 + " tanesi M6 CAD sonrası değişecek</div>" : "") +
        "</td><td class='n'>×" + x.adet + "</td></tr>").join("") + "</table>" : "<p class='bos'>Yok.</p>") +
        (st.baglanti_md ? "<p class='not'>M6 tablosu: " + md(st.baglanti_md) + "</p>" : "");
      // kontrol listesi
      const kk = (oku().kontrol || {})[st.kod] || [];
      $("kontrol").innerHTML = st.kontrol.length ? st.kontrol.map((t, i) =>
        "<li class='" + (kk[i] ? "tamam" : "") + "'><input type='checkbox' data-i='" + i + "'" + (kk[i] ? " checked" : "") + "><span>" + md(t) + "</span></li>").join("")
        : "<li class='bos'>Bu adım için kontrol listesi henüz yazılmadı (M6 erişim notuna bak).</li>";
      // kablo kancası
      const kab = st.kablo.map((t) => "<li>" + md(t) + "</li>");
      VERI.parcalar.forEach((p) => {
        if (p.renk && p.a === s) kab.push("<li><i class='sw' style='background:" + p.renk + "'></i>" + esc(p.ad) + "</li>");
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

    function lejant(say, s) {
      const k = Object.keys(say);
      if (s > 0) k.push("onceki");
      $("lejant").innerHTML = k.map((c) => "<span><i style='background:" + SINIF[c][0] + "'></i>" + SINIF[c][1] + "</span>").join("");
    }

    // ---------------------------------------------------------------- gezinme
    $("secim").innerHTML = ADIM.map((a) => "<option value='" + a.i + "'>" + a.i + " · " + esc(a.kod) + " · " + esc(a.baslik) + "</option>").join("");
    $("secim").addEventListener("change", (e) => git(+e.target.value));
    $("geri").addEventListener("click", () => git(su - 1));
    $("ileri").addEventListener("click", () => git(su + 1));
    $("tekrar").addEventListener("click", () => uygula(su, true));
    $("sifirla").addEventListener("click", () => kameraYerlestir(uygula(su, false)));
    $("onceki-gizle").addEventListener("change", () => { uygula(su, false); });
    document.addEventListener("keydown", (e) => {
      if (e.target.tagName === "SELECT" || e.target.tagName === "INPUT") return;
      if (e.key === "ArrowRight" || e.key === "PageDown") { git(su + 1); e.preventDefault(); }
      else if (e.key === "ArrowLeft" || e.key === "PageUp") { git(su - 1); e.preventDefault(); }
      else if (e.key === "r" || e.key === "R") uygula(su, true);
      else if (e.key === "v" || e.key === "V") kameraYerlestir(uygula(su, false));
      else if (e.key === "t" || e.key === "T") temaDegis();
    });
    let dok = null;                                   // panel / üst şeritte yatay kaydırma = adım değiştir
    document.addEventListener("touchstart", (e) => { if (e.target === tuval || e.touches.length !== 1) { dok = null; return; } dok = [e.touches[0].clientX, e.touches[0].clientY]; }, { passive: true });
    document.addEventListener("touchend", (e) => {
      if (!dok) return; const t = e.changedTouches[0]; const dx = t.clientX - dok[0], dy = t.clientY - dok[1]; dok = null;
      if (Math.abs(dx) > 70 && Math.abs(dy) < 45) git(su + (dx < 0 ? 1 : -1));
    }, { passive: true });

    function temaDegis() {
      const sira = [undefined, "dark", "light"];
      const simdi = document.documentElement.dataset.theme;
      const yeni = sira[(sira.indexOf(simdi) + 1) % 3];
      if (yeni) document.documentElement.dataset.theme = yeni; else delete document.documentElement.dataset.theme;
      yaz("tema", yeni || null);
      sahneRengi(); uygula(su, false);
    }
    $("tema").addEventListener("click", temaDegis);
    matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { sahneRengi(); uygula(su, false); });
  };

  // tema kaydı: sayfa açılır açılmaz uygula
  const t = oku().tema;
  if (t === "dark" || t === "light") document.documentElement.dataset.theme = t;
  if (new URLSearchParams(location.search).get("tema")) document.documentElement.dataset.theme = new URLSearchParams(location.search).get("tema");
})();
