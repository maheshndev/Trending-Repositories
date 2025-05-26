import requests
import datetime
import os
import calendar
import re

README_FILE = "README.md"

def fetch_trending_repositories():
    # GitHub does not provide official API for trending,
    # but there are some unofficial APIs, e.g.:
    # https://github-trending-api.now.sh/repositories?since=daily
    # We'll use a common unofficial API for demo

    url = "https://ghapi.huchen.dev/repositories?since=daily"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        trending = resp.json()
        # Each item contains: author, name, url, description, stars, language etc.
        return trending[:10]  # top 10 trending repos
    except Exception as e:
        print(f"Failed to fetch trending repos: {e}")
        return []

def format_trending_section(date_obj, repos):
    date_str = date_obj.strftime("%Y-%m-%d")
    header = f"## Trending On Date {date_str}\n\n"
    content = ""
    for repo in repos:
        name = repo.get("name", "")
        author = repo.get("author", "")
        url = repo.get("url", "")
        desc = repo.get("description", "") or ""
        stars = repo.get("stars", 0)
        lang = repo.get("language") or "Unknown"

        content += f"- [{author}/{name}]({url}) - {desc} ⭐ {stars} - {lang}\n"

    content += "\n"
    return header + content

def read_file(filename):
    if not os.path.exists(filename):
        return ""
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def write_file(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def find_daily_sections(text):
    # Matches daily trending sections starting with ## Trending On Date YYYY-MM-DD
    pattern = r"(## Trending On Date \d{4}-\d{2}-\d{2}\n(?:- .*\n)+\n?)"
    matches = re.findall(pattern, text)
    return matches

def find_sections_by_month(text, year, month):
    # Filter daily sections in given year/month from the readme text
    daily_sections = find_daily_sections(text)
    filtered = []
    for section in daily_sections:
        # Extract date from section header
        m = re.match(r"## Trending On Date (\d{4})-(\d{2})-(\d{2})", section)
        if m:
            y, mth, _ = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if y == year and mth == month:
                filtered.append(section)
    return filtered

def remove_sections(text, sections_to_remove):
    for sec in sections_to_remove:
        text = text.replace(sec, "")
    return text

def main():
    today = datetime.date.today()
    current_year = today.year
    current_month = today.month
    current_month_name = calendar.month_name[current_month]
    first_day_of_month = today.day == 1

    readme_text = read_file(README_FILE)

    # On the 1st of the month, archive previous month
    if first_day_of_month:
        # Determine previous month and year
        prev_month = current_month - 1 or 12
        prev_year = current_year if current_month != 1 else current_year - 1
        prev_month_name = calendar.month_name[prev_month]

        # Find all previous month's sections
        prev_month_sections = find_sections_by_month(readme_text, prev_year, prev_month)

        if prev_month_sections:
            # Create monthly archive file
            archive_filename = f"Trending On Month {prev_month_name}-{prev_year}.md"

            # Join all previous month sections
            archive_content = f"# Trending On Month {prev_month_name}-{prev_year}\n\n"
            archive_content += "".join(prev_month_sections)

            # Write to archive file
            write_file(archive_filename, archive_content)

            # Remove previous month sections from README.md
            readme_text = remove_sections(readme_text, prev_month_sections)

            # Add link to monthly archive file at top or bottom (here at top)
            link_line = f"[View Previous Month → {archive_filename}](./{archive_filename})\n\n"

            # Remove any existing previous month link (optional: use regex to find)
            readme_text = re.sub(r"\[View Previous Month → Trending On Month .*-.*\.md\]\(.*\)\n*\n*", "", readme_text)

            # Prepend the link to README.md content
            readme_text = link_line + readme_text

    # Fetch today's trending repos
    trending_repos = fetch_trending_repositories()

    # Prepare today's trending section
    today_section = format_trending_section(today, trending_repos)

    # Remove any existing today section (in case of rerun)
    readme_text = re.sub(rf"## Trending On Date {today.strftime('%Y-%m-%d')}\n(?:- .*\n)+\n?", "", readme_text)

    # Append today's section to README.md (at the end)
    if not readme_text.endswith("\n"):
        readme_text += "\n"
    readme_text += today_section

    # Write back to README.md
    write_file(README_FILE, readme_text)

    print("Trending data updated.")

if __name__ == "__main__":
    main()
