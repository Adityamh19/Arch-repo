import streamlit as st
import os
from datetime import datetime
from PIL import Image
import base64

# ---------------------------
# BASIC CONFIG
# ---------------------------
SHARED_PASSWORD = "ARCH"
BASE_STORAGE_FOLDER = "gallery_storage"
PAGE_TITLE = "ROYAL ARCHIVE"
PAGE_ICON = "🏛"

st.set_page_config(layout="wide", page_title=PAGE_TITLE, page_icon=PAGE_ICON)

# ---------------------------
# GLOBAL STYLES (NO F-STRINGS)
# ---------------------------
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
    background: radial-gradient(circle at top, #1c1f24 0, #0b0c0d 40%, #050607 100%);
    color: var(--muted);
    font-family: 'Lato', sans-serif;
    padding: 10px 18px 30px 18px;
}

/* Sidebar tweaks */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#111318,#050608);
    border-right: 1px solid rgba(255,255,255,0.05);
}

/* Headers */
h1, h2, h3, h4 {
    font-family: 'Playfair Display', serif;
    letter-spacing: 1px;
}

/* HERO */
.hero-box {
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(10,10,10,0.96), rgba(15,15,15,0.9));
    padding: 28px 30px;
    box-shadow: 0 18px 50px rgba(0,0,0,0.75);
    border: 1px solid rgba(255,255,255,0.05);
}
.hero-title {
    font-size: 34px;
    color: #ffffff;
    margin-bottom: 8px;
}
.hero-sub {
    font-size: 15px;
    max-width: 720px;
    color: #e5e5e5;
}
.hero-pill {
    display:inline-block;
    padding:4px 10px;
    border-radius:999px;
    border:1px solid rgba(255,255,255,0.15);
    font-size:11px;
    text-transform:uppercase;
    letter-spacing:1px;
    margin-bottom:12px;
}
.hero-badge {
    color: var(--gold);
}
.hero-image-frame {
    border-radius: 14px;
    overflow:hidden;
    border:1px solid rgba(255,255,255,0.12);
    box-shadow:0 14px 40px rgba(0,0,0,0.9);
}

/* Streamlit buttons */
.stButton button {
    border-radius: 6px;
    border: 1px solid rgba(255,255,255,0.1);
    background: #17191d;
    color: #f1f1f1;
    font-weight: 600;
    padding: 0.4rem 0.8rem;
    transition: all 0.18s ease;
    font-size: 0.9rem;
}
.stButton button:hover {
    border-color: var(--gold);
    color: var(--gold);
}

/* FEATURED SCROLLER */
.scroller {
    display:flex;
    overflow-x:auto;
    gap:18px;
    padding: 10px 4px 4px 4px;
    scroll-snap-type:x mandatory;
}
.scroller::-webkit-scrollbar { height:8px; }
.scroller::-webkit-scrollbar-thumb {
    background:rgba(255,255,255,0.12);
    border-radius:8px;
}
.project-card {
    min-width: 260px;
    max-width: 320px;
    background: linear-gradient(180deg, #181a1f, #111317);
    border-radius: 14px;
    overflow:hidden;
    border:1px solid rgba(255,255,255,0.06);
    box-shadow:0 14px 40px rgba(0,0,0,0.8);
    scroll-snap-align:start;
    transition: transform .18s ease, box-shadow .18s ease;
}
.project-card:hover {
    transform: translateY(-6px);
    box-shadow:0 20px 60px rgba(0,0,0,0.92);
}
.project-card img {
    width:100%;
    height:180px;
    object-fit:cover;
    display:block;
}
.project-meta {
    padding:10px 12px 12px 12px;
}
.project-meta h4 {
    font-size:15px;
    color:#fff;
    margin:0 0 4px 0;
}
.project-meta p {
    font-size:12px;
    color:#cfcfcf;
    margin:0;
}

/* GALLERY CARDS */
.gallery-card {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.04);
    background: #14161b;
    box-shadow: 0 12px 36px rgba(0,0,0,0.75);
    transition: transform .16s ease;
}
.gallery-card:hover {
    transform: translateY(-5px);
}
.gallery-caption {
    font-size: 12px;
    color: #d0d0d0;
    margin-top: 6px;
}

