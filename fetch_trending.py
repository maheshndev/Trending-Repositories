import requests
from datetime import datetime, timedelta
import calendar

README = "README.md"

def get_trending_repositories():
    url = "https://api.github.com/search/repositories?q=stars:>1000&sort=stars&order=desc"
    headers = {"Accept": "application/vnd.github.v3+json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("items", [])[:5]
    return []

def is_second_last_day_of_month(today):
    last_day = calendar.monthrange(today.year, today.month)[1]
    return today.day == last_day - 1

def append_to_readme(content):
    with open(README, "a") as f:
        f.write(content)

def create_monthly_archive(month_file, readme_data):
    with open(month_file, "w") as f:
        f.write(readme_data)

def read_readme():
    try:
        with open(README, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def overwrite_readme(link, today_section):
    with open(README, "w") as f:
        f.write(link + "\n\n" + today_section)

def format_section(repos, title):
    section = f"## {title}\n\n"
    for repo in repos:
        section += f"- [{repo['full_name']}]({repo['html_url']}) ⭐ {repo['stargazers_count']}\n"
    section += "\n---\n"
    return section

def main():
    today = datetime.now()
    trending_repos = get_trending_repositories()
    if not trending_repos:
        print("No trending repos found.")
        return

    # Create today's section
    title = f"Trending On Date {today.strftime('%Y-%m-%d')}"
    today_section = format_section(trending_repos, title)

    # Check for archiving
    if is_second_last_day_of_month(today):
        print("Archiving current month's data...")
        month_name = today.strftime('%B')
        year = today.year
        archive_filename = f"Trending On Month {month_name}-{year}.md"
        current_readme = read_readme()

        # Write monthly archive
        create_monthly_archive(archive_filename, current_readme)

        # Replace README.md with a link to archive + today's trending
        archive_link = f"[View Archive for {month_name}-{year}]({archive_filename})"
        overwrite_readme(archive_link, today_section)
    else:
        append_to_readme(today_section)

    print("Trending data updated.")

if __name__ == "__main__":
    main()
