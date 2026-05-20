import feedparser
import requests
import schedule
import time
from bs4 import BeautifulSoup

BOT_TOKEN = "8707378004:AAHpL1m3UMqSO4wjSZ2zGhV0o0O_SaP8WQI"
CHAT_ID = "612420092"

KEYWORDS = [
    "ui",
    "ux",
    "product designer",
    "ui/ux",
    "figma",
    "web designer",
    "framer",
    "webflow"
]

RSS_FEEDS = [
    "https://remoteok.com/remote-design-jobs.rss",
    "https://weworkremotely.com/categories/remote-design-jobs.rss",
]

SEEN_FILE = "seen_jobs.txt"

# -----------------------------
# TELEGRAM
# -----------------------------

def send_telegram_message(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    requests.post(url, data=data)

# -----------------------------
# SAVE SEEN JOBS
# -----------------------------

def load_seen_jobs():

    try:
        with open(SEEN_FILE, "r") as f:
            return set(f.read().splitlines())

    except FileNotFoundError:
        return set()

def save_seen_job(job_id):

    with open(SEEN_FILE, "a") as f:
        f.write(job_id + "\n")

seen_jobs = load_seen_jobs()

# -----------------------------
# FILTER
# -----------------------------

def is_relevant(title):

    title = title.lower()

    return any(keyword in title for keyword in KEYWORDS)

# -----------------------------
# RSS JOBS
# -----------------------------

def fetch_rss_jobs():

    jobs = []

    for feed_url in RSS_FEEDS:

        try:

            feed = feedparser.parse(feed_url)

            for item in feed.entries[:20]:

                title = item.title
                link = item.link

                job_id = link

                if job_id in seen_jobs:
                    continue

                if is_relevant(title):

                    seen_jobs.add(job_id)
                    save_seen_job(job_id)

                    jobs.append({
                        "title": title,
                        "link": link,
                        "source": "RSS"
                    })

        except Exception as e:
            print(e)

    return jobs

# -----------------------------
# LINKEDIN SCRAPER
# -----------------------------

def fetch_linkedin_jobs():

    jobs = []

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    url = "https://www.linkedin.com/jobs/search/?keywords=UI%20UX%20Designer&location=Worldwide"

    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "lxml")

    cards = soup.find_all("div", class_="base-search-card")

    for card in cards[:10]:

        try:

            title = card.find("h3").text.strip()

            link = card.find("a")["href"]

            job_id = link

            if job_id in seen_jobs:
                continue

            if is_relevant(title):

                seen_jobs.add(job_id)
                save_seen_job(job_id)

                jobs.append({
                    "title": title,
                    "link": link,
                    "source": "LinkedIn"
                })

        except:
            pass

    return jobs

# -----------------------------
# MAIN
# -----------------------------

def fetch_all_jobs():

    all_jobs = []

    all_jobs.extend(fetch_rss_jobs())
    all_jobs.extend(fetch_linkedin_jobs())

    if not all_jobs:

        print("No new jobs.")

        return

    message = "🎨 <b>New UI/UX Remote Jobs</b>\n\n"

    for job in all_jobs[:15]:

        message += (
            f"💼 <b>{job['title']}</b>\n"
            f"🌍 {job['source']}\n"
            f"🔗 {job['link']}\n\n"
        )

    send_telegram_message(message)

    print("Jobs sent!")

# Run immediately
fetch_all_jobs()

# Daily at 8 AM
fetch_all_jobs()