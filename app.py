import streamlit as st
import os
from datetime import datetime
from PIL import Image
import base64
import io

# --- CONFIGURATION ---
SHARED_PASSWORD = "ARCH"
BASE_STORAGE_FOLDER = "gallery_storage"
PAGE_TITLE = "ARCHIPELAGO | STUDIO"
PAGE_ICON = "🏙"

# --- PAGE SETUP ---
st.set_page_config(layout="wide", page_title=PAGE_TITLE, page_icon=PAGE_ICON)

# --- BRIGHT "ARCHIPELAGO" THEME CSS ---
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700;900&display=swap');

:root{
  --bg: #ffffff;
  --muted: #444444;
  --accent: #0b6cff;
  --card: #ffffff;
  --shadow: 0 10px 30px rgba(17,17,17,0.06);
}

html, body, [class*="css"] {
  font-family: 'Montserrat', sans-serif;
  background: var(--bg);
  color: var(--muted);
}

/* block container spacing */
.block-container {
  padding-top: 2.5rem;
  padding-bottom: 4rem;
}

/* Hero */
.hero {
  display: flex;
  gap: 24px;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
}
.hero-left {
  flex: 1.3;
}
.hero-tag {
  font-size: 12px;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 700;
  margin-bottom: 10px;
}
.hero-title {
  font-size: 52px;
  line-height: 1.02;
  margin: 0;
  color: #0b0b0b;
  font-weight: 900;
}
.hero-sub {
  margin-top: 12px;
  color: #555;
  font-size: 16px;
  max-width: 720px;
}

