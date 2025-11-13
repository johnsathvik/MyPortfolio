from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify
import os, json
import requests

app = Flask(__name__)

# Firebase wrapper class to connect to Firebase Realtime Database
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
        """GET request to fetch data from Firebase"""
        url = self._build_path(path, key)
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json() if response.text else None
        except requests.exceptions.RequestException:
            return None

# Initialize Firebase connection (same database as admin)
fb = FirebaseApplication('https://portfolio-536e2-default-rtdb.firebaseio.com/', None)

# --- Home Page ---
@app.route('/')
def home():
    try:
        # Fetch all data from Firebase (same structure as admin uses)
        landing_data = fb.get('/landing', None) or {}
        about_data = fb.get('/about', None) or {}
        experience_data = fb.get('/experience', None) or {}
        education_data = fb.get('/resume/education', None) or {}
        links = fb.get('/links/-OOvwHeVJtSsrjh3QnWR/links', None) or {}

        # Extract contact/social links
        email = links.get('email', '') if isinstance(links, dict) else ''
        phone = links.get('phone', '') if isinstance(links, dict) else ''
        linkedin = links.get('linkedin', '') if isinstance(links, dict) else ''
        telegram = links.get('telegram', '') if isinstance(links, dict) else ''
        whatsapp = links.get('whatsapp', '') if isinstance(links, dict) else ''
        github = links.get('github', '') if isinstance(links, dict) else ''

        # Extract skills from landing page (for typed items)
        raw_skills = landing_data.get('skills-list', {}) if isinstance(landing_data, dict) else {}
        skills = []
        if isinstance(raw_skills, dict):
            for block in raw_skills.values():
                if isinstance(block, dict) and 'skills' in block:
                    if isinstance(block.get('skills'), list):
                        skills.extend(block.get('skills', []))
        
        # Format skills for typed.js (comma-separated string)
        typed_items = ', '.join(skills) if skills else 'AWS Solutions Architect, Web Developer, Cloud Enthusiast'

        # Extract bio from landing page
        raw_bio = landing_data.get('bio', {}) if isinstance(landing_data, dict) else {}
        bio = ''
        if isinstance(raw_bio, dict) and raw_bio:
            try:
                bio_value = next(iter(raw_bio.values()))
                if isinstance(bio_value, dict):
                    bio = bio_value.get('bio', '')
                elif isinstance(bio_value, str):
                    bio = bio_value
            except (StopIteration, AttributeError):
                bio = ''

        # Extract about section data
        about_bio = ''
        about_heading = ''
        if isinstance(about_data, dict):
            raw_about_bio = about_data.get('bio', {})
            if isinstance(raw_about_bio, dict) and raw_about_bio:
                try:
                    bio_val = next(iter(raw_about_bio.values()))
                    if isinstance(bio_val, dict):
                        about_bio = bio_val.get('bio', '')
                    elif isinstance(bio_val, str):
                        about_bio = bio_val
                except (StopIteration, AttributeError):
                    pass
            
            raw_about_heading = about_data.get('heading', {})
            if isinstance(raw_about_heading, dict) and raw_about_heading:
                try:
                    heading_val = next(iter(raw_about_heading.values()))
                    if isinstance(heading_val, dict):
                        about_heading = heading_val.get('heading', '')
                    elif isinstance(heading_val, str):
                        about_heading = heading_val
                except (StopIteration, AttributeError):
                    pass

        # Extract about skills
        about_skills = []
        if isinstance(about_data, dict):
            raw_about_skills = about_data.get('skills', {})
            if isinstance(raw_about_skills, dict):
                for block in raw_about_skills.values():
                    if isinstance(block, dict) and 'skills' in block:
                        if isinstance(block.get('skills'), list):
                            about_skills.extend(block.get('skills', []))

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
            professional_summary = 'AWS Solutions Architect (Associate Certified) with strong expertise in designing and deploying scalable, secure, and fault-tolerant cloud architectures. Experienced in building 3-tier AWS applications, automation, and full-stack web solutions with measurable business impact. Adept at bridging technical design with client requirements to deliver cost-optimized, resilient systems.'
        
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
            # Default technical skills if none found
            technical_skills = [
                {'name': 'Cloud & DevOps', 'percentage': 95},
                {'name': 'Programming & Scripting', 'percentage': 85},
                {'name': 'Databases', 'percentage': 90},
                {'name': 'Web Development', 'percentage': 80}
            ]

        # Get Certifications
        certifications_data = fb.get('/certifications', None) or {}
        certifications = certifications_data if isinstance(certifications_data, dict) else {}
        
        # Get Projects
        projects_data = fb.get('/projects', None) or {}
        projects = projects_data if isinstance(projects_data, dict) else {}

        # Prepare data dictionary for template
        data = {
            'name': 'John Sathvik Madipalli',  # Can be moved to Firebase later
            'specialization': 'AWS Solutions Architect & Web Developer',
            'bio': bio,
            'about_bio': about_bio,
            'about_heading': about_heading,
            'skills': skills,
            'typed_items': typed_items,  # For the typed.js animation
            'about_skills': about_skills,
            'experiences': experience_data if isinstance(experience_data, dict) else {},
            'education': education_data if isinstance(education_data, dict) else {},
            'professional_summary': professional_summary,
            'technical_skills': technical_skills,
            'certifications': certifications,
            'projects': projects,
            'email': email,
            'phone': phone,
            'linkedin': linkedin,
            'telegram': telegram,
            'whatsapp': whatsapp,
            'github': github
        }

        # Debug: Print what we're sending to template
        print(f"DEBUG: about_skills count: {len(about_skills)}")
        print(f"DEBUG: about_skills: {about_skills}")
        print(f"DEBUG: about_skills type: {type(about_skills)}")
        print(f"DEBUG: about_skills is truthy: {bool(about_skills)}")

        return render_template('index.html', data=data)
    
    except Exception as e:
        # Log error and return template with fallback data
        print(f"Error loading data from Firebase: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback data if Firebase fails
        data = {
            'name': 'John Sathvik Madipalli',
            'specialization': 'AWS Solutions Architect & Web Developer',
            'bio': '',
            'about_bio': '',
            'about_heading': '',
            'skills': [],
            'typed_items': 'AWS Solutions Architect, Web Developer, Cloud Enthusiast',
            'about_skills': [],
            'experiences': {},
            'education': {},
            'email': '',
            'phone': '',
            'linkedin': '',
            'telegram': '',
            'whatsapp': '',
            'github': ''
        }
        return render_template('index.html', data=data)

# --- Edit Page (GET & POST) - Redirected to Admin Dashboard ---
@app.route('/edit', methods=['GET', 'POST'])
def edit():
    # Redirect to admin dashboard for editing
    # Admin dashboard is at http://localhost:5001/admin-login
    return redirect('http://localhost:5001/admin-login')

@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')

    # Send to Telegram (optional - same as admin uses)
    try:
        bot_token = '7634605210:AAGV3zH26-TjdCx25AjrLO8SG9EuRhJZRPs'
        chat_id = 914342868
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': f"Name: {name}\nEmail: {email}\nSubject: {subject}\nMessage: {message}"
        }
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

    print(f"\n📩 New Contact Message:")
    print(f"Name: {name}")
    print(f"Email: {email}")
    print(f"Subject: {subject}")
    print(f"Message: {message}\n")

    return "OK"


