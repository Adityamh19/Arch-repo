# app.py
import streamlit as st
import os
import json
import requests
from datetime import datetime
from PIL import Image
import base64

# ---------------- CONFIG ----------------
SHARED_PASSWORD = "ARCH"
BASE_STORAGE_FOLDER = "gallery_storage"
PAGE_TITLE = "ARCHIPELAGO | STUDIO"
PAGE_ICON = "🏙"
SETTINGS_FILE = os.path.join(BASE_STORAGE_FOLDER, "app_settings.json")

st.set_page_config(layout="wide", page_title=PAGE_TITLE, page_icon=PAGE_ICON)

# ---------------- SAFE RERUN ----------------
def safe_rerun():
    try:
        if hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
        elif hasattr(st, "rerun"):
            st.rerun()
    except Exception:
        try:
            st.stop()
        except Exception:
            pass

# ---------------- DEFAULT SETTINGS ----------------
DEFAULT_SETTINGS = {
    "theme_mode": "Light",        # "Light" or "Dark"
    "accent": "#0b6cff",
    "show_timestamps": True,
    "grid_columns": 4,
    "thumb_size": "medium",
    "autoplay_hero": False,
    "autoplay_interval": 5,
    "auto_ping_interval": 0,
    "webhook_url": "",
    "auto_save": False
}

# ---------------- STORAGE ----------------
if not os.path.exists(BASE_STORAGE_FOLDER):
    os.makedirs(BASE_STORAGE_FOLDER)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                cfg = DEFAULT_SETTINGS.copy()
                cfg.update(json.load(f))
                return cfg
        except Exception:
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception:
        return False

if "app_settings" not in st.session_state:
    st.session_state["app_settings"] = load_settings()

def S():
    return st.session_state["app_settings"]

# ---------------- FILE HELPERS ----------------
def init_storage():
    if not os.path.exists(BASE_STORAGE_FOLDER):
        os.makedirs(BASE_STORAGE_FOLDER)
    default_section = os.path.join(BASE_STORAGE_FOLDER, "Selected Works")
    if not os.path.exists(default_section):
        os.makedirs(default_section)

def get_sections():
    if not os.path.exists(BASE_STORAGE_FOLDER):
        return []
    return [d for d in os.listdir(BASE_STORAGE_FOLDER) if os.path.isdir(os.path.join(BASE_STORAGE_FOLDER, d))]

def create_new_section(section_name):
    clean_name = "".join(c for c in section_name if c.isalnum() or c in (' ', '_', '-')).strip()
    if not clean_name:
        return False
    path = os.path.join(BASE_STORAGE_FOLDER, clean_name)
    if not os.path.exists(path):
        os.makedirs(path)
        return True
    return False

