import requests
import datetime
import os
import calendar
import re

README = "README.md"

def fetch_trending_repos():
    """Fetch top 10 daily trending GitHub repos."""
    url = "https://ghapi.huchen.dev/repositories?since=daily"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()[:10]
    except Exception as e:
        print(f"Error fetching trending repos: {e}")
        return []

def format_daily_section(date_obj, repos):
    """Format a markdown section for a single day."""
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
    """Return list of all daily trending markdown sections."""
    pattern = r"(## Trending On Date \d{4}-\d{2}-\d{2}\n(?:- .*\n)+\n?)"
    return re.findall(pattern, text)

def parse_date_from_section(section):
    """Extract date from daily section header."""
    m = re.match(r"## Trending On Date (\d{4}-\d{2}-\d{2})", section)
    return datetime.datetime.strptime(m.group(1), "%Y-%m-%d").date() if m else None

def find_sections_by_month(text, year, month):
    """Return all daily sections from given month."""
    sections = find_daily_sections(text)
    return [sec for sec in sections if (d := parse_date_from_section(sec)) and d.year == year and d.month == month]

def remove_sections(text, sections):
    for sec in sections:
        text = text.replace(sec, "")
    return text

def find_all_archive_links(text):
    pattern = r"\[View Previous Month → (Trending On Month .+?\.md)\]\(./.+?\.md\)"
    return re.findall(pattern, text)

def remove_all_archive_links(text):
    pattern = r"\[View Previous Month → Trending On Month .+?\.md\]\(./.+?\.md\)\n*"
    return re.sub(pattern, "", text)

def main():
    today = datetime.date.today()
    year, month = today.year, today.month
    month_name = calendar.month_name[month]

    readme_text = read_file(README)

    # 1st day of month: archive previous month data
    if today.day == 1:
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        prev_month_name = calendar.month_name[prev_month]

        prev_month_sections = find_sections_by_month(readme_text, prev_year, prev_month)

        if prev_month_sections:
            archive_filename = f"Trending On Month {prev_month_name}-{prev_year}.md"
            archive_content = f"# Trending On Month {prev_month_name}-{prev_year}\n\n" + "".join(prev_month_sections)
            write_file(archive_filename, archive_content)
            print(f"Archived previous month sections to {archive_filename}")

            # Remove archived sections from README
            readme_text = remove_sections(readme_text, prev_month_sections)

        # Clean all existing archive links to avoid duplicates
        readme_text = remove_all_archive_links(readme_text)

        # Collect all archive files sorted ascending
        archive_files = sorted(
            [f for f in os.listdir(".") if re.match(r"Trending On Month [A-Za-z]+-\d{4}\.md", f)],
            key=lambda f: datetime.datetime.strptime(f[len("Trending On Month "):-3], "%B-%Y")
        )

        archive_links = [f"[View Previous Month → {af[:-3]}](./{af})" for af in archive_files]
        if archive_links:
            readme_text = "\n".join(archive_links) + "\n\n" + readme_text

    # Remove today's section if exists
    today_section_pattern = rf"## Trending On Date {today.strftime('%Y-%m-%d')}\n(?:- .*\n)+\n?"
    readme_text = re.sub(today_section_pattern, "", readme_text)

    # Filter out any daily sections not from current month (keep only current month daily sections)
    all_sections = find_daily_sections(readme_text)
    for sec in all_sections:
        date = parse_date_from_section(sec)
        if date and (date.year != year or date.month != month):
            readme_text = readme_text.replace(sec, "")

    # Fetch trending repos & append today's section
    trending_repos = fetch_trending_repos()
    today_section = format_daily_section(today, trending_repos)

    if not readme_text.endswith("\n"):
        readme_text += "\n"
    readme_text += today_section

    write_file(README, readme_text)
    print(f"README.md updated with trending repos for {today}")

if __name__ == "__main__":
    main()
