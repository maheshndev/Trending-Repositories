import requests
import datetime
import os
import calendar
import re

README = "README.md"


def fetch_trending_repos():
    """Fetch top 10 daily trending GitHub repos from public API."""
    url = "https://ghapi.huchen.dev/repositories?since=daily"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        return data[:10]
    except Exception as e:
        print(f"Error fetching trending repos: {e}")
        return []


def format_daily_section(date_obj, repos):
    """Format markdown section for one day of trending repos."""
    date_str = date_obj.strftime("%Y-%m-%d")
    header = f"## Trending On Date {date_str}\n\n"
    lines = []
    for repo in repos:
        name = repo.get("name", "")
        author = repo.get("author", "")
        url = repo.get("url", "")
        desc = repo.get("description") or ""
        stars = repo.get("stars", 0)
        language = repo.get("language") or "Unknown"
        lines.append(f"- [{author}/{name}]({url}) — {desc} ⭐ {stars} — {language}")
    return header + "\n".join(lines) + "\n\n"


def read_file(filename):
    if not os.path.exists(filename):
        return ""
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


def write_file(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)


def find_daily_sections(text):
    """Return list of all daily trending markdown sections in text."""
    pattern = r"(## Trending On Date \d{4}-\d{2}-\d{2}\n(?:- .*\n)+\n?)"
    return re.findall(pattern, text)


def parse_date_from_section(section):
    """Extract date object from daily section header."""
    m = re.match(r"## Trending On Date (\d{4}-\d{2}-\d{2})", section)
    if m:
        return datetime.datetime.strptime(m.group(1), "%Y-%m-%d").date()
    return None


def find_sections_by_month(text, year, month):
    """Return all daily sections in given year and month."""
    sections = find_daily_sections(text)
    filtered = []
    for sec in sections:
        date_obj = parse_date_from_section(sec)
        if date_obj and date_obj.year == year and date_obj.month == month:
            filtered.append(sec)
    return filtered


def remove_sections(text, sections):
    """Remove all given sections from text."""
    for sec in sections:
        text = text.replace(sec, "")
    return text


def find_all_archive_links(text):
    """Find all previous month archive markdown links in README.md."""
    pattern = r"\[View Previous Month → (Trending On Month .+?\.md)\]\(./.+?\.md\)"
    return re.findall(pattern, text)


def remove_all_archive_links(text):
    """Remove all previous archive links from README.md."""
    pattern = r"\[View Previous Month → Trending On Month .+?\.md\]\(./.+?\.md\)\n*"
    return re.sub(pattern, "", text)


def main():
    today = datetime.date.today()
    year = today.year
    month = today.month
    month_name = calendar.month_name[month]

    readme_text = read_file(README)

    # 1. Archive previous month data if today is 1st of month
    if today.day == 1:
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        prev_month_name = calendar.month_name[prev_month]

        # Extract previous month's daily sections
        prev_month_sections = find_sections_by_month(readme_text, prev_year, prev_month)

        if prev_month_sections:
            # Write to monthly archive file
            archive_filename = f"Trending On Month {prev_month_name}-{prev_year}.md"
            archive_content = f"# Trending On Month {prev_month_name}-{prev_year}\n\n"
            archive_content += "".join(prev_month_sections)

            write_file(archive_filename, archive_content)
            print(f"Created archive file: {archive_filename}")

            # Remove these daily sections from README
            readme_text = remove_sections(readme_text, prev_month_sections)

        # Remove all old archive links to prevent duplicates
        readme_text = remove_all_archive_links(readme_text)

        # Add archive links for all existing archive files sorted by date
        archive_files = sorted(
            [f for f in os.listdir(".") if re.match(r"Trending On Month [A-Za-z]+-\d{4}\.md", f)],
            key=lambda f: datetime.datetime.strptime(f[len("Trending On Month "):-3], "%B-%Y"),
            reverse=False,
        )

        archive_links = []
        for af in archive_files:
            display_name = af.replace(".md", "")
            archive_links.append(f"[View Previous Month → {display_name}](./{af})")

        if archive_links:
            # Put all archive links at top of README, separated by lines
            archive_links_text = "\n".join(archive_links) + "\n\n"
            readme_text = archive_links_text + readme_text

    # 2. Fetch today's trending repos and format section
    trending_repos = fetch_trending_repos()
    today_section = format_daily_section(today, trending_repos)

    # Remove existing section for today if any
    today_section_pattern = rf"## Trending On Date {today.strftime('%Y-%m-%d')}\n(?:- .*\n)+\n?"
    readme_text = re.sub(today_section_pattern, "", readme_text)

    # Append today's trending section at end
    if not readme_text.endswith("\n"):
        readme_text += "\n"
    readme_text += today_section

    # Save updated README.md
    write_file(README, readme_text)
    print(f"README.md updated with trending repos for {today}")

if __name__ == "__main__":
    main()
