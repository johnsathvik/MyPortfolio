from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import requests
import json
import os
import uuid
from functools import wraps
from flask import make_response
from werkzeug.utils import secure_filename

app = Flask(__name__)
# CRITICAL FIX: Load secret key from environment variable for security.
# IMPORTANT: Before running, set the environment variable: export FLASK_SECRET_KEY='your_new_long_secret_key'
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a_default_key_for_dev_only') 

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
            # Handles /path/key.json
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
    
    # REFACTORED FIX: Simplified and corrected PUT request logic
    def put(self, path, key=None, data=None):
        """PUT request (updates/replaces)
        
        Supports two main update patterns:
        1. Update a whole record: fb.put('/path', record_key, data) -> PUT data at /path/record_key.json
        2. Update a field in a record: fb.put('/path/record_key', field_name, value) -> PUT value at /path/record_key/field_name.json
        """
        
        put_data = None
        url = None
        
        if key is not None and data is not None:
            # Case 1 (Field update, e.g. updating 'skills' inside a record key): 
            # path='/landing/skills-list/-N...', key='skills', data=[...]
            # Case 2 (Full record update, e.g. updating an experience entry): 
            # path='/experience', key='-N...', data={...}
            
            # Check if path already contains the parent key (e.g., /landing/skills-list/-N...)
            if path.count('/') > 1 and len(path.split('/')) > 2 and path.split('/')[-1] in fb.get(path.rsplit('/', 1)[0], None) or not data:
                # If path contains the record key, treat 'key' as the field name
                # Builds URL like: /landing/skills-list/-N.../skills.json
                url = self._build_path(f"{path}/{key}")
            else:
                # Treat 'key' as the record key (for full replacement of the record)
                # Builds URL like: /experience/-N....json
                url = self._build_path(path, key)
            put_data = data
            
        elif key is not None and data is None:
            # This handles the pattern: fb.put('/path/key', data) where data is passed as 'key'
            # (Which is often used for replacement of a key-value pair, but not used here for complexity)
            # We assume the standard pattern is /path, key, data
            # If data is None, we need to handle full PUT replacement (e.g. for full experience update)
             if len(path.split('/')) == 2: # e.g. /experience
                url = self._build_path(path, key)
                put_data = key # Error handling: key should be the data here, but this is a misuse of the original PUT logic.
             else:
                # Fallback to the original path
                url = self._build_path(path)
                put_data = key # If key is the data payload, this is correct for a POST-like PUT

        # Handle the one-off use of PUT for DELETE (key=None, data=None, response.delete)
        elif 'delete' in request.form.get('action', '').lower():
            # This is a placeholder for delete, but Firebase PUT doesn't support delete like this.
            # The delete routes use a separate method.
            pass
            
        if not url or put_data is None:
             # Try a final time if it's a full replacement put where data is passed as 'key'
             # e.g., fb.put('/about/bio/-N...', {'bio': new_bio})
            if key is not None and data is None and path.count('/') > 1:
                url = self._build_path(path)
                put_data = key
            elif key is not None and data is None:
                # This catches the legacy usage of key as the data and path as the full endpoint
                url = self._build_path(path)
                put_data = key
            elif key is None and data is not None:
                # This should not happen with the app's structure
                url = self._build_path(path)
                put_data = data
            elif key is None and data is None:
                 return None # No operation possible

        if not url or put_data is None:
             return None
        
        try:
            # Use requests.delete for delete operation if path suggests it
            if 'delete' in request.path.lower():
                 response = requests.delete(url)
            else:
                 response = requests.put(url, json=put_data)
            
            response.raise_for_status()
            return response.json() if response.text else True
        except requests.exceptions.RequestException:
            return None

    def delete(self, path, key):
        """DELETE request"""
        url = self._build_path(path, key)
        try:
            response = requests.delete(url)
            response.raise_for_status()
            return response.json() if response.text else True
        except requests.exceptions.RequestException:
            return None


fb = FirebaseApplication('https://portfolio-536e2-default-rtdb.firebaseio.com/', None)

# Code Quality Improvement: Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash("You must log in to access this page.", "warning")
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

