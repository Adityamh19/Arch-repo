import os
import uuid  
from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory

# --- 1. Configuration and Setup ---

# WARNING: In a production application, set the UPLOAD_FOLDER outside the app root for security.
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the upload directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Dummy structure to simulate sections and images (in a real app, use a DB)
dummy_gallery_data = {
    "Vibrant Art": ["img_vibrant_1.jpg", "img_vibrant_2.png"],
    "Monochrome": ["img_mono_1.jpg"],
}

# --- 2. Utility Functions ---

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- 3. Frontend Content (HTML, CSS, JS) ---

CSS_CONTENT = """
/* --- 1. Global & Utility Styles --- */
:root {
    --bg-color: #2b2b2b; /* Dark Greyish Background */
    --text-color: #ffffff; /* Bright White Text */
    --accent-color: #4CAF50; /* A vibrant green for accent */
    --hover-color: #1a7e4b;
    --card-bg: #3c3c3c; /* Slightly lighter card background */
    --spacing-large: 40px;
    --border-radius: 8px;
}
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    font-family: 'Arial', sans-serif;
}
body {
    background-color: var(--bg-color);
    color: var(--text-color);
    line-height: 1.6;
    min-height: 100vh;
    padding: var(--spacing-large);
}
a {
    color: var(--text-color);
    text-decoration: none;
}
/* --- 2. Header & Controls --- */
header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: var(--spacing-large);
    border-bottom: 2px solid var(--card-bg);
    margin-bottom: var(--spacing-large);
}
header h1 {
    font-size: 3em;
    font-weight: 700;
    letter-spacing: 2px;
}
.highlight {
    color: var(--accent-color);
    text-shadow: 0 0 10px rgba(76, 175, 80, 0.5);
}
.control-btn, .submit-btn, .cancel-btn {
    padding: 10px 20px;
    border: none;
    border-radius: var(--border-radius);
    background-color: var(--accent-color);
    color: var(--text-color);
    font-size: 1em;
    cursor: pointer;
    transition: background-color 0.3s, transform 0.2s;
    font-weight: bold;
}
.control-btn:hover, .submit-btn:hover {
    background-color: var(--hover-color);
    transform: translateY(-2px);
}
.cancel-btn {
    background-color: #888;
    margin-left: 10px;
}
.modal {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: var(--card-bg);
    padding: 20px;
    border-radius: var(--border-radius);
    z-index: 1000;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.8);
}
.modal form {
    display: flex;
    gap: 10px;
}
.modal input[type="text"] {
    padding: 10px;
    background-color: var(--bg-color);
    color: var(--text-color);
    border: 1px solid var(--accent-color);
    border-radius: 4px;
    min-width: 300px;
}
/* --- 3. Gallery Structure (Spacious Exhibition Display) --- */
.gallery-container {
    display: flex;
    flex-direction: column;
    gap: 60px;
}
.gallery-section {
    background-color: var(--card-bg);
    padding: var(--spacing-large);
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    transition: all 0.5s ease;
}
.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    border-bottom: 1px solid #555;
    padding-bottom: 15px;
}
.section-title {
    font-size: 2.5em;
    cursor: pointer;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}
.rename-form {
    display: flex;
    gap: 5px;
}
.rename-form input {
    padding: 8px;
    background-color: var(--bg-color);
    color: var(--text-color);
    border: 1px solid var(--accent-color);
    border-radius: 4px;
}
.upload-label {
    display: inline-block;
    padding: 10px 15px;
    background-color: var(--accent-color);
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
    transition: background-color 0.3s;
}
.upload-label:hover {
    background-color: var(--hover-color);
}
/* --- 4. Image Grid & Hover Effects --- */
.image-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 30px;
}
.image-card {
    position: relative;
    overflow: hidden;
    border-radius: 6px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    aspect-ratio: 4/3;
    background-color: #555;
}
.image-card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 0.4s ease-in-out;
}
.image-card:hover img {
    transform: scale(1.05);
}
/* --- 5. Hover Controls (Maximizing, Delete, Download) --- */
.image-controls {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.7);
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
}
.image-card:hover .image-controls {
    opacity: 1;
    pointer-events: all;
}
.control-icon {
    font-size: 2em;
    color: var(--text-color);
    padding: 10px;
    border-radius: 50%;
    background-color: rgba(0, 0, 0, 0.5);
    transition: color 0.2s, background-color 0.2s, transform 0.2s;
    cursor: pointer;
}
.control-icon:hover {
    color: var(--accent-color);
    background-color: rgba(255, 255, 255, 0.2);
    transform: scale(1.1);
}
/* --- 6. Empty State --- */
.empty-message {
    grid-column: 1 / -1;
    text-align: center;
    padding: 40px;
    color: #aaa;
    font-style: italic;
    border: 2px dashed #444;
    border-radius: var(--border-radius);
}
"""

