import streamlit as st
import os
from datetime import datetime
from PIL import Image
import base64

# --- CONFIGURATION ---
SHARED_PASSWORD = "ARCH"
BASE_STORAGE_FOLDER = "gallery_storage"
PAGE_TITLE = "ARCHIPELAGO | STUDIO"
PAGE_ICON = "🏙"

# --- PAGE SETUP ---
st.set_page_config(layout="wide", page_title=PAGE_TITLE, page_icon=PAGE_ICON)

# --- Session defaults for settings ---
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Light"  # "Light" or "Dark"
if "accent" not in st.session_state:
    st.session_state["accent"] = "#0b6cff"
if "show_timestamps" not in st.session_state:
    st.session_state["show_timestamps"] = True

# ---------- Helper: generate CSS based on settings ----------
def get_dynamic_css(theme_mode: str, accent_color: str) -> str:
    # Light defaults
    bg = "#fafafa"
    text = "#222"
    sidebar_bg = "#ffffff"
    sidebar_text = "#111"
    card_bg = "#ffffff"
    subtle_border = "#e6e6e6"
    shadow = "0 12px 30px rgba(17,17,17,0.06)"

    if theme_mode == "Dark":
        bg = "#0f1113"
        text = "#ffffff"
        sidebar_bg = "#0b0c0d"
        sidebar_text = "#f2f2f2"
        card_bg = "#121214"
        subtle_border = "rgba(255,255,255,0.06)"
        shadow = "0 12px 30px rgba(0,0,0,0.75)"

    # Build CSS string
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700;900&display=swap');

    :root {{
      --bg: {bg};
      --text: {text};
      --accent: {accent_color};
      --sidebar-bg: {sidebar_bg};
      --sidebar-text: {sidebar_text};
      --card-bg: {card_bg};
      --subtle-border: {subtle_border};
      --shadow: {shadow};
    }}

    html, body, [class*="css"] {{
      font-family: 'Montserrat', sans-serif;
      background: var(--bg) !important;
      color: var(--text) !important;
    }}
    .block-container {{
      padding-top: 1.5rem;
      padding-bottom: 3.5rem;
    }}

    /* HERO */
    .hero-wrap {{ display:flex; gap:28px; align-items:center; justify-content:space-between; margin-bottom:28px; }}
    .hero-left{{ flex:1.4; padding:18px 8px; }}
    .hero-tag{{ color:var(--accent); font-weight:700; font-size:12px; letter-spacing:2px; text-transform:uppercase; margin-bottom:8px; }}
    .hero-title{{ font-size:48px; line-height:1.02; margin:0 0 6px 0; font-weight:900; color:var(--text); text-transform:uppercase; }}
    .hero-sub{{ color: rgba( {int(text[1:3],16) if text.startswith('#') else 0}, {int(text[3:5],16) if text.startswith('#') else 0}, {int(text[5:7],16) if text.startswith('#') else 0}, 0.75 ); margin-top:8px; max-width:720px; font-size:15px; }}

    /* Buttons */
    .hero-ctas{{ margin-top:18px; display:flex; gap:10px; }}
    .btn-primary {{
      background: linear-gradient(90deg,var(--accent),#3ab0ff);
      color:white; padding:10px 16px; border-radius:8px; border:none; font-weight:700; cursor:pointer;
    }}
    .btn-ghost {{
      background: transparent; border: 1px solid var(--subtle-border); color:var(--text); padding:9px 14px; border-radius:8px;
    }}

    /* Hero image */
    .hero-image {{
      flex:1; border-radius:10px; overflow:hidden; border:1px solid var(--subtle-border); box-shadow: var(--shadow); height:320px; display:flex; align-items:center; justify-content:center;
    }}
    .hero-image img{{ width:100%; height:100%; object-fit:cover; display:block; }}

    /* Featured scroller */
    .scroller{{ display:flex; gap:14px; overflow-x:auto; padding:10px 0; scroll-snap-type:x mandatory; }}
    .project-card{{ min-width:260px; background:var(--card-bg); border-radius:10px; overflow:hidden; border:1px solid var(--subtle-border); box-shadow:var(--shadow); scroll-snap-align:center; }}
    .project-card img{{ width:100%; height:160px; object-fit:cover; display:block; }}
    .project-meta{{ padding:10px; color:var(--text); }}

    /* Gallery grid */
    .gallery-grid{{ display:grid; grid-template-columns:repeat(auto-fill, minmax(220px, 1fr)); gap:18px; margin-top:10px; }}
    .gallery-card{{ background:var(--card-bg); border-radius:10px; padding:8px; border:1px solid var(--subtle-border); box-shadow:var(--shadow); transition:transform .14s ease; }}
    .gallery-card:hover{{ transform:translateY(-6px); }}

    /* Sidebar (darkened) */
    section[data-testid="stSidebar"] {{
      background-color: #0b0c0d !important;
      color: white !important;
      border-right: 1px solid rgba(255,255,255,0.04) !important;
    }}
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] .stText {{
      color: white !important;
    }}

    /* Sidebar buttons & inputs */
    section[data-testid="stSidebar"] .stButton button {{
      background-color: transparent !important;
      border: 1px solid rgba(255,255,255,0.12) !important;
      color: white !important;
    }}
    section[data-testid="stSidebar"] .stTextInput input, section[data-testid="stSidebar"] .stSelect select {{
      background: #0f1113 !important;
      color: white !important;
      border: 1px solid rgba(255,255,255,0.06) !important;
    }}

    /* Make global text white in dark mode for main area */
    {"body, .css-1d391kg, .block-container, .stApp { color: white !important; }" if theme_mode == "Dark" else ""}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
      border-bottom: 2px solid var(--subtle-border) !important;
      margin-bottom: 25px;
    }}
    .stTabs [data-baseweb="tab"] {{
      color: #777 !important;
      font-weight: 600 !important;
      background-color: transparent !important;
    }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
      color: var(--text) !important;
      border-bottom: 3px solid var(--text) !important;
    }}

    /* Hide default Streamlit elements lightly */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
    """
    return css

# ---------- Backend (unchanged) ----------
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
    images=[]
    section_path = os.path.join(BASE_STORAGE_FOLDER, section)
    if os.path.exists(section_path):
        for root, dirs, files in os.walk(section_path):
            for file in files:
                if file.lower().endswith(('.png','.jpg','.jpeg')):
                    full_path = os.path.join(root,file)
                    try:
                        folder_date = os.path.basename(root)
                        time_stamp = file.split('_')[0].replace(':','-').replace('-',':')  # safe transform
                    except:
                        folder_date="Unknown"; time_stamp=""
                    images.append({"path":full_path,"filename":file,"date":folder_date,"time":time_stamp,"sort_key":f"{folder_date}{time_stamp}"})
    return sorted(images, key=lambda x: x['sort_key'], reverse=True)

def file_to_base64(path):
    try:
        with open(path,"rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

# ---------- UI & Settings ----------
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# Sidebar top: Settings icon & controls
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    # Theme select
    theme_choice = st.radio("Theme mode", options=["Light", "Dark"], index=0 if st.session_state["theme_mode"]=="Light" else 1)
    if theme_choice != st.session_state["theme_mode"]:
        st.session_state["theme_mode"] = theme_choice
        # Force immediate rerun so CSS will update
        st.experimental_rerun()

    # Accent color
    acc = st.color_picker("Accent color", value=st.session_state["accent"])
    if acc != st.session_state["accent"]:
        st.session_state["accent"] = acc
        st.experimental_rerun()

    # Convenience options
    show_ts = st.checkbox("Show timestamps", value=st.session_state["show_timestamps"])
    st.session_state["show_timestamps"] = show_ts

    st.markdown("---")
    st.markdown("**Quick actions**")
    if st.button("Clear cache (reload)"):
        st.experimental_rerun()
    st.write("")
    st.markdown("")

# Insert dynamic CSS
st.markdown(get_dynamic_css(st.session_state["theme_mode"], st.session_state["accent"]), unsafe_allow_html=True)

# ---------- Main app UI (keeps previous structure) ----------
def login_page():
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image("https://images.unsplash.com/photo-1511818966892-d7d671e672a2?q=80&w=1000&auto=format&fit=crop", use_container_width=True)
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        # Make title white in sidebar dark + adjust color in main via CSS
        st.markdown("<h1 style='text-align: left; color: var(--text); letter-spacing: -1px;'>ARCHIPELAGO.</h1>", unsafe_allow_html=True)
        st.write("AUTHENTICATION REQUIRED")
        st.write("---")
        password = st.text_input("ENTER PASSKEY", type="password")
        if st.button("ENTER STUDIO"):
            if password == SHARED_PASSWORD:
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("ACCESS DENIED")

def main_app():
    # top controls
    col_left, col_right = st.columns([3,1])
    with col_left:
        st.markdown("<small style='color:var(--text)'>Status: <strong>Live</strong></small>", unsafe_allow_html=True)
    with col_right:
        if st.button("🔔 Ping / Wake"):
            st.balloons()
            st.success(f"Ping sent — {datetime.now().strftime('%H:%M:%S')}")

    # HERO
    c1, c2 = st.columns([1.4,1])
    with c1:
        st.markdown("<div class='hero-left'>", unsafe_allow_html=True)
        st.markdown("<div class='hero-tag'>CURATED • SELECTED</div>", unsafe_allow_html=True)
        st.markdown("<div class='hero-title'>ARCHITECTURE THAT BREATHES</div>", unsafe_allow_html=True)
        st.markdown("<div class='hero-sub'>Bright, image-first gallery for studio work. Upload high-res renders, organize by project, preview collections with clarity.</div>", unsafe_allow_html=True)
        st.markdown("<div class='hero-ctas'><button class='btn-primary'>Browse Collections</button><button class='btn-ghost'>Upload</button></div>", unsafe_allow_html=True)
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
                img = Image.open(hero_path)
                st.markdown("<div class='hero-image'>", unsafe_allow_html=True)
                st.image(img, use_column_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception:
                st.markdown("<div class='hero-image'><img src='https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070&auto=format&fit=crop' style='width:100%;height:100%;object-fit:cover;'></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='hero-image'><img src='https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070&auto=format&fit=crop' style='width:100%;height:100%;object-fit:cover;'></div>", unsafe_allow_html=True)

    st.markdown("---")

    # sidebar controls (kept minimal because Settings are at the top)
    with st.sidebar:
        st.markdown("")  # space placeholder

    # upload area
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
            files = st.file_uploader("", accept_multiple_files=True, type=['png','jpg','jpeg'])
            submitted = st.form_submit_button("Add to Archive")
            if submitted and files:
                for f in files:
                    save_file(f, target_section)
                st.success("Uploaded")
                st.rerun()

    st.markdown("---")

    # Featured strip
    st.subheader("Featured Projects")
    featured = []
    for s in sections:
        imgs = get_images_in_section(s)
        if imgs:
            featured.append((s, imgs[0]))
        if len(featured) >= 8:
            break

    if featured:
        sc_html = "<div class='scroller'>"
        for sec, img in featured:
            b64 = file_to_base64(img['path'])
            if b64:
                sc_html += "<div class='project-card'><img src='data:image/jpeg;base64," + b64 + "' /><div class='project-meta'><strong style='color:var(--text)'>" + img['filename'].rsplit('.',1)[0] + "</strong><div style='color:var(--text);font-size:13px;margin-top:6px'>Collection: " + sec + "</div></div></div>"
        sc_html += "</div>"
        st.markdown(sc_html, unsafe_allow_html=True)
    else:
        st.info("No featured projects yet.")

    st.markdown("---")

    # Gallery
    st.subheader("Browse Collections")
    if sections:
        for sec in sections:
            st.markdown(f"### {sec}")
            images = get_images_in_section(sec)
            if not images:
                st.write("No images yet.")
                continue

            st.markdown("<div class='gallery-grid'>", unsafe_allow_html=True)
            for im in images:
                st.markdown("<div class='gallery-card'>", unsafe_allow_html=True)
                try:
                    thumb = Image.open(im['path'])
                    st.image(thumb, use_column_width=True)
                except:
                    st.markdown("<div style='height:140px;background:#f4f4f4;border-radius:6px;'></div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # Filename and optional timestamp
                st.markdown(f"**{im['filename']}**")
                if st.session_state["show_timestamps"]:
                    st.caption(f"{im['date']} • {im['time']}")
                else:
                    st.caption("")

                c1, c2 = st.columns([1,1])
                with c1:
                    try:
                        with open(im['path'],"rb") as f:
                            st.download_button("⬇ Save", data=f, file_name=im['filename'], mime="image/jpeg", key="dl_"+im['path'])
                    except:
                        st.button("⬇", key="dl_hold_"+im['path'])
                with c2:
                    if st.button("🗑 Delete", key="del_"+im['path']):
                        delete_image(im['path'])
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("No sections found. Create one from the sidebar.")

# ---------- Run ----------
if not st.session_state['authenticated']:
    login_page()
else:
    main_app()
