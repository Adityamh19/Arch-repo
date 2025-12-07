import streamlit as st
import os
from datetime import datetime
from PIL import Image
import io

# --- CONFIGURATION ---
SHARED_PASSWORD = "ARCH"
BASE_STORAGE_FOLDER = "gallery_storage"
PAGE_TITLE = "ROYAL ARCHIVE"
PAGE_ICON = "🏛"

# --- PAGE SETUP ---
st.set_page_config(layout="wide", page_title=PAGE_TITLE, page_icon=PAGE_ICON)

# --- ENHANCED ROYAL THEME CSS & LAYOUT ---
st.markdown(
    """
    <style>
    /* Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Lato:wght@300;400;700&display=swap');

    :root{
        --bg-dark: #0f1113;
        --panel: #131516;
        --muted: #bdbdbd;
        --gold: #D4AF37;
        --accent: #2fd7c1;
        --card: #17191a;
    }

    /* Basic App */
    .stApp {
        background: linear-gradient(180deg, #0b0c0d 0%, #0f1113 100%);
        color: var(--muted);
        font-family: 'Lato', sans-serif;
    }

    /* Header / Hero */
    .hero {
        position: relative;
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 30px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.6);
    }
    .hero .hero-inner {
        padding: 80px 60px;
        display: flex;
        align-items: center;
        gap: 40px;
        background-position: center;
        background-size: cover;
        background-attachment: fixed;
        min-height: 320px;
    }
    .hero .hero-text h1 {
        font-family: 'Playfair Display', serif;
        font-size: 42px;
        color: white;
        margin: 0 0 8px 0;
        letter-spacing: 1px;
    }
    .hero .hero-text p {
        color: #e8e8e8;
        opacity: 0.9;
        margin: 0 0 16px 0;
        max-width: 720px;
        line-height: 1.5;
    }
    .hero .hero-actions {
        margin-top: 10px;
    }
    .btn-cta {
        background: linear-gradient(90deg, var(--gold), #f2d07a);
        border: none;
        color: #111;
        padding: 10px 18px;
        margin-right: 12px;
        border-radius: 6px;
        font-weight: 700;
        cursor: pointer;
        box-shadow: 0 6px 18px rgba(212,175,55,0.12);
        transition: transform .18s ease;
    }
    .btn-cta:hover { transform: translateY(-3px); }

    .btn-outline {
        background: transparent;
        border: 1px solid rgba(255,255,255,0.08);
        color: var(--muted);
        padding: 10px 16px;
        border-radius: 6px;
    }

    /* Sidebar adjustments */
    .css-1d39w8q { /* Streamlit sidebar container class may vary by version - this is a best-effort tweak */
        background: rgba(0,0,0,0.06);
        border-right: 1px solid rgba(255,255,255,0.02);
    }

    /* Featured horizontal scroller */
    .scroller {
        display: flex;
        overflow-x: auto;
        gap: 18px;
        padding: 18px;
        scroll-snap-type: x mandatory;
    }
    .scroller::-webkit-scrollbar { height: 10px; }
    .scroller::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.06); border-radius: 12px; }
    .project-card {
        min-width: 340px;
        background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
        border-radius: 12px;
        padding: 0;
        overflow: hidden;
        scroll-snap-align: start;
        box-shadow: 0 12px 30px rgba(0,0,0,0.65);
        transition: transform .2s ease, box-shadow .2s ease;
        border: 1px solid rgba(255,255,255,0.03);
    }
    .project-card:hover { transform: translateY(-8px); box-shadow: 0 20px 48px rgba(0,0,0,0.75); }
    .project-card img { display:block; width:100%; height:200px; object-fit:cover; }
    .project-card .meta { padding: 14px; }
    .project-card .meta h3 { margin:0; color: #fff; font-size:18px; font-weight:700; }
    .project-card .meta p { margin:6px 0 0 0; color: #cfcfcf; font-size:13px; }

    /* Gallery cards */
    .gallery-card {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.03);
        background: var(--card);
        transition: transform .18s ease;
    }
    .gallery-card:hover { transform: translateY(-6px); box-shadow: 0 18px 40px rgba(0,0,0,0.6); }

    .caption {
        font-size: 12px;
        color: var(--muted);
        margin-top: 8px;
    }

    /* small screens */
    @media (max-width: 900px) {
        .hero .hero-inner {
            padding: 40px 18px;
            flex-direction: column;
            text-align: center;
        }
        .project-card { min-width: 280px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------
# Backend (unchanged logic)
# --------------------------

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
    clean_name = "".join(c for c in section_name if c.isalnum() or c in (" ", "_", "-")).strip()
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

# --------------------------
# Helper: pick a hero image (first image found)
# --------------------------
def pick_hero_image():
    # scan sections for any image and return the first found PIL bytes and a caption
    sections = get_sections()
    for sec in sections:
        imgs = get_images_in_section(sec)
        if imgs:
            try:
                img_path = imgs[0]['path']
                with open(img_path, "rb") as f:
                    b = f.read()
                return b, imgs[0].get('filename', '')
            except:
                continue
    return None, None

# --------------------------
# Frontend
# --------------------------
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

init_storage()

def login_page():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🔒 RESTRICTED ARCHIVE")
        st.write("Please authenticate to access the design vault.")
        password = st.text_input("Passkey", type="password")
        if st.button("ENTER VAULT"):
            if password == SHARED_PASSWORD:
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("Invalid Credentials.")

def main_app():
    # Sidebar controls (same features)
    with st.sidebar:
        st.title(f"{PAGE_ICON} CONTROLS")
        st.write("Logged in as Member.")
        st.markdown("---")
        st.subheader("📁 Create Section")
        new_section_name = st.text_input("New Category Name", placeholder="e.g. Interior Doors")
        if st.button("Create Category"):
            if create_new_section(new_section_name):
                st.success(f"Created: {new_section_name}")
                st.rerun()
            else:
                st.warning("Invalid name or already exists.")
        st.markdown("---")
        if st.button("LOGOUT"):
            st.session_state['authenticated'] = False
            st.rerun()

    # HERO
    hero_bytes, hero_caption = pick_hero_image()
    hero_style = ""
    if hero_bytes:
        # create data URI for background inline
        data_uri = "data:image/jpeg;base64," + (io.BytesIO(hero_bytes).getvalue()).hex()
        # Note: hex will not render as base64. Instead we'll use inline <img> approach below.
        # We'll just render an <img> inside the hero with overlay for full compatibility.
        pass

    # We'll render the hero with a large overlay and optional image preview on the right
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-inner" style="background: linear-gradient(90deg, rgba(10,10,10,0.85), rgba(10,10,10,0.35));">
                <div class="hero-text" style="flex:1">
                    <h1>A Royal Archive for Architectural Excellence</h1>
                    <p>Showcase your best designs in a curated, image-first portfolio. Upload, categorize and present your work with refined typography, rich imagery and elegant spacing — inspired by leading architecture studios.</p>
                    <div class="hero-actions">
                        <button class="btn-cta" onclick="(function(){})()">Explore Collections</button>
                        <button class="btn-outline" onclick="(function(){})()">Learn More</button>
                    </div>
                </div>
                <div style="width:420px;">
    """
        ,
        unsafe_allow_html=True,
    )

    # show a right-side image (first hero image if exists)
    if hero_bytes:
        try:
            img = Image.open(io.BytesIO(hero_bytes))
            st.image(img, width=420)
        except Exception:
            st.markdown(
                '<div style="width:420px;height:260px;background:linear-gradient(135deg,#111,#222);border-radius:8px;"></div>',
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            '<div style="width:420px;height:260px;background:linear-gradient(135deg,#111,#222);border-radius:8px;"></div>',
            unsafe_allow_html=True
        )

    st.markdown("</div></div></div>", unsafe_allow_html=True)

    st.markdown("---")

    # UPLOAD area (kept as form)
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
            uploaded_files = st.file_uploader("", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
            submitted = st.form_submit_button("ADD TO ARCHIVE")
            if submitted and uploaded_files:
                for file in uploaded_files:
                    save_file(file, target_section)
                st.success(f"Successfully archived in '{target_section}'.")
                st.rerun()

    st.markdown("---")

    # FEATURED PROJECTS horizontal scroller
    st.write("#### ✨ Featured Projects")
    # pick some images across sections for demo cards
    featured = []
    for sec in sections:
        imgs = get_images_in_section(sec)
        if imgs:
            featured.append((sec, imgs[0]))
        if len(featured) >= 6:
            break

    # Build HTML scroller
    scroller_html = '<div class="scroller">'
    if featured:
        for sec, imgdata in featured:
            # encode image inline (small preview)
            try:
                with open(imgdata['path'], "rb") as f:
                    b = f.read()
                import base64
                b64 = base64.b64encode(b).decode()
                img_tag = f'<img src="data:image/jpeg;base64,{b64}" />'
            except:
                img_tag = '<div style="height:200px;background:linear-gradient(135deg,#222,#111)"></div>'

            title = os.path.splitext(imgdata['filename'])[0]
            scroller_html += f"""
            <div class="project-card">
                {img_tag}
                <div class="meta">
                    <h3>{title}</h3>
                    <p>Collection: {sec}</p>
                </div>
            </div>
            """
    else:
        # empty state
        scroller_html += """
        <div class="project-card">
            <div style="height:200px;background:linear-gradient(135deg,#222,#111)"></div>
            <div class="meta"><h3>No projects yet</h3><p>Upload to create featured projects</p></div>
        </div>
        """
    scroller_html += '</div>'
    st.markdown(scroller_html, unsafe_allow_html=True)

    st.markdown("---")

    # GALLERY: show selected section images with cards
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
                            # display card
                            st.markdown('<div class="gallery-card">', unsafe_allow_html=True)
                            try:
                                image = Image.open(img_data['path'])
                                st.image(image, use_column_width=True)
                            except Exception:
                                st.image(None)

                            st.markdown("</div>", unsafe_allow_html=True)
                            st.caption(f"📅 {img_data['date']} | ⏰ {img_data['time']}")
                            b1, b2 = st.columns([1,1])
                            with b1:
                                try:
                                    with open(img_data['path'], "rb") as file:
                                        st.download_button(
                                            label="⬇ Save",
                                            data=file,
                                            file_name=img_data['filename'],
                                            mime="image/jpeg",
                                            key=f"dl_{img_data['path']}"
                                        )
                                except Exception:
                                    st.button("⬇ Save", key=f"dl_hold_{img_data['path']}")
                            with b2:
                                if st.button("🗑 Delete", key=f"del_{img_data['path']}"):
                                    delete_image(img_data['path'])
                                    st.rerun()
    else:
        st.error("No sections found. Create one in the sidebar.")

# Run appropriate page
if not st.session_state['authenticated']:
    login_page()
else:
    main_app()
