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
        
        return render_template('admin-login.html')
    
    return render_template('admin-login.html')




@app.route('/admin-home', methods=['GET', 'POST'])
@login_required
@nocache
def admin_intro():
    # Strict validation handled by decorator


    if request.method == 'POST':
        # GUEST GUARD
        if session.get('is_guest'):
            flash("Guest Mode: Read-only access. Changes are not saved.", "warning")
            return redirect(request.url)

        if request.is_json:
            data = request.get_json()
            if 'reorder_skills' in data:
                # GUEST GUARD
                if session.get('is_guest'):
                    return {'status': 'guest_mode', 'message': "Guest Mode: Changes simulated."}, 200
                
                new_order = data['reorder_skills']
                if isinstance(new_order, list) and new_order:
                    raw = fb.get('/landing/skills-list', None) or {}
                    if raw:
                        key = next(iter(raw))
                        fb.put(f'/landing/skills-list/{key}', 'skills', new_order)
                        return {'status': 'success'}, 200
                    else:
                         return {'status': 'error', 'message': 'No skills found'}, 400

        form = request.form
        if 'new_skill' in form:
            new_skill = form['new_skill'].strip()
            if new_skill:
                raw = fb.get('/landing/skills-list', None) or {}
                if raw:
                    key = next(iter(raw))
                    skills = raw[key].get('skills', [])
                    skills.append(new_skill)
                    fb.put(f'/landing/skills-list/{key}', 'skills', skills)
                else:
                    fb.post('/landing/skills-list', {'skills': [new_skill]})
                flash('Skill added successfully!', 'success')
        elif 'edited_skill' in form:
            idx = int(form['edit_index'])
            edited = form['edited_skill'].strip()
            raw = fb.get('/landing/skills-list', None) or {}
            if raw:
                key = next(iter(raw))
                skills = raw[key].get('skills', [])
                if 0 <= idx < len(skills):
                    skills[idx] = edited
                    fb.put(f'/landing/skills-list/{key}', 'skills', skills)
                    flash('Skill updated successfully!', 'success')
        elif 'delete_index' in form:
            idx = int(form['delete_index'])
            raw = fb.get('/landing/skills-list', None) or {}
            if raw:
                key = next(iter(raw))
                skills = raw[key].get('skills', [])
                if 0 <= idx < len(skills):
                    skills.pop(idx)
                    fb.put(f'/landing/skills-list/{key}', 'skills', skills)
                    flash('Skill deleted successfully!', 'success')
        elif 'edited_bio' in form:
            new_bio = form['edited_bio'].strip()
            if new_bio:
                raw_bio = fb.get('/landing/bio', None) or {}
                if raw_bio:
                    bio_key = next(iter(raw_bio))
                    fb.put(f'/landing/bio/{bio_key}', 'bio', new_bio)
                else:
                    fb.post('/landing/bio', {'bio': new_bio})
                flash('Bio updated successfully!', 'success')
        return redirect(url_for('admin_intro'))

    raw = fb.get('/landing/skills-list', None) or {}
    skills = []
    for block in raw.values():
        skills.extend(block.get('skills', []))

    raw_bio = fb.get('/landing/bio', None) or {}
    bio = next(iter(raw_bio.values())).get('bio', '') if raw_bio else ''

    # Get profile image path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    profile_image_path = os.path.join(base_dir, 'main', 'project', 'static', 'assets', 'img', 'profile', 'main.jpg')
    profile_image_url = url_for('admin_profile_image', filename='main.jpg') if os.path.exists(profile_image_path) else None

    return render_template('admin-home.html', skills=skills, bio=bio, profile_image_url=profile_image_url)



