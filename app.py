import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path
from PIL import Image
import mimetypes

# ----------------------
# Configuration
# ----------------------
SHARED_PASSWORD = "ARCH"
BASE_STORAGE_FOLDER = Path("gallery_storage")
PAGE_TITLE = "ARCHIPELAGO | STUDIO"
PAGE_ICON = "🏙"

st.set_page_config(layout="wide", page_title=PAGE_TITLE, page_icon=PAGE_ICON)

# ----------------------
# Utility functions
# ----------------------

def init_storage():
    BASE_STORAGE_FOLDER.mkdir(exist_ok=True)
    default = BASE_STORAGE_FOLDER / "Selected Works"
    default.mkdir(exist_ok=True)


def sanitize_name(name: str) -> str:
    return "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip()


def get_sections():
    if not BASE_STORAGE_FOLDER.exists():
        return []
    return sorted([p.name for p in BASE_STORAGE_FOLDER.iterdir() if p.is_dir()])


def create_new_section(section_name: str) -> bool:
    clean = sanitize_name(section_name)
    if not clean:
        return False
    path = BASE_STORAGE_FOLDER / clean
    if path.exists():
        return False
    path.mkdir(parents=True, exist_ok=False)
    return True


def delete_section(section_name: str):
    path = BASE_STORAGE_FOLDER / section_name
    if path.exists() and path.is_dir():
        for item in path.rglob('*'):
            if item.is_file():
                item.unlink()
        for folder in sorted(path.rglob('*'), reverse=True):
            if folder.is_dir():
                try:
                    folder.rmdir()
                except Exception:
                    pass
        try:
            path.rmdir()
        except Exception:
            pass


def save_file(uploaded_file, section: str):
    now = datetime.now()
    date_subfolder = now.strftime("%Y-%m-%d")
    time_prefix = now.strftime("%H-%M-%S")
    section_path = BASE_STORAGE_FOLDER / section
    date_path = section_path / date_subfolder
    date_path.mkdir(parents=True, exist_ok=True)
    clean_name = f"{time_prefix}_{uploaded_file.name}"
    file_path = date_path / clean_name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


# Metadata per folder (simple JSON alongside images)

def metadata_path_for(folder: Path) -> Path:
    return folder / "_metadata.json"


def load_metadata(folder: Path) -> dict:
    mp = metadata_path_for(folder)
    if mp.exists():
        try:
            return json.loads(mp.read_text(encoding='utf-8'))
        except Exception:
            return {}
    return {}


def save_metadata(folder: Path, data: dict):
    mp = metadata_path_for(folder)
    mp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def delete_image(file_path: Path):
    if file_path.exists():
        folder = file_path.parent
        data = load_metadata(folder)
        data.pop(file_path.name, None)
        save_metadata(folder, data)
        file_path.unlink()


def get_images_in_section(section: str) -> list:
    images = []
    section_path = BASE_STORAGE_FOLDER / section
    if not section_path.exists():
        return images
    for root, dirs, files in os.walk(section_path):
        folder = Path(root)
        meta = load_metadata(folder)
        for file in sorted(files, reverse=True):
            if file.startswith('_'):
                continue
            if file.lower().endswith(('png', 'jpg', 'jpeg', 'webp', 'gif')):
                full_path = folder / file
                folder_date = folder.name
                time_stamp = file.split('_')[0].replace('-', ':') if '_' in file else ''
                caption = meta.get(file, '')
                images.append({
                    'path': full_path,
                    'filename': file,
                    'date': folder_date,
                    'time': time_stamp,
                    'caption': caption
                })
    # Sort by date and time desc
    images.sort(key=lambda x: (x['date'], x['time']), reverse=True)
    return images


