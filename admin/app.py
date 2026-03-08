from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import requests
import json
import os
import sys
import uuid
from functools import wraps
from flask import make_response
from werkzeug.utils import secure_filename

# Handle both local run (from admin/) and gunicorn run (from root directory MyPortfolio/)
current_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(current_dir) == 'admin':
    # We are in admin/ folder, add parent to find config
    sys.path.insert(1, os.path.abspath(os.path.join(current_dir, '..')))
else:
    # We might be run from root as a module, add current dir
    sys.path.insert(1, current_dir)

# 1. Load .env for local development only
from dotenv import load_dotenv
load_dotenv()

# 2. Load AWS SSM secrets (overrides .env in prod)
from config.secrets import load_secrets
load_secrets()


app = Flask(__name__)
app.secret_key = '*John3211#*John3211#*John3211#*John3211#*John3211#'

# Firebase wrapper class to replace python-firebase
class FirebaseApplication:
    def __init__(self, url, auth=None):
        self.url = url.rstrip('/')
    
    def _build_path(self, path, key=None):
        """Build the full URL path"""
        if path.startswith('/'):
            path = path[1:]
        url = f"{self.url}/{path}.json"
        if key:
            url = f"{self.url}/{path}/{key}.json"
        return url
    
    def get(self, path, key=None):
        """GET request"""
        url = self._build_path(path, key)
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json() if response.text else None
        except requests.exceptions.RequestException:
            return None
    
    def post(self, path, data):
        """POST request (creates new entry)"""
        url = self._build_path(path)
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None
    
    def put(self, path, key=None, data=None):
        """PUT request (updates/replaces)
        
        Usage patterns:
        - fb.put('/path', key, data) -> PUT data at /path/key
        - fb.put('/path/field', 'field_name', value) -> PUT value at /path/field/field_name
        - fb.put('/path', data) -> PUT data at /path
        """
        if key is not None and data is not None:
            # Handle: fb.put('/path', key, data) or fb.put('/path/field', 'field', value)
            # If path already ends with key-like pattern, treat key as field name
            if '/' in path and path.split('/')[-1] not in ['', None]:
                # Path already has a key, treat key as field name and data as value
                url = self._build_path(f"{path}/{key}")
            else:
                # Standard: path/key
                url = self._build_path(path, key)
            put_data = data
        elif key is not None and data is None:
            # Handle: fb.put('/path', key) where key is the data
            url = self._build_path(path)
            put_data = key
        else:
            # Handle: fb.put('/path', data) - data is passed as key parameter
            url = self._build_path(path)
            put_data = key if key is not None else data
        
        try:
            response = requests.put(url, json=put_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None
    
    def delete(self, path, key=None):
        """DELETE request"""
        url = self._build_path(path, key)
        try:
            response = requests.delete(url)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException:
            return False

fb = FirebaseApplication('https://portfolio-536e2-default-rtdb.firebaseio.com/', None)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Check if session has login flag
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        
        # 2. STRICT VALIDATION: Check if session credentials match current DB credentials
        # This prevents access if password was changed in DB but user still has old cookie
        
        # GUEST MODE BYPASS: Guests don't have DB credentials to validate
        if session.get('is_guest'):
            return f(*args, **kwargs)

        current_db_links = fb.get('/links/-OOvwHeVJtSsrjh3QnWR/links', None)
        if not current_db_links:
             # Safety fallback: if DB unreadable, force re-login
             session.clear()
             flash("Session expired or database error. Please login again.")
             return redirect(url_for('admin_login'))

        db_username = current_db_links.get('admin_username')
        db_password = current_db_links.get('admin_password')
        
        session_username = session.get('admin_username')
        session_password = session.get('admin_password')

        if session_username != db_username or session_password != db_password:
            session.clear()
            flash("Credentials changed. Please login again.")
            return redirect(url_for('admin_login'))

        return f(*args, **kwargs)
    return decorated_function



def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return no_cache

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    if "Cache-Control" not in response.headers:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

@app.route('/admin-profile-image/<path:filename>')
def admin_profile_image(filename):
    """Serve profile images from main project static folder"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(base_dir, 'main', 'project', 'static', 'assets', 'img', 'profile')
    return send_from_directory(static_dir, filename)

@app.route('/admin-guest-login')
def guest_login():
    """Handle Guest Login (Read-Only)"""
    session.clear() # Clear any existing session
    session['admin_logged_in'] = True
    session['is_guest'] = True
    session['admin_username'] = "Guest User"
    # Debug logging
    print(f"DEBUG - Guest login successful")
    print(f"DEBUG - Session contents: {dict(session)}")
    print(f"DEBUG - is_guest value: {session.get('is_guest')}")
    flash("Logged in as Guest (Read-Only Mode)", "info")
    return redirect(url_for('admin_intro'))

@app.route('/admin-login', methods=["GET", "POST"])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        links = fb.get('/links/-OOvwHeVJtSsrjh3QnWR/links', None)
        if links:
            stored_username = links.get('admin_username')
            stored_password = links.get('admin_password')

            if username == stored_username and password == stored_password:
                session['admin_logged_in'] = True
                session['is_guest'] = False  # Explicitly clear guest mode flag
                # Store credentials in session for strict validation
                session['admin_username'] = stored_username
                session['admin_password'] = stored_password
                # Debug logging
                print(f"DEBUG - Admin login successful for user: {stored_username}")
                print(f"DEBUG - Session contents: {dict(session)}")
                print(f"DEBUG - is_guest value: {session.get('is_guest')}")
                return redirect(url_for('admin_intro'))
            else:
                flash("Invalid username or password.")
        else:
            flash("Admin credentials not found.")
        
        return render_template(
        'admin-resume.html',
        professional_summary=professional_summary,
        technical_skills=technical_skills,
        experiences=experiences,
        education=education
    )


@app.route('/delete-certification', methods=["POST"])
@login_required
@nocache
def delete_certification():
    # Strict validation handled by decorator
    # GUEST GUARD
    if session.get('is_guest'):
        flash("Guest Mode: Read-only access. Changes are not saved.", "warning")
        return redirect(url_for('admin_certification'))

    key = request.form.get('key')
    if key:
        fb.delete('/certifications', key)
        flash('Certification deleted successfully!', 'success')
    return redirect(url_for('admin_certification'))


@app.route('/admin-project', methods=["GET", "POST"])
@login_required
@nocache
def admin_project():
    # Strict validation handled by decorator
    
    edit_data = None
    
    if request.method == "POST":
        # GUEST GUARD
        if session.get('is_guest'):
            flash("Guest Mode: Read-only access. Changes are not saved.", "warning")
            return redirect(request.url)

        # Edit button clicked
        if 'edit_key' in request.form:
            key = request.form['edit_key']
            edit_data = fb.get(f'/projects/{key}', None)
            if edit_data:
                edit_data['key'] = key
        
        # Update button submitted
        elif 'update_key' in request.form:
            key = request.form['update_key']
            updated = {
                "title": request.form['title'],
                "description": request.form['description'],
                "icon": request.form['icon'],
                "url": request.form.get('url', '')  # Optional
            }
            fb.put('/projects', key, updated)
            flash('Project updated successfully!', 'success')
            return redirect(url_for('admin_project'))
        
        # Add new entry
        else:
            title = request.form.get("title")
            description = request.form.get("description")
            icon = request.form.get("icon")
            url = request.form.get("url", "")  # Optional
            
            if title and description and icon:
                fb.post('/projects', {
                    "title": title,
                    "description": description,
                    "icon": icon,
                    "url": url
                })
                flash('Project added successfully!', 'success')
            
            return redirect(url_for('admin_project'))
    
    projects = fb.get('/projects', None) or {}
    return render_template(
        'admin-project.html',
        projects=projects,
        edit_data=edit_data
    )


@app.route('/delete-project', methods=["POST"])
@login_required
@nocache
def delete_project():
    # Strict validation handled by decorator
    # GUEST GUARD
    if session.get('is_guest'):
        flash("Guest Mode: Read-only access. Changes are not saved.", "warning")
        return redirect(url_for('admin_project'))

    key = request.form.get('key')
    if key:
        fb.delete('/projects', key)
        flash('Project deleted successfully!', 'success')
    return redirect(url_for('admin_project'))


@app.route('/admin-contact', methods=["GET", "POST"])
@login_required
@nocache
def admin_contact():
    # Strict validation handled by decorator
    
    if request.method == "POST":
        # GUEST GUARD
        if session.get('is_guest'):
            flash("Guest Mode: Read-only access. Changes are not saved.", "warning")
            return redirect(url_for('admin_contact'))

        # Get the links data
        links = fb.get('/links/-OOvwHeVJtSsrjh3QnWR/links', None) or {}
        
        # Update contact information
        if 'email' in request.form or 'phone' in request.form:
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            
            links['email'] = email
            links['phone'] = phone
            
            fb.put('/links/-OOvwHeVJtSsrjh3QnWR/links', 'email', email)
            fb.put('/links/-OOvwHeVJtSsrjh3QnWR/links', 'phone', phone)
            
            flash('Contact information updated successfully!', 'success')
            return redirect(url_for('admin_contact'))
        
        # Update social media links
        elif 'linkedin' in request.form or 'github' in request.form or 'telegram' in request.form or 'whatsapp' in request.form:
            linkedin = request.form.get('linkedin', '').strip()
            github = request.form.get('github', '').strip()
            telegram = request.form.get('telegram', '').strip()
            whatsapp = request.form.get('whatsapp', '').strip()
            
            fb.put('/links/-OOvwHeVJtSsrjh3QnWR/links', 'linkedin', linkedin)
            fb.put('/links/-OOvwHeVJtSsrjh3QnWR/links', 'github', github)
            fb.put('/links/-OOvwHeVJtSsrjh3QnWR/links', 'telegram', telegram)
            fb.put('/links/-OOvwHeVJtSsrjh3QnWR/links', 'whatsapp', whatsapp)
            
            flash('Social media links updated successfully!', 'success')
            return redirect(url_for('admin_contact'))

        # Handle Credential Update
        elif request.form.get('action') == 'update_credentials':
            new_username = request.form.get('new_username', '').strip()
            new_password = request.form.get('new_password', '').strip()
            
            updates = {}
            msg_parts = []
            
            if new_username:
                updates['admin_username'] = new_username
                msg_parts.append("Username")
            
            if new_password:
                updates['admin_password'] = new_password
                msg_parts.append("Password")
            
            if updates:
                # Update Firebase
                for key, val in updates.items():
                    fb.put('/links/-OOvwHeVJtSsrjh3QnWR/links', key, val)
                
                # Clear session and redirect to login
                session.clear()
                flash(f"{' and '.join(msg_parts)} updated successfully. Please login with your new credentials.", 'success')
                return redirect(url_for('admin_login'))
            else:
                flash('No changes detected.', 'info')
                return redirect(url_for('admin_contact'))
    
    # Get current contact information
    contact_info = fb.get('/links/-OOvwHeVJtSsrjh3QnWR/links', None) or {}
    
    return render_template('admin-contact.html', contact_info=contact_info)



@app.route('/admin-logout')
def admin_logout():
    # Clear session data
    session.clear()
    
    # Create response to redirect to login
    response = make_response(redirect(url_for('admin_login')))
    
    # Aggressively expire cookies
    response.set_cookie('session', '', expires=0, path='/')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    
    return response

@app.route('/')
def index():
    return redirect(url_for('admin_login')) 

if __name__ == "__main__":
    app.run(port=5001, debug=True)