@app.route('/admin-about', methods=['GET', 'POST'])
@login_required
def admin_about():
    # Strict validation handled by decorator

    # Handle file upload
    if 'resume_file' in request.files:
        # GUEST GUARD
        if session.get('is_guest'):
            flash("Guest Mode: Read-only access. Changes are not saved.", "warning")
            return redirect(request.url)

        file = request.files['resume_file']
        if file and file.filename:
            # Check file extension
            filename = secure_filename(file.filename)
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext not in ['.pdf', '.txt']:
                flash('Invalid file type. Please upload a PDF or TXT file.', 'error')
                return redirect(url_for('admin_about'))
            
            # Define the path to save the resume
            # Path to main project's static/resume folder
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            resume_dir = os.path.join(base_dir, 'main', 'project', 'static', 'resume')
            
            # Create directory if it doesn't exist
            os.makedirs(resume_dir, exist_ok=True)
            
            # Save file as Resume.pdf or Resume.txt
            resume_filename = f'Resume{file_ext}'
            resume_path = os.path.join(resume_dir, resume_filename)
            
            # Remove old resume files if they exist
            old_pdf = os.path.join(resume_dir, 'Resume.pdf')
            old_txt = os.path.join(resume_dir, 'Resume.txt')
            if os.path.exists(old_pdf) and resume_filename != 'Resume.pdf':
                os.remove(old_pdf)
            if os.path.exists(old_txt) and resume_filename != 'Resume.txt':
                os.remove(old_txt)
            
            # Save the new file
            file.save(resume_path)
            
            # Store resume info in Firebase
            raw_resume = fb.get('/about/resume', None) or {}
            if raw_resume:
                key = next(iter(raw_resume))
                fb.put(f'/about/resume/{key}', 'filename', resume_filename)
                fb.put(f'/about/resume/{key}', 'file_type', file_ext[1:].upper())
            else:
                fb.post('/about/resume', {
                    'filename': resume_filename,
                    'file_type': file_ext[1:].upper()
                })
            
            flash('Resume uploaded successfully!', 'success')
            return redirect(url_for('admin_about'))

    if 'new_title' in request.form:
        # GUEST GUARD
        if session.get('is_guest'):
            flash("Guest Mode: Read-only access. Changes are not saved.", "warning")
            return redirect(request.url)

        title = request.form['new_title'].strip()
        desc = request.form['new_description'].strip()
        pct = int(request.form['new_percentage'])
        category = request.form.get('new_category', 'Cloud & DevOps').strip()
        if title and desc and 0 <= pct <= 100:
            raw = fb.get('/about/skills', None) or {}
            if raw:
                key = next(iter(raw))
                skills = raw[key].get('skills', [])
                skills.append({
                    'Skill': title,
                    'Description': desc,
                    'percentage': pct,
                    'category': category
                })
                fb.put(f'/about/skills/{key}', 'skills', skills)
            else:
                fb.post('/about/skills', {
                    'skills': [{
                        'Skill': title,
                        'Description': desc,
                        'percentage': pct,
                        'category': category
                    }]
                })
            flash('Skill added successfully!', 'success')

    elif request.method == 'POST':
        # GUEST GUARD
        if session.get('is_guest'):
            flash("Guest Mode: Read-only access. Changes are not saved.", "warning")
            return redirect(request.url)

        if 'edited_bio_heading' in request.form:
            new_heading = request.form['edited_bio_heading'].strip()
            raw_head = fb.get('/about/heading', None) or {}
            if raw_head:
                key = next(iter(raw_head))
                fb.put(f'/about/heading/{key}', 'heading', new_heading)
            else:
                fb.post('/about/heading', {'heading': new_heading})
            flash('About heading updated successfully!', 'success')

        elif 'edited_bio' in request.form:
            new_bio = request.form['edited_bio'].strip()
            raw = fb.get('/about/bio', None) or {}
            if raw:
                key = next(iter(raw))
                fb.put(f'/about/bio/{key}', 'bio', new_bio)
            else:
                fb.post('/about/bio', {'bio': new_bio})
            flash('About bio updated successfully!', 'success')

        elif 'delete_index' in request.form:
            idx = int(request.form['delete_index'])
            raw = fb.get('/about/skills', None) or {}
            if raw:
                key = next(iter(raw))
                skills = raw[key].get('skills', [])
                if 0 <= idx < len(skills):
                    skills.pop(idx)
                    fb.put(f'/about/skills/{key}', 'skills', skills)
                    flash('Skill deleted successfully!', 'success')

        elif 'edited_skill' in request.form and 'edited_description' in request.form and 'edited_percentage' in request.form:
            idx   = int(request.form['edit_index'])
            title = request.form['edited_skill'].strip()
            desc  = request.form['edited_description'].strip()
            pct   = int(request.form['edited_percentage'])
            category = request.form.get('edited_category', 'Cloud & DevOps').strip()
            raw   = fb.get('/about/skills', None) or {}
            if raw:
                key    = next(iter(raw))
                skills = raw[key].get('skills', [])
                if 0 <= idx < len(skills):
                    skills[idx]['Skill']       = title
                    skills[idx]['Description'] = desc
                    skills[idx]['percentage']  = pct
                    skills[idx]['category']    = category
                    fb.put(f'/about/skills/{key}', 'skills', skills)
                    flash('Skill updated successfully!', 'success')

        return redirect(url_for('admin_about'))

    raw_bio = fb.get('/about/bio', None) or {}
    bio = next(iter(raw_bio.values())).get('bio', '') if raw_bio else ''

    raw_head = fb.get('/about/heading', None) or {}
    heading = next(iter(raw_head.values())).get('heading', '') if raw_head else ''

    raw_skills = fb.get('/about/skills', None) or {}
    skills = []
    for block in raw_skills.values():
        skills.extend(block.get('skills', []))

    # Get resume info
    raw_resume = fb.get('/about/resume', None) or {}
    current_resume = None
    resume_type = None
    if raw_resume:
        resume_data = next(iter(raw_resume.values()))
        current_resume = resume_data.get('filename', '')
        resume_type = resume_data.get('file_type', '')

    return render_template('admin-about.html', bio=bio, heading=heading, skills=skills, current_resume=current_resume, resume_type=resume_type)



