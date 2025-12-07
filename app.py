import streamlit as st
import os
import shutil
from datetime import datetime
from PIL import Image

# --- CONFIGURATION ---
SHARED_PASSWORD = "ARCH"
BASE_STORAGE_FOLDER = "gallery_storage"
PAGE_TITLE = "ROYAL ARCHIVE"
PAGE_ICON = "🏛"

# --- PAGE SETUP ---
st.set_page_config(layout="wide", page_title=PAGE_TITLE, page_icon=PAGE_ICON)

# --- THE "ROYAL" AESTHETIC CSS ---
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Lato:wght@300;400&display=swap');

    .stApp {
        background-color: #1a1a1a;
        color: #e0e0e0;
    }

    h1, h2, h3 {
        font-family: 'Playfair Display', serif;
        color: #D4AF37;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #333;
        border-radius: 4px 4px 0 0;
        color: white;
        font-family: 'Lato', sans-serif;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #D4AF37;
        color: black;
        font-weight: bold;
    }

    .stButton button {
        border: 1px solid #555;
        background-color: #2b2b2b;
        color: white;
        font-family: 'Lato', sans-serif;
        transition: 0.3s ease;
    }
    .stButton button:hover {
        border-color: #D4AF37;
        color: #D4AF37;
    }

    div[data-testid="column"] {
        background-color: #252525;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #333;
        margin-bottom: 20px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- BACKEND LOGIC ---


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
        st.title("🔒 RESTRICTED ARCHIVE")
        st.write("Please authenticate to access the design vault.")

        password = st.text_input("Passkey", type="password")

        if st.button("ENTER VAULT"):
            if password == SHARED_PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Invalid Credentials.")


def main_app():
    # SIDEBAR
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

    # MAIN HEADER
    st.markdown(f"# {PAGE_ICON} THE DESIGN VAULT")
    st.markdown("### A Royal Archive for Architectural Excellence")
    st.markdown("---")

    # UPLOAD AREA
    sections = get_sections()
    if not sections:
        init_storage()
        sections = get_sections()

    st.write("#### 📤 Upload New Masterpieces")

    col_up1, col_up2 = st.columns([1, 3])

    with col_up1:
        target_section = st.selectbox("Select Target Section", sections)

    with col_up2:
        with st.form("upload_form", clear_on_submit=True):
            uploaded_files = st.file_uploader(
                "", accept_multiple_files=True, type=["png", "jpg", "jpeg"]
            )
            submitted = st.form_submit_button("ADD TO ARCHIVE")

            if submitted and uploaded_files:
                for file in uploaded_files:
                    save_file(file, target_section)
                st.success(f"Successfully archived in '{target_section}'.")
                st.rerun()

    st.markdown("---")

    # GALLERY SECTION
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
                            image = Image.open(img_data["path"])
                            st.image(image, use_container_width=True)

                            st.caption(f"📅 {img_data['date']} | ⏰ {img_data['time']}")

                            b1, b2 = st.columns(2)

                            with b1:
                                with open(img_data["path"], "rb") as file:
                                    st.download_button(
                                        label="⬇ Save",
                                        data=file,
                                        file_name=img_data["filename"],
                                        mime="image/jpeg",
                                        key=f"dl_{img_data['path']}",
                                    )

                            with b2:
                                if st.button("🗑 Delete", key=f"del_{img_data['path']}"):
                                    delete_image(img_data["path"])
                                    st.rerun()
    else:
        st.error("No sections found. Create one in the sidebar.")


# --- EXECUTION ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

init_storage()

if not st.session_state["authenticated"]:
    login_page()
else:
    main_app()
