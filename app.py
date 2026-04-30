import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import re
from collections import Counter

st.set_page_config(
    page_title="WordCloud Studio",
    page_icon="☁️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── MASTER CSS + JS ───────────────────────────────────────────────────────────
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700;900&family=Outfit:wght@300;400;500;600&display=swap');

/* ═══════════ ROOT ═══════════ */
:root {
  --bg:      #04050a;
  --card:    #111320;
  --glow1:   #00f5ff;
  --glow2:   #ff00c8;
  --glow3:   #ffcc00;
  --glow4:   #00ff88;
  --text:    #e8edf8;
  --muted:   #5a6080;
  --r:       20px;
}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="block-container"] {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Outfit', sans-serif;
}
[data-testid="stSidebar"], [data-testid="stToolbar"], footer { display:none !important; }
[data-testid="block-container"] { padding-top:0 !important; }

/* ═══════════ CANVAS BG ═══════════ */
#three-canvas {
  position: fixed; top:0; left:0;
  width:100vw; height:100vh;
  z-index:0; pointer-events:none;
}

.main-content { position:relative; z-index:10; }

/* ═══════════ HERO ═══════════ */
@keyframes gradShift {
  0%   { background-position:0% 50%; }
  50%  { background-position:100% 50%; }
  100% { background-position:0% 50%; }
}
@keyframes floatTitle {
  0%,100% { transform: translateY(0px) rotateX(0deg) scale(1); }
  50%      { transform: translateY(-10px) rotateX(3deg) scale(1.02); }
}
.hero-wrap { text-align:center; padding:3rem 1rem 1.8rem; perspective:800px; }
.hero-title {
  font-family:'Cinzel Decorative', serif;
  font-size: clamp(1.8rem, 5vw, 3.4rem);
  font-weight:900; letter-spacing:0.06em;
  background: linear-gradient(270deg, #00f5ff, #ff00c8, #ffcc00, #00ff88, #00f5ff);
  background-size: 400% 400%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradShift 4s ease infinite, floatTitle 5s ease-in-out infinite;
  display:inline-block; transform-style:preserve-3d;
}
.hero-sub {
  color:var(--muted); font-size:0.95rem; font-weight:300;
  letter-spacing:0.18em; text-transform:uppercase; margin-top:0.7rem;
}

/* ═══════════ GLASS CARD ═══════════ */
@property --bangle { syntax:'<angle>'; initial-value:0deg; inherits:false; }
@keyframes borderSpin { from{--bangle:0deg} to{--bangle:360deg} }
@keyframes cardFloat {
  0%,100% { transform: translateY(0) rotateX(1.5deg) rotateY(-1deg);
             box-shadow: 0 20px 60px rgba(0,245,255,0.08), 0 0 0 1px rgba(0,245,255,0.12); }
  50%      { transform: translateY(-8px) rotateX(-1deg) rotateY(1.5deg);
             box-shadow: 0 32px 80px rgba(255,0,200,0.12), 0 0 0 1px rgba(255,0,200,0.18); }
}

.glass-card {
  background: linear-gradient(145deg, rgba(17,19,32,0.96), rgba(13,15,26,0.98));
  border-radius: var(--r);
  padding: 2.5rem 2rem;
  position: relative;
  transform-style: preserve-3d;
  animation: cardFloat 7s ease-in-out infinite, borderSpin 4s linear infinite;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  margin-bottom: 2rem;
}
.glass-card::before {
  content:'';
  position:absolute; inset:-2px;
  border-radius: calc(var(--r) + 2px);
  background: conic-gradient(from var(--bangle), #00f5ff, #ff00c8, #ffcc00, #00ff88, #00f5ff);
  z-index:-1; opacity:0.75;
}
.glass-card::after {
  content:''; position:absolute; inset:0;
  border-radius: var(--r);
  background: linear-gradient(145deg, rgba(0,245,255,0.04) 0%, transparent 50%, rgba(255,0,200,0.03) 100%);
  pointer-events:none;
}

/* ═══════════ UPLOAD ZONE ═══════════ */
@keyframes dashPulse {
  0%,100% { border-color:rgba(0,245,255,0.3); background:rgba(0,245,255,0.02); }
  50%      { border-color:rgba(0,245,255,0.65); background:rgba(0,245,255,0.06); }
}
[data-testid="stFileUploader"] { background:transparent !important; }
[data-testid="stFileUploader"] > div {
  border:2px dashed rgba(0,245,255,0.35) !important;
  border-radius:14px !important;
  background:rgba(0,245,255,0.03) !important;
  animation:dashPulse 2.5s ease-in-out infinite;
  transition:all 0.3s;
}
[data-testid="stFileUploader"] > div:hover {
  border-color:rgba(0,245,255,0.8) !important;
  transform:scale(1.01);
}

/* ═══════════ LABELS ═══════════ */
.stSlider label, .stSelectbox label, .stCheckbox label {
  color:var(--muted) !important; font-size:0.78rem !important;
  letter-spacing:0.1em; text-transform:uppercase;
}

/* ═══════════ BUTTON ═══════════ */
@keyframes btnGlow {
  0%,100% { box-shadow:0 0 20px rgba(0,245,255,0.35), 0 0 50px rgba(0,245,255,0.1); }
  50%      { box-shadow:0 0 35px rgba(255,0,200,0.45), 0 0 70px rgba(255,0,200,0.15); }
}
.stButton > button {
  width:100%; padding:1rem 2rem !important;
  background:linear-gradient(135deg, rgba(0,245,255,0.12), rgba(255,0,200,0.12)) !important;
  color:var(--glow1) !important;
  font-family:'Outfit',sans-serif !important; font-weight:600 !important;
  font-size:1rem !important; letter-spacing:0.12em !important;
  text-transform:uppercase !important;
  border:1.5px solid rgba(0,245,255,0.4) !important;
  border-radius:12px !important;
  animation:btnGlow 2s ease-in-out infinite;
  transition:transform 0.2s, filter 0.2s !important;
}
.stButton > button:hover { transform:translateY(-3px) scale(1.02) !important; filter:brightness(1.3) !important; }
.stButton > button:active { transform:translateY(0) scale(0.99) !important; }

/* ═══════════ STATS ═══════════ */
@keyframes chipIn { from{opacity:0;transform:translateY(16px) scale(0.9)} to{opacity:1;transform:none} }
.stats-row { display:flex; flex-wrap:wrap; gap:0.8rem; justify-content:center; margin:1.8rem 0; }
.stat-chip {
  background:linear-gradient(135deg, rgba(0,245,255,0.08), rgba(255,0,200,0.06));
  border:1px solid rgba(0,245,255,0.2);
  border-radius:999px; padding:0.5rem 1.2rem;
  font-size:0.82rem; color:var(--muted);
  animation:chipIn 0.5s ease both;
}
.stat-chip strong { color:var(--glow1); font-weight:600; }

/* ═══════════ CLOUD FRAME ═══════════ */
@keyframes revealCloud {
  from { opacity:0; transform:perspective(800px) rotateX(20deg) translateY(50px) scale(0.92); }
  to   { opacity:1; transform:perspective(800px) rotateX(0deg) translateY(0) scale(1); }
}
@keyframes floatCloud {
  0%,100% { transform:perspective(900px) rotateX(1.5deg) rotateY(-1.5deg); }
  50%      { transform:perspective(900px) rotateX(-1.5deg) rotateY(1.5deg); }
}
.cloud-outer { perspective:900px; margin-bottom:2rem; }
.cloud-frame {
  border-radius:var(--r); overflow:hidden; position:relative;
  animation:revealCloud 1s cubic-bezier(0.22,1,0.36,1) both, floatCloud 9s ease-in-out 1.2s infinite;
  box-shadow: 0 0 0 1px rgba(0,245,255,0.2),
              0 0 50px rgba(0,245,255,0.18),
              0 30px 90px rgba(0,0,0,0.75),
              inset 0 1px 0 rgba(255,255,255,0.05);
  transform-style:preserve-3d;
}
.cloud-frame::after {
  content:''; position:absolute; inset:0;
  background:linear-gradient(135deg,rgba(255,255,255,0.06) 0%,transparent 45%,rgba(0,245,255,0.04) 100%);
  pointer-events:none; z-index:2;
}

/* ═══════════ BARS ═══════════ */
@keyframes barGrow { from { width:0 !important; } }
.bars-section { margin-top:2rem; }
.section-label {
  font-size:0.7rem; letter-spacing:0.2em; text-transform:uppercase;
  color:var(--muted); margin-bottom:1rem;
  border-left:3px solid var(--glow1); padding-left:0.6rem;
}
.bar-row { display:flex; align-items:center; gap:0.75rem; margin-bottom:0.65rem; animation:chipIn 0.4s ease both; }
.bar-word { width:115px; text-align:right; font-size:0.88rem; color:var(--text); font-weight:500; }
.bar-track { flex:1; height:9px; background:rgba(255,255,255,0.05); border-radius:99px; overflow:hidden; }
.bar-fill {
  height:100%; border-radius:99px;
  animation:barGrow 1.2s cubic-bezier(0.22,1,0.36,1) both;
  position:relative;
}
.bar-fill::after {
  content:''; position:absolute; right:0; top:0;
  width:20px; height:100%; background:rgba(255,255,255,0.35);
  filter:blur(4px); border-radius:99px;
}
.bar-count { font-size:0.76rem; color:var(--muted); width:36px; }

/* ═══════════ DOWNLOAD ═══════════ */
[data-testid="stDownloadButton"] > button {
  background:linear-gradient(135deg,rgba(0,255,136,0.1),rgba(0,245,255,0.1)) !important;
  color:var(--glow4) !important;
  border:1.5px solid rgba(0,255,136,0.35) !important;
  border-radius:12px !important;
  font-family:'Outfit',sans-serif !important;
  font-weight:500 !important; letter-spacing:0.08em !important;
  transition:all 0.2s !important;
}
[data-testid="stDownloadButton"] > button:hover {
  transform:translateY(-2px) !important;
  box-shadow:0 0 30px rgba(0,255,136,0.25) !important;
  filter:brightness(1.2) !important;
}

/* ═══════════ IDLE ═══════════ */
@keyframes breathe { 0%,100%{opacity:0.4;transform:scale(1)} 50%{opacity:0.9;transform:scale(1.05)} }
.idle-hint { text-align:center; padding:1.2rem 0; color:var(--muted); font-size:0.9rem; }
.idle-dot { display:inline-block; width:7px; height:7px; border-radius:50%; background:var(--glow1); margin-right:7px; vertical-align:middle; animation:breathe 1.8s ease-in-out infinite; }

/* ═══════════ PARTICLES ═══════════ */
.pfield { position:fixed; inset:0; pointer-events:none; z-index:1; overflow:hidden; }
.pt { position:absolute; border-radius:50%; }
@keyframes ptRise { 0%{transform:translateY(105vh) scale(0);opacity:0} 10%{opacity:1} 90%{opacity:.5} 100%{transform:translateY(-10vh) scale(1.5);opacity:0} }

.footer-txt { text-align:center; margin-top:3rem; padding-bottom:2rem; color:var(--muted); font-size:0.75rem; letter-spacing:0.1em; }
</style>

<canvas id="three-canvas"></canvas>

<script>
(function(){
  const s=document.createElement('script');
  s.src='https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
  s.onload=boot;
  document.head.appendChild(s);

  function boot(){
    const canvas=document.getElementById('three-canvas');
    const renderer=new THREE.WebGLRenderer({canvas,alpha:true,antialias:true});
    renderer.setPixelRatio(Math.min(devicePixelRatio,2));
    renderer.setSize(innerWidth,innerHeight);
    const scene=new THREE.Scene();
    const cam=new THREE.PerspectiveCamera(60,innerWidth/innerHeight,0.1,1000);
    cam.position.z=28;

    /* rings */
    const ringGeo=new THREE.TorusGeometry(9,0.04,2,140);
    const ringCols=[0x00f5ff,0xff00c8,0xffcc00,0x00ff88];
    const rings=ringCols.map((c,i)=>{
      const m=new THREE.Mesh(ringGeo,new THREE.MeshBasicMaterial({color:c,transparent:true,opacity:0.15}));
      m.rotation.set(Math.PI*(i*0.25+0.1),Math.PI*i*0.37,0);
      scene.add(m); return m;
    });

    /* particles */
    const N=1200, pos=new Float32Array(N*3), col=new Float32Array(N*3);
    const pal=[[0,.96,1],[1,0,.78],[1,.8,0],[0,1,.53]];
    for(let i=0;i<N;i++){
      const r=13+Math.random()*10, th=Math.random()*Math.PI*2, ph=Math.acos(2*Math.random()-1);
      pos[i*3]=r*Math.sin(ph)*Math.cos(th); pos[i*3+1]=r*Math.sin(ph)*Math.sin(th); pos[i*3+2]=r*Math.cos(ph);
      const[pr,pg,pb]=pal[i%4]; col[i*3]=pr; col[i*3+1]=pg; col[i*3+2]=pb;
    }
    const ptGeo=new THREE.BufferGeometry();
    ptGeo.setAttribute('position',new THREE.BufferAttribute(pos,3));
    ptGeo.setAttribute('color',new THREE.BufferAttribute(col,3));
    scene.add(new THREE.Points(ptGeo,new THREE.PointsMaterial({size:0.13,vertexColors:true,transparent:true,opacity:0.55})));

    /* icosahedron */
    const ico=new THREE.Mesh(
      new THREE.IcosahedronGeometry(6,1),
      new THREE.MeshBasicMaterial({color:0x00f5ff,wireframe:true,transparent:true,opacity:0.05})
    );
    scene.add(ico);

    /* small orbiting sphere */
    const orb=new THREE.Mesh(
      new THREE.SphereGeometry(0.5,16,16),
      new THREE.MeshBasicMaterial({color:0xff00c8,transparent:true,opacity:0.7})
    );
    scene.add(orb);

    let mx=0,my=0,t=0;
    addEventListener('mousemove',e=>{ mx=(e.clientX/innerWidth-.5)*.5; my=(e.clientY/innerHeight-.5)*.5; });
    addEventListener('resize',()=>{ cam.aspect=innerWidth/innerHeight; cam.updateProjectionMatrix(); renderer.setSize(innerWidth,innerHeight); });

    (function loop(){
      requestAnimationFrame(loop); t+=0.005;
      rings.forEach((r,i)=>{ r.rotation.x+=.002*(i%2?1:-1); r.rotation.y+=.003*(i%2?-1:1); r.rotation.z+=.001; });
      ico.rotation.x=t*.28+my; ico.rotation.y=t*.18+mx;
      orb.position.set(Math.cos(t*1.5)*11, Math.sin(t*2)*6, Math.sin(t)*5);
      cam.position.x+=(mx*3-cam.position.x)*.04;
      cam.position.y+=(-my*3-cam.position.y)*.04;
      cam.lookAt(scene.position);
      renderer.render(scene,cam);
    })();
  }
})();
</script>

<div class="pfield" id="pf"></div>
<script>
(function(){
  const f=document.getElementById('pf');
  const c=['#00f5ff','#ff00c8','#ffcc00','#00ff88'];
  for(let i=0;i<45;i++){
    const p=document.createElement('div'), sz=2+Math.random()*4;
    p.className='pt';
    p.style.cssText=`width:${sz}px;height:${sz}px;left:${Math.random()*100}vw;background:${c[i%4]};opacity:${.3+Math.random()*.5};animation:ptRise ${8+Math.random()*18}s linear ${-Math.random()*20}s infinite;filter:blur(${Math.random()*1.5}px);box-shadow:0 0 6px ${c[i%4]};`;
    f.appendChild(p);
  }
})();
</script>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-content">
<div class="hero-wrap">
  <div class="hero-title">☁ WordCloud Studio</div>
  <div class="hero-sub">Transform text &nbsp;·&nbsp; Visualize meaning &nbsp;·&nbsp; Feel the words</div>
</div>
""", unsafe_allow_html=True)

# ── CARD ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Drop your .txt file here",
    type=["txt"],
    label_visibility="collapsed",
)

STOP_WORDS = {
    "the","a","an","and","or","but","in","on","at","to","for","of","with","is","it",
    "this","that","as","are","was","were","be","been","being","have","has","had","do",
    "does","did","will","would","could","should","may","might","shall","can","not","no",
    "from","by","about","into","through","over","after","before","between","out","up",
    "i","you","he","she","we","they","me","him","her","us","them","my","your","his",
    "their","its","our","which","who","what","there","here","all","more","so","if",
    "than","just","also","each","any","some","other","then","when","where","how","why",
}

PALETTES = {
    "⚡ Neon Plasma":   "plasma",
    "🌊 Ocean Depths":  "cool",
    "🔥 Inferno":       "inferno",
    "🌈 Vivid Rainbow": "gist_rainbow",
    "🍬 Candy Spring":  "spring",
    "🌿 Aurora":        "summer",
    "☀️ Solar Flare":   "YlOrRd",
    "💎 Crystal":       "winter",
    "🎭 Twilight":      "twilight",
    "🦋 Spectral":      "Spectral",
}

BG_COLORS = {
    "⬛ Void Black":   "#04050a",
    "🌌 Deep Space":   "#070b14",
    "🎱 Pure Black":   "#000000",
    "🌃 Midnight":     "#0d0f1a",
}

if uploaded_file:
    c1, c2 = st.columns(2)
    with c1:
        max_words   = st.slider("Max words", 30, 400, 150, 10)
        palette_lbl = st.selectbox("Color palette", list(PALETTES.keys()))
    with c2:
        bg_lbl      = st.selectbox("Background", list(BG_COLORS.keys()))
        remove_stop = st.checkbox("Remove common words", value=True)

    generate = st.button("✦  Generate Word Cloud  ✦")

st.markdown('</div>', unsafe_allow_html=True)

# ── GENERATE ─────────────────────────────────────────────────────────────────
if uploaded_file and generate:
    raw   = uploaded_file.read().decode("utf-8", errors="ignore")
    all_w = re.findall(r"[a-zA-Z]{3,}", raw.lower())
    words = [w for w in all_w if w not in STOP_WORDS] if remove_stop else all_w
    freq  = Counter(words)

    wc = WordCloud(
        width=1600, height=800,
        background_color=BG_COLORS[bg_lbl],
        colormap=PALETTES[palette_lbl],
        max_words=max_words,
        prefer_horizontal=0.72,
        margin=8, collocations=False,
        min_font_size=10, max_font_size=220,
    ).generate_from_frequencies(freq)

    delays = ["0s","0.1s","0.2s","0.3s"]
    chips  = [("Total words",f"{len(all_w):,}"),("Unique",f"{len(set(all_w)):,}"),
              ("Rendered",f"{min(max_words,len(freq))}"),("Palette",palette_lbl.split()[-1])]
    chips_html = '<div class="stats-row">' + "".join(
        f'<div class="stat-chip" style="animation-delay:{delays[i]}">{l}: <strong>{v}</strong></div>'
        for i,(l,v) in enumerate(chips)
    ) + '</div>'
    st.markdown(chips_html, unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(16,8), facecolor=BG_COLORS[bg_lbl])
    ax.imshow(wc, interpolation="bilinear"); ax.axis("off")
    plt.tight_layout(pad=0)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor=BG_COLORS[bg_lbl], dpi=160)
    buf.seek(0); plt.close(fig)

    st.markdown('<div class="cloud-outer"><div class="cloud-frame">', unsafe_allow_html=True)
    st.image(buf, use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    buf.seek(0)
    st.download_button("⬇  Save as PNG", data=buf, file_name="wordcloud.png", mime="image/png")

    # top word bars
    BCOLS = ["#00f5ff","#ff00c8","#ffcc00","#00ff88","#ff6b6b","#c77dff","#ff9f1c","#2ec4b6","#e71d36","#a7c957"]
    top = freq.most_common(10); mx = top[0][1] if top else 1
    rows = "".join(
        f'<div class="bar-row" style="animation-delay:{i*0.07:.2f}s">'
        f'<div class="bar-word">{w}</div>'
        f'<div class="bar-track"><div class="bar-fill" style="width:{cnt/mx*100:.1f}%;background:linear-gradient(90deg,{BCOLS[i%10]}88,{BCOLS[i%10]});animation-delay:{i*0.1:.2f}s"></div></div>'
        f'<div class="bar-count">{cnt}</div></div>'
        for i,(w,cnt) in enumerate(top)
    )
    st.markdown(f'<div class="bars-section"><div class="section-label">Top words</div>{rows}</div>', unsafe_allow_html=True)

elif not uploaded_file:
    st.markdown('<div class="idle-hint"><span class="idle-dot"></span>Upload a .txt file to begin your cloud journey</div>', unsafe_allow_html=True)

st.markdown('<div class="footer-txt">WordCloud Studio &nbsp;·&nbsp; Built with Streamlit &amp; Three.js &nbsp;·&nbsp; ☁</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)