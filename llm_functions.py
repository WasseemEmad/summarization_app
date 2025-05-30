import os
import requests
import pandas as pd
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from openai import OpenAI

# Load OpenAI API key
load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')
openai = OpenAI()

# Model to use
MODEL = "gpt-4o-mini"


class Website:
    def __init__(self, url):
        self.url = url
        self.title = ""
        self.text = ""

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            self.title = soup.title.string if soup.title else "No title found"
            body = soup.body
            if body:
                for tag in body(["script", "style", "img", "input"]):
                    tag.decompose()
                self.text = body.get_text(separator="\n", strip=True)

        except Exception as e:
            print(f"[ERROR] Failed to fetch {url}: {e}")


def fetch_latest_articles(topic, max_results=5):
    """
    Fetch the latest articles using DuckDuckGo.
    """
    results = DDGS().text(topic, safesearch='off', backend="lite", timelimit='m', max_results=max_results)
    return [item['href'] for item in results]


def get_system_prompt(topic):
    return f"""
You are an AI assistant helping a design software company identify potential customers in the 3D printing space.

You will:
- Summarize the content of the website.
- Identify any companies mentioned.
- Highlight announcements, trends, or projects that suggest they might need 3D design software.
- Score how likely they are to be interested (0-10) and explain why.

Respond in markdown format.
"""


def build_user_prompt(website):
    return f"""You are looking at a webpage titled: "{website.title}"

Here is the full content of the website:

{website.text}

Please:
1. Summarize the key points.
2. List any companies mentioned.
3. Identify potential buying signals for 3D design software.
4. Rate the buying potential from 0 to 10 and justify it.
"""


def analyze_articles(topic="3D Printing trends", max_results=5, save_csv=True):
    links = fetch_latest_articles(topic, max_results=max_results)

    summaries = []

    for link in links:
        print(f"\n[INFO] Processing: {link}")
        website = Website(link)

        if not website.text.strip():
            print("[WARN] No text content found, skipping.")
            continue

        messages = [
            {"role": "system", "content": get_system_prompt(topic)},
            {"role": "user", "content": build_user_prompt(website)}
        ]

        try:
            response = openai.chat.completions.create(model=MODEL, messages=messages)
            summary = response.choices[0].message.content
            summaries.append({
                "url": link,
                "title": website.title,
                "summary": summary
            })
            print("[SUCCESS] Summary generated.")

        except Exception as e:
            print(f"[ERROR] OpenAI failed: {e}")

    if save_csv:
        df = pd.DataFrame(summaries)
        df.to_csv("3d_trend_company_insights.csv", index=False)
        print("\n✅ Results saved to 3d_trend_company_insights.csv")

    return summaries


if __name__ == "__main__":
    topic = "3D Printing market trends"
    results = analyze_articles(topic=topic, max_results=5)
    for i, res in enumerate(results, 1):
        print(f"\n==== ARTICLE #{i} ====\nTitle: {res['title']}\nURL: {res['url']}\n\n{res['summary']}\n")
