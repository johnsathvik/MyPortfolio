import os

about_file = r"d:\Disk\MyPortfolio\admin\templates\admin-about.html"

with open(about_file, 'r', encoding='utf-8') as f:
    content = f.read()

profile_details_html = """
        <hr class="section-divider">

        <!-- Manage Profile Details Card -->
        <div class="card">
          <div class="card-header">
            <i class="bi bi-person-lines-fill"></i> Profile Details (Public Homepage)
          </div>
          <div class="card-body">
            <div class="row mb-4">
              <div class="col-md-6 mb-3">
                <label class="text-muted small">Name</label>
                <div class="text-white">{{ profile.name if profile and profile.name else 'Not set' }}</div>
              </div>
              <div class="col-md-6 mb-3">
                <label class="text-muted small">Title / Profession</label>
                <div class="text-white">{{ profile.title if profile and profile.title else 'Not set' }}</div>
              </div>
              <div class="col-md-6 mb-3">
                <label class="text-muted small">Location</label>
                <div class="text-white">{{ profile.location if profile and profile.location else 'Not set' }}</div>
              </div>
              <div class="col-md-6 mb-3">
                <label class="text-muted small">Specialization</label>
                <div class="text-white">{{ profile.specialization if profile and profile.specialization else 'Not set' }}</div>
              </div>
              <div class="col-md-6 mb-3">
                <label class="text-muted small">Experience Level</label>
                <div class="text-white">{{ profile.experience_level if profile and profile.experience_level else 'Not set' }}</div>
              </div>
              <div class="col-md-6 mb-3">
                <label class="text-muted small">Education (Short)</label>
                <div class="text-white">{{ profile.education if profile and profile.education else 'Not set' }}</div>
              </div>
              <div class="col-md-12 mb-3">
                <label class="text-muted small">Languages</label>
                <div class="text-white">{{ profile.languages if profile and profile.languages else 'Not set' }}</div>
              </div>
            </div>
            <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#editProfileModal">
              <i class="bi bi-pencil-square"></i> Edit Profile Details
            </button>
          </div>
        </div>

        <!-- Edit Profile Details Modal -->
        <div class="modal fade" id="editProfileModal" tabindex="-1" aria-hidden="true">
          <div class="modal-dialog modal-lg">
            <form method="post" action="{{ url_for('admin_about') }}">
              <div class="modal-content">
                <div class="modal-header">
                  <h5 class="modal-title highlight">
                    <i class="bi bi-person-lines-fill"></i> Edit Profile Details
                  </h5>
                  <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                  <input type="hidden" name="action_type" value="update_profile">
                  <div class="row">
                    <div class="col-md-6 mb-3">
                      <label for="profileName" class="form-label">Name</label>
                      <input type="text" class="form-control" id="profileName" name="profile_name" 
                        value="{{ profile.name if profile and profile.name else '' }}" required>
                    </div>
                    <div class="col-md-6 mb-3">
                      <label for="profileTitle" class="form-label">Title / Profession</label>
                      <input type="text" class="form-control" id="profileTitle" name="profile_title" 
                        value="{{ profile.title if profile and profile.title else '' }}" required>
                    </div>
                    <div class="col-md-6 mb-3">
                      <label for="profileLocation" class="form-label">Location</label>
                      <input type="text" class="form-control" id="profileLocation" name="profile_location" 
                        value="{{ profile.location if profile and profile.location else '' }}" required>
                    </div>
                    <div class="col-md-6 mb-3">
                      <label for="profileSpecialization" class="form-label">Specialization</label>
                      <input type="text" class="form-control" id="profileSpecialization" name="profile_specialization" 
                        value="{{ profile.specialization if profile and profile.specialization else '' }}" required>
                    </div>
                    <div class="col-md-6 mb-3">
                      <label for="profileExperience" class="form-label">Experience Level</label>
                      <input type="text" class="form-control" id="profileExperience" name="profile_experience" 
                        value="{{ profile.experience_level if profile and profile.experience_level else '' }}" required>
                    </div>
                    <div class="col-md-6 mb-3">
                      <label for="profileEducation" class="form-label">Education (Short)</label>
                      <input type="text" class="form-control" id="profileEducation" name="profile_education" 
                        value="{{ profile.education if profile and profile.education else '' }}" required>
                    </div>
                    <div class="col-md-12 mb-3">
                      <label for="profileLanguages" class="form-label">Languages (Comma separated)</label>
                      <input type="text" class="form-control" id="profileLanguages" name="profile_languages" 
                        value="{{ profile.languages if profile and profile.languages else '' }}" required>
                    </div>
                  </div>
                </div>
                <div class="modal-footer">
                  <button type="submit" class="btn btn-primary">
                    <i class="bi bi-check-circle"></i> Save Profile Details
                  </button>
                  <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                </div>
              </div>
            </form>
          </div>
        </div>
"""

# Insert right after the bio section and before the resume upload section
insert_point = "<!-- Resume Upload -->"
if insert_point in content and profile_details_html not in content:
    content = content.replace(insert_point, profile_details_html + "\n        " + insert_point)
    with open(about_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully added Profile Details form to admin-about.html")
else:
    print("Could not find insertion point or form already exists.")
