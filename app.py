# app.py
import streamlit as st
import os
import json
import requests
from datetime import datetime
from PIL import Image
import base64
import sys

# ------------------- Configuration -------------------
SHARED_PASSWORD = "ARCH"
BASE_STORAGE_FOLDER = "gallery_storage"
PAGE_TITLE = "ARCHIPELAGO | STUDIO"
PAGE_ICON = "🏙"
SETTINGS_FILE = os.path.join(BASE_STORAGE_FOLDER, "app_settings.json")

# ------------------- Page setup -------------------
st.set_page_config(layout="wide", page_title=PAGE_TITLE, page_icon=PAGE_ICON)

# ------------------- Safe rerun helper -------------------
def safe_rerun():
    """
    Attempt to rerun cleanly; if Streamlit runtime lacks rerun API,
    fall back to st.stop() to avoid AttributeError.
    """
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

# ------------------- Default settings -------------------
DEFAULT_SETTINGS = {
    "theme_mode": "Light",            # "Light" or "Dark"
    "accent": "#0b6cff",
    "show_timestamps": True,
    "grid_columns": 4,                # 2-6
    "thumb_size": "medium",           # small|medium|large
    "autoplay_hero": False,
    "autoplay_interval": 5,           # secs
    "auto_ping_interval": 0,          # minutes, 0 disabled
    "webhook_url": "",
    "auto_save": False
}

# ------------------- Ensure storage -------------------
if not os.path.exists(BASE_STORAGE_FOLDER):
    os.makedirs(BASE_STORAGE_FOLDER)

# ------------------- Settings persistence -------------------
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            cfg = DEFAULT_SETTINGS.copy()
            cfg.update(data)
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

# ------------------- Session-state settings -------------------
if "app_settings" not in st.session_state:
    st.session_state["app_settings"] = load_settings()

def S():
    return st.session_state["app_settings"]

# ------------------- File / gallery utilities (unchanged behavior) -------------------
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
    if clean_name:
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