/* Small screens */
@media(max-width: 900px) {
    .hero-box { padding:20px; }
    .hero-title { font-size:26px; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------------------------
# BACKEND HELPERS
# ---------------------------
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

def create_new_section(section_name: str) -> bool:
    clean_name = "".join(
        c for c in section_name if c.isalnum() or c in (" ", "_", "-")
    ).strip()
    if clean_name:
        path = os.path.join(BASE_STORAGE_FOLDER, clean_name)
        if not os.path.exists(path):
            os.makedirs(path)
            return True
    return False

def save_file(uploaded_file, section: str):
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

def delete_image(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)

def get_images_in_section(section: str):
    images = []
    section_path = os.path.join(BASE_STORAGE_FOLDER, section)

    if os.path.exists(section_path):
        for root, dirs, files in os.walk(section_path):
            for file in files:
                if file.lower().endswith((".png", ".jpg", ".jpeg")):
                    full_path = os.path.join(root, file)
                    folder_date = os.path.basename(root)
                    time_stamp = file.split("_")[0].replace("-", ":")
                    images.append(
                        {
                            "path": full_path,
                            "filename": file,
                            "date": folder_date,
                            "time": time_stamp,
                            "sort_key": f"{folder_date}{time_stamp}",
                        }
                    )

    return sorted(images, key=lambda x: x["sort_key"], reverse=True)

def pick_any_image_for_preview():
    """Return path of first image found across all sections (or None)."""
    for sec in get_sections():
        imgs = get_images_in_section(sec)
        if imgs:
            return imgs[0]["path"], sec
    return None, None

def image_file_to_base64(path: str):
    try:
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return None

# ---------------------------
# AUTH + INIT
# ---------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

init_storage()

# ---------------------------
# LOGIN PAGE
# ---------------------------
def login_page():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.title("🔒 RESTRICTED ARCHIVE")
        st.write("Please authenticate to access the design vault.")
        password = st.text_input("Passkey", type="password")
        if st.button("ENTER VAULT"):
            if password == SHARED_PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Invalid Credentials.")

# ---------------------------
# MAIN APP (AFTER LOGIN)
# ---------------------------
def main_app():
    # ---- SIDEBAR ----
    with st.sidebar:
        st.title(f"{PAGE_ICON} CONTROLS")
        st.write("Logged in as Member.")
        st.markdown("---")
        st.subheader("📁 Create Section")
        new_section_name = st.text_input(
            "New Category Name", placeholder="e.g. DOOR DESIGNS"
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

    # ---- HERO SECTION ----
    st.markdown('<div class="hero-box">', unsafe_allow_html=True)
    hero_col1, hero_col2 = st.columns([2, 1])

    with hero_col1:
        st.markdown(
            """
            <div class="hero-pill"><span class="hero-badge">ARCHIVE</span> • Studio-grade gallery</div>
            <div class="hero-title">A Royal Archive for Architectural Excellence</div>
            <div class="hero-sub">
                Curate your work like a professional studio portfolio. Categorise doors, facades,
                interiors and experimental ideas into clean collections, each with rich visuals and a
                timeless dark interface inspired by high-end architectural sites.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        btn1, btn2 = st.columns(2)
        with btn1:
            if st.button("➕ Upload Designs"):
                # Just a hint: scroll to upload section manually
                st.info("Scroll a bit down to find the upload panel.")
        with btn2:
            if st.button("✨ Tips for Use"):
                st.info("Create sections like DOOR DESIGNS, INTERIORS, FACADE, etc. Then upload images into each.")

    with hero_col2:
        preview_path, preview_sec = pick_any_image_for_preview()
        if preview_path:
            try:
                img = Image.open(preview_path)
                st.markdown('<div class="hero-image-frame">', unsafe_allow_html=True)
                st.image(img, use_column_width=True, caption=f"From: {preview_sec}")
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception:
                st.empty()
        else:
            st.markdown(
                """
                <div class="hero-image-frame" style="height:200px;
                    background:radial-gradient(circle at top,#303540,#15171c);display:flex;
                    align-items:center;justify-content:center;font-size:13px;color:#e0e0e0;">
                    No images yet. Upload your first masterpiece below.
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)  # close hero-box
    st.markdown("")

    # ---- UPLOAD PANEL ----
    st.markdown("### 📤 Upload New Masterpieces")

    sections = get_sections()
    if not sections:
        init_storage()
        sections = get_sections()

    up_col1, up_col2 = st.columns([1, 3])

    with up_col1:
        target_section = st.selectbox("Select Target Section", sections)

    with up_col2:
        with st.form("upload_form", clear_on_submit=True):
            uploaded_files = st.file_uploader(
                "Drag & drop your designs here",
                accept_multiple_files=True,
                type=["png", "jpg", "jpeg"],
            )
            submitted = st.form_submit_button("ADD TO ARCHIVE")
            if submitted and uploaded_files:
                for file in uploaded_files:
                    save_file(file, target_section)
                st.success(f"Successfully archived in '{target_section}'.")
                st.rerun()

    st.markdown("---")

    # ---- FEATURED STRIP ----
    st.markdown("### ✨ Featured Projects")

    featured = []
    for sec in sections:
        imgs = get_images_in_section(sec)
        if imgs:
            featured.append((sec, imgs[0]))
        if len(featured) >= 8:
            break

    strip_html = '<div class="scroller">'
    if featured:
        for sec, imgdata in featured:
            b64 = image_file_to_base64(imgdata["path"])
            if b64:
                img_tag = f'<img src="data:image/jpeg;base64,{b64}" />'
            else:
                img_tag = '<div style="height:180px;background:linear-gradient(135deg,#222,#111);"></div>'
            title = os.path.splitext(imgdata["filename"])[0]
            card = (
                '<div class="project-card">'
                f"{img_tag}"
                '<div class="project-meta">'
                f"<h4>{title}</h4>"
                f"<p>Collection: {sec}</p>"
                "</div></div>"
            )
            strip_html += card
    else:
        strip_html += (
            '<div class="project-card">'
            '<div style="height:180px;background:linear-gradient(135deg,#222,#111);"></div>'
            '<div class="project-meta"><h4>No projects yet</h4>'
            '<p>Upload images into any section to see them here.</p></div></div>'
        )

    strip_html += "</div>"
    st.markdown(strip_html, unsafe_allow_html=True)

    st.markdown("---")

    # ---- GALLERY PER SECTION ----
    st.markdown("### 🏛 Browse Collections")

    if sections:
        tabs = st.tabs(sections)
        for i, section in enumerate(sections):
            with tabs[i]:
                images = get_images_in_section(section)
                if not images:
                    st.info(f"No designs in '{section}' yet.")
                else:
                    grid_cols = st.columns(4)
                    for idx, img_data in enumerate(images):
                        col_index = idx % 4
                        with grid_cols[col_index]:
                            st.markdown('<div class="gallery-card">', unsafe_allow_html=True)
                            try:
                                image = Image.open(img_data["path"])
                                st.image(image, use_column_width=True)
                            except Exception:
                                st.markdown(
                                    '<div style="height:150px;background:linear-gradient(135deg,#222,#111);"></div>',
                                    unsafe_allow_html=True,
                                )
                            st.markdown("</div>", unsafe_allow_html=True)

                            st.markdown(
                                f'<div class="gallery-caption">📅 {img_data["date"]} &nbsp;·&nbsp; ⏰ {img_data["time"]}</div>',
                                unsafe_allow_html=True,
                            )

                            d1, d2 = st.columns(2)
                            with d1:
                                try:
                                    with open(img_data["path"], "rb") as file:
                                        st.download_button(
                                            label="⬇ Save",
                                            data=file,
                                            file_name=img_data["filename"],
                                            mime="image/jpeg",
                                            key=f"dl_{img_data['path']}",
                                        )
                                except Exception:
                                    st.button("⬇ Save", key=f"dl_hold_{img_data['path']}")
                            with d2:
                                if st.button("🗑 Delete", key=f"del_{img_data['path']}"):
                                    delete_image(img_data["path"])
                                    st.rerun()
    else:
        st.error("No sections found. Create one in the sidebar.")

# ---------------------------
# APP ENTRY
# ---------------------------
if not st.session_state["authenticated"]:
    login_page()
else:
    main_app()
