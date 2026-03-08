import os
import glob
import re

template_dir = r"d:\Disk\MyPortfolio\admin\templates"
html_files = glob.glob(os.path.join(template_dir, "admin-*.html"))

skills_nav_item = """              <li class="nav-item">
                <a class="nav-link" href="/admin-skills">
                  <i class="bi bi-tools"></i> Skills
                </a>
              </li>
"""

about_nav_item_pattern = re.compile(r'(<li class="nav-item">\s*<a class="nav-link(?: active)?" href="/admin-about">\s*<i class="bi bi-person"></i> About\s*</a>\s*</li>)')

for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already has Skills nav item
    if 'href="/admin-skills"' not in content:
        # Insert after About
        content = about_nav_item_pattern.sub(r'\1\n' + skills_nav_item, content)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
            print(f"Updated sidebar in {file}")

