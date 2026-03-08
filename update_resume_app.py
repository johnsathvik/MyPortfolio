import os

app_file = r"d:\Disk\MyPortfolio\admin\app.py"

with open(app_file, 'r', encoding='utf-8') as f:
    app_content = f.read()

# 1. Remove the Edit request handler
edit_logic_start = app_content.find("        # Handle Edit request")
if edit_logic_start != -1:
    edit_logic_end = app_content.find("        # Handle Update submission for Experience", edit_logic_start)
    if edit_logic_end != -1:
        # Remove the block cleanly
        app_content = app_content[:edit_logic_start] + app_content[edit_logic_end:]

# 2. Update the variable passed to render_template
old_context = """    return render_template(
        'admin-resume.html',
        professional_summary=professional_summary,
        technical_skills=technical_skills,
        experiences=experiences,
        education=education,
        edit_data=edit_data,
        edit_data_type=edit_data_type
    )"""

new_context = """    return render_template(
        'admin-resume.html',
        professional_summary=professional_summary,
        technical_skills=technical_skills,
        experiences=experiences,
        education=education
    )"""

if old_context in app_content:
    app_content = app_content.replace(old_context, new_context)
else:
    print("WARNING: Could not find exact old_context string!")

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(app_content)
    print("Successfully removed edit form handling from app.py safely!")
