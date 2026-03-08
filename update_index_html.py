import os

index_file = r"d:\Disk\MyPortfolio\PortfolioMain\templates\index.html"

with open(index_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace hardcoded JOHN SATHVIK inside Get to Know Me section (around line 212)
# Original:                 <h3>JOHN SATHVIK </h3>
content = content.replace("                <h3>JOHN SATHVIK </h3>", "                <h3>{{ data.profile.name }}</h3>")

# Replace profession under Name
# Original:                 <p class="profession">AWS Solutions Architect</p>
content = content.replace('                <p class="profession">AWS Solutions Architect</p>', '                <p class="profession">{{ data.profile.title }}</p>')

# Replace hardcoded location
# Original:                   <a href="#" class="contact-item"><i class="bi bi-geo-alt"></i> St. Louis, Missouri, United States</a>
content = content.replace('<a href="#" class="contact-item"><i class="bi bi-geo-alt"></i> St. Louis, Missouri, United States</a>', '<a href="#" class="contact-item"><i class="bi bi-geo-alt"></i> {{ data.profile.location }}</a>')

# Replace Specialization value
# Original:                   <div class="detail-item"><span class="detail-label">Specialization</span><span
#                       class="detail-value">Cloud Architecture & Web Development</span></div>
content = content.replace('<span class="detail-value">Cloud Architecture & Web Development</span>', '<span class="detail-value">{{ data.profile.specialization }}</span>')

# Replace Experience Level value
# Original:                   <div class="detail-item"><span class="detail-label">Experience Level</span><span
#                       class="detail-value">Mid-level Professional</span></div>
content = content.replace('<span class="detail-value">Mid-level Professional</span>', '<span class="detail-value">{{ data.profile.experience_level }}</span>')

# Replace Education value
# Original:                   <div class="detail-item"><span class="detail-label">Education</span><span
#                       class="detail-value">Computer Science, MS</span></div>
content = content.replace('<span class="detail-value">Computer Science, MS</span>', '<span class="detail-value">{{ data.profile.education }}</span>')

# Replace Languages value
# Original:                   <div class="detail-item"><span class="detail-label">Languages</span><span
#                       class="detail-value">English, Telugu, Hindi</span></div>
content = content.replace('<span class="detail-value">English, Telugu, Hindi</span>', '<span class="detail-value">{{ data.profile.languages }}</span>')

with open(index_file, 'w', encoding='utf-8') as f:
    f.write(content)
    print("Successfully updated PortfolioMain/templates/index.html to use profile details")
