import requests
import re

login_url = "https://johnsathvik.com/admin"
resume_url = "https://johnsathvik.com/admin-resume"

# We saw the admin username/password environment logic in earlier conversations, 
# but it was typically "admin" / "johN@123$" or they fetch from firebase.
# Let's just try basic request first to see what we get.
session = requests.Session()

# If we get a 200 on /admin-login, let's see. We don't have the password explicitly known.
# Wait, do we know the password? 
# Maybe we can just check if we can run curl from within the EC2 instance? We couldn't SSH.
# Wait, can we GET the raw github URL instead? We know the github branch `main` has the modals.

print("Checking github repo directly to confirm what we pushed...")
branch_url = "https://raw.githubusercontent.com/sathvikjohn/MyPortfolio/main/admin/templates/admin-resume.html"
resp = requests.get("https://raw.githubusercontent.com/sathvik-john/MyPortfolio/main/admin/templates/admin-resume.html")
# URL might be different. Let's run a local git log.

import subprocess
out = subprocess.check_output("git log -n 1 --stat", shell=True).decode()
print("Recent commit stat locally: ")
print(out)
