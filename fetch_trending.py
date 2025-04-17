import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_trending():
    url = 'https://github.com/trending'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    repos = soup.find_all('article', class_='Box-row')

    trending_list = []
    for repo in repos[:10]:  # Limit to top 10
        title = repo.h1.get_text(strip=True).replace(' ', '')
        description = repo.p.get_text(strip=True) if repo.p else 'No description'
        link = f"https://github.com/{title}"
        trending_list.append(f"- [{title}]({link}): {description}")

    return trending_list

def update_readme(trending_list):
    with open("README.md", "w") as f:
        f.write("# 🔥 GitHub Trending Repositories\n\n")
        f.write(f"_Updated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC_\n\n")
        f.write("\n".join(trending_list))

if __name__ == "__main__":
    trending = fetch_trending()
    update_readme(trending)
