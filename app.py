import os
import streamlit as st
from jinja2 import Template # <-- NEW: Direct Jinja2 import

# --- 1. Configuration and Setup ---

# DUMMY_DATA: Use placeholders and Streamlit session state for persistence.
# Data structure is shared between Streamlit sessions.
if 'gallery_data' not in st.session_state:
    st.session_state['gallery_data'] = {
        "Vibrant Art": ["Placeholder Image 1", "Placeholder Image 2"],
        "Monochrome": ["Placeholder Image 3"],
        "New Section Idea": [],
    }

# --- 2. Utility Functions ---

# Function to sanitize user input (section names)
def sanitize_name(name):
    return name.strip().replace('/', '-').replace('\\', '-') 

# --- 3. Frontend Content (HTML, CSS, JS) - FULLY SELF-CONTAINED ---

# NOTE: The Jinja2 syntax ({{ url_for(...) }}) is replaced with simple path strings,
# as Flask's url_for is the main source of the RuntimeError.

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
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 1.5em;
    font-weight: bold;
    text-align: center;
}
.image-card img {
    display: none;
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
        <form method="get" action="/"> 
            <input type="hidden" name="section_action" value="add_section">
            <button type="submit" class="control-btn" style="display: none;" id="add-section-submit"></button>
            <button type="button" class="control-btn" onclick="showAddSectionForm()">+ New Section</button>
        </form>
    </header>

    <div id="add-section-form" class="modal" style="display:none;">
        <form method="get" action="/">
            <input type="hidden" name="section_action" value="add_section">
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
                
                <form method="get" action="/" class="rename-form" style="display:none;">
                    <input type="hidden" name="section_action" value="rename_section">
                    <input type="hidden" name="old_name" value="{{{{ section_name }}}}">
                    <input type="text" name="new_name" value="{{{{ section_name }}}}" required>
                    <button type="submit" class="rename-submit-btn control-btn">✅</button>
                </form>
                
                <button class="upload-label" onclick="alert('File upload disabled in hosted version.')">
                    <i class="fas fa-cloud-upload-alt"></i> Upload
                </button>
            </div>
            
            <div class="image-grid">
                {{% for image_filename in images %}}
                <div class="image-card">
                    <span>{{{{ image_filename }}}}</span>
                    
                    <div class="image-controls">
                        <button title="Maximize/View" class="control-icon" onclick="alert('Maximize disabled.')"><i class="fas fa-expand-alt"></i></button>
                        <button title="Download" class="control-icon" onclick="alert('Download disabled.')"><i class="fas fa-download"></i></button>
                        
                        <form method="get" action="/" style="display:inline;">
                            <input type="hidden" name="section_action" value="delete_image">
                            <input type="hidden" name="section_name" value="{{{{ section_name }}}}">
                            <input type="hidden" name="image_filename" value="{{{{ image_filename }}}}">
                            <button type="submit" title="Delete" class="control-icon" onclick="return confirm('Delete image?');"><i class="fas fa-trash-alt"></i></button>
                        </form>
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

# --- 4. Logic Functions (Streamlit Execution) ---

def handle_actions():
    """Handles all form submissions via Streamlit's query parameters."""
    query_params = st.experimental_get_query_params()
    action = query_params.get('section_action', [''])[0]

    if action == 'add_section':
        new_name = sanitize_name(query_params.get('new_section_name', ['New Section'])[0])
        if new_name and new_name not in st.session_state['gallery_data']:
            st.session_state['gallery_data'][new_name] = []
            
    elif action == 'rename_section':
        old_name = query_params.get('old_name', [''])[0]
        new_name = sanitize_name(query_params.get('new_name', [''])[0])

        if new_name and old_name in st.session_state['gallery_data'] and new_name != old_name:
            st.session_state['gallery_data'][new_name] = st.session_state['gallery_data'].pop(old_name)
            
    elif action == 'delete_image':
        section_name = query_params.get('section_name', [''])[0]
        image_filename = query_params.get('image_filename', [''])[0]
        
        if section_name in st.session_state['gallery_data'] and image_filename in st.session_state['gallery_data'][section_name]:
            st.session_state['gallery_data'][section_name].remove(image_filename)

    # Clean the query parameters to refresh the page without re-executing the action
    st.experimental_set_query_params()


def render_app():
    """The main Streamlit function that renders the Jinja2 template."""
    
    # 1. Handle user actions first (adding, renaming, deleting)
    handle_actions()
    
    # 2. Compile the template
    template = Template(HTML_TEMPLATE)
    
    # 3. Render the template with the current gallery data
    html_content = template.render(gallery=st.session_state['gallery_data'])
    
    # 4. Use Streamlit to display the content as raw HTML
    # We use a large, fixed height to ensure the whole content loads.
    st.components.v1.html(html_content, height=1000, scrolling=True)


# --- 5. Run Application ---

if __name__ == '__main__':
    render_app()
