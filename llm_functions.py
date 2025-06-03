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
    results = DDGS().text(topic, safesearch='off', backend="lite", timelimit='d', max_results=max_results)
    return [item['href'] for item in results]


def get_system_prompt(topic):
    return f"""
You are an AI assistant helping a freelancer identify potential customers in the 3D printing industry who might be interested in design automation solutions like Trinckle 3D.
You will be analyzing full article pages. If the article content is missing or invalid, it will be skipped and not included in the results.

You will:
- Summarize the website's key content.
- Identify companies, their projects, and technologies they’re using.
- Highlight trends or initiatives in design automation, customization, or parametric modeling.
- Note any signs they might benefit from Trinckle 3D-like software.
- Mention how to get started with any mentioned trend or tech.
- Rate their likelihood of buying design software (0-10) and explain why.

Focus especially on:
- Parametric design
- Custom part generation
- Internal workflows or software development
- Manufacturing automation or design bottlenecks
- Partnerships in AM (Additive Manufacturing)
    
Respond in markdown format with structured headings.

⚠️ If the webpage has no usable content (e.g., access denied, JavaScript required, blank page), do not generate a summary or include the article.
Respond only if you can extract meaningful information, if this happends do not return a respond with more than 100 character.
Output must be in markdown.

If it did not provide usable content for analysis do not use it in the results.
"""


def build_user_prompt(website):
    return f"""You're reviewing a webpage titled: "{website.title}"

Here's the full text content:

{website.text}

Please perform the following:
1. Summarize the key insights.
2. List all companies mentioned and their projects.
3. Extract any 3D design or manufacturing trends (especially parametric, automated, or customizable workflows).
4. Identify any signs that they might benefit from Trinckle 3D software (design automation, mass customization, etc.).
5. Explain how one might get started with any of the trends or tools mentioned.
6. Rate the company’s buying potential for a design automation tool (0-10) and justify it with clear evidence.
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
