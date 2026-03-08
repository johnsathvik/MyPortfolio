import os
import glob
import re

template_dir = r"d:\Disk\MyPortfolio\admin\templates"
html_files = glob.glob(os.path.join(template_dir, "admin-*.html"))

# We want to replace this block:
#               <li class="nav-item">
#                 <a class="nav-link" href="/admin-experience">
#                   <i class="bi bi-briefcase"></i> Experience
#                 </a>
#               </li>
#               <li class="nav-item">
#                 <a class="nav-link" href="/admin-education">
#                   <i class="bi bi-mortarboard"></i> Education
#                 </a>
#               </li>

# With this:
#               <li class="nav-item">
#                 <a class="nav-link" href="/admin-resume">
#                   <i class="bi bi-file-earmark-text"></i> Resume
#                 </a>
#               </li>

# Also handle "active" states
exp_edu_pattern = re.compile(
r'(\s*<li class="nav-item">\s*<a class="nav-link(?: active)?" href="/admin-experience">\s*<i class="bi bi-briefcase"></i> Experience\s*</a>\s*</li>\s*<li class="nav-item">\s*<a class="nav-link(?: active)?" href="/admin-education">\s*<i class="bi bi-mortarboard"></i> Education\s*</a>\s*</li>)'
)

resume_nav_item = """
              <li class="nav-item">
                <a class="nav-link" href="/admin-resume">
                  <i class="bi bi-file-earmark-text"></i> Resume
                </a>
              </li>"""


for file in html_files:
    if "admin-resume.html" in file:
        continue # Already processed during creation
        
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if needs replacing
    if re.search(exp_edu_pattern, content):
        content = re.sub(exp_edu_pattern, resume_nav_item, content)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
            print(f"Updated sidebar in {file}")