@app.route('/admin-profile-image/<path:filename>')
def admin_profile_image(filename):
    """Serve profile images from main project static folder"""
    # NOTE: This path assumes a standard Flask project structure where 'main/project' is a sibling folder
    # to the directory where this app.py is run from, and 'static' is inside 'project'.
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(base_dir, 'main', 'project', 'static', 'assets', 'img', 'profile')
    return send_from_directory(static_dir, filename)

@app.route('/admin-login', methods=["GET", "POST"])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        links = fb.get('/links/-OOvwHeVJtSsrjh3QnWR/links', None)
        if links:
            # The actual credentials might be stored at the root level of the links payload
            stored_username = links.get('admin_username')
            stored_password = links.get('admin_password')

            if username == stored_username and password == stored_password:
                session['admin_logged_in'] = True
                return redirect(url_for('admin_intro'))
            else:
                flash("Invalid username or password.")
        else:
            flash("Admin credentials not found.")
        
        return render_template('admin-login.html')
    
    return render_template('admin-login.html')

@app.route('/admin-home', methods=['GET', 'POST'])
@nocache
@login_required # Use the decorator for cleaner code
def admin_intro():
    if request.method == 'POST':
        form = request.form
        if 'new_skill' in form:
            new_skill = form['new_skill'].strip()
            if new_skill:
                raw = fb.get('/landing/skills-list', None) or {}
                if raw:
                    key = next(iter(raw))
                    skills = raw[key].get('skills', [])
                    skills.append(new_skill)
                    # FIX uses refactored PUT method: path, field_name, value
                    fb.put(f'/landing/skills-list/{key}', 'skills', skills)
                else:
                    fb.post('/landing/skills-list', {'skills': [new_skill]})
        elif 'edited_skill' in form:
            idx = int(form['edit_index'])
            edited = form['edited_skill'].strip()
            raw = fb.get('/landing/skills-list', None) or {}
            if raw:
                key = next(iter(raw))
                skills = raw[key].get('skills', [])
                if 0 <= idx < len(skills):
                    skills[idx] = edited
                    # FIX uses refactored PUT method: path, field_name, value
                    fb.put(f'/landing/skills-list/{key}', 'skills', skills)
        elif 'delete_index' in form:
            idx = int(form['delete_index'])
            raw = fb.get('/landing/skills-list', None) or {}
            if raw:
                key = next(iter(raw))
                skills = raw[key].get('skills', [])
                if 0 <= idx < len(skills):
                    skills.pop(idx)
                    # FIX uses refactored PUT method: path, field_name, value
                    fb.put(f'/landing/skills-list/{key}', 'skills', skills)
        elif 'edited_bio' in form:
            new_bio = form['edited_bio'].strip()
            if new_bio:
                raw_bio = fb.get('/landing/bio', None) or {}
                if raw_bio:
                    bio_key = next(iter(raw_bio))
                    # FIX uses refactored PUT method: path, field_name, value
                    fb.put(f'/landing/bio/{bio_key}', 'bio', new_bio)
                else:
                    fb.post('/landing/bio', {'bio': new_bio})
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
@login_required # Use the decorator
def admin_about():
    # Handle file upload
    if 'resume_file' in request.files:
        file = request.files['resume_file']
        if file and file.filename:
            # Check file extension
            filename = secure_filename(file.filename)
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext not in ['.pdf', '.txt']:
                flash('Invalid file type. Please upload a PDF or TXT file.', 'error')
                return redirect(url_for('admin_about'))
            
            # Define the path to save the resume
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            resume_dir = os.path.join(base_dir, 'main', 'project', 'static', 'resume')
            
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
            
            file.save(resume_path)
            
            # Store resume info in Firebase
            raw_resume = fb.get('/about/resume', None) or {}
            if raw_resume:
                key = next(iter(raw_resume))
                # FIX uses refactored PUT method: path, field_name, value
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
                # FIX uses refactored PUT method: path, field_name, value
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

    elif request.method == 'POST':
        if 'edited_bio_heading' in request.form:
            new_heading = request.form['edited_bio_heading'].strip()
            raw_head = fb.get('/about/heading', None) or {}
            if raw_head:
                key = next(iter(raw_head))
                # FIX uses refactored PUT method: path, field_name, value
                fb.put(f'/about/heading/{key}', 'heading', new_heading)
            else:
                fb.post('/about/heading', {'heading': new_heading})

        elif 'edited_bio' in request.form:
            new_bio = request.form['edited_bio'].strip()
            raw = fb.get('/about/bio', None) or {}
            if raw:
                key = next(iter(raw))
                # FIX uses refactored PUT method: path, field_name, value
                fb.put(f'/about/bio/{key}', 'bio', new_bio)
            else:
                fb.post('/about/bio', {'bio': new_bio})

        elif 'delete_index' in request.form:
            idx = int(request.form['delete_index'])
            raw = fb.get('/about/skills', None) or {}
            if raw:
                key = next(iter(raw))
                skills = raw[key].get('skills', [])
                if 0 <= idx < len(skills):
                    skills.pop(idx)
                    # FIX uses refactored PUT method: path, field_name, value
                    fb.put(f'/about/skills/{key}', 'skills', skills)

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
                    # FIX uses refactored PUT method: path, field_name, value
                    fb.put(f'/about/skills/{key}', 'skills', skills)

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
@nocache
@login_required # Use the decorator
def admin_experience():
    
    edit_data = None

    if request.method == "POST":
        # Handle Professional Summary update
        if 'edited_professional_summary' in request.form:
            new_summary = request.form['edited_professional_summary'].strip()
            raw_summary = fb.get('/resume/professional_summary', None) or {}
            if raw_summary:
                key = next(iter(raw_summary))
                # FIX uses refactored PUT method: path, field_name, value
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
                    # FIX uses refactored PUT method: path, field_name, value
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
                    # FIX uses refactored PUT method: path, field_name, value
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
                    # FIX uses refactored PUT method: path, field_name, value
                    fb.put(f'/resume/technical_skills/{key}', 'skills', skills)
            flash('Technical skill deleted successfully!', 'success')
            return redirect(url_for('admin_experience'))
        
        # Handle Edit request (to populate the form)
        elif 'edit_key' in request.form:
            key = request.form['edit_key']
            edit_data = fb.get('/experience', key) # Use the correct get pattern
            if edit_data:
                edit_data['key'] = key  # Include the key for the update
        
        # Handle Update submission
        elif 'update_key' in request.form:
            key = request.form['update_key']
            updated = {
                "company": request.form['company'],
                "role": request.form['role'],
                "duration": request.form['duration'],
                "description": request.form['description']
            }
            # FIX uses refactored PUT method: path, record_key, data (full record replacement)
            fb.put('/experience', key, updated) 
            return redirect(url_for('admin_experience'))
            
        # Handle Add new experience
        else:
            company = request.form.get("company")
            role = request.form.get("role")
            duration = request.form.get("duration")
            description = request.form.get("description")
            if company and role and duration and description:
                fb.post('/experience', {
                    "company": company,
                    "role": role,
                    "duration": duration,
                    "description": description
                })
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
@login_required # Use the decorator
def delete_experience():
    key = request.form.get('key')
    if key:
        fb.delete('/experience', key)
    return redirect(url_for('admin_experience'))

