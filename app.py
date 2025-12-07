import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path
from PIL import Image
import mimetypes
import zipfile
import io
import base64

# ----------------------
# Configuration
# ----------------------
SHARED_PASSWORD = "ARCH"
BASE_STORAGE_FOLDER = Path("gallery_storage")
PAGE_TITLE = "ARCHIPELAGO | STUDIO"
PAGE_ICON = "🏙"

st.set_page_config(layout="wide", page_title=PAGE_TITLE, page_icon=PAGE_ICON)

# ----------------------
# Safe rerun helper
# ----------------------

def safe_rerun():
    try:
        if hasattr(st, 'experimental_rerun'):
            st.experimental_rerun()
            return
        if hasattr(st, 'rerun'):
            st.rerun()
            return
    except Exception:
        try:
            st.session_state['__refresh'] = datetime.now().isoformat()
        except Exception:
            pass
        try:
            st.stop()
        except Exception:
            pass

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
                try:
                    item.unlink()
                except Exception:
                    pass
        for folder in sorted([d for d in path.rglob('*') if d.is_dir()], reverse=True):
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
    try:
        mp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception:
        pass


def delete_image(file_path: Path):
    if file_path.exists():
        folder = file_path.parent
        data = load_metadata(folder)
        data.pop(file_path.name, None)
        save_metadata(folder, data)
        try:
            file_path.unlink()
        except Exception:
            pass


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
    images.sort(key=lambda x: (x['date'], x['time']), reverse=True)
    return images


def make_zip_of_section(section: str) -> bytes:
    section_path = BASE_STORAGE_FOLDER / section
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(section_path):
            for f in files:
                if f.startswith('_'):
                    continue
                fp = Path(root) / f
                arcname = str(fp.relative_to(BASE_STORAGE_FOLDER))
                zf.write(fp, arcname)
    mem.seek(0)
    return mem.read()

