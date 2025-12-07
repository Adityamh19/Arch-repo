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
st.markdown(
    """
<style>
    /* IMPORT FONTS: Montserrat (Modern Urban) */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700;900&display=swap');

    /* GENERAL SETTINGS */
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
        background-color: #ffffff; /* Crisp White */
        color: #1a1a1a; /* Dark Grey Text */
    }
    
    /* REMOVE DEFAULT PADDING for a "Full Bleed" feel */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    /* BIG HERO TEXT STYLING */
    /* We target the specific H1 that we create in the app */
    h1.hero-title {
        font-size: 70px !important;
        font-weight: 900 !important;
        letter-spacing: -2px !important;
        line-height: 1.1 !important;
        color: #000000 !important;
        text-transform: uppercase;
        margin-bottom: 0px !important;
        animation: fadeIn 1.5s ease-in-out;
    }
    
    .sub-hero {
        font-size: 20px;
        font-weight: 300;
        color: #666;
        margin-bottom: 50px;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    /* SCROLL ANIMATIONS */
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    /* LIVELY IMAGE CARDS */
    div[data-testid="column"] {
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-radius: 0px; 
        overflow: hidden;
        padding: 10px;
        border: 1px solid transparent; /* Invisible border to prevent layout shift */
    }
    
    /* HOVER EFFECT: Lift and Shadow */
    div[data-testid="column"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.1);
        background-color: #fafafa;
        border: 1px solid #eee;
    }

    /* BUTTON STYLING (Minimalist) */
    .stButton button {
        background-color: transparent;
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
        border-color: #000;
    }

    /* TAB STYLING */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 2px solid #eee;
        margin-bottom: 30px;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 16px;
        font-weight: 600;
        color: #888;
        border: none;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #000;
        border-bottom: 3px solid #000;
    }
    
    /* HIDE UGLY STREAMLIT ELEMENTS */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""",
    unsafe_allow_html=True,
)

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
    return [
        d
        for d in os.listdir(BASE_STORAGE_FOLDER)
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
                if file.lower().endswith((".png", ".jpg", ".jpeg")):
                    full_path = os.path.join(root, file)
                    try:
                        folder_date = os.path.basename(root)
                        time_stamp = file.split("_")[0].replace("-", ":")
                    except:
                        folder_date = "Unknown"
                        time_stamp = ""
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


# --- FRONTEND ---


def login_page():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            "<h1 style='text-align: center; color: black;'>ARCHIPELAGO</h1>",
            unsafe_allow_html=True,
        )
        st.write(
            "<p style='text-align: center; color: grey;'>Internal Design Review System</p>",
            unsafe_allow_html=True,
        )
        st.write("---")
        password = st.text_input("Enter Passkey", type="password")
        if st.button("ENTER STUDIO"):
            if password == SHARED_PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Access Denied")


def main_app():
    # --- HERO SECTION (CRASH PROOF VERSION) ---
    # We use standard HTML inside markdown but simplify the structure to prevent errors
    st.markdown(
        """
        <h1 class="hero-title">CITIES.<br>PEOPLE.<br>DESIGN.</h1>
        <div class="sub-hero">A Curated Collection of Architectural Excellence</div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # --- SIDEBAR CONTROLS ---
    with st.sidebar:
        # Simple text header instead of image to prevent loading errors
        st.header("MENU")

        # New Section Creator
        with st.expander("➕ New Project Category"):
            new_section_name = st.text_input("Category Name")
            if st.button("Create"):
                if create_new_section(new_section_name):
                    st.success("Created!")
                    st.rerun()

        st.write("")
        if st.button("LOGOUT"):
            st.session_state["authenticated"] = False
            st.rerun()

    # --- UPLOAD SECTION ---
    sections = get_sections()
    if not sections:
        init_storage()
        sections = get_sections()

    with st.expander("📤  UPLOAD TO ARCHIVE (Click to Expand)", expanded=False):
        col_up1, col_up2 = st.columns([1, 2])
        with col_up1:
            target_section = st.selectbox("Select Project Category", sections)
        with col_up2:
            with st.form("upload_form", clear_on_submit=True):
                uploaded_files = st.file_uploader(
                    "Select files", accept_multiple_files=True, type=["png", "jpg", "jpeg"]
                )
                submitted = st.form_submit_button("UPLOAD")
                if submitted and uploaded_files:
                    for file in uploaded_files:
                        save_file(file, target_section)
                    st.success("Uploaded.")
                    st.rerun()

    st.write("")

    # --- GALLERY SECTION ---
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
                            image = Image.open(img_data["path"])
                            st.image(image, use_container_width=True)

                            st.markdown(f"{img_data['filename']}")
                            st.caption(f"{img_data['date']}")

                            c1, c2 = st.columns(2)
                            with c1:
                                with open(img_data["path"], "rb") as file:
                                    st.download_button(
                                        "⬇",
                                        data=file,
                                        file_name=img_data["filename"],
                                        mime="image/jpeg",
                                        key=f"dl_{img_data['path']}",
                                    )
                            with c2:
                                if st.button("✕", key=f"del_{img_data['path']}"):
                                    delete_image(img_data["path"])
                                    st.rerun()


# --- EXECUTION ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

init_storage()

if not st.session_state["authenticated"]:
    login_page()
else:
    main_app()
