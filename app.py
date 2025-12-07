import os
from flask import Flask, render_template_string, request, redirect, url_for

# --- 1. Configuration and Setup ---

# Since file uploads are too risky/unreliable on this host, we focus on the UI.
# Remove all file-system related configurations.
# DUMMY_DATA: Use placeholders instead of real filenames.
dummy_gallery_data = {
    "Vibrant Art": ["Placeholder Image 1", "Placeholder Image 2"],
    "Monochrome": ["Placeholder Image 3"],
    "New Section Idea": [],
}

app = Flask(__name__)

# --- 2. Utility Functions (Removed file-system logic) ---

# No utility functions needed as we are not dealing with files.

# --- 3. Frontend Content (HTML, CSS, JS) - FULLY SELF-CONTAINED ---

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
    /* Placeholder style */
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 1.5em;
    font-weight: bold;
    text-align: center;
}
.image-card img {
    /* Set img to display the placeholder text instead */
    display: none;
}
.image-card:hover img {
    transform: none; /* No scaling on hover for placeholders */
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
                
                <button class="upload-label" onclick="alert('File upload functionality is disabled in this hosted version.')">
                    <i class="fas fa-cloud-upload-alt"></i> Upload
                </button>
            </div>
            
            <div class="image-grid">
                {{% for image_filename in images %}}
                <div class="image-card">
                    <span>{{{{ image_filename }}}}</span>
                    
                    <div class="image-controls">
                        <button title="Maximize/View" class="control-icon" onclick="alert('Maximize feature is disabled for placeholders.')">
                            <i class="fas fa-expand-alt"></i>
                        </button>
                        
                        <button title="Download" class="control-icon" onclick="alert('Download feature is disabled for placeholders.')">
                            <i class="fas fa-download"></i>
                        </button>
                        
                        <button title="Delete" class="control-icon" onclick="alert('Deletion is disabled for placeholders.')">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                </div>
                {{% endfor %}}
                
                {{% if not images %}}
                <p class="empty-message">This section is empty. Use the '+ New Section' button to see how it works!</p>
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

# Removed /upload, /uploads/<filename>, and /delete_image routes as they rely on a functional file system.

# --- 5. Run Application (Deployment Ready) ---

# The app object is defined and ready to be imported and run by the deployment server.

# You still need this for local testing if you choose to:
if __name__ == '__main__':
    app.run(debug=True)
