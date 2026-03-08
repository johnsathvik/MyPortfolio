import os

exp_file = r"d:\Disk\MyPortfolio\admin\templates\admin-experience.html"
edu_file = r"d:\Disk\MyPortfolio\admin\templates\admin-education.html"
resume_file = r"d:\Disk\MyPortfolio\admin\templates\admin-resume.html"

with open(exp_file, 'r', encoding='utf-8') as f:
    exp_content = f.read()

with open(edu_file, 'r', encoding='utf-8') as f:
    edu_content = f.read()

# 1. Base the new file off admin-experience.html
resume_content = exp_content

# 2. Update Title and Headers
resume_content = resume_content.replace('<title>Admin Dashboard - Experience</title>', '<title>Admin Dashboard - Resume</title>')
resume_content = resume_content.replace('<i class="bi bi-briefcase"></i> Manage Experience', '<i class="bi bi-file-earmark-text"></i> Manage Resume')
resume_content = resume_content.replace('Manage your professional experience and technical skills', 'Manage your professional summary, skills, experience, and education')

# 3. Form actions
resume_content = resume_content.replace('action="{{ url_for(\'admin_experience\') }}"', 'action="{{ url_for(\'admin_resume\') }}"')
resume_content = resume_content.replace('action="/delete-experience"', 'action="/delete-experience"') # We'll keep these separate action endpoints but change redirect in app.py

# 4. Sidebar Nav Active State update
resume_content = resume_content.replace(
'''              <li class="nav-item">
                <a class="nav-link active" href="/admin-experience">
                  <i class="bi bi-briefcase"></i> Experience
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="/admin-education">
                  <i class="bi bi-mortarboard"></i> Education
                </a>
              </li>''',
'''              <li class="nav-item">
                <a class="nav-link active" href="/admin-resume">
                  <i class="bi bi-file-earmark-text"></i> Resume
                </a>
              </li>'''
)

# Replace remaining nav links in case it missed (this replaces globally)
# (Done via update_sidebar.py later for all files, so let's just make sure it's here)

# 5. Extract Education Section from edu_content
# from: <!-- Add Education Form --> to end of </main>
edu_start = edu_content.find('<!-- Add Education Form -->')
edu_end = edu_content.find('</main>')
if edu_start != -1 and edu_end != -1:
    education_html = edu_content[edu_start:edu_end]
    
    # Change action URLs for education forms
    education_html = education_html.replace('action="/delete-education"', 'action="/delete-education"')
    # We need to make sure the POST targets current url if no action specified
    # The default POST simply goes to the current URL.
    
    # Find insertion point in resume_content (after Experience Table card)
    exp_table_end = resume_content.find('</div>\n        </div>\n      </main>')
    if exp_table_end != -1:
        # Insert a divider and the education html
        insert_idx = exp_table_end + 14 # After the last </div> of card
        resume_content = resume_content[:insert_idx] + '\n\n        <hr class="section-divider">\n\n        ' + education_html + resume_content[insert_idx:]

with open(resume_file, 'w', encoding='utf-8') as f:
    f.write(resume_content)
    print("Created admin-resume.html")