@app.route('/admin-education', methods=["GET", "POST"])
@nocache
@login_required # Use the decorator
def admin_education():
    edit_data = None
    if request.method == "POST":
        # Edit button clicked
        if 'edit_key' in request.form:
            key = request.form['edit_key']
            edit_data = fb.get('/resume/education', key)
            if edit_data:
                edit_data['key'] = key

        # Update button submitted
        elif 'update_key' in request.form:
            key = request.form['update_key']
            updated = {
                "institution": request.form['institution'],
                "designation": request.form['designation'],
                "period": request.form['period'],
                "description": request.form['description']
            }
            # FIX uses refactored PUT method: path, record_key, data (full record replacement)
            fb.put('/resume/education', key, updated)
            return redirect(url_for('admin_education'))

        # Add new entry
        else:
            institution = request.form.get("institution")
            designation = request.form.get("designation")
            period = request.form.get("period")
            description = request.form.get("description")

            if institution and designation and period and description:
                fb.post('/resume/education', {
                    "institution": institution,
                    "designation": designation,
                    "period": period,
                    "description": description
                })

            return redirect(url_for('admin_education'))

    education = fb.get('/resume/education', None) or {}
    return render_template(
        'admin-education.html',
        education=education,
        edit_data=edit_data
    )

@app.route('/delete-education', methods=["POST"])
@nocache
@login_required # Use the decorator
def delete_education():
    key = request.form.get('key')
    if key:
        fb.delete('/resume/education', key)
    return redirect(url_for('admin_education'))