/* CTA */
.hero-cta {
  margin-top: 18px;
  display:flex;
  gap:10px;
}
.btn-primary {
  background: linear-gradient(90deg,var(--accent),#3ab0ff);
  color: white;
  padding:10px 16px;
  border-radius: 6px;
  border: none;
  font-weight: 700;
  cursor:pointer;
}
.btn-light {
  background: transparent;
  border: 1px solid #ddd;
  color: var(--muted);
  padding:10px 14px;
  border-radius:6px;
}

/* Hero image strip (horizontal scroll) */
.hero-strip {
  flex: 1;
  display: block;
  height: 240px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
  border-radius: 10px;
  border: 1px solid #eee;
  box-shadow: var(--shadow);
}
.hero-strip .strip-inner {
  display:flex;
  gap: 10px;
  padding: 10px;
  align-items: center;
}
.strip-card {
  min-width: 420px;
  height: 220px;
  border-radius: 8px;
  overflow: hidden;
  flex: 0 0 auto;
  scroll-snap-align: center;
  background: #fafafa;
  border: 1px solid #f0f0f0;
}
.strip-card img {
  width:100%;
  height:100%;
  object-fit: cover;
  display:block;
}

/* Featured scroller (smaller cards) */
.scroller {
  display:flex;
  gap:14px;
  overflow-x:auto;
  padding:12px 2px;
  scroll-snap-type: x mandatory;
}
.project-card {
  min-width: 260px;
  background: var(--card);
  border-radius:8px;
  overflow:hidden;
  border: 1px solid #f3f3f3;
  box-shadow: var(--shadow);
  scroll-snap-align: center;
}
.project-card img { width:100%; height:160px; object-fit:cover; display:block; }

/* Gallery card */
.gallery-card {
  background: #fff;
  border-radius: 8px;
  padding: 8px;
  border: 1px solid #f2f2f2;
  box-shadow: var(--shadow);
  transition: transform .14s ease;
}
.gallery-card:hover { transform: translateY(-6px); }

/* small screens */
@media (max-width:900px) {
  .hero { flex-direction: column; align-items:flex-start; gap:14px; }
  .hero-strip { width:100%; order: -1; }
  .hero-left { width:100%; }
  .hero-title { font-size:36px; }
  .strip-card { min-width:320px; height:180px; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------- Backend logic (kept intact) ----------

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
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    full_path = os.path.join(root, file)
                    try:
                        folder_date = os.path.basename(root)
                        time_stamp = file.split('_')[0].replace('-', ':')
                    except:
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

# ---------- Image helper for embedding local developer-provided images ----------
def file_to_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

# developer-provided images (these live in the container at /mnt/data/)
DEV_IMAGE_PATHS = [
    "/mnt/data/pexels-borja-lopez-1059078.jpg",
    "/mnt/data/pexels-pixabay-262367.jpg",
    "/mnt/data/pexels-scottwebb-137594.jpg",
]

def load_dev_images():
    imgs = []
    for p in DEV_IMAGE_PATHS:
        b64 = file_to_base64(p)
        if b64:
            imgs.append(("data:image/jpeg;base64," + b64, os.path.basename(p)))
    return imgs

# ---------- Auth ----------
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

init_storage()

def login_page():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='text-align:center'><h3 style='margin:0'>ARCHIPELAGO</h3><div style='color:#666'>Studio Archive</div></div>", unsafe_allow_html=True)
        st.write("---")
        password = st.text_input("Enter Passkey", type="password")
        if st.button("ENTER STUDIO"):
            if password == SHARED_PASSWORD:
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("Access Denied")

# ---------- Main UI ----------
def main_app():
    # top hero area: left text, right scrollable strip
    dev_imgs = load_dev_images()  # list of (data_uri, filename)

    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown("<div class='hero-left'>", unsafe_allow_html=True)
        st.markdown("<div class='hero-tag'>CURATED • SELECTED</div>", unsafe_allow_html=True)
        st.markdown("<h1 class='hero-title'>Architecture that breathes.</h1>", unsafe_allow_html=True)
        st.markdown("<div class='hero-sub'>A bright, image-first gallery for your studio work — upload high-res renders and drawings, organize by project, and preview collections with a tactile scroll experience.</div>", unsafe_allow_html=True)
        st.markdown("<div class='hero-cta'><button class='btn-primary' onclick=''>Browse Collections</button><button class='btn-light' onclick=''>Upload</button></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # right strip: horizontal scroll of the provided images (fall back to recent gallery images)
    with c2:
        st.markdown("<div class='hero-strip'><div class='strip-inner'>", unsafe_allow_html=True)
        if dev_imgs:
            for data_uri, fname in dev_imgs:
                st.markdown("<div class='strip-card'><img src='" + data_uri + "' alt='" + fname + "'/></div>", unsafe_allow_html=True)
        else:
            # fallback: show first images from Stored gallery (if any)
            sections = get_sections()
            shown = 0
            for sec in sections:
                imgs = get_images_in_section(sec)
                for im in imgs:
                    if shown >= 3:
                        break
                    try:
                        b64 = file_to_base64(im['path'])
                        if b64:
                            data_uri = "data:image/jpeg;base64," + b64
                            st.markdown("<div class='strip-card'><img src='" + data_uri + "' alt='' /></div>", unsafe_allow_html=True)
                            shown += 1
                    except:
                        continue
                if shown >= 3:
                    break
            if shown == 0:
                st.markdown("<div class='strip-card' style='display:flex;align-items:center;justify-content:center;color:#777'>No hero images found</div>", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    # Sidebar controls
    with st.sidebar:
        st.header("Controls")
        with st.expander("➕ Create Category"):
            new_name = st.text_input("Category Name")
            if st.button("Create Category"):
                if create_new_section(new_name):
                    st.success("Created")
                    st.rerun()
        st.markdown("---")
        if st.button("LOGOUT"):
            st.session_state['authenticated'] = False
            st.rerun()

    # Upload area
    st.subheader("Upload New Masterpieces")
    sections = get_sections()
    if not sections:
        init_storage()
        sections = get_sections()

    col_a, col_b = st.columns([1, 3])
    with col_a:
        target_section = st.selectbox("Target Category", sections)
    with col_b:
        with st.form("upload_form", clear_on_submit=True):
            files = st.file_uploader("", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
            submitted = st.form_submit_button("Add to Archive")
            if submitted and files:
                for f in files:
                    save_file(f, target_section)
                st.success("Uploaded")
                st.rerun()

    st.markdown("---")

    # Featured horizontal scroller (from each section show one)
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
                sc_html += "<div class='project-card'><img src='data:image/jpeg;base64," + b64 + "'/><div style='padding:10px'><strong style='font-size:14px;color:#111'>" + (img['filename'].split('.')[0]) + "</strong><div style='color:#666;font-size:13px;margin-top:6px'>Collection: " + sec + "</div></div></div>"
        sc_html += "</div>"
        st.markdown(sc_html, unsafe_allow_html=True)
    else:
        st.info("No featured projects yet. Upload to populate.")

    st.markdown("---")

    # Gallery tabs
    st.subheader("Browse Collections")
    if sections:
        tabs = st.tabs(sections)
        for i, sec in enumerate(sections):
            with tabs[i]:
                images = get_images_in_section(sec)
                if not images:
                    st.write("No images yet in this category.")
                else:
                    cols = st.columns(4)
                    for idx, im in enumerate(images):
                        col_idx = idx % 4
                        with cols[col_idx]:
                            st.markdown("<div class='gallery-card'>", unsafe_allow_html=True)
                            try:
                                img = Image.open(im['path'])
                                st.image(img, use_column_width=True)
                            except:
                                st.markdown("<div style='height:140px;background:#f4f4f4;border-radius:6px;'></div>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                            st.markdown(f"**{im['filename']}**")
                            st.caption(f"{im['date']} • {im['time']}")
                            c1, c2 = st.columns(2)
                            with c1:
                                try:
                                    with open(im['path'], "rb") as file:
                                        st.download_button("⬇ Save", data=file, file_name=im['filename'], mime="image/jpeg", key="dl_"+im['path'])
                                except:
                                    st.button("⬇", key="dl_hold_"+im['path'])
                            with c2:
                                if st.button("🗑 Delete", key="del_"+im['path']):
                                    delete_image(im['path'])
                                    st.rerun()
    else:
        st.error("No sections found. Create one from the sidebar.")

# ---------- Run ----------
if not st.session_state['authenticated']:
    login_page()
else:
    main_app()
