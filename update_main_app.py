import os

app_file = r"d:\Disk\MyPortfolio\PortfolioMain\app.py"

with open(app_file, 'r', encoding='utf-8') as f:
    app_content = f.read()

# We need to extract Profile Details and pass to `data`
context_start = app_content.find("        # Process experience descriptions to split bullet points")
if context_start != -1:
    profile_logic = """
        # Get Profile Details for About section
        raw_profile = fb.get('/about/profile', None) or {}
        profile_details = next(iter(raw_profile.values())) if raw_profile else {}
        
        # Merge profile details, providing defaults if not set
        profile = {
            'name': profile_details.get('name', 'JOHN SATHVIK') if profile_details.get('name') else 'JOHN SATHVIK',
            'title': profile_details.get('title', 'AWS Solutions Architect') if profile_details.get('title') else 'AWS Solutions Architect',
            'location': profile_details.get('location', 'St. Louis, Missouri, United States') if profile_details.get('location') else 'St. Louis, Missouri, United States',
            'specialization': profile_details.get('specialization', 'Cloud Architecture & Web Development') if profile_details.get('specialization') else 'Cloud Architecture & Web Development',
            'experience_level': profile_details.get('experience_level', 'Mid-level Professional') if profile_details.get('experience_level') else 'Mid-level Professional',
            'education': profile_details.get('education', 'Computer Science, MS') if profile_details.get('education') else 'Computer Science, MS',
            'languages': profile_details.get('languages', 'English, Telugu, Hindi') if profile_details.get('languages') else 'English, Telugu, Hindi'
        }
"""
    app_content = app_content[:context_start] + profile_logic + app_content[context_start:]
    
    # Update the data dictionary assignment
    data_dict_start = app_content.find("        # Prepare data dictionary for template")
    dict_content = """        # Prepare data dictionary for template
        data = {
            'profile': profile,
            'name': profile['name'],  # Use dynamic name
            'specialization': profile['specialization'], # Use dynamic specialization
"""
    app_content = app_content.replace("""        # Prepare data dictionary for template
        data = {
            'name': 'John Sathvik Madipalli',  # Can be moved to Firebase later
            'specialization': 'AWS Solutions Architect & Web Developer',""", dict_content)

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(app_content)
    print("Successfully updated PortfolioMain/app.py with profile details logic")
