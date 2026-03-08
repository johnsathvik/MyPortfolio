import os
import re

app_file = r"d:\Disk\MyPortfolio\admin\app.py"

with open(app_file, 'r', encoding='utf-8') as f:
    app_content = f.read()

# 1. Capture the new_title logic
skills_add_code = """
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

    elif request.method == 'POST':"""

# Replace it with just `    if request.method == 'POST':` in admin_about
app_content = app_content.replace(skills_add_code, "\n    if request.method == 'POST':")

# 2. Capture delete and edit logic
skills_del_edit_code = """
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
                    flash('Skill updated successfully!', 'success')"""

app_content = app_content.replace(skills_del_edit_code, "")

# 3. Capture fetching skills in admin_about
skills_fetch_code = """
    raw_skills = fb.get('/about/skills', None) or {}
    skills = []
    for block in raw_skills.values():
        skills.extend(block.get('skills', []))"""

app_content = app_content.replace(skills_fetch_code, "")

# Remove skills=skills from render_template
app_content = app_content.replace('skills=skills, current_resume=current_resume', 'current_resume=current_resume')

# Create the new admin_skills function
new_admin_skills_code = """
@app.route('/admin-skills', methods=['GET', 'POST'])
@login_required
@nocache
def admin_skills():
    # Strict validation handled by decorator
    
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

        if 'delete_index' in request.form:
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

        return redirect(url_for('admin_skills'))

    raw_skills = fb.get('/about/skills', None) or {}
    skills = []
    for block in raw_skills.values():
        skills.extend(block.get('skills', []))

    return render_template('admin-skills.html', skills=skills)
"""

# Inject before @app.route('/admin-experience'
app_content = app_content.replace('@app.route(\'/admin-experience\', methods=["GET", "POST"])', new_admin_skills_code + '\n@app.route(\'/admin-experience\', methods=["GET", "POST"])')

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(app_content)
    print("Updated admin/app.py")