# --- Resume Download Route ---
@app.route('/download_resume')
def download_resume():
    # Get resume info from Firebase
    raw_resume = fb.get('/about/resume', None) or {}
    resume_filename = 'Resume.pdf'  # Default to PDF
    
    if raw_resume:
        resume_data = next(iter(raw_resume.values()))
        resume_filename = resume_data.get('filename', 'Resume.pdf')
    
    resume_path = os.path.join(app.root_path, 'static', 'resume', resume_filename)
    
    # Check if file exists, if not try default PDF
    if not os.path.exists(resume_path):
        resume_path = os.path.join(app.root_path, 'static', 'resume', 'Resume.pdf')
    
    return send_file(resume_path, as_attachment=True)

# --- Social Links ---
@app.route('/github')
def github():
    links = fb.get('/links/-OOvwHeVJtSsrjh3QnWR/links', None) or {}
    github_url = links.get('github', 'https://github.com') if isinstance(links, dict) else 'https://github.com'
    if not github_url.startswith('http'):
        github_url = f'https://{github_url}'
    return redirect(github_url)

@app.route('/linkedin')
def linkedin():
    links = fb.get('/links/-OOvwHeVJtSsrjh3QnWR/links', None) or {}
    linkedin_url = links.get('linkedin', 'https://linkedin.com') if isinstance(links, dict) else 'https://linkedin.com'
    if not linkedin_url.startswith('http'):
        linkedin_url = f'https://{linkedin_url}'
    return redirect(linkedin_url)

# --- Run Flask App ---
if __name__ == '__main__':
    app.run(debug=True)
