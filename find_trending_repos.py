import requests
from datetime import datetime

# GitHub API to get trending repositories
def get_trending_repositories():
    url = "https://api.github.com/search/repositories?q=stars:>1000&sort=stars&order=desc"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()["items"][:5]  # Top 5 trending repositories
    else:
        return []

# Function to update README with trending repositories
def update_readme(trending_repos):
    # Read the current README.md file
    with open("README.md", "r") as file:
        readme_content = file.read()

    # Get today's date
    today = datetime.today().strftime('%Y-%m-%d')
    
    # Generate the section for trending repositories
    trending_section = f"\n## Trending Repositories {today}\n\n"
    for repo in trending_repos:
        repo_name = repo["name"]
        repo_url = repo["html_url"]
        trending_section += f"- [{repo_name}]({repo_url})\n"

    # Check if the trending section already exists
    if "## Trending Repositories" in readme_content:
        # Remove the old trending section
        start_index = readme_content.find("## Trending Repositories")
        end_index = readme_content.find("\n\n", start_index)
        readme_content = readme_content[:start_index] + readme_content[end_index + 2:]
    
    # Add the new trending section at the end of README.md
    readme_content += trending_section

    # Write the updated content back to README.md
    with open("README.md", "w") as file:
        file.write(readme_content)

# Main function to fetch repos and update README
def main():
    trending_repos = get_trending_repositories()
    if trending_repos:
        update_readme(trending_repos)
        print("README.md updated with trending repositories.")
    else:
        print("No trending repositories found.")

if __name__ == "__main__":
    main()