JS_CONTENT = """
// --- Function to toggle the "Add New Section" form ---
function showAddSectionForm() {
    const form = document.getElementById('add-section-form');
    form.style.display = 'block';
}

function hideAddSectionForm() {
    const form = document.getElementById('add-section-form');
    form.style.display = 'none';
}

// --- Function to toggle Section Renaming ---
function enableRename(titleElement, sectionName) {
    const header = titleElement.closest('.section-header');
    const renameForm = header.querySelector('.rename-form');
    
    // 1. Hide the title and upload button
    titleElement.style.display = 'none';
    header.querySelector('.upload-form').style.display = 'none';

    // 2. Show the rename form
    renameForm.style.display = 'flex';
    
    // 3. Focus on the input field
    const input = renameForm.querySelector('input[name="new_name"]');
    input.focus();
    
    // Optional: Add a simple way to cancel the rename by blurring the input
    input.addEventListener('blur', function() {
        // Only revert if the form hasn't been submitted (e.g., if user clicked somewhere else)
        if (input.closest('form').style.display !== 'none') {
            titleElement.style.display = 'block';
            header.querySelector('.upload-form').style.display = 'block';
            renameForm.style.display = 'none';
        }
    }, { once: true });
}
"""

# The full HTML template using Jinja2 syntax
HTML_TEMPLATE = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎨 Exhibition Gallery</title>
    <style>{CSS_CONTENT}</style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
    <header>
        <h1>The <span class="highlight">Grand</span> Exhibition</h1>
        <button id="add-section-btn" class="control-btn" onclick="showAddSectionForm()">+ New Section</button>
    </header>

    <div id="add-section-form" class="modal" style="display:none;">
        <form action="{{{{ url_for('add_section') }}}}" method="POST">
            <input type="text" name="new_section_name" placeholder="Enter new section name" required>
            <button type="submit" class="submit-btn">Create</button>
            <button type="button" class="cancel-btn" onclick="hideAddSectionForm()">Cancel</button>
        </form>
    </div>

    <main class="gallery-container">
        {{% for section_name, images in gallery.items() %}}
        <section class="gallery-section">
            <div class="section-header">
                <h2 class="section-title" onclick="enableRename(this, '{{{{ section_name }}}}')">{{{{ section_name }}}}</h2>
                
                <form action="{{{{ url_for('rename_section', old_name=section_name) }}}}" method="POST" class="rename-form" style="display:none;">
                    <input type="text" name="new_name" value="{{{{ section_name }}}}" required>
                    <button type="submit" class="rename-submit-btn control-btn">✅</button>
                </form>
                
                <form action="{{{{ url_for('upload_file') }}}}" method="POST" enctype="multipart/form-data" class="upload-form">
                    <input type="hidden" name="section_name" value="{{{{ section_name }}}}">
                    <label for="file-{{{{ loop.index }}}}" class="upload-label">
                        <i class="fas fa-cloud-upload-alt"></i> Upload
                    </label>
                    <input type="file" name="file" id="file-{{{{ loop.index }}}}" onchange="this.form.submit()" style="display: none;" required>
                </form>
            </div>
            
            <div class="image-grid">
                {{% for image_filename in images %}}
                <div class="image-card">
                    <img src="{{{{ url_for('uploaded_file', filename=image_filename) }}}}" alt="{{{{ image_filename }}}}">
                    
                    <div class="image-controls">
                        <a href="{{{{ url_for('uploaded_file', filename=image_filename) }}}}" target="_blank" title="Maximize/View">
                            <i class="fas fa-expand-alt control-icon"></i>
                        </a>
                        
                        <a href="{{{{ url_for('uploaded_file', filename=image_filename) }}}}" download="{{{{ image_filename }}}}" title="Download">
                            <i class="fas fa-download control-icon"></i>
                        </a>
                        
                        <a href="{{{{ url_for('delete_image', section_name=section_name, filename=image_filename) }}}}" title="Delete" onclick="return confirm('Are you sure you want to delete this image?');">
                            <i class="fas fa-trash-alt control-icon"></i>
                        </a>
                    </div>
                </div>
                {{% endfor %}}
                
                {{% if not images %}}
                <p class="empty-message">This section is empty. Upload your first photo!</p>
                {{% endif %}}
            </div>
        </section>
        {{% endfor %}}
    </main>

    <script>{JS_CONTENT}</script>
