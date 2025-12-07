import streamlit as st
from jinja2 import Template
import json # Used to pass data to JavaScript

# --- 1. Configuration and Setup ---

# Initialize data and store it in Streamlit's session state for persistence.
if 'gallery_data' not in st.session_state:
    st.session_state['gallery_data'] = {
        "Vibrant Art": ["Placeholder Image 1", "Placeholder Image 2"],
        "Monochrome": ["Placeholder Image 3"],
    }

# --- 2. Utility Functions ---

def sanitize_name(name):
    """Clean user input for section names."""
    return name.strip().replace('/', '-').replace('\\', '-') 

# --- 3. JavaScript Interaction Handler (New Structure) ---

def handle_js_interaction():
    """Checks for commands passed back from JavaScript and updates state."""
    # This uses a Streamlit custom component trick to read data from the HTML side.
    # We use a simple JSON string stored in a hidden Streamlit text area.
    
    # Check if the JavaScript bridge has sent a command
    command_json = st.session_state.get('js_command', '{}')
    
    try:
        command = json.loads(command_json)
        action = command.get('action')
    except json.JSONDecodeError:
        action = None
        
    if not action:
        return

    # --- Execute Actions ---
    data = st.session_state['gallery_data']
    
    if action == 'add_section':
        new_name = sanitize_name(command.get('name'))
        if new_name and new_name not in data:
            data[new_name] = []
            
    elif action == 'rename_section':
        old_name = command.get('old_name')
        new_name = sanitize_name(command.get('new_name'))
        if new_name and old_name in data and new_name != old_name:
            data[new_name] = data.pop(old_name)
            
    elif action == 'delete_image':
        section_name = command.get('section_name')
        image_filename = command.get('image_filename')
        if section_name in data and image_filename in data[section_name]:
            data[section_name].remove(image_filename)
    
    # Crucial: Reset the command to prevent infinite loops/re-execution
    st.session_state['js_command'] = '{}'
    # Rerun the Streamlit app to refresh the HTML with new data
    st.experimental_rerun()


# --- 4. Frontend Content (HTML, CSS, JS) ---

# The CSS is heavily optimized for smooth, modern aesthetics.
CSS_CONTENT = """
/* --- MODERN AESTHETICS & ANIMATIONS --- */
:root {
    --bg-color: #1a1a1a; /* Very Dark Background */
    --text-color: #f0f0f0; /* Soft White Text */
    --accent-color: #00bcd4; /* Vibrant Cyan for Modern Pop */
    --hover-color: #0097a7;
    --card-bg: #2c2c2c; /* Slightly Lighter Card Background */
    --spacing-large: 40px;
    --border-radius: 12px;
}
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    font-family: 'Montserrat', sans-serif; /* Modern Font */
}
body {
    background-color: var(--bg-color);
    color: var(--text-color);
    line-height: 1.6;
    min-height: 100vh;
    padding: var(--spacing-large);
    overflow-x: hidden;
}
header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: var(--spacing-large);
    border-bottom: 2px solid var(--card-bg);
    margin-bottom: var(--spacing-large);
}
header h1 {
    font-size: 3.5em;
    font-weight: 800;
    letter-spacing: 3px;
    text-transform: uppercase;
}
.highlight {
    color: var(--accent-color);
    text-shadow: 0 0 20px rgba(0, 188, 212, 0.5); /* Stronger neon glow */
}
.control-btn, .upload-label, .submit-btn, .cancel-btn {
    padding: 12px 25px;
    border: none;
    border-radius: 50px; /* Pill shape for modern look */
    background-color: var(--accent-color);
    color: var(--bg-color);
    font-size: 1.1em;
    cursor: pointer;
    transition: background-color 0.3s, transform 0.2s, box-shadow 0.3s;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(0, 188, 212, 0.4);
}
.control-btn:hover, .submit-btn:hover, .upload-label:hover {
    background-color: var(--hover-color);
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0, 188, 212, 0.6);
}
.modal {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: var(--card-bg);
    padding: 30px;
    border-radius: var(--border-radius);
    z-index: 1000;
    box-shadow: 0 0 30px rgba(0, 0, 0, 0.8);
    animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
    from {opacity: 0; transform: translate(-50%, -60%);}
    to {opacity: 1; transform: translate(-50%, -50%);}
}
.modal input[type="text"] {
    padding: 12px;
    background-color: var(--bg-color);
    color: var(--text-color);
    border: 1px solid var(--accent-color);
    border-radius: 6px;
    min-width: 350px;
}
.gallery-container {
    display: flex;
    flex-direction: column;
    gap: 80px; /* Increased spacing */
}
.gallery-section {
    background-color: var(--card-bg);
    padding: var(--spacing-large);
    border-radius: var(--border-radius);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
    transition: all 0.5s ease;
}
.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 40px;
    border-bottom: 1px solid #444;
    padding-bottom: 20px;
}
.section-title {
    font-size: 2.8em;
    cursor: pointer;
    text-transform: capitalize;
    letter-spacing: 1.8px;
    transition: color 0.3s;
}
.section-title:hover {
    color: var(--accent-color);
}
.rename-form {
    display: flex;
    gap: 10px;
}
.image-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 35px; 
}
.image-card {
    position: relative;
    overflow: hidden;
    border-radius: 8px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5);
    aspect-ratio: 16/10; /* Cinematic ratio */
    background-color: #444;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 1.6em;
    font-weight: 600;
    text-align: center;
    transition: transform 0.4s ease-out;
}
.image-card:hover {
    transform: scale(1.03);
    box-shadow: 0 15px 35px rgba(0, 188, 212, 0.2);
}
.image-controls {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(26, 26, 26, 0.9);
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 25px;
    opacity: 0;
    transition: opacity 0.4s ease-in-out;
    pointer-events: none;
}
.image-card:hover .image-controls {
    opacity: 1;
    pointer-events: all;
}
.control-icon {
    font-size: 2.2em;
    color: var(--text-color);
    transition: color 0.3s, transform 0.3s;
    cursor: pointer;
}
.control-icon:hover {
    color: var(--accent-color);
    transform: scale(1.2);
}
.empty-message {
    grid-column: 1 / -1;
    text-align: center;
    padding: 50px;
    color: #888;
    font-style: italic;
    border: 3px dashed #333;
    border-radius: var(--border-radius);
}
"""