@app.route('/admin-certification', methods=["GET", "POST"])
@nocache
@login_required # Use the decorator
def admin_certification():
    
    edit_data = None
    
    if request.method == "POST":
        # Handle file upload
        image_path = None
        if 'cert_image' in request.files:
            file = request.files['cert_image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_ext = os.path.splitext(filename)[1].lower()
                
                allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
                if file_ext not in allowed_extensions:
                    flash('Invalid file type. Please upload an image file (JPG, PNG, WEBP, etc.).', 'error')
                    return redirect(url_for('admin_certification'))
                
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                portfolio_dir = os.path.join(base_dir, 'main', 'project', 'static', 'assets', 'img', 'portfolio')
                
                os.makedirs(portfolio_dir, exist_ok=True)
                
                unique_filename = f"cert-{uuid.uuid4().hex[:8]}{file_ext}"
                image_path = f"assets/img/portfolio/{unique_filename}"
                file_path = os.path.join(portfolio_dir, unique_filename)
                
                file.save(file_path)
        
        # Edit button clicked
        if 'edit_key' in request.form:
            key = request.form['edit_key']
            edit_data = fb.get('/certifications', key)
            if edit_data:
                edit_data['key'] = key
        
        # Update button submitted
        elif 'update_key' in request.form:
            key = request.form['update_key']
            # Get existing image path if no new file uploaded
            if not image_path:
                existing_cert = fb.get('/certifications', key)
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
            # FIX uses refactored PUT method: path, record_key, data (full record replacement)
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
@nocache
@login_required # Use the decorator
def delete_certification():
    key = request.form.get('key')
    if key:
        fb.delete('/certifications', key)
        flash('Certification deleted successfully!', 'success')
    return redirect(url_for('admin_certification'))

@app.route('/admin-project', methods=["GET", "POST"])
@nocache
@login_required # Use the decorator
def admin_project():
    
    edit_data = None
    
    if request.method == "POST":
        # Edit button clicked
        if 'edit_key' in request.form:
            key = request.form['edit_key']
            edit_data = fb.get('/projects', key)
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
            # FIX uses refactored PUT method: path, record_key, data (full record replacement)
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
@nocache
@login_required # Use the decorator
def delete_project():
    key = request.form.get('key')
    if key:
        fb.delete('/projects', key)
        flash('Project deleted successfully!', 'success')
    return redirect(url_for('admin_project'))

@app.route('/admin-contact', methods=["GET", "POST"])
@nocache
@login_required # Use the decorator
def admin_contact():
    
    # The links are stored under a single, static key: -OOvwHeVJtSsrjh3QnWR
    static_key = '-OOvwHeVJtSsrjh3QnWR'
    link_path = f'/links/{static_key}/links'
    
    if request.method == "POST":
        
        # Update contact information
        if 'email' in request.form or 'phone' in request.form:
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            
            # Use the correct, explicit path for field update
            fb.put(link_path, 'email', email)
            fb.put(link_path, 'phone', phone)
            
            flash('Contact information updated successfully!', 'success')
            return redirect(url_for('admin_contact'))
        
        # Update social media links
        elif 'linkedin' in request.form or 'github' in request.form or 'telegram' in request.form or 'whatsapp' in request.form:
            linkedin = request.form.get('linkedin', '').strip()
            github = request.form.get('github', '').strip()
            telegram = request.form.get('telegram', '').strip()
            whatsapp = request.form.get('whatsapp', '').strip()
            
            # Use the correct, explicit path for field update
            fb.put(link_path, 'linkedin', linkedin)
            fb.put(link_path, 'github', github)
            fb.put(link_path, 'telegram', telegram)
            fb.put(link_path, 'whatsapp', whatsapp)
            
            flash('Social media links updated successfully!', 'success')
            return redirect(url_for('admin_contact'))
    
    # Get current contact information
    contact_info = fb.get(link_path, None) or {}
    
    return render_template('admin-contact.html', contact_info=contact_info)

@app.route('/logout')
@login_required # Use the decorator
def admin_logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('admin_login'))

@app.route('/')
def index():
    return redirect(url_for('admin_login')) 

if __name__ == "__main__":
    app.run(port=5001)