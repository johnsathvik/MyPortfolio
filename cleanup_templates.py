import os
import re

about_file = r"d:\Disk\MyPortfolio\admin\templates\admin-about.html"
skills_file = r"d:\Disk\MyPortfolio\admin\templates\admin-skills.html"

# 1. Clean up admin-about.html (remove manage skills section)
with open(about_file, 'r', encoding='utf-8') as f:
    about_content = f.read()

# The skills section starts with:
#         <div class="card">
#           <div class="card-header d-flex justify-content-between align-items-center">
#             <span><i class="bi bi-tags"></i> Manage Skills</span>
# And ends before:
#         <!-- Resume Upload -->
skills_start = about_content.find('<div class="card">\n          <div class="card-header d-flex justify-content-between align-items-center">\n            <span><i class="bi bi-tags"></i> Manage Skills</span>')
resume_start_str = '<!-- Resume Upload -->'
resume_start = about_content.find(resume_start_str)

if skills_start != -1 and resume_start != -1:
    # Delete the skills section and the section divider right before it.
    # The dividing line: <hr class="section-divider">
    # Let's find the previous hr
    hr_before = about_content.rfind('<hr class="section-divider">', 0, skills_start)
    if hr_before != -1:
        skills_start = hr_before

    about_content = about_content[:skills_start] + '\n        ' + about_content[resume_start:]
    
    with open(about_file, 'w', encoding='utf-8') as f:
        f.write(about_content)
    print("Cleaned up admin-about.html (removed Skills)")

# 2. Clean up admin-skills.html (remove Bio Heading, Bio, and Resume sections, update texts)
with open(skills_file, 'r', encoding='utf-8') as f:
    skills_content = f.read()

# Make Title: About -> Skills
skills_content = skills_content.replace('<title>Admin Dashboard - About</title>', '<title>Admin Dashboard - Skills</title>')

# Make Page Header: Manage About Section -> Manage Skills
skills_content = skills_content.replace(
'''              <h1 class="mb-2" style="font-size: 2rem; font-weight: 700;">
                <i class="bi bi-person-circle"></i> Manage About Section
              </h1>
              <p class="mb-0 opacity-75">Manage your bio, skills, and resume information</p>''',
'''              <h1 class="mb-2" style="font-size: 2rem; font-weight: 700;">
                <i class="bi bi-tools"></i> Manage Skills
              </h1>
              <p class="mb-0 opacity-75">Manage your skills and expertise areas</p>'''
)

# Update form action
skills_content = skills_content.replace('action="{{ url_for(\'admin_about\') }}"', 'action="{{ url_for(\'admin_skills\') }}"')

# Change active nav link
skills_content = skills_content.replace(
'''<a class="nav-link active" href="/admin-about">''',
'''<a class="nav-link" href="/admin-about">'''
)
skills_content = skills_content.replace(
'''<a class="nav-link" href="/admin-skills">
                  <i class="bi bi-tools"></i> Skills''',
'''<a class="nav-link active" href="/admin-skills">
                  <i class="bi bi-tools"></i> Skills'''
)

# Remove Bio Heading & Bio
toast_end = skills_content.find('{% include \'toast_notifications.html\' %}') + len('{% include \'toast_notifications.html\' %}')
manage_skills_start = skills_content.find('<div class="card">\n          <div class="card-header d-flex justify-content-between align-items-center">\n            <span><i class="bi bi-tags"></i> Manage Skills</span>')

if manage_skills_start != -1:
    hr_before = skills_content.rfind('<hr class="section-divider">', toast_end, manage_skills_start)
    if hr_before != -1:
         skills_content = skills_content[:toast_end] + '\n\n        <br>\n\n        ' + skills_content[manage_skills_start:]
    else:
         skills_content = skills_content[:toast_end] + '\n\n        <br>\n\n        ' + skills_content[manage_skills_start:]

# Remove Resume Upload
new_resume_start = skills_content.find('<!-- Resume Upload -->')
if new_resume_start != -1:
    hr_before_resume = skills_content.rfind('<hr class="section-divider">', 0, new_resume_start)
    end_main = skills_content.find('</main>')
    if hr_before_resume != -1 and end_main != -1:
        skills_content = skills_content[:hr_before_resume] + '\n      ' + skills_content[end_main:]

with open(skills_file, 'w', encoding='utf-8') as f:
    f.write(skills_content)
    print("Cleaned up admin-skills.html")
