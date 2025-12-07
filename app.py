import streamlit as st
import os
import shutil
from datetime import datetime
from PIL import Image

# --- CONFIGURATION ---
SHARED_PASSWORD = "ARCH"
STORAGE_FOLDER = "gallery_storage"
PAGE_TITLE = "ARCH | REPOSITORY"

# --- PAGE SETUP ---
st.set_page_config(layout="wide", page_title=PAGE_TITLE, page_icon="🏛")

# --- CUSTOM CSS (Architectural Theme) ---
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto Mono', monospace; }
    .stButton button { width: 100%; border-radius: 0px; border: 1px solid #333; }
    .stButton button:hover { background-color: #ff4b4b; color: white; border-color: #ff4b4b; }
</style>
""",
    unsafe_allow_html=True,
)

# --- BACKEND LOGIC ---


def init_storage():
    if not os.path.exists(STORAGE_FOLDER):
        os.makedirs(STORAGE_FOLDER)


def save_file(uploaded_file):
    now = datetime.now()
    date_subfolder = now.strftime("%Y-%m-%d")
    time_prefix = now.strftime("%H-%M-%S")

    folder_path = os.path.join(STORAGE_FOLDER, date_subfolder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    clean_name = f"{time_prefix}_{uploaded_file.name}"
    file_path = os.path.join(folder_path, clean_name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())


def delete_image(file_path):
    """Deletes a specific image file."""
    if os.path.exists(file_path):
        os.remove(file_path)


def get_gallery_images():
    images = []
    if os.path.exists(STORAGE_FOLDER):
        for root, dirs, files in os.walk(STORAGE_FOLDER):
            for file in files:
                if file.lower().endswith((".png", ".jpg", ".jpeg")):
                    full_path = os.path.join(root, file)
                    folder_date = os.path.basename(root)
                    time_stamp = file.split("_")[0].replace("-", ":")
                    images.append(
                        {
                            "path": full_path,
                            "date": folder_date,
                            "time": time_stamp,
                            "sort_key": f"{folder_date}{time_stamp}",
                        }
                    )
    return sorted(images, key=lambda x: x["sort_key"], reverse=True)


# --- FRONTEND ---


def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("ACCESS REQUIRED")
        password = st.text_input("ENTER ACCESS KEY", type="password")
        if st.button("AUTHENTICATE"):
            if password == SHARED_PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("ACCESS DENIED")


def main_app():
    with st.sidebar:
        st.write("Logged in.")
        if st.button("LOGOUT"):
            st.session_state["authenticated"] = False
            st.rerun()

    # --- HEADER ---
    st.title("ARCHITECTURAL DESIGNS")  # <--- Renamed as requested
    st.write("Secure Project Repository.")

    # --- UPLOAD FORM (Fixes the re-upload issue) ---
    with st.form("upload_form", clear_on_submit=True):
        uploaded_files = st.file_uploader(
            "Add New Designs", accept_multiple_files=True, type=["png", "jpg", "jpeg"]
        )
        submitted = st.form_submit_button("UPLOAD PHOTOS")

        if submitted and uploaded_files:
            for file in uploaded_files:
                save_file(file)
            st.success("Upload Complete.")
            st.rerun()  # Refresh immediately to show new photos

    st.write("---")

    # --- GALLERY WITH DELETE BUTTONS ---
    images = get_gallery_images()

    if not images:
        st.info("Repository is empty.")
    else:
        cols = st.columns(4)
        for idx, img_data in enumerate(images):
            col_index = idx % 4
            with cols[col_index]:
                image = Image.open(img_data["path"])
                st.image(image, use_container_width=True)
                st.caption(f"{img_data['date']} | {img_data['time']}")

                # The DELETE Button
                if st.button("🗑 DELETE", key=img_data["path"]):
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
