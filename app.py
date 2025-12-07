import streamlit as st
import os
import shutil
from datetime import datetime
from PIL import Image

# --- CONFIGURATION ---
# 1. The Password your friends will use
SHARED_PASSWORD = "ARCH"
# 2. Where images live
STORAGE_FOLDER = "gallery_storage"
PAGE_TITLE = "ARCH | REPOSITORY"

# --- PAGE SETUP ---
st.set_page_config(layout="wide", page_title=PAGE_TITLE, page_icon="🏛")

# --- CUSTOM ARCHITECTURAL THEME CSS ---
st.markdown(
    """
<style>
    /* Import a clean font */
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto Mono', monospace;
    }
    
    /* Header Styling */
    h1, h2, h3 {
        font-weight: 700;
        letter-spacing: -1px;
    }
    
    /* Input Fields */
    .stTextInput input {
        border-radius: 0px;
        border: 1px solid #333;
    }
    
    /* Buttons */
    .stButton button {
        border-radius: 0px;
        border: 1px solid #333;
        background-color: white;
        color: black;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton button:hover {
        background-color: black;
        color: white;
        border-color: black;
    }
    
    /* Upload Box */
    [data-testid='stFileUploader'] {
        border: 1px dashed #333;
        border-radius: 0px;
        background-color: #f9f9f9;
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- BACKEND LOGIC ---


def init_storage():
    """Creates the storage folder if it doesn't exist."""
    if not os.path.exists(STORAGE_FOLDER):
        os.makedirs(STORAGE_FOLDER)


def save_file(uploaded_file):
    """Saves file with HH-MM-SS timestamp in a YYYY-MM-DD folder."""
    now = datetime.now()
    date_subfolder = now.strftime("%Y-%m-%d")  # e.g., 2024-12-07
    time_prefix = now.strftime("%H-%M-%S")  # e.g., 14-30-01

    # 1. Make sure today's folder exists
    folder_path = os.path.join(STORAGE_FOLDER, date_subfolder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # 2. Create the strict architectural filename
    clean_name = f"{time_prefix}_{uploaded_file.name}"
    file_path = os.path.join(folder_path, clean_name)

    # 3. Save
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())


def get_gallery_images():
    """Crawls the folder to find all images."""
    images = []
    if os.path.exists(STORAGE_FOLDER):
        # Walk through the directory tree
        for root, dirs, files in os.walk(STORAGE_FOLDER):
            for file in files:
                if file.lower().endswith((".png", ".jpg", ".jpeg")):
                    full_path = os.path.join(root, file)

                    # Parse info for display
                    folder_date = os.path.basename(root)
                    time_stamp = file.split("_")[0].replace("-", ":")

                    images.append(
                        {
                            "path": full_path,
                            "date": folder_date,
                            "time": time_stamp,
                            "sort_key": f"{folder_date}{time_stamp}",  # For sorting
                        }
                    )
    # Sort: Newest uploads first
    return sorted(images, key=lambda x: x["sort_key"], reverse=True)


# --- FRONTEND INTERFACE ---


def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("ACCESS REQUIRED")
        st.write("Restricted Architectural Repository.")
        password = st.text_input("ENTER ACCESS KEY", type="password")

        if st.button("AUTHENTICATE"):
            if password == SHARED_PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("ACCESS DENIED.")


def main_app():
    # Sidebar
    with st.sidebar:
        st.title("ARCH | REPO")
        st.write("Logged in.")
        if st.button("LOGOUT"):
            st.session_state["authenticated"] = False
            st.rerun()

    # Main Area
    st.title("PROJECT UPLOAD STREAM")
    st.write("Select gallery photos. System will auto-tag date and time.")

    # Uploader
    uploaded_files = st.file_uploader(
        "DROP FILES HERE", accept_multiple_files=True, type=["png", "jpg", "jpeg"]
    )

    if uploaded_files:
        st.write("---")
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, file in enumerate(uploaded_files):
            save_file(file)
            # Update math for progress bar
            progress = (i + 1) / len(uploaded_files)
            progress_bar.progress(progress)
            status_text.text(f"Archiving: {file.name}")

        st.success("UPLOAD COMPLETE. DATABASE UPDATED.")
        st.button("REFRESH GALLERY")  # Button just to trigger a reload

    st.write("---")
    st.subheader("RECENT ARCHIVES")

    # Gallery Grid
    images = get_gallery_images()

    if not images:
        st.write("Repository is empty.")
    else:
        # Create a 4-column grid
        cols = st.columns(4)
        for idx, img_data in enumerate(images):
            col_index = idx % 4
            with cols[col_index]:
                image = Image.open(img_data["path"])
                st.image(image, use_container_width=True)
                st.caption(f"{img_data['date']} | {img_data['time']}")


# --- EXECUTION ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

init_storage()

if not st.session_state["authenticated"]:
    login_page()
else:
    main_app()
