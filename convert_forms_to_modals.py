import os
import re

html_file = r"d:\Disk\MyPortfolio\admin\templates\admin-resume.html"

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove the static Add Experience Form
exp_form_start = content.find('        <!-- Add Experience Form -->')
if exp_form_start != -1:
    exp_form_end = content.find('        <!-- Experience Table -->')
    if exp_form_end != -1:
        # We also want to remove the `<hr class="section-divider">` before the table
        hr_before_table = content.rfind('<hr class="section-divider">', exp_form_start, exp_form_end)
        if hr_before_table != -1:
            content = content[:exp_form_start] + content[exp_form_end:]

# 2. Update the Experience Table Header to include the Add button
exp_header_old = """          <div class="card-header">
            <i class="bi bi-list-ul"></i> Experience List
          </div>"""
exp_header_new = """          <div class="card-header d-flex justify-content-between align-items-center">
            <span><i class="bi bi-briefcase"></i> Manage Experience</span>
            <button type="button" class="btn btn-light btn-sm" data-bs-toggle="modal" data-bs-target="#addExperienceModal">
              <i class="bi bi-plus-circle"></i> Add New Experience
            </button>
          </div>"""
content = content.replace(exp_header_old, exp_header_new)

# 3. Update the Experience Edit button in the table to use Modal
exp_edit_old = """                      <form method="POST" style="display:inline;">
                        <input type="hidden" name="edit_key" value="{{ key }}">
                        <button class="btn btn-sm btn-primary me-1" type="submit">
                          <i class="bi bi-pencil"></i> Edit
                        </button>
                      </form>"""
exp_edit_new = """                      <button class="btn btn-sm btn-primary me-1 edit-exp-btn" 
                        data-key="{{ key }}" 
                        data-company="{{ exp.company|e }}" 
                        data-role="{{ exp.role|e }}" 
                        data-duration="{{ exp.duration|e }}" 
                        data-location="{{ exp.location|e if exp.location else '' }}" 
                        data-description="{{ exp.description|e }}" 
                        data-bs-toggle="modal" data-bs-target="#editExperienceModal">
                        <i class="bi bi-pencil"></i> Edit
                      </button>"""
content = content.replace(exp_edit_old, exp_edit_new)


# 4. Remove the static Add Education Form
edu_form_start = content.find('        <!-- Add Education Form -->')
if edu_form_start != -1:
    edu_form_end = content.find('        <!-- Education Table -->')
    if edu_form_end != -1:
        content = content[:edu_form_start] + content[edu_form_end:]

# 5. Update the Education Table Header to include the Add button
edu_header_old = """          <div class="card-header">
            <i class="bi bi-list-ul"></i> Education List
          </div>"""
edu_header_new = """          <div class="card-header d-flex justify-content-between align-items-center">
            <span><i class="bi bi-mortarboard"></i> Manage Education</span>
            <button type="button" class="btn btn-light btn-sm" data-bs-toggle="modal" data-bs-target="#addEducationModal">
              <i class="bi bi-plus-circle"></i> Add New Education
            </button>
          </div>"""
content = content.replace(edu_header_old, edu_header_new)

# 6. Update the Education Edit button in the table to use Modal
edu_edit_old = """                      <form method="POST" style="display:inline;">
                        <input type="hidden" name="edit_key" value="{{ key }}">
                        <button class="btn btn-sm btn-primary" type="submit">
                          <i class="bi bi-pencil"></i> Edit
                        </button>
                      </form>"""
edu_edit_new = """                      <button class="btn btn-sm btn-primary edit-edu-btn" 
                        data-key="{{ key }}" 
                        data-institution="{{ edu.institution|e }}" 
                        data-designation="{{ edu.designation|e }}" 
                        data-period="{{ edu.period|e }}" 
                        data-location="{{ edu.location|e if edu.location else '' }}" 
                        data-description="{{ edu.description|e }}" 
                        data-bs-toggle="modal" data-bs-target="#editEducationModal">
                        <i class="bi bi-pencil"></i> Edit
                      </button>"""
content = content.replace(edu_edit_old, edu_edit_new)