@app.route('/admin-experience', methods=["GET", "POST"])
@login_required
@nocache
def admin_experience():
    # Strict validation handled by decorator
    
    edit_data = None

    if request.method == "POST":
        # GUEST GUARD
        if session.get('is_guest'):
            flash("Guest Mode: Read-only access. Changes are not saved.", "warning")
            return redirect(request.url)

        # Handle Professional Summary update
        if 'edited_professional_summary' in request.form:
            new_summary = request.form['edited_professional_summary'].strip()
            raw_summary = fb.get('/resume/professional_summary', None) or {}
            if raw_summary:
                key = next(iter(raw_summary))
                fb.put(f'/resume/professional_summary/{key}', 'summary', new_summary)
            else:
                fb.post('/resume/professional_summary', {'summary': new_summary})
            flash('Professional Summary updated successfully!', 'success')
            return redirect(url_for('admin_experience'))
        
        # Handle Add Technical Skill
        elif 'new_tech_skill_name' in request.form:
            skill_name = request.form['new_tech_skill_name'].strip()
            skill_pct = int(request.form['new_tech_skill_percentage'])
            if skill_name and 0 <= skill_pct <= 100:
                raw = fb.get('/resume/technical_skills', None) or {}
                if raw:
                    key = next(iter(raw))
                    skills = raw[key].get('skills', [])
                    skills.append({
                        'name': skill_name,
                        'percentage': skill_pct
                    })
                    fb.put(f'/resume/technical_skills/{key}', 'skills', skills)
                else:
                    fb.post('/resume/technical_skills', {
                        'skills': [{
                            'name': skill_name,
                            'percentage': skill_pct
                        }]
                    })
            flash('Technical skill added successfully!', 'success')
            return redirect(url_for('admin_experience'))
        
        # Handle Edit Technical Skill
        elif 'edited_tech_skill_name' in request.form and 'edited_tech_skill_percentage' in request.form:
            idx = int(request.form['edit_tech_skill_index'])
            skill_name = request.form['edited_tech_skill_name'].strip()
            skill_pct = int(request.form['edited_tech_skill_percentage'])
            raw = fb.get('/resume/technical_skills', None) or {}
            if raw:
                key = next(iter(raw))
                skills = raw[key].get('skills', [])
                if 0 <= idx < len(skills):
                    skills[idx]['name'] = skill_name
                    skills[idx]['percentage'] = skill_pct
                    fb.put(f'/resume/technical_skills/{key}', 'skills', skills)
            flash('Technical skill updated successfully!', 'success')
            return redirect(url_for('admin_experience'))
        
        # Handle Delete Technical Skill
        elif 'delete_tech_skill_index' in request.form:
            idx = int(request.form['delete_tech_skill_index'])
            raw = fb.get('/resume/technical_skills', None) or {}
            if raw:
                key = next(iter(raw))
                skills = raw[key].get('skills', [])
                if 0 <= idx < len(skills):
                    skills.pop(idx)
                    fb.put(f'/resume/technical_skills/{key}', 'skills', skills)
            flash('Technical skill deleted successfully!', 'success')
            return redirect(url_for('admin_experience'))
        
        # Handle Edit request
        elif 'edit_key' in request.form:
            key = request.form['edit_key']
            edit_data = fb.get(f'/experience/{key}', None)
            if edit_data:
                edit_data['key'] = key  # Include the key for the update
        
        # Handle Update submission
        elif 'update_key' in request.form:
            key = request.form['update_key']
            updated = {
                "company": request.form['company'],
                "role": request.form['role'],
                "duration": request.form['duration'],
                "location": request.form.get('location', ''),
                "description": request.form['description']
            }
            fb.put('/experience', key, updated)
            flash('Experience updated successfully!', 'success')
            return redirect(url_for('admin_experience'))
        # Handle Add new experience
        else:
            company = request.form.get("company")
            role = request.form.get("role")
            duration = request.form.get("duration")
            location = request.form.get("location", "")
            description = request.form.get("description")
            if company and role and duration and description:
                fb.post('/experience', {
                    "company": company,
                    "role": role,
                    "duration": duration,
                    "location": location,
                    "description": description
                })
                flash('Experience added successfully!', 'success')
            return redirect(url_for('admin_experience'))

    # Get Professional Summary
    professional_summary = ''
    try:
        raw_summary = fb.get('/resume/professional_summary', None) or {}
        if raw_summary:
            summary_data = next(iter(raw_summary.values()))
            if isinstance(summary_data, dict):
                professional_summary = summary_data.get('summary', '')
    except Exception as e:
        print(f"Error getting professional summary: {e}")
        professional_summary = ''
    
    # Get Technical Skills
    technical_skills = []
    try:
        raw_tech_skills = fb.get('/resume/technical_skills', None) or {}
        if raw_tech_skills:
            for block in raw_tech_skills.values():
                if isinstance(block, dict) and 'skills' in block:
                    if isinstance(block.get('skills'), list):
                        technical_skills.extend(block.get('skills', []))
    except Exception as e:
        print(f"Error getting technical skills: {e}")
        technical_skills = []

    experiences = fb.get('/experience', None) or {}
    
    # Ensure variables are always defined
    if professional_summary is None:
        professional_summary = ''
    if technical_skills is None:
        technical_skills = []
    if edit_data is None:
        edit_data = None
    
    return render_template('admin-experience.html', 
                         experiences=experiences, 
                         edit_data=edit_data,
                         professional_summary=professional_summary,
                         technical_skills=technical_skills)


