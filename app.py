import streamlit as st
import os
import shutil
from datetime import datetime
from PIL import Image

# --- CONFIGURATION ---
SHARED_PASSWORD = "ARCH"
BASE_STORAGE_FOLDER = "gallery_storage"
PAGE_TITLE = "ARCHIPELAGO | STUDIO"
PAGE_ICON = "🏙"

# --- PAGE SETUP ---
st.set_page_config(layout="wide", page_title=PAGE_TITLE, page_icon=PAGE_ICON)

# --- THE "ARCHIPELAGO" AESTHETIC CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
        background-color: #ffffff; 
        color: #1a1a1a;
    }
    
    /* REMOVE DEFAULT PADDING */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 5rem;
    }

    /* HERO TEXT */
    h1.hero-title {
        font-size: 60px !important;
        font-weight: 900 !important;
        letter-spacing: -2px !important;
        line-height: 1.0 !important;
        color: #000000 !important;
        text-transform: uppercase;
        margin-top: 20px !important;
    }
    
    .sub-hero {
        font-size: 18px;
        font-weight: 400;
        color: #666;
        margin-bottom: 40px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* IMAGE CARDS HOVER EFFECT */
    div[data-testid="column"] img {
        transition: transform 0.3s ease;
    }
    div[data-testid="column"]:hover img {
        transform: scale(1.02);
    }
    
    /* BUTTONS */
    .stButton button {
        background-color: white;
        border: 1px solid #000;
        color: #000;
        border-radius: 0px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #000;
        color: #fff;
    }

    /* HIDE STREAMLIT ELEMENTS */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- BACKEND LOGIC ---
def init_storage():
    if not os.path.exists(BASE_STORAGE_FOLDER):
        os.makedirs(BASE_STORAGE_FOLDER)
    default_section = os.path.join(BASE_STORAGE_FOLDER, "Selected Works")
    if not os.path.exists(default_section):
        os.makedirs(default_section)


def get_sections():
    if not os.path.exists(BASE_STORAGE_FOLDER):
        return []
    return [d for d in os.listdir(BASE_STORAGE_FOLDER)
            if os.path.isdir(os.path.join(BASE_STORAGE_FOLDER, d))]


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

# --- FRONTEND ---
def login_page():
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image(
            "https://images.unsplash.com/photo-1511818966892-d7d671e672a2?q=80&w=1000&auto=format&fit=crop",
            use_container_width=True
        )
    
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown(
            "<h1 style='text-align: left; color: black; letter-spacing: -1px;'>ARCHIPELAGO.</h1>",
            unsafe_allow_html=True
        )
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
    # --- HERO SECTION ---
    st.image(
        "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070&auto=format&fit=crop",
        use_container_width=True
    )
    
    st.markdown("""
        <h1 class="hero-title">CITIES.<br>PEOPLE.<br>DESIGN.</h1>
        <div class="sub-hero">The Digital Archive</div>
    """, unsafe_allow_html=True)

    # --- SIDEBAR CONTROLS ---
    with st.sidebar:
        st.image(
            "https://images.unsplash.com/photo-1503387762-592deb58ef4e?q=80&w=600&auto=format&fit=crop",
            use_container_width=True
        )
        st.write("### STUDIO CONTROLS")
        st.write("---")

        with st.expander("➕ New Category"):
            new_section_name = st.text_input("Name")
            if st.button("Create"):
                if create_new_section(new_section_name):
                    st.success("Created!")
                    st.rerun()

        st.write("")
        if st.button("LOGOUT"):
            st.session_state['authenticated'] = False
            st.rerun()

    # --- UPLOAD SECTION ---
    sections = get_sections()

    with st.expander("📤  UPLOAD NEW WORK", expanded=False):
        col_up1, col_up2 = st.columns([1, 2])

        with col_up1:
            target_section = st.selectbox("Select Project Category", sections)

        with col_up2:
            with st.form("upload_form", clear_on_submit=True):
                uploaded_files = st.file_uploader(
                    "Select files",
                    accept_multiple_files=True,
                    type=['png', 'jpg', 'jpeg']
                )
                submitted = st.form_submit_button("UPLOAD")

                if submitted and uploaded_files:
                    for file in uploaded_files:
                        save_file(file, target_section)
                    st.success("Uploaded.")
                    st.rerun()

    st.write("---")

    # --- GALLERY ---
    if sections:
        tabs = st.tabs([s.upper() for s in sections])

        for i, section in enumerate(sections):
            with tabs[i]:
                images = get_images_in_section(section)

                if not images:
                    st.caption(f"No visuals in {section} yet.")
                else:
                    cols = st.columns(4)

                    for idx, img_data in enumerate(images):
                        col_index = idx % 4

                        with cols[col_index]:
                            image = Image.open(img_data['path'])
                            st.image(image, use_container_width=True)

                            st.markdown(f"{img_data['filename']}")
                            st.caption(f"{img_data['date']}")

                            c1, c2 = st.columns(2)

                            with c1:
                                with open(img_data['path'], "rb") as file:
                                    st.download_button(
                                        "⬇",
                                        data=file,
                                        file_name=img_data['filename'],
                                        mime="image/jpeg",
                                        key=f"dl_{img_data['path']}"
                                    )

                            with c2:
                                if st.button("✕", key=f"del_{img_data['path']}"):
                                    delete_image(img_data['path'])
                                    st.rerun()

# --- EXECUTION ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

init_storage()

if not st.session_state['authenticated']:
    login_page()
else:
    main_app()
