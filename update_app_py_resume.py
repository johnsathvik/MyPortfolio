import os

app_file = r"d:\Disk\MyPortfolio\admin\app.py"

with open(app_file, 'r', encoding='utf-8') as f:
    app_content = f.read()

# 1. Find the start of admin_experience and delete to end of delete_education
start_idx = app_content.find("@app.route('/admin-experience', methods=[\"GET\", \"POST\"])")
end_idx = app_content.find("@app.route('/admin-certification', methods=[\"GET\", \"POST\"])")

if start_idx != -1 and end_idx != -1:
    admin_resume_code = """
@app.route('/admin-resume', methods=["GET", "POST"])
@login_required
@nocache
def admin_resume():
    # Strict validation handled by decorator
    
    edit_data = None
    edit_data_type = None # 'experience' or 'education'

    if request.method == "POST":
        # GUEST GUARD
        if session.get('is_guest'):
            flash("Guest Mode: Read-only access. Changes are not saved.", "warning")
            return redirect(request.url)

        # ---------------- EXPERIENCE HANDLING ----------------
        # Handle Professional Summary update
        if 'edited_professional_summary' in request.form:
            new_summary = request.form['edited_professional_summary'].strip()
            raw_summary = fb.get('/resume/professional_summary', None) or {}
            if raw_summary:
                key = next(iter(raw_summary))
                fb.put(f'/resume/professional_summary/{key}', 'summary', new_summary)
            else:
                fb.post('/resume/professional_summary', {'summary': new_summary})
            flash('Professional Summary updated successfully!', 'success')
            return redirect(url_for('admin_resume'))
        
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
                    fb.put(f'/resume/technical_skills/{key}', 'skills', skills)
                else:
                    fb.post('/resume/technical_skills', {
                        'skills': [{
                            'name': skill_name,
                            'percentage': skill_pct
                        }]
                    })
            flash('Technical skill added successfully!', 'success')
            return redirect(url_for('admin_resume'))
        
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
                    fb.put(f'/resume/technical_skills/{key}', 'skills', skills)
            flash('Technical skill updated successfully!', 'success')
            return redirect(url_for('admin_resume'))
        
        # Handle Delete Technical Skill
        elif 'delete_tech_skill_index' in request.form:
            idx = int(request.form['delete_tech_skill_index'])
            raw = fb.get('/resume/technical_skills', None) or {}
            if raw:
                key = next(iter(raw))
                skills = raw[key].get('skills', [])
                if 0 <= idx < len(skills):
                    skills.pop(idx)
                    fb.put(f'/resume/technical_skills/{key}', 'skills', skills)
            flash('Technical skill deleted successfully!', 'success')
            return redirect(url_for('admin_resume'))
        
        # Handle Edit request
        elif 'edit_key' in request.form:
            key = request.form['edit_key']
            edit_data = fb.get(f'/experience/{key}', None)
            if edit_data:
                edit_data['key'] = key
                edit_data_type = 'experience'
            else:
                edit_data = fb.get(f'/resume/education/{key}', None)
                if edit_data:
                    edit_data['key'] = key
                    edit_data_type = 'education'

        # Handle Update submission for Experience
        elif 'update_key' in request.form and 'company' in request.form:
            key = request.form['update_key']
            updated = {
                "company": request.form['company'],
                "role": request.form['role'],
                "duration": request.form['duration'],
                "location": request.form.get('location', ''),
                "description": request.form['description']
            }
            fb.put('/experience', key, updated)
            flash('Experience updated successfully!', 'success')
            return redirect(url_for('admin_resume'))

        # Handle Update submission for Education
        elif 'update_key' in request.form and 'institution' in request.form:
            key = request.form['update_key']
            updated = {
                "institution": request.form['institution'],
                "designation": request.form['designation'],
                "period": request.form['period'],
                "location": request.form.get('location', ''),
                "description": request.form['description']
            }
            fb.put('/resume/education', key, updated)
            flash('Education updated successfully!', 'success')
            return redirect(url_for('admin_resume'))

        # Handle Add new Experience
        elif 'company' in request.form:
            company = request.form.get("company")
            role = request.form.get("role")
            duration = request.form.get("duration")
            location = request.form.get("location", "")
            description = request.form.get("description")
            if company and role and duration and description:
                fb.post('/experience', {
                    "company": company,
                    "role": role,
                    "duration": duration,
                    "location": location,
                    "description": description
                })
                flash('Experience added successfully!', 'success')
            return redirect(url_for('admin_resume'))

        # Handle Add new Education
        elif 'institution' in request.form:
            institution = request.form.get("institution")
            designation = request.form.get("designation")
            period = request.form.get("period")
            location = request.form.get("location", "")
            description = request.form.get("description")

            if institution and designation and period and description:
                fb.post('/resume/education', {
                    "institution": institution,
                    "designation": designation,
                    "period": period,
                    "location": location,
                    "description": description
                })
                flash('Education added successfully!', 'success')

            return redirect(url_for('admin_resume'))

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
    education = fb.get('/resume/education', None) or {}
    
    # Ensure variables are always defined
    if professional_summary is None:
        professional_summary = ''
    if technical_skills is None:
        technical_skills = []
    if edit_data is None:
        edit_data = None
    
    return render_template('admin-resume.html', 
                         experiences=experiences, 
                         education=education,
                         edit_data=edit_data,
                         edit_data_type=edit_data_type,
                         professional_summary=professional_summary,
                         technical_skills=technical_skills)


@app.route('/delete-experience', methods=['POST'])
@nocache
def delete_experience():
    # GUEST GUARD
    if session.get('is_guest'):
        flash("Guest Mode: Read-only access. Changes are not saved.", "warning")
        return redirect(url_for('admin_resume'))

    key = request.form.get('key')
    if key:
        fb.delete('/experience', key)
        flash('Experience deleted successfully!', 'success')
    return redirect(url_for('admin_resume'))

@app.route('/delete-education', methods=["POST"])
@login_required
@nocache
def delete_education():
    # GUEST GUARD
    if session.get('is_guest'):
        flash("Guest Mode: Read-only access. Changes are not saved.", "warning")
        return redirect(url_for('admin_resume'))

    key = request.form.get('key')
    if key:
        fb.delete('/resume/education', key)
        flash('Education deleted successfully!', 'success')
    return redirect(url_for('admin_resume'))

"""
    app_content = app_content[:start_idx] + admin_resume_code + app_content[end_idx:]

    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(app_content)
    print("Updated admin/app.py with unified /admin-resume logic")