@app.route('/delete-experience', methods=['POST'])
@nocache
def delete_experience():
    # GUEST GUARD
    if session.get('is_guest'):
        flash("Guest Mode: Read-only access. Changes are not saved.", "warning")
        return redirect(url_for('admin_experience'))

    key = request.form.get('key')
    if key:
        fb.delete('/experience', key)
        flash('Experience deleted successfully!', 'success')
    return redirect(url_for('admin_experience'))



@app.route('/admin-education', methods=["GET", "POST"])
@login_required
@nocache
def admin_education():
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
            edit_data = fb.get(f'/resume/education/{key}', None)
            if edit_data:
                edit_data['key'] = key

        # Update button submitted
        elif 'update_key' in request.form:
            key = request.form['update_key']
            updated = {
                "institution": request.form['institution'],
                "designation": request.form['designation'],
                "period": request.form['period'],
                "location": request.form.get('location', ''),
                "description": request.form['description']
            }
            fb.put('/resume/education', key, updated)
            flash('Education updated successfully!', 'success')
            return redirect(url_for('admin_education'))

        # Add new entry
        else:
            institution = request.form.get("institution")
            designation = request.form.get("designation")
            period = request.form.get("period")
            location = request.form.get("location", "")
            description = request.form.get("description")

            if institution and designation and period and description:
                fb.post('/resume/education', {
                    "institution": institution,
                    "designation": designation,
                    "period": period,
                    "location": location,
                    "description": description
                })
                flash('Education added successfully!', 'success')

            return redirect(url_for('admin_education'))

    education = fb.get('/resume/education', None) or {}
    return render_template(
        'admin-education.html',
        education=education,
        edit_data=edit_data
    )