# ----------------------
# Styling (CSS)
# ----------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
    }
    .block-container{padding-top:1.5rem;padding-bottom:3rem}

    h1.hero {font-size:64px;letter-spacing:-1px;margin-bottom:4px}
    .sub-hero{font-size:18px;color:#666;margin-bottom:24px}

    /* Image cards */
    .img-card{border-radius:6px;overflow:hidden;padding:8px;transition:transform .2s, box-shadow .2s}
    .img-card:hover{transform:translateY(-6px);box-shadow:0 12px 30px rgba(0,0,0,0.12)}

    /* Buttons */
    .stButton>button{border-radius:6px;padding:8px 12px;font-weight:700}

    /* small captions */
    .small-muted{font-size:12px;color:#777}

    /* center text */
    .center{text-align:center}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------
# App Pages
# ----------------------


def login_page():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 class='center hero'>ARCHIPELAGO</h1>", unsafe_allow_html=True)
        st.markdown("<div class='center sub-hero'>Internal Design Review System</div>", unsafe_allow_html=True)
        st.write("---")
        password = st.text_input("Enter Passkey", type="password")
        if st.button("ENTER STUDIO"):
            if password == SHARED_PASSWORD:
                st.session_state['authenticated'] = True
                st.experimental_rerun()
            else:
                st.error("Access Denied")


def main_app():
    # Header
    left, right = st.columns([3, 1])
    with left:
        st.markdown("<h1 class='hero'>CITIES.<br>PEOPLE.<br>DESIGN.</h1>", unsafe_allow_html=True)
        st.markdown("<div class='sub-hero'>A curated collection of architectural excellence — internal studio archive</div>", unsafe_allow_html=True)
    with right:
        if st.button("🔒 Logout"):
            st.session_state['authenticated'] = False
            st.experimental_rerun()

    st.write("---")

    # Sidebar controls and management
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/25/25694.png", width=64)
        st.markdown("### MENU")

        # Create section
        with st.expander("➕ New Project Category", expanded=False):
            name = st.text_input("Category Name", key="new_section_name")
            if st.button("Create Category"):
                if create_new_section(name):
                    st.success(f"Created '{name}'")
                    st.experimental_rerun()
                else:
                    st.warning("Failed to create. Maybe empty name or already exists.")

        # Manage sections
        st.markdown("---")
        sections = get_sections()
        if sections:
            sel = st.selectbox("Select Category to Manage", sections, key='manage_section')
            if st.button("Delete Selected Category"):
                confirm_fn = getattr(st, 'confirm', None)
                if confirm_fn:
                    pass
                # simple confirm modal replacement
                if st.button("⚠️ Confirm Delete Category"):
                    delete_section(sel)
                    st.success(f"Deleted '{sel}'")
                    st.experimental_rerun()

        st.write("")
        st.caption("Tip: Create categories then upload into them from the upload panel.")

    # Upload panel
    sections = get_sections()
    if not sections:
        init_storage()
        sections = get_sections()

    with st.expander("📤 UPLOAD TO ARCHIVE", expanded=True):
        col1, col2 = st.columns([1, 2])
        with col1:
            target_section = st.selectbox("Project Category", sections)
        with col2:
            with st.form("upload_form", clear_on_submit=True):
                uploaded_files = st.file_uploader("Select image files", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'webp', 'gif'])
                submitted = st.form_submit_button("UPLOAD")
                if submitted and uploaded_files:
                    for f in uploaded_files:
                        p = save_file(f, target_section)
                        # add empty caption to metadata
                        meta_folder = p.parent
                        meta = load_metadata(meta_folder)
                        meta[p.name] = ""
                        save_metadata(meta_folder, meta)
                    st.success("Uploaded successfully.")
                    st.experimental_rerun()

    st.write("")

    # Gallery display with search/sort
    cols_top = st.columns([3, 1])
    with cols_top[0]:
        search = st.text_input("Search images by filename or caption...")
    with cols_top[1]:
        sort_opt = st.selectbox("Sort", ['Newest', 'Oldest'])

    for section in sections:
        st.markdown(f"### {section}")
        images = get_images_in_section(section)
        if search:
            images = [img for img in images if search.lower() in img['filename'].lower() or search.lower() in (img.get('caption') or '').lower()]
        if sort_opt == 'Oldest':
            images = list(reversed(images))

        if not images:
            st.info("No visuals in this category yet.")
            continue

        # Display grid
        cols = st.columns(4)
        for idx, img in enumerate(images):
            col = cols[idx % 4]
            with col:
                st.markdown("<div class='img-card'>", unsafe_allow_html=True)
                try:
                    im = Image.open(img['path'])
                    st.image(im, use_column_width=True)
                except Exception:
                    st.caption("Unable to render image")

                st.markdown(f"**{img['filename']}**")
                st.markdown(f"<div class='small-muted'>{img['date']}</div>", unsafe_allow_html=True)
                if img.get('caption'):
                    st.markdown(f"_{img['caption']}_")

                # actions
                c1, c2, c3 = st.columns([1,1,1])
                with c1:
                    # Download
                    try:
                        mime, _ = mimetypes.guess_type(img['path'])
                        if not mime:
                            mime = 'application/octet-stream'
                        with open(img['path'], 'rb') as f:
                            st.download_button("⬇ Download", data=f, file_name=img['filename'], mime=mime, key=f"dl_{img['filename']}")
                    except Exception:
                        st.button("⬇", disabled=True)
                with c2:
                    if st.button("🔍 Preview", key=f"preview_{img['filename']}"):
                        # show modal-like preview
                        st.session_state['preview_image'] = str(img['path'])
                with c3:
                    if st.button("✖ Delete", key=f"del_{img['filename']}"):
                        # confirm (quick pattern): set to state then show confirm button
                        st.session_state['to_delete'] = str(img['path'])

                st.markdown("</div>", unsafe_allow_html=True)

        st.write("---")

    # Preview modal (lightbox)
    if st.session_state.get('preview_image'):
        path = Path(st.session_state['preview_image'])
        if path.exists():
            st.markdown("### Preview")
            cols = st.columns([2,1])
            with cols[0]:
                st.image(Image.open(path), use_column_width=True)
            with cols[1]:
                st.markdown(f"**Filename:** {path.name}")
                st.markdown(f"**Folder:** {path.parent.name}")
                meta = load_metadata(path.parent)
                caption = meta.get(path.name, "")
                new_caption = st.text_area("Edit caption", value=caption, key=f"cap_{path.name}")
                if st.button("Save Caption"):
                    meta[path.name] = new_caption
                    save_metadata(path.parent, meta)
                    st.success("Saved")
                    st.session_state.pop('preview_image', None)
                    st.experimental_rerun()
                if st.button("Close Preview"):
                    st.session_state.pop('preview_image', None)
                    st.experimental_rerun()

    # Delete confirmation flow
    if st.session_state.get('to_delete'):
        path = Path(st.session_state['to_delete'])
        if path.exists():
            st.warning(f"You're about to delete {path.name}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Confirm Delete"):
                    delete_image(path)
                    st.success("Deleted")
                    st.session_state.pop('to_delete', None)
                    st.experimental_rerun()
            with c2:
                if st.button("Cancel"):
                    st.session_state.pop('to_delete', None)
                    st.experimental_rerun()


# ----------------------
# Run
# ----------------------

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

init_storage()

if not st.session_state['authenticated']:
    login_page()
else:
    main_app()
