import os

app_file = r"d:\Disk\MyPortfolio\admin\app.py"

with open(app_file, 'r', encoding='utf-8') as f:
    app_content = f.read()

# 1. We need to add logic for handling POST request of Profile Details.
# We'll put it right after checking for `if request.method == 'POST': ... if session.get('is_guest'): ...`
post_start = app_content.find("        if 'edited_bio_heading' in request.form:")
if post_start != -1:
    profile_logic = """
        if 'action_type' in request.form and request.form['action_type'] == 'update_profile':
            profile_data = {
                'name': request.form.get('profile_name', '').strip(),
                'title': request.form.get('profile_title', '').strip(),
                'location': request.form.get('profile_location', '').strip(),
                'specialization': request.form.get('profile_specialization', '').strip(),
                'experience_level': request.form.get('profile_experience', '').strip(),
                'education': request.form.get('profile_education', '').strip(),
                'languages': request.form.get('profile_languages', '').strip()
            }
            raw_profile = fb.get('/about/profile', None) or {}
            if raw_profile:
                key = next(iter(raw_profile))
                fb.put('/about', f'profile/{key}', profile_data)
            else:
                fb.post('/about/profile', profile_data)
            flash('Profile details updated successfully!', 'success')
            return redirect(url_for('admin_about'))
            
"""
    app_content = app_content[:post_start] + profile_logic + app_content[post_start:]

# 2. We need to fetch the existing profile on GET and pass it to render_template
context_start = app_content.find("    return render_template('admin-about.html', bio=bio, heading=heading, current_resume=current_resume, resume_type=resume_type)")
if context_start != -1:
    fetch_logic = """
    # Get profile details
    raw_profile = fb.get('/about/profile', None) or {}
    profile = next(iter(raw_profile.values())) if raw_profile else {}
"""
    app_content = app_content[:context_start] + fetch_logic + app_content[context_start:]
    
    # Update the render_template call
    old_call = "    return render_template('admin-about.html', bio=bio, heading=heading, current_resume=current_resume, resume_type=resume_type)"
    new_call = "    return render_template('admin-about.html', bio=bio, heading=heading, current_resume=current_resume, resume_type=resume_type, profile=profile)"
    app_content = app_content.replace(old_call, new_call)

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(app_content)
    print("Successfully updated admin/app.py for profile details")
