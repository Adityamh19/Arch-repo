import streamlit as st
import os
from datetime import datetime
from PIL import Image
import base64

# --- CONFIGURATION ---
SHARED_PASSWORD = "ARCH"
BASE_STORAGE_FOLDER = "gallery_storage"
PAGE_TITLE = "ROYAL ARCHIVE"
PAGE_ICON = "🏛"

# --- PAGE SETUP ---
st.set_page_config(layout="wide", page_title=PAGE_TITLE, page_icon=PAGE_ICON)

# --- CSS THEME ---
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Lato:wght@300;400;700&display=swap');

:root{
    --bg-dark: #0f1113;
    --panel: #131516;
    --muted: #bdbdbd;
    --gold: #D4AF37;
    --accent: #2fd7c1;
    --card: #17191a;
}

.stApp {
    background: linear-gradient(180deg, #0b0c0d 0%, #0f1113 100%);
    color: var(--muted);
    font-family: 'Lato', sans-serif;
    padding: 18px;
}

/* Hero */
.hero {
    position: relative;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 30px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.6);
    background: radial-gradient(circle at top left, #2b3137 0, #0b0c0d 45%);
}
.hero-inner {
    padding: 48px;
    display: flex;
    gap: 32px;
    align-items: center;
    min-height: 260px;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 40px;
    color: #ffffff;
    letter-spacing: 1px;
    margin-bottom: 8px;
}
.hero-sub {
    color: #e8e8e8;
    opacity: 0.95;
    max-width: 640px;
    line-height: 1.5;
    font-size: 15px;
}
.hero-tag {
    text-transform: uppercase;
    letter-spacing: 3px;
    font-size: 11px;
    color: var(--gold);
    margin-bottom: 6px;
}
.hero-actions {
    margin-top: 18px;
}
.btn-cta {
    background: linear-gradient(90deg, var(--gold), #f2d07a);
    border: none;
    color: #111;
    padding: 9px 16px;
    margin-right: 10px;
    border-radius: 6px;
    font-weight: 700;
    cursor: pointer;
    box-shadow: 0 6px 18px rgba(212,175,55,0.18);
    transition: transform .18s ease;
    font-size: 13px;
}
.btn-cta:hover { transform: translateY(-3px); }
.btn-outline {
    background: transparent;
    border: 1px solid rgba(255,255,255,0.12);
    color: var(--muted);
    padding: 9px 16px;
    border-radius: 6px;
    font-size: 13px;
}

/* Featured scroller */
.scroller {
    display: flex;
    overflow-x: auto;
    gap: 18px;
    padding: 12px 4px 8px 4px;
    scroll-snap-type: x mandatory;
}
.scroller::-webkit-scrollbar { height: 8px; }
.scroller::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.12);
    border-radius: 10px;
}
.project-card {
    min-width: 310px;
    background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
    border-radius: 12px;
    overflow: hidden;
    scroll-snap-align: start;
    box-shadow: 0 12px 30px rgba(0,0,0,0.65);
    border: 1px solid rgba(255,255,255,0.03);
    transition: transform .2s ease, box-shadow .2s ease;
}
.project-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 18px 46px rgba(0,0,0,0.8);
}
.project-card img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    display:block;
}
.project-meta {
    padding: 12px 14px 14px 14px;
}
.project-meta h3 {
    margin: 0;
    color: #ffffff;
    font-size: 17px;
}
.project-meta p {
    margin: 6px 0 0 0;
    color: #cfcfcf;
    font-size: 13px;
}

/* Gallery cards */
.gallery-card {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.05);
    background: var(--card);
    transition: transform .18s ease, box-shadow .18s ease;
}
.gallery-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 16px 40px rgba(0,0,0,0.7);
}
.gallery-caption {
    font-size: 12px;
    color: var(--muted);
    margin-top: 6px;
}