JS_CONTENT = f"""
// --- JavaScript to communicate with Streamlit (CRITICAL FOR INTERACTIVITY) ---

// Function to send a command to Streamlit's session state
function sendCommandToStreamlit(commandObject) {{
    const commandInput = document.getElementById('js_command_input');
    const commandSubmit = document.getElementById('js_command_submit');
    
    if (commandInput && commandSubmit) {{
        commandInput.value = JSON.stringify(commandObject);
        // Simulate a click on the hidden Streamlit button to trigger Python rerun
        commandSubmit.click();
    }} else {{
        console.error("Streamlit bridge elements not found.");
        alert("Action failed. Try refreshing the page.");
    }}
}}

// --- Front-end Logic for Sections and Modals ---

function showAddSectionForm() {{
    const form = document.getElementById('add-section-form');
    form.style.display = 'block';
}}

function hideAddSectionForm() {{
    const form = document.getElementById('add-section-form');
    form.style.display = 'none';
}}

function handleAddSection() {{
    const input = document.getElementById('new-section-name-input');
    const name = input.value;
    if (name) {{
        sendCommandToStreamlit({{ action: 'add_section', name: name }});
        hideAddSectionForm();
    }}
    return false; // Prevent default form submission
}}

function enableRename(titleElement, sectionName) {{
    const header = titleElement.closest('.section-header');
    const renameForm = header.querySelector('.rename-form');
    
    titleElement.style.display = 'none';
    header.querySelector('.upload-label').style.display = 'none'; // Use upload-label instead of upload-form
    renameForm.style.display = 'flex';
    
    const input = renameForm.querySelector('input[name="new_name"]');
    input.focus();
}}

function handleRename(event, oldName) {{
    event.preventDefault(); // Stop the default submit action
    const form = event.target;
    const newName = form.querySelector('input[name="new_name"]').value;
    
    if (newName && newName !== oldName) {{
        sendCommandToStreamlit({{ action: 'rename_section', old_name: oldName, new_name: newName }});
    }} else {{
        // Revert UI if no change
        const header = form.closest('.section-header');
        header.querySelector('.section-title').style.display = 'block';
        header.querySelector('.upload-label').style.display = 'block';
        form.style.display = 'none';
    }}
    return false;
}}

function handleDeleteImage(sectionName, imageFilename) {{
    if (confirm('Are you sure you want to delete ' + imageFilename + '?')) {{
        sendCommandToStreamlit({{ action: 'delete_image', section_name: sectionName, image_filename: imageFilename }});
    }}
}}
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
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;800&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <h1>The <span class="highlight">Grand</span> Exhibition</h1>
        <button type="button" class="control-btn" onclick="showAddSectionForm()">+ New Section</button>
    </header>

    <div id="add-section-form" class="modal" style="display:none;">
        <form onsubmit="return handleAddSection()">
            <input type="text" id="new-section-name-input" placeholder="Enter new section name" required>
            <button type="submit" class="submit-btn">Create</button>
            <button type="button" class="cancel-btn" onclick="hideAddSectionForm()">Cancel</button>
        </form>
    </div>

    <main class="gallery-container">
        {{% for section_name, images in gallery.items() %}}
        <section class="gallery-section">
            <div class="section-header">
                <h2 class="section-title" onclick="enableRename(this, '{{{{ section_name }}}}')">{{{{ section_name }}}}</h2>
                
                <form class="rename-form" style="display:none;" onsubmit="return handleRename(event, '{{{{ section_name }}}}')">
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
                        
                        <button type="button" title="Delete" class="control-icon" onclick="handleDeleteImage('{{{{ section_name }}}}', '{{{{ image_filename }}}}')"><i class="fas fa-trash-alt"></i></button>
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

    <form style="display:none;">
        <textarea id="js_command_input" name="js_command_input" style="display:none;"></textarea>
        <button id="js_command_submit" type="submit"></button>
    </form>

    <script>{JS_CONTENT}</script>
</body>
</html>
"""

# --- 5. Streamlit Execution Wrapper ---

def render_app():
    """The main Streamlit function that renders the Jinja2 template."""
    
    # Hidden Streamlit form elements to receive data from the JavaScript side
    # The 'key' ensures Streamlit listens for updates on the hidden form
    js_command = st.text_area(
        'JS Command Bridge', 
        value='{}', 
        key='js_command', 
        height=1, 
        label_visibility="collapsed"
    )

    # 1. Handle user actions based on data received from JavaScript
    handle_js_interaction()
    
    # 2. Compile and Render the template
    template = Template(HTML_TEMPLATE)
    html_content = template.render(gallery=st.session_state['gallery_data'])
    
    # 3. Use Streamlit to display the content as raw HTML
    st.components.v1.html(html_content, height=1000, scrolling=True)


# --- 6. Run Application ---

if __name__ == '__main__':
    render_app()