def save_file(uploaded_file, section):
    now = datetime.now()
    date_subfolder = now.strftime("%Y-%m-%d")
    time_prefix = now.strftime("%H-%M-%S")
    section_path = os.path.join(BASE_STORAGE_FOLDER, section)
    date_path = os.path.join(section_path, date_subfolder)
    if not os.path.exists(date_path):
        os.makedirs(date_path)
    clean_name = f"{time_prefix}_{uploaded_file.name}"
    file_path = os.path.join(date_path, clean_name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

def delete_image(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

def get_images_in_section(section):
    images = []
    section_path = os.path.join(BASE_STORAGE_FOLDER, section)
    if os.path.exists(section_path):
        for root, dirs, files in os.walk(section_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    full_path = os.path.join(root, file)
                    try:
                        folder_date = os.path.basename(root)
                        time_stamp = file.split('_')[0].replace('-', ':')
                    except Exception:
                        folder_date = "Unknown"
                        time_stamp = ""
                    images.append({
                        "path": full_path,
                        "filename": file,
                        "date": folder_date,
                        "time": time_stamp,
                        "sort_key": f"{folder_date}{time_stamp}"
                    })
    return sorted(images, key=lambda x: x['sort_key'], reverse=True)

def file_to_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

# ---------------- CSS (visibility-first) ----------------
def build_css(settings):
    theme = settings.get("theme_mode", "Light")
    accent = settings.get("accent", "#0b6cff")

    if theme == "Dark":
        page_bg = "#0f1113"
        text = "#FFFFFF"
        subtitle = "rgba(255,255,255,0.92)"
        hero_left_bg = "rgba(0,0,0,0.55)"
        hero_overlay = "linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5))"
        border = "rgba(255,255,255,0.06)"
        shadow = "0 20px 40px rgba(0,0,0,0.75)"
    else:
        page_bg = "#fafafa"
        text = "#071025"
        subtitle = "rgba(7,16,37,0.88)"
        hero_left_bg = "rgba(255,255,255,0.92)"
        hero_overlay = "linear-gradient(rgba(255,255,255,0.36), rgba(255,255,255,0.36))"
        border = "#e8e8e8"
        shadow = "0 12px 30px rgba(17,17,17,0.06)"

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700;900&display=swap');

    :root {{
      --page-bg: {page_bg};
      --text: {text};
      --subtitle: {subtitle};
      --accent: {accent};
      --hero-left-bg: {hero_left_bg};
      --hero-overlay: {hero_overlay};
      --border: {border};
      --shadow: {shadow};
    }}

    html, body, [class*="css"] {{
      font-family: 'Montserrat', sans-serif;
      background: var(--page-bg) !important;
      color: var(--text) !important;
    }}
    .block-container {{ padding-top: 1.6rem; padding-bottom: 3.5rem; }}

    /* HERO LEFT: semi-opaque box ensures readability */
    .hero-wrap {{ display:flex; gap:24px; align-items:center; justify-content:space-between; margin-bottom:28px; }}
    .hero-left {{
      flex: 1.4;
      padding: 22px 18px;
      background: var(--hero-left-bg);
      border-radius: 12px;
      box-shadow: var(--shadow);
      border: 1px solid var(--border);
      min-height: 180px;
    }}
    .hero-tag {{ color: var(--accent); font-weight:700; font-size:12px; letter-spacing:2px; text-transform:uppercase; margin-bottom:10px; }}
    .hero-title {{
      font-size:56px;
      line-height:1.02;
      margin:0;
      font-weight:900;
      color: var(--text) !important;
      text-transform:uppercase;
      text-shadow: 0 10px 30px rgba(0,0,0,0.45);
      -webkit-font-smoothing:antialiased;
    }}
    .hero-sub {{ color: var(--subtitle) !important; margin-top:12px; max-width:760px; font-size:16px; }}

    /* HERO IMAGE: overlay dims image for readability */
    .hero-image {{
      flex:1;
      border-radius:12px;
      overflow:hidden;
      border: 1px solid var(--border);
      box-shadow: var(--shadow);
      height:360px;
      position:relative;
      display:flex; align-items:center; justify-content:center;
    }}
    .hero-image img {{ width:100%; height:100%; object-fit:cover; display:block; filter: contrast(1.03) saturate(1.06); }}
    .hero-image::after {{
      content: "";
      position: absolute;
      inset: 0;
      background: var(--hero-overlay);
      pointer-events: none;
    }}

    /* scrollable featured strip */
    .scroller {{ display:flex; gap:14px; overflow-x:auto; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch; }}
    .project-card {{ min-width:260px; background:var(--page-bg); border-radius:10px; overflow:hidden; border:1px solid var(--border); box-shadow:var(--shadow); scroll-snap-align:center; }}
    .project-card img {{ width:100%; height:160px; object-fit:cover; display:block; }}
    .project-meta {{ padding:10px; color:var(--text); }}

    /* gallery grid */
    .gallery-grid {{ display:grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap:18px; margin-top:12px; }}
    .gallery-card {{ background:var(--page-bg); border-radius:10px; padding:8px; border:1px solid var(--border); box-shadow:var(--shadow); transition: transform .14s ease; }}
    .gallery-card:hover {{ transform: translateY(-8px); box-shadow: 0 28px 60px rgba(10,10,10,0.08); }}

    /* Sidebar dark with white text */
    section[data-testid="stSidebar"] {{
      background-color: #0b0c0d !important;
      color: white !important;
      border-right: 1px solid rgba(255,255,255,0.04) !important;
    }}
    section[data-testid="stSidebar"] .stText, section[data-testid="stSidebar"] .stMarkdown {{
      color: white !important;
    }}
    section[data-testid="stSidebar"] .stButton button {{
      background-color: transparent !important;
      border: 1px solid rgba(255,255,255,0.10) !important;
      color: white !important;
      border-radius: 8px !important;
      padding: 8px 10px !important;
    }}
    section[data-testid="stSidebar"] .stTextInput input, section[data-testid="stSidebar"] .stSelect select {{
      background: #0f1113 !important;
      color: white !important;
      border: 1px solid rgba(255,255,255,0.06) !important;
    }}

    /* bright headings globally */
    h1, h2, h3, h4, .stMarkdown h1 {{ color: var(--text) !important; text-shadow: 0 6px 20px rgba(0,0,0,0.25); }}

    @media (max-width: 900px) {{
      .hero-wrap {{ flex-direction: column; gap:14px; }}
      .hero-title {{ font-size:36px; }}
      .hero-image {{ height:220px; }}
      .hero-left {{ background: transparent; padding: 8px 4px; border-radius: 0; }}
    }}
    </style>
    """
    return css

st.markdown(build_css(S()), unsafe_allow_html=True)

# ---------------- SIDEBAR: SETTINGS ----------------
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    # Theme
    theme_choice = st.radio("Theme mode", options=["Light", "Dark"], index=0 if S().get("theme_mode","Light")=="Light" else 1)
    if theme_choice != S().get("theme_mode"):
        S()["theme_mode"] = theme_choice
        if S().get("auto_save"):
            save_settings(S())

    # Accent color
    acc = st.color_picker("Accent color", value=S().get("accent","#0b6cff"))
    if acc != S().get("accent"):
        S()["accent"] = acc
        if S().get("auto_save"):
            save_settings(S())

    S()["show_timestamps"] = st.checkbox("Show timestamps", value=S().get("show_timestamps", True))

    st.markdown("---")
    st.markdown("**Gallery layout**")
    S()["grid_columns"] = st.slider("Grid columns", min_value=2, max_value=6, value=S().get("grid_columns",4))
    S()["thumb_size"] = st.selectbox("Thumbnail size", options=["small","medium","large"], index=["small","medium","large"].index(S().get("thumb_size","medium")))

    st.markdown("---")
    st.markdown("**Hero & Pings**")
    S()["autoplay_hero"] = st.checkbox("Autoplay featured strip", value=S().get("autoplay_hero", False))
    S()["autoplay_interval"] = st.number_input("Autoplay interval (seconds)", min_value=2, max_value=30, value=S().get("autoplay_interval",5))
    S()["auto_ping_interval"] = st.number_input("Auto-ping (minutes, 0=off)", min_value=0, max_value=60, value=S().get("auto_ping_interval",0))
    S()["webhook_url"] = st.text_input("Webhook URL (optional)", value=S().get("webhook_url",""), placeholder="https://hooks.example.com/...")

    if st.button("Test Webhook"):
        url = S().get("webhook_url","").strip()
        if not url:
            st.error("Enter webhook URL first.")
        else:
            payload = {"source":"ARCHIPELAGO","time":datetime.now().isoformat(), "message":"Test ping"}
            try:
                resp = requests.post(url, json=payload, timeout=6)
                st.success(f"Webhook responded: {resp.status_code}")
                st.write(resp.text[:200])
            except Exception as e:
                st.error(f"Webhook call failed: {e}")

    st.markdown("---")
    S()["auto_save"] = st.checkbox("Auto-save settings", value=S().get("auto_save", False))

    if st.button("Save settings"):
        ok = save_settings(S())
        if ok:
            st.success("Settings saved.")
        else:
            st.error("Failed to save settings.")

    if st.button("Reset to defaults"):
        st.session_state["app_settings"] = DEFAULT_SETTINGS.copy()
        save_settings(st.session_state["app_settings"])
        safe_rerun()

# Reapply CSS (reflect any change)
st.markdown(build_css(S()), unsafe_allow_html=True)

# ---------------- AUTH ----------------
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

def login_page():
    c1, c2 = st.columns([1,1])
    with c1:
        st.image("https://images.unsplash.com/photo-1511818966892-d7d671e672a2?q=80&w=1200&auto=format&fit=crop", use_container_width=True)
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align:left;color:var(--text);font-weight:900'>ARCHIPELAGO</h1>", unsafe_allow_html=True)
        st.write("Authentication Required")
        st.write("---")
        password = st.text_input("Enter passkey", type="password")
        if st.button("Enter studio"):
            if password == SHARED_PASSWORD:
                st.session_state['authenticated'] = True
                safe_rerun()
            else:
                st.error("Invalid passkey")

# ---------------- MAIN APP ----------------
def main_app():
    # top status and ping
    left, right = st.columns([3,1])
    with left:
        st.markdown(f"<small style='color:var(--subtitle)'>Status: <strong style='color:var(--accent)'>Live</strong></small>", unsafe_allow_html=True)
    with right:
        if st.button("🔔 Ping"):
            st.balloons()
            st.success(f"Ping sent — {datetime.now().strftime('%H:%M:%S')}")
            url = S().get("webhook_url","").strip()
            if url:
                payload = {"source":"ARCHIPELAGO","time":datetime.now().isoformat(), "message":"Manual ping"}
                try:
                    requests.post(url, json=payload, timeout=6)
                except Exception:
                    st.warning("Webhook ping failed (check URL)")

    # HERO: left text box (semi-opaque) + right image
    c1, c2 = st.columns([1.4, 1])
    with c1:
        st.markdown("<div class='hero-left'>", unsafe_allow_html=True)
        st.markdown("<div class='hero-tag'>CURATED • SELECTED</div>", unsafe_allow_html=True)
        st.markdown("<div class='hero-title'>ARCHITECTURE THAT BREATHES</div>", unsafe_allow_html=True)
        st.markdown("<div class='hero-sub'>Bright, image-first gallery for studio work. Upload high-res renders, organize by project, preview collections with clarity.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        hero_path = None
        sections = get_sections()
        if "Selected Works" in sections:
            imgs = get_images_in_section("Selected Works")
            if imgs:
                hero_path = imgs[0]['path']
        if hero_path:
            try:
                hero_img = Image.open(hero_path)
                st.markdown("<div class='hero-image'>", unsafe_allow_html=True)
                st.image(hero_img, use_column_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception:
                st.markdown("<div class='hero-image'><img src='https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070&auto=format&fit=crop' style='width:100%;height:100%;object-fit:cover;'></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='hero-image'><img src='https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070&auto=format&fit=crop' style='width:100%;height:100%;object-fit:cover;'></div>", unsafe_allow_html=True)

    st.markdown("---")

    # Upload UI
    st.subheader("Upload New Masterpieces")
    sections = get_sections()
    if not sections:
        init_storage()
        sections = get_sections()

    col_a, col_b = st.columns([1,3])
    with col_a:
        target_section = st.selectbox("Target Category", sections)
    with col_b:
        with st.form("upload_form", clear_on_submit=True):
            files = st.file_uploader("Select files (PNG/JPG/JPEG/WEBP)", accept_multiple_files=True, type=['png','jpg','jpeg','webp'])
            submitted = st.form_submit_button("Add to Archive")
            if submitted and files:
                for f in files:
                    save_file(f, target_section)
                st.success("Uploaded")
                if S().get("auto_save"):
                    save_settings(S())
                # no forced rerun

    st.markdown("---")

    # Featured strip
    st.subheader("Featured Projects")
    featured = []
    for s in sections:
        imgs = get_images_in_section(s)
        if imgs:
            featured.append((s, imgs[0]))
        if len(featured) >= 12:
            break

    if featured:
        sc_html = "<div class='scroller' id='hero-scroll'>"
        for sec, img in featured:
            b64 = file_to_base64(img['path'])
            if b64:
                fname = img['filename'].rsplit('.',1)[0]
                sc_html += f"<div class='project-card'><img src='data:image/jpeg;base64,{b64}' /><div class='project-meta'><strong style='color:var(--text)'>{fname}</strong><div style='color:var(--subtitle);font-size:13px;margin-top:6px'>Collection: {sec}</div></div></div>"
        sc_html += "</div>"
        st.markdown(sc_html, unsafe_allow_html=True)

        if S().get("autoplay_hero", False):
            interval_ms = max(2000, int(S().get("autoplay_interval",5)) * 1000)
            js = f"""
            <script>
            (function() {{
                const scroller = document.getElementById('hero-scroll');
                if (!scroller) return;
                let pos = 0;
                const step = 300;
                function autoScroll() {{
                    if (!scroller) return;
                    pos += step;
                    if (pos >= scroller.scrollWidth - scroller.clientWidth) {{
                        pos = 0;
                    }}
                    scroller.scrollTo({{ left: pos, behavior: 'smooth' }});
                }}
                let timer = setInterval(autoScroll, {interval_ms});
                window._arch_autoscroll = timer;
            }})();
            </script>
            """
            st.markdown(js, unsafe_allow_html=True)
    else:
        st.info("No featured projects yet.")

    st.markdown("---")

    # Gallery grid
    st.subheader("Browse Collections")
    cols_num = S().get("grid_columns", 4)
    thumb_size = S().get("thumb_size", "medium")

    if sections:
        for sec in sections:
            st.markdown(f"### {sec}")
            images = get_images_in_section(sec)
            if not images:
                st.write("No images yet.")
                continue

            gallery_cols = st.columns([1]*cols_num)
            for idx, im in enumerate(images):
                col_idx = idx % cols_num
                with gallery_cols[col_idx]:
                    st.markdown("<div class='gallery-card'>", unsafe_allow_html=True)
                    try:
                        img = Image.open(im['path'])
                        st.image(img, use_column_width=True)
                    except Exception:
                        st.markdown("<div style='height:160px;background:#f4f4f4;border-radius:6px;'></div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown(f"**{im['filename']}**")
                    if S().get("show_timestamps"):
                        st.caption(f"{im['date']} • {im['time']}")
                    else:
                        st.caption("")

                    c1, c2 = st.columns([1,1])
                    with c1:
                        try:
                            with open(im['path'], "rb") as f:
                                st.download_button("⬇ Save", data=f, file_name=im['filename'], mime="image/jpeg", key="dl_"+im['path'])
                        except Exception:
                            st.button("⬇", key="dl_hold_"+im['path'])
                    with c2:
                        if st.button("🗑 Delete", key="del_"+im['path']):
                            delete_image(im['path'])
                            # UI updates on interaction (no forced rerun)
    else:
        st.error("No sections found. Create one from the sidebar.")

    st.markdown("---")
    st.markdown(f"**Runtime:** Streamlit {st.__version__} — Settings saved: {'yes' if os.path.exists(SETTINGS_FILE) else 'no'}")

# ---------------- RUN ----------------
init_storage()
if not st.session_state['authenticated']:
    login_page()
else:
    main_app()