# 7. Append the 4 new Modals before the closing `</main>` tag
modals_html = """
        <!-- Add Experience Modal -->
        <div class="modal fade" id="addExperienceModal" tabindex="-1" aria-hidden="true">
          <div class="modal-dialog modal-lg">
            <form method="post" action="{{ url_for('admin_resume') }}">
              <div class="modal-content">
                <div class="modal-header">
                  <h5 class="modal-title highlight"><i class="bi bi-plus-circle"></i> Add New Experience</h5>
                  <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                  <div class="row">
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Institution/Company</label>
                      <input type="text" class="form-control" name="company" required>
                    </div>
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Role</label>
                      <input type="text" class="form-control" name="role" required>
                    </div>
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Period</label>
                      <input type="text" class="form-control" name="duration" required>
                    </div>
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Location</label>
                      <input type="text" class="form-control" name="location" placeholder="e.g., Hyderabad, India">
                    </div>
                    <div class="col-12 mb-3">
                      <label class="form-label">Description</label>
                      <textarea class="form-control" name="description" rows="4" required></textarea>
                    </div>
                  </div>
                </div>
                <div class="modal-footer">
                  <button type="submit" class="btn btn-primary"><i class="bi bi-check-circle"></i> Add Experience</button>
                  <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                </div>
              </div>
            </form>
          </div>
        </div>

        <!-- Edit Experience Modal -->
        <div class="modal fade" id="editExperienceModal" tabindex="-1" aria-hidden="true">
          <div class="modal-dialog modal-lg">
            <form method="post" action="{{ url_for('admin_resume') }}">
              <div class="modal-content">
                <div class="modal-header">
                  <h5 class="modal-title highlight"><i class="bi bi-pencil"></i> Edit Experience</h5>
                  <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                  <input type="hidden" name="update_key" id="editExpKey">
                  <div class="row">
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Institution/Company</label>
                      <input type="text" class="form-control" id="editExpCompany" name="company" required>
                    </div>
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Role</label>
                      <input type="text" class="form-control" id="editExpRole" name="role" required>
                    </div>
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Period</label>
                      <input type="text" class="form-control" id="editExpDuration" name="duration" required>
                    </div>
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Location</label>
                      <input type="text" class="form-control" id="editExpLocation" name="location">
                    </div>
                    <div class="col-12 mb-3">
                      <label class="form-label">Description</label>
                      <textarea class="form-control" id="editExpDescription" name="description" rows="4" required></textarea>
                    </div>
                  </div>
                </div>
                <div class="modal-footer">
                  <button type="submit" class="btn btn-primary"><i class="bi bi-check-circle"></i> Update Experience</button>
                  <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                </div>
              </div>
            </form>
          </div>
        </div>

        <!-- Add Education Modal -->
        <div class="modal fade" id="addEducationModal" tabindex="-1" aria-hidden="true">
          <div class="modal-dialog modal-lg">
            <form method="post" action="{{ url_for('admin_resume') }}">
              <div class="modal-content">
                <div class="modal-header">
                  <h5 class="modal-title highlight"><i class="bi bi-plus-circle"></i> Add New Education</h5>
                  <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                  <div class="row">
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Institution</label>
                      <input type="text" class="form-control" name="institution" required>
                    </div>
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Degree / Designation</label>
                      <input type="text" class="form-control" name="designation" required>
                    </div>
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Period</label>
                      <input type="text" class="form-control" name="period" required>
                    </div>
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Location</label>
                      <input type="text" class="form-control" name="location" placeholder="e.g., St. Louis, Missouri">
                    </div>
                    <div class="col-12 mb-3">
                      <label class="form-label">Description</label>
                      <textarea class="form-control" name="description" rows="4" required></textarea>
                    </div>
                  </div>
                </div>
                <div class="modal-footer">
                  <button type="submit" class="btn btn-primary"><i class="bi bi-check-circle"></i> Add Education</button>
                  <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                </div>
              </div>
            </form>
          </div>
        </div>

        <!-- Edit Education Modal -->
        <div class="modal fade" id="editEducationModal" tabindex="-1" aria-hidden="true">
          <div class="modal-dialog modal-lg">
            <form method="post" action="{{ url_for('admin_resume') }}">
              <div class="modal-content">
                <div class="modal-header">
                  <h5 class="modal-title highlight"><i class="bi bi-pencil"></i> Edit Education</h5>
                  <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                  <input type="hidden" name="update_key" id="editEduKey">
                  <div class="row">
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Institution</label>
                      <input type="text" class="form-control" id="editEduInstitution" name="institution" required>
                    </div>
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Degree / Designation</label>
                      <input type="text" class="form-control" id="editEduDesignation" name="designation" required>
                    </div>
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Period</label>
                      <input type="text" class="form-control" id="editEduPeriod" name="period" required>
                    </div>
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Location</label>
                      <input type="text" class="form-control" id="editEduLocation" name="location">
                    </div>
                    <div class="col-12 mb-3">
                      <label class="form-label">Description</label>
                      <textarea class="form-control" id="editEduDescription" name="description" rows="4" required></textarea>
                    </div>
                  </div>
                </div>
                <div class="modal-footer">
                  <button type="submit" class="btn btn-primary"><i class="bi bi-check-circle"></i> Update Education</button>
                  <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                </div>
              </div>
            </form>
          </div>
        </div>

       </div>
      </main>"""

content = content.replace("       </div>\n      </main>", modals_html)


# 8. Add JavaScript to pre-fill the Edit modals and remove the scrolling behavior
js_modals = """
      // Experience Modal Prefill
      const editExperienceModal = document.getElementById('editExperienceModal');
      if (editExperienceModal) {
        editExperienceModal.addEventListener('show.bs.modal', event => {
          const btn = event.relatedTarget;
          document.getElementById('editExpKey').value = btn.dataset.key || '';
          document.getElementById('editExpCompany').value = btn.dataset.company || '';
          document.getElementById('editExpRole').value = btn.dataset.role || '';
          document.getElementById('editExpDuration').value = btn.dataset.duration || '';
          document.getElementById('editExpLocation').value = btn.dataset.location || '';
          document.getElementById('editExpDescription').value = btn.dataset.description || '';
        });
      }

      // Education Modal Prefill
      const editEducationModal = document.getElementById('editEducationModal');
      if (editEducationModal) {
        editEducationModal.addEventListener('show.bs.modal', event => {
          const btn = event.relatedTarget;
          document.getElementById('editEduKey').value = btn.dataset.key || '';
          document.getElementById('editEduInstitution').value = btn.dataset.institution || '';
          document.getElementById('editEduDesignation').value = btn.dataset.designation || '';
          document.getElementById('editEduPeriod').value = btn.dataset.period || '';
          document.getElementById('editEduLocation').value = btn.dataset.location || '';
          document.getElementById('editEduDescription').value = btn.dataset.description || '';
        });
      }
    });

    // Removed the scrolling behavior since we are using modals now!
  </script>"""

# Replace the previous auto-scroll logic with the new modal prefill logic
js_old_start = content.find("    // Auto-scroll to form after submission")
if js_old_start != -1:
    js_old_end = content.find("</script>", js_old_start)
    if js_old_end != -1:
        content = content[:js_old_start-14] + js_modals + content[js_old_end+9:]

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(content)
    print("Successfully updated admin-resume.html to use layout with Modals")