# ------------------- Dynamic CSS generator -------------------
def build_css(settings):
    theme = settings.get("theme_mode", "Light")
    accent = settings.get("accent", "#0b6cff")

    if theme == "Dark":
        bg = "#0b0c0d"
        page_bg = "#0f1113"
        text = "#FFFFFF"
        subtitle = "rgba(255,255,255,0.85)"
        card_bg = "#0f1113"
        border = "rgba(255,255,255,0.06)"
        shadow = "0 20px 40px rgba(0,0,0,0.7)"
        hero_overlay = "linear-gradient(rgba(0,0,0,0.35), rgba(0,0,0,0.35))"
    else:
        bg = "#ffffff"
        page_bg = "#fafafa"
        text = "#0b0b0b"
        subtitle = "rgba(17,17,17,0.75)"
        card_bg = "#ffffff"
        border = "#e8e8e8"
        shadow = "0 12px 30px rgba(17,17,17,0.06)"
        hero_overlay = "linear-gradient(rgba(255,255,255,0.35), rgba(255,255,255,0.35))"

    # Keep hero text luminous for readability on any image
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700;900&display=swap');

    :root {{
        --bg: {page_bg};
        --surface: {bg};
        --text: {text};
        --subtitle: {subtitle};
        --accent: {accent};
        --card-bg: {card_bg};
        --border: {border};
        --shadow: {shadow};
    }}

    html, body, [class*="css"] {{
        font-family: 'Montserrat', sans-serif;
        background: var(--bg) !important;
        color: var(--text) !important;
    }}

    .block-container {{
        padding-top: 1.6rem;
        padding-bottom: 3.5rem;
    }}

    /* HERO */
    .hero-wrap {{ display:flex; gap:24px; align-items:center; justify-content:space-between; margin-bottom:28px; }}
    .hero-left{{ flex:1.4; padding: 12px 8px; }}
    .hero-tag{{ color: var(--accent); font-weight:700; font-size:12px; letter-spacing:2px; text-transform:uppercase; margin-bottom:8px; }}
    .hero-title{{ font-size:56px; line-height:1.02; margin:0; font-weight:900; color:var(--text); text-transform:uppercase; text-shadow: 0 6px 20px rgba(0,0,0,0.25); }}
    .hero-sub{{ color: var(--subtitle); margin-top:12px; max-width:760px; font-size:16px; }}

    /* hero image panel */
    .hero-image {{
        flex:1;
        border-radius:12px;
        overflow:hidden;
        border: 1px solid var(--border);
        box-shadow: var(--shadow);
        height:360px;
        position:relative;
        display:flex;
        align-items:center;
        justify-content:center;
    }}
    .hero-image img {{ width:100%; height:100%; object-fit:cover; display:block; filter: saturate(1.05) contrast(1.03); }}
    .hero-image::after {{
        content:"";
        position:absolute;
        inset:0;
        background: {hero_overlay};
        pointer-events:none;
    }}
    .hero-title, .hero-sub {{ position:relative; z-index:4; }}

    /* featured scroller */
    .scroller {{ display:flex; gap:14px; overflow-x:auto; padding:10px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch; }}
    .project-card {{ min-width:260px; background:var(--card-bg); border-radius:10px; overflow:hidden; border:1px solid var(--border); box-shadow:var(--shadow); scroll-snap-align:center; }}
    .project-card img {{ width:100%; height:160px; object-fit:cover; display:block; }}
    .project-meta {{ padding:10px; color:var(--text); }}

    /* gallery */
    .gallery-grid {{ display:grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap:18px; margin-top:12px; }}
    .gallery-card {{ background:var(--card-bg); border-radius:10px; padding:8px; border:1px solid var(--border); box-shadow:var(--shadow); transition: transform .14s ease, box-shadow .14s ease; }}
    .gallery-card:hover {{ transform: translateY(-8px); box-shadow: 0 28px 60px rgba(10,10,10,0.08); }}

    /* bright, radiant headings */
    h1, h2, h3, h4, h5, .stMarkdown h1 {{ color: var(--text) !important; }}

    /* sidebar: dark theme intentionally */
    section[data-testid="stSidebar"] {{
        background: #0b0c0d !important;
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
        border-radius: 6px !important;
        padding: 6px 8px !important;
    }}

    /* buttons look */
    .btn-primary-custom {{
        background: linear-gradient(90deg, var(--accent), #3ab0ff);
        color: white;
        padding: 10px 16px;
        border-radius: 8px;
        border: none;
        font-weight: 700;
        cursor: pointer;
    }}
    .btn-ghost-custom {{
        background: transparent;
        border: 1px solid var(--border);
        color: var(--text);
        padding: 9px 14px;
        border-radius: 8px;
    }}

    /* small screen adjustments */
    @media (max-width: 900px) {{
        .hero-wrap {{ flex-direction: column; gap:14px; }}
        .hero-title {{ font-size: 36px; }}
        .hero-image {{ height: 220px; }}
    }}
    </style>
    """
    return css

# ------------------- Apply CSS -------------------
st.markdown(build_css(S()), unsafe_allow_html=True)

# ------------------- Sidebar SETTINGS UI -------------------
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    # Theme:
    theme_choice = st.radio("Theme mode", options=["Light", "Dark"], index=0 if S().get("theme_mode","Light")=="Light" else 1)
    if theme_choice != S().get("theme_mode"):
        S()["theme_mode"] = theme_choice
        if S().get("auto_save"):
            save_settings(S())
        # we do not force a rerun here; Streamlit will re-execute on next interaction

    # Accent:
    acc = st.color_picker("Accent color", value=S().get("accent","#0b6cff"))
    if acc != S().get("accent"):
        S()["accent"] = acc
        if S().get("auto_save"):
            save_settings(S())

    # Show timestamps
    show_ts = st.checkbox("Show timestamps", value=S().get("show_timestamps", True))
    S()["show_timestamps"] = show_ts

    st.markdown("---")
    st.markdown("**Gallery layout**")
    cols = st.slider("Grid columns", min_value=2, max_value=6, value=S().get("grid_columns",4))
    S()["grid_columns"] = cols

    thumb = st.selectbox("Thumbnail size", options=["small","medium","large"], index=["small","medium","large"].index(S().get("thumb_size","medium")))
    S()["thumb_size"] = thumb

    st.markdown("---")
    st.markdown("**Hero & Pings**")
    autoplay = st.checkbox("Autoplay hero (scroll)", value=S().get("autoplay_hero", False))
    S()["autoplay_hero"] = autoplay

    autoplay_interval = st.number_input("Autoplay interval (seconds)", min_value=2, max_value=30, value=S().get("autoplay_interval",5))
    S()["autoplay_interval"] = int(autoplay_interval)

    st.markdown("Auto-ping (keeps some hosts awake)")
    auto_ping = st.number_input("Ping interval (minutes) — 0 = disabled", min_value=0, max_value=60, value=S().get("auto_ping_interval",0))
    S()["auto_ping_interval"] = int(auto_ping)

    webhook_url = st.text_input("Webhook URL (optional)", value=S().get("webhook_url",""), placeholder="https://hooks.example.com/...")
    S()["webhook_url"] = webhook_url

    if st.button("Test Webhook"):
        url = S().get("webhook_url","").strip()
        if not url:
            st.error("Enter a webhook URL first.")
        else:
            payload = {"source":"ARCHIPELAGO","time":datetime.now().isoformat(), "message":"Test webhook ping"}
            try:
                resp = requests.post(url, json=payload, timeout=6)
                st.success(f"Webhook responded: {resp.status_code}")
                st.write(resp.text[:200])
            except Exception as e:
                st.error(f"Webhook call failed: {e}")

    st.markdown("---")
    st.write("Persistence")
    auto_save = st.checkbox("Auto-save settings", value=S().get("auto_save", False))
    S()["auto_save"] = auto_save

    if st.button("Save settings"):
        ok = save_settings(S())
        if ok:
            st.success("Settings saved to disk.")
        else:
            st.error("Failed to save settings.")

    if st.button("Reset to defaults"):
        st.session_state["app_settings"] = DEFAULT_SETTINGS.copy()
        save_settings(st.session_state["app_settings"])
        safe_rerun()

# Re-apply CSS to reflect settings change without forcing rerun
st.markdown(build_css(S()), unsafe_allow_html=True)

# ------------------- Auth / Login UI -------------------
def login_page():
    col1, col2 = st.columns([1,1])
    with col1:
        # big attractive image
        st.image("https://images.unsplash.com/photo-1511818966892-d7d671e672a2?q=80&w=1200&auto=format&fit=crop", use_container_width=True)
    with col2:
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

# ------------------- Main App UI -------------------
def main_app():
    # Top controls row with visible status and ping
    col_left, col_right = st.columns([3,1])
    with col_left:
        st.markdown(f"<small style='color:var(--subtitle)'>Status: <strong style='color:var(--accent)'>Live</strong></small>", unsafe_allow_html=True)
    with col_right:
        if st.button("🔔 Ping / Wake"):
            st.balloons()
            st.success(f"Ping sent — {datetime.now().strftime('%H:%M:%S')}")
            url = S().get("webhook_url","").strip()
            if url:
                payload = {"source":"ARCHIPELAGO","time":datetime.now().isoformat(), "message":"Manual ping"}
                try:
                    requests.post(url, json=payload, timeout=6)
                except Exception:
                    st.warning("Webhook ping failed — check URL.")

    # Hero split: left text, right image that always has overlay for readability
    c1, c2 = st.columns([1.4, 1])
    with c1:
        st.markdown("<div class='hero-left'>", unsafe_allow_html=True)
        st.markdown("<div class='hero-tag'>CURATED • SELECTED</div>", unsafe_allow_html=True)
        st.markdown("<div class='hero-title'>ARCHITECTURE THAT BREATHES</div>", unsafe_allow_html=True)
        st.markdown("<div class='hero-sub'>Bright, image-first gallery for studio work. Upload high-res renders, organize by project, preview collections with clarity.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        # pick hero image: first image from Selected Works, fallback to curated remote
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

    # Sidebar bottom is minimal as settings are top; keep small placeholder
    with st.sidebar:
        st.markdown("")

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
                # no forced rerun — UI will update

    st.markdown("---")

    # Featured horizontal scroller (one image per section)
    st.subheader("Featured Projects")
    featured = []
    for s in sections:
        imgs = get_images_in_section(s)
        if imgs:
            featured.append((s, imgs[0]))
        if len(featured) >= 8:
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

        # If autoplay is enabled, inject a small JS snippet to auto scroll the hero scroller
        if S().get("autoplay_hero", False):
            interval_ms = max(2000, int(S().get("autoplay_interval",5))*1000)
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
                // keep reference to clear if user navigates away
                window._arch_autoscroll = timer;
            }})(); 
            </script>
            """
            st.markdown(js, unsafe_allow_html=True)
    else:
        st.info("No featured projects yet.")

    st.markdown("---")

    # Gallery grid - use selected columns and thumbnail size
    st.subheader("Browse Collections")
    cols_num = S().get("grid_columns", 4)
    thumb_size = S().get("thumb_size", "medium")

    if sections:
        for sec in sections:
            st.markdown(f"### {sec}")
            images = get_images_in_section(sec)
            if not images:
                st.write("No images yet in this collection.")
                continue

            # Create dynamic columns
            col_layout = [1] * cols_num
            gallery_cols = st.columns(col_layout)

            for idx, im in enumerate(images):
                col_idx = idx % cols_num
                with gallery_cols[col_idx]:
                    st.markdown("<div class='gallery-card'>", unsafe_allow_html=True)
                    try:
                        thumb = Image.open(im['path'])
                        st.image(thumb, use_column_width=True)
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
                            # no forced rerun
    else:
        st.error("No sections found. Create one from the sidebar.")

    # Diagnostics / info footer
    st.markdown("---")
    st.markdown(f"**Runtime info:** Streamlit {st.__version__} — safe_rerun available: {'yes' if hasattr(st, 'experimental_rerun') or hasattr(st, 'rerun') else 'no'}")
    saved = os.path.exists(SETTINGS_FILE)
    st.markdown(f"Settings persisted at: `{SETTINGS_FILE}` — saved: {'yes' if saved else 'no'}")

# ------------------- Run -------------------
init_storage()
if not st.session_state['authenticated']:
    login_page()
else:
    main_app()
