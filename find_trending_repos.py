import requests
from datetime import datetime

# Fetch today's date and extract the last digit
today = datetime.today()
last_digit = int(str(today.day)[-1])

# GitHub trending repositories API
TRENDING_URL = 'https://api.github.com/search/repositories'

# Function to get trending repositories
def get_trending_repositories():
    params = {
        'q': 'stars:>1000',  # Filter trending repos with more than 1000 stars
        'sort': 'stars',
        'order': 'desc',
    }
    response = requests.get(TRENDING_URL, params=params)
    response.raise_for_status()
    repos = response.json().get('items', [])
    trending_repos = []
    for repo in repos[:last_digit]:  # Limit to the number of commits based on the date's last digit
        trending_repos.append(f"- [{repo['name']}]({repo['html_url']})")
    return trending_repos

# Prepare the section to add to README.md
trending_section = f"\n## Trending Repositories {today.strftime('%Y-%m-%d')}\n\n"
trending_repositories = get_trending_repositories()

# Add trending repositories to the section
trending_section += '\n'.join(trending_repositories)

# Update the README.md file
with open('README.md', 'a') as readme:
    readme.write(trending_section)

print("Trending repositories section updated in README.md.")