/* Responsive */
@media (max-width: 900px) {
    .hero-inner {
        padding: 30px 20px;
        flex-direction: column;
        text-align: center;
    }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------- Backend logic ----------

def init_storage():
    if not os.path.exists(BASE_STORAGE_FOLDER):
        os.makedirs(BASE_STORAGE_FOLDER)
    default_section = os.path.join(BASE_STORAGE_FOLDER, "General Architecture")
    if not os.path.exists(default_section):
        os.makedirs(default_section)

def get_sections():
    if not os.path.exists(BASE_STORAGE_FOLDER):
        return []
    return [
        d for d in os.listdir(BASE_STORAGE_FOLDER)
        if os.path.isdir(os.path.join(BASE_STORAGE_FOLDER, d))
    ]

def create_new_section(section_name):
    clean_name = "".join(
        c for c in section_name if c.isalnum() or c in (" ", "_", "-")
    ).strip()
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

def pick_hero_image_path():
    sections = get_sections()
    for sec in sections:
        imgs = get_images_in_section(sec)
        if imgs:
            return imgs[0]['path']
    return None

def img_to_base64(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return None

# ---------- Auth ----------

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

init_storage()

def login_page():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔒 RESTRICTED ARCHIVE")
        st.write("Please authenticate to access the design vault.")
        password = st.text_input("Passkey", type="password")
        if st.button("ENTER VAULT"):
            if password == SHARED_PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Invalid Credentials.")

# ---------- Main UI ----------

def main_app():
    # Sidebar
    with st.sidebar:
        st.title(f"{PAGE_ICON} CONTROLS")
        st.write("Logged in as Member.")
        st.markdown("---")
        st.subheader("📁 Create Section")
        new_section_name = st.text_input(
            "New Category Name", placeholder="e.g. Interior Doors"
        )
        if st.button("Create Category"):
            if create_new_section(new_section_name):
                st.success(f"Created: {new_section_name}")
                st.rerun()
            else:
                st.warning("Invalid name or already exists.")
        st.markdown("---")
        if st.button("LOGOUT"):
            st.session_state["authenticated"] = False
            st.rerun()

    # HERO
    hero_img_path = pick_hero_image_path()
    hero_html = """
    <div class="hero">
      <div class="hero-inner">
        <div style="flex:2;">
          <div class="hero-tag">ARCHITECTURE • CURATED ARCHIVE</div>
          <div class="hero-title">A Royal Archive for Architectural Excellence</div>
          <div class="hero-sub">
            A minimal yet expressive interface for storing and reviewing architectural work.
            Create categories for projects, upload drawings and renders, and browse collections
            with a studio-grade aesthetic inspired by contemporary practice.
          </div>
          <div class="hero-actions">
            <button class="btn-cta">Browse Collections</button>
            <button class="btn-outline">Upload New Work</button>
          </div>
        </div>
        <div style="flex:1; text-align:right;">
    """
    st.markdown(hero_html, unsafe_allow_html=True)

    # Right side hero image
    if hero_img_path:
        try:
            img = Image.open(hero_img_path)
            st.image(img, use_column_width=True)
        except Exception:
            st.markdown(
                "<div style='width:100%;height:190px;background:linear-gradient(135deg,#222,#101010);border-radius:10px;'></div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            "<div style='width:100%;height:190px;background:linear-gradient(135deg,#222,#101010);border-radius:10px;'></div>",
            unsafe_allow_html=True,
        )

    st.markdown("      </div></div></div>", unsafe_allow_html=True)
    st.markdown("---")

    # UPLOAD AREA
    st.write("#### 📤 Upload New Masterpieces")
    sections = get_sections()
    if not sections:
        init_storage()
        sections = get_sections()

    col_up1, col_up2 = st.columns([1, 3])
    with col_up1:
        target_section = st.selectbox("Select Target Section", sections)
    with col_up2:
        with st.form("upload_form", clear_on_submit=True):
            uploaded_files = st.file_uploader(
                "",
                accept_multiple_files=True,
                type=["png", "jpg", "jpeg"]
            )
            submitted = st.form_submit_button("ADD TO ARCHIVE")
            if submitted and uploaded_files:
                for file in uploaded_files:
                    save_file(file, target_section)
                st.success(f"Successfully archived in '{target_section}'.")
                st.rerun()

    st.markdown("---")

    # FEATURED SCROLLER
    st.write("#### ✨ Featured Projects")
    featured = []
    for sec in sections:
        imgs = get_images_in_section(sec)
        if imgs:
            featured.append((sec, imgs[0]))
        if len(featured) >= 8:
            break

    scroller_html = '<div class="scroller">'
    if featured:
        for sec, img_data in featured:
            b64 = img_to_base64(img_data["path"])
            if b64:
                img_tag = '<img src="data:image/jpeg;base64,' + b64 + '" />'
            else:
                img_tag = '<div style="height:200px;background:linear-gradient(135deg,#222,#111);"></div>'
            title = os.path.splitext(img_data["filename"])[0]
            card = (
                '<div class="project-card">'
                + img_tag
                + '<div class="project-meta">'
                + "<h3>" + title + "</h3>"
                + "<p>Collection: " + sec + "</p>"
                + "</div></div>"
            )
            scroller_html += card
    else:
        scroller_html += (
            '<div class="project-card">'
            '<div style="height:200px;background:linear-gradient(135deg,#222,#111);"></div>'
            '<div class="project-meta"><h3>No projects yet</h3>'
            '<p>Upload to start your archive.</p></div></div>'
        )
    scroller_html += "</div>"
    st.markdown(scroller_html, unsafe_allow_html=True)

    st.markdown("---")

    # GALLERY TABS
    st.write("#### 🏛 Browse Collections")
    if sections:
        tabs = st.tabs(sections)
        for i, section in enumerate(sections):
            with tabs[i]:
                images = get_images_in_section(section)
                if not images:
                    st.info(f"No designs in '{section}' yet.")
                else:
                    cols = st.columns(4)
                    for idx, img_data in enumerate(images):
                        col_index = idx % 4
                        with cols[col_index]:
                            st.markdown('<div class="gallery-card">', unsafe_allow_html=True)
                            try:
                                image = Image.open(img_data["path"])
                                st.image(image, use_column_width=True)
                            except Exception:
                                st.markdown(
                                    "<div style='height:160px;background:linear-gradient(135deg,#222,#111);'></div>",
                                    unsafe_allow_html=True,
                                )
                            st.markdown("</div>", unsafe_allow_html=True)

                            st.markdown(
                                f"<div class='gallery-caption'>📅 {img_data['date']} &nbsp;&nbsp; ⏰ {img_data['time']}</div>",
                                unsafe_allow_html=True,
                            )

                            b1, b2 = st.columns(2)
                            with b1:
                                try:
                                    with open(img_data["path"], "rb") as file:
                                        st.download_button(
                                            label="⬇ Save",
                                            data=file,
                                            file_name=img_data["filename"],
                                            mime="image/jpeg",
                                            key="dl_" + img_data["path"],
                                        )
                                except Exception:
                                    st.button("⬇ Save", key="dl_placeholder_" + img_data["path"])
                            with b2:
                                if st.button("🗑 Delete", key="del_" + img_data["path"]):
                                    delete_image(img_data["path"])
                                    st.rerun()
    else:
        st.error("No sections found. Create one in the sidebar.")

# ---------- Run ----------

if not st.session_state["authenticated"]:
    login_page()
else:
    main_app()
