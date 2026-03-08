import os
import re

resume_file = r"d:\Disk\MyPortfolio\admin\templates\admin-resume.html"

with open(resume_file, 'r', encoding='utf-8') as f:
    resume_content = f.read()

# Fix Experience Form action and Add hidden input
exp_form_start = resume_content.find('<!-- Add Experience Form -->')
exp_form_end = resume_content.find('<!-- Experience Table -->')
if exp_form_start != -1 and exp_form_end != -1:
    exp_form_html = resume_content[exp_form_start:exp_form_end]
    # Replace action empty
    exp_form_html = exp_form_html.replace('action="{{ url_for(\'admin_resume\') }}"', 'action="{{ url_for(\'admin_resume\') }}"')
    
    # We need to make sure we show edit correct fields for experience
    exp_form_html = exp_form_html.replace('{% if edit_data %}', '{% if edit_data and edit_data_type == "experience" %}')
    exp_form_html = exp_form_html.replace('edit_data.', 'edit_data.') # Just to check, it relies on python dict keys, so 'company', 'role'
    # Default values logic string replacement to be safe:
    exp_form_html = exp_form_html.replace("edit_data.company if edit_data", "edit_data.company if edit_data and edit_data_type == 'experience'")
    exp_form_html = exp_form_html.replace("edit_data.role if edit_data", "edit_data.role if edit_data and edit_data_type == 'experience'")
    exp_form_html = exp_form_html.replace("edit_data.duration if edit_data", "edit_data.duration if edit_data and edit_data_type == 'experience'")
    exp_form_html = exp_form_html.replace("edit_data.location if edit_data", "edit_data.location if edit_data and edit_data_type == 'experience'")
    exp_form_html = exp_form_html.replace("edit_data.description if edit_data", "edit_data.description if edit_data and edit_data_type == 'experience'")
    exp_form_html = exp_form_html.replace("'Update Experience' if edit_data else", "'Update Experience' if edit_data and edit_data_type == 'experience' else")

    resume_content = resume_content[:exp_form_start] + exp_form_html + resume_content[exp_form_end:]

# Fix Education form 
edu_form_start = resume_content.find('<!-- Add Education Form -->')
edu_table_start = resume_content.find('<!-- Education Table -->')
if edu_form_start != -1:
    end_idx = edu_table_start if edu_table_start != -1 else resume_content.find('</main>')
    edu_form_html = resume_content[edu_form_start:end_idx]
    
    # Replace conditionals for education to be sure
    edu_form_html = edu_form_html.replace('{% if edit_data %}', '{% if edit_data and edit_data_type == "education" %}')
    edu_form_html = edu_form_html.replace("edit_data.institution if edit_data", "edit_data.institution if edit_data and edit_data_type == 'education'")
    edu_form_html = edu_form_html.replace("edit_data.designation if edit_data", "edit_data.designation if edit_data and edit_data_type == 'education'")
    edu_form_html = edu_form_html.replace("edit_data.period if edit_data", "edit_data.period if edit_data and edit_data_type == 'education'")
    edu_form_html = edu_form_html.replace("edit_data.location if edit_data", "edit_data.location if edit_data and edit_data_type == 'education'")
    edu_form_html = edu_form_html.replace("edit_data.description if edit_data", "edit_data.description if edit_data and edit_data_type == 'education'")
    edu_form_html = edu_form_html.replace("'Update Entry' if edit_data else", "'Update Education' if edit_data and edit_data_type == 'education' else")
    
    resume_content = resume_content[:edu_form_start] + edu_form_html + resume_content[end_idx:]


with open(resume_file, 'w', encoding='utf-8') as f:
    f.write(resume_content)
    print("Refined admin-resume.html forms to handle edit types")