@app.route('/delete-education', methods=["POST"])
@login_required
@nocache
def delete_education():
    # Strict validation handled by decorator
    # GUEST GUARD
    if session.get('is_guest'):
        flash("Guest Mode: Read-only access. Changes are not saved.", "warning")
        return redirect(url_for('admin_education'))

    key = request.form.get('key')
    if key:
        fb.delete('/resume/education', key)
        flash('Education deleted successfully!', 'success')
    return redirect(url_for('admin_education'))


@app.route('/admin-certification', methods=["GET", "POST"])
@login_required
@nocache
def admin_certification():
    # Strict validation handled by decorator
    
    edit_data = None
    
    if request.method == "POST":
        # GUEST GUARD
        if session.get('is_guest'):
            flash("Guest Mode: Read-only access. Changes are not saved.", "warning")
            return redirect(request.url)

        # Handle file upload
        image_path = None
        if 'cert_image' in request.files:
            file = request.files['cert_image']
            if file and file.filename:
                # Get file extension
                filename = secure_filename(file.filename)
                file_ext = os.path.splitext(filename)[1].lower()
                
                # Validate file type
                allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
                if file_ext not in allowed_extensions:
                    flash('Invalid file type. Please upload an image file (JPG, PNG, WEBP, etc.).', 'error')
                    return redirect(url_for('admin_certification'))
                
                # Define the path to save the image
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                portfolio_dir = os.path.join(base_dir, 'main', 'project', 'static', 'assets', 'img', 'portfolio')
                
                # Create directory if it doesn't exist
                os.makedirs(portfolio_dir, exist_ok=True)
                
                # Generate unique filename
                unique_filename = f"cert-{uuid.uuid4().hex[:8]}{file_ext}"
                image_path = f"assets/img/portfolio/{unique_filename}"
                file_path = os.path.join(portfolio_dir, unique_filename)
                
                # Save the file
                file.save(file_path)
        
        # Edit button clicked
        if 'edit_key' in request.form:
            key = request.form['edit_key']
            edit_data = fb.get(f'/certifications/{key}', None)
            if edit_data:
                edit_data['key'] = key
        
        # Update button submitted
        elif 'update_key' in request.form:
            key = request.form['update_key']
            # Get existing image path if no new file uploaded
            if not image_path:
                existing_cert = fb.get(f'/certifications/{key}', None)
                if existing_cert:
                    image_path = existing_cert.get('image', '')
                else:
                    flash('Error: Could not find existing certification.', 'error')
                    return redirect(url_for('admin_certification'))
            
            updated = {
                "title": request.form['title'],
                "image": image_path,
                "filter": request.form['filter'],
                "url": request.form.get('url', '')  # Optional
            }
            fb.put('/certifications', key, updated)
            flash('Certification updated successfully!', 'success')
            return redirect(url_for('admin_certification'))
        
        # Add new entry
        else:
            title = request.form.get("title")
            filter_category = request.form.get("filter")
            url = request.form.get("url", "")  # Optional
            
            if title and filter_category and image_path:
                fb.post('/certifications', {
                    "title": title,
                    "image": image_path,
                    "filter": filter_category,
                    "url": url
                })
                flash('Certification added successfully!', 'success')
            else:
                flash('Please fill in all required fields and upload an image.', 'error')
            
            return redirect(url_for('admin_certification'))
    
    certifications = fb.get('/certifications', None) or {}
    return render_template(
        'admin-certification.html',
        certifications=certifications,
        edit_data=edit_data
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