# ----------------------
# Styling (CSS) inspired by archipelago.com.au
# ----------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700;900&display=swap');
:root{--accent:#000;--muted:#666}
html, body, [class*="css"]{font-family: 'Montserrat', sans-serif}
.block-container{padding-top:2rem;padding-left:3rem;padding-right:3rem}

/* Hero */
.hero-wrap{display:flex;align-items:center;justify-content:space-between;margin-bottom:30px}
.hero-title{font-size:76px;font-weight:900;letter-spacing:-2px;line-height:0.95;text-transform:uppercase}
.hero-sub{font-size:18px;color:var(--muted);letter-spacing:3px}

/* Masonry-ish columns */
.masonry{display:flex;gap:18px}
.masonry-col{flex:1;display:flex;flex-direction:column;gap:18px}
.img-card{position:relative;border-radius:6px;overflow:hidden}
.img-card img{width:100%;height:auto;display:block}
.img-overlay{position:absolute;left:0;right:0;bottom:0;padding:12px;background:linear-gradient(0deg, rgba(0,0,0,0.5), rgba(0,0,0,0));color:white;}
.img-meta{font-size:13px}

/* Buttons */
.btn{display:inline-block;padding:8px 12px;border:1px solid var(--accent);background:white;color:var(--accent);font-weight:700;border-radius:4px}
.btn:hover{background:var(--accent);color:white}

/* subtle hover */
.img-card:hover{transform:translateY(-6px);box-shadow:0 12px 30px rgba(0,0,0,0.12)}

/* responsive */
@media (max-width: 900px){.hero-title{font-size:44px}}

</style>
""", unsafe_allow_html=True)

# ----------------------
# Pages
# ----------------------

def login_page():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div class='center hero-wrap'><div><div class='hero-title'>ARCHIPELAGO</div><div class='hero-sub'>Internal Design Review System</div></div></div>", unsafe_allow_html=True)
        st.write("---")

    # Apply hero background CSS if uploaded
    if st.session_state.get('hero_bg_bytes'):
        try:
            b64 = base64.b64encode(st.session_state['hero_bg_bytes']).decode()
            css = f"""
            <style>
            .block-container { background-image: url('data:image/jpeg;base64,{b64}'); background-size: cover; background-position: center; }
            .hero-title{color: white; text-shadow: 0 6px 30px rgba(0,0,0,0.6)}
            .hero-sub{color: rgba(255,255,255,0.9)}
            </style>
            """
            st.markdown(css, unsafe_allow_html=True)
        except Exception:
            pass

        password = st.text_input("Enter Passkey", type="password")
        if st.button("ENTER STUDIO"):
            if password == SHARED_PASSWORD:
                st.session_state['authenticated'] = True
                safe_rerun()
            else:
                st.error("Access Denied")


def main_app():
    left, right = st.columns([3,1])
    with left:
        st.markdown("<div class='hero-title'>CITIES.<br>PEOPLE.<br>DESIGN.</div>", unsafe_allow_html=True)
        st.markdown("<div class='hero-sub'>A curated collection of architectural excellence — internal studio archive</div>", unsafe_allow_html=True)
    with right:
        if st.button("🔒 Logout"):
            st.session_state['authenticated'] = False
            safe_rerun()

    st.write("---")

    with st.sidebar:
        st.markdown("<h3>ARCHIPELAGO</h3>", unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/25/25694.png", width=64)

        # Hero background selector / uploader
        st.markdown("**Hero background**")
        bg_choice = st.selectbox("Use background from:",["None","Upload a new image","Use sample image"], key='bg_choice')
        bg_data = None
        if bg_choice == "Upload a new image":
            bg_file = st.file_uploader("Upload hero background (jpg/png)", type=['png','jpg','jpeg'], key='bg_upload')
            if bg_file is not None:
                # store raw bytes in session for CSS rendering
                st.session_state['hero_bg_bytes'] = bg_file.getvalue()
                st.success("Background uploaded. Scroll up to see changes.")
        elif bg_choice == "Use sample image":
            sample = st.selectbox("Sample images", ["Sample 1","Sample 2","Sample 3","Sample 4","Sample 5"], key='bg_sample')
            # Map sample names to bundled images (if provided in working dir)
            sample_map = {
                "Sample 1": "pexels-borja-lopez-1059078 - Copy.jpg",
                "Sample 2": "pexels-pixabay-262367 - Copy.jpg",
                "Sample 3": "pexels-scottwebb-137594 - Copy.jpg",
                "Sample 4": "pexels-yentl-jacobs-43020-157811 - Copy.jpg",
                "Sample 5": "RDT_20250331_0038012434882102056392262.jpg",
            }
            chosen = sample_map.get(sample)
            if chosen and Path(chosen).exists():
                try:
                    st.session_state['hero_bg_bytes'] = Path(chosen).read_bytes()
                except Exception:
                    pass

        with st.expander("➕ New Project Category", expanded=False):
            name = st.text_input("Category Name", key="new_section_name")
            if st.button("Create Category"):
                if create_new_section(name):
                    st.success(f"Created '{name}'")
                    safe_rerun()
                else:
                    st.warning("Failed to create. Empty name or already exists.")

        st.markdown("---")
        sections = get_sections()
        if sections:
            sel = st.selectbox("Manage Category", sections, key='manage_section')
            if st.button("Export Category as ZIP"):
                try:
                    data = make_zip_of_section(sel)
                    st.download_button(label="Download ZIP", data=data, file_name=f"{sel}.zip")
                except Exception:
                    st.error("Failed to create zip.")
            if st.button("Delete Selected Category"):
                if st.button("⚠️ Confirm Delete Category"):
                    delete_section(sel)
                    st.success(f"Deleted '{sel}'")
                    safe_rerun()

        st.caption("Tip: Use 'Export' to download a full project folder.")

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
                        meta_folder = p.parent
                        meta = load_metadata(meta_folder)
                        meta[p.name] = ""
                        save_metadata(meta_folder, meta)
                    st.success("Uploaded successfully.")
                    safe_rerun()

    st.write("")

    # Search + sort
    cols_top = st.columns([3, 1])
    with cols_top[0]:
        search = st.text_input("Search images by filename or caption...")
    with cols_top[1]:
        sort_opt = st.selectbox("Sort", ['Newest', 'Oldest'])

    # For each section show a masonry-like gallery
    for section in sections:
        st.markdown(f"<h2 style='margin-top:30px'>{section}</h2>", unsafe_allow_html=True)
        images = get_images_in_section(section)
        if search:
            images = [img for img in images if search.lower() in img['filename'].lower() or search.lower() in (img.get('caption') or '').lower()]
        if sort_opt == 'Oldest':
            images = list(reversed(images))

        if not images:
            st.info("No visuals in this category yet.")
            continue

        # Masonry columns (3 columns)
        cols = st.columns(3)
        # Simple height balancing by filenames length (heuristic)
        stacks = [0,0,0]
        assignments = [ [] for _ in range(3) ]
        for img in images:
            i = stacks.index(min(stacks))
            assignments[i].append(img)
            stacks[i] += len(img['filename'])

        for col_idx, col_imgs in enumerate(assignments):
            with cols[col_idx]:
                for img in col_imgs:
                    st.markdown("<div class='img-card'>", unsafe_allow_html=True)
                    try:
                        im = Image.open(img['path'])
                        st.image(im, use_column_width=True)
                    except Exception:
                        st.caption("Unable to render image")

                    # overlay meta
                    st.markdown(f"<div class='img-overlay'><div class='img-meta'><strong>{img['filename']}</strong><div style='font-size:12px;opacity:0.8'>{img['date']}</div></div></div>", unsafe_allow_html=True)

                    # actions
                    c1, c2, c3 = st.columns([1,1,1])
                    with c1:
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
                            st.session_state['preview_image'] = str(img['path'])
                    with c3:
                        if st.button("✖ Delete", key=f"del_{img['filename']}"):
                            st.session_state['to_delete'] = str(img['path'])

                    st.markdown("</div>", unsafe_allow_html=True)

        st.write("---")

    # Preview
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
                    safe_rerun()
                if st.button("Close Preview"):
                    st.session_state.pop('preview_image', None)
                    safe_rerun()

    # Delete confirmation
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
                    safe_rerun()
            with c2:
                if st.button("Cancel"):
                    st.session_state.pop('to_delete', None)
                    safe_rerun()

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