</body>
</html>
"""

# --- 4. Flask Routes (Backend Logic) ---

@app.route('/')
def index():
    """Renders the main gallery page."""
    return render_template_string(HTML_TEMPLATE, gallery=dummy_gallery_data)

@app.route('/add_section', methods=['POST'])
def add_section():
    """Handles adding a new gallery section."""
    section_name = request.form.get('new_section_name', 'New Section')
    section_name = section_name.strip().replace('/', '-').replace('\\', '-') 
    
    if section_name and section_name not in dummy_gallery_data:
        dummy_gallery_data[section_name] = []
    return redirect(url_for('index'))

@app.route('/rename_section/<old_name>', methods=['POST'])
def rename_section(old_name):
    """Handles renaming an existing section."""
    new_name = request.form.get('new_name')
    new_name = new_name.strip().replace('/', '-').replace('\\', '-') 

    if new_name and old_name in dummy_gallery_data and new_name != old_name:
        dummy_gallery_data[new_name] = dummy_gallery_data.pop(old_name)
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles file upload to a specific section and saves it to the disk."""
    if 'file' not in request.files or 'section_name' not in request.form:
        return redirect(url_for('index'))
    
    file = request.files['file']
    section_name = request.form['section_name']

    if file.filename == '' or not allowed_file(file.filename):
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename) and section_name in dummy_gallery_data:
        original_ext = file.filename.rsplit('.', 1)[1].lower()
        secure_filename = str(uuid.uuid4()) + '.' + original_ext
        
        try:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename)
            file.save(file_path)
            
            dummy_gallery_data[section_name].append(secure_filename)
        except Exception as e:
            print(f"Error saving file: {e}")
            pass

    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serves uploaded files from the 'uploads' directory."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete_image/<section_name>/<filename>')
def delete_image(section_name, filename):
    """Deletes an image from the gallery data and the disk."""
    if section_name in dummy_gallery_data and filename in dummy_gallery_data[section_name]:
        # 1. Remove from dummy data
        dummy_gallery_data[section_name].remove(filename)
        
        # 2. Delete the file from the disk
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {filename}: {e}")
    
    return redirect(url_for('index'))

# --- 5. Run Application (Deployment Ready) ---

# The 'if __name__ == "__main__":' block is modified for deployment safety.
if __name__ == '__main__':
    # Initialize dummy files if they don't exist
    for section, files in dummy_gallery_data.items():
        for d_file in files:
            file_path = os.path.join(UPLOAD_FOLDER, d_file)
            if not os.path.exists(file_path):
                try:
                    with open(file_path, 'w') as f:
                        f.write(f"Placeholder content for {d_file}")
                except Exception:
                    pass

    # IMPORTANT: The problematic 'app.run(debug=True)' is REMOVED/COMMENTED OUT.
    # When deployed, the platform (e.g., Streamlit Cloud) will import the 'app' 
    # object and run it automatically.
    # To test locally, you would typically use:
    # app.run(debug=True)
    
    print("Flask app defined. Ready for deployment server to run it.")
