#!/usr/bin/env python
import requests
import re  # Regular expression library

def github_latest_release_version(gh_project):
    api_url = f"https://api.github.com/repos/{gh_project}/releases/latest"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        version = data.get('tag_name', 'Unknown version')

        # Remove all characters except digits and period
        semver_version = re.sub(r"[^0-9.]", "", version)
        return semver_version
    else:
        return f"Failed to retrieve data: HTTP {response.status_code}"

gh_project = "metallb/metallb"
latest_version = github_latest_release_version(gh_project)
print(f"Latest release version for {gh_project}: {latest_version}")
