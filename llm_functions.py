import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from openai import OpenAI

class Website:

    def __init__(self, url):
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        }
        """
        Create this Website object from the given url using the BeautifulSoup library
        """
        self.url = url
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)
        
load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

openai = OpenAI()
MODEL = "gpt-4o-mini"


def fetch_latest_articles(topic, max_results=5):
        """
        Fetch the latest articles from 3DPrint.com based on a specific topic.
        """
        results = DDGS().text(topic,safesearch='off',backend="lite", timelimit='m', max_results=max_results)
        return results
    
def get_links_from_results(articles):
        """
        Extract links from the search results.
        """
        
        return [item['href'] for item in articles]
        
def get_system_prompt(topic):
        system_prompt = f"You are an assistant that analyzes the contents of 5 website with the topic about {topic} and provides a short summary, ignoring text that might be navigation related. \
                        Respond in markdown."
        return system_prompt


def user_prompt_for(articles):
        user_prompt = f"You are looking at a article titled {articles.title}"
        user_prompt += "\nThe contents of this website is as follows; \
    please provide a short summary of this website in markdown. \
    If it includes news or announcements, then summarize these too.\n\n"
        user_prompt += articles.text
        return user_prompt


def get_user_prompt(links):
    user_prompt = ""
    for link in links:
        website = Website(link)
        if website.text.strip():  # only if content exists
            user_prompt += user_prompt_for(website)
    return user_prompt

def message_for_openai(system_prompt,user_prompt):
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
def get_message(topic,max_results=2):
        """
        Get the message to send to OpenAI.
        """
        articles = fetch_latest_articles(topic, max_results)
        links = get_links_from_results(articles)
        system_prompt = get_system_prompt(topic)
        user_prompt = get_user_prompt(links)
        return message_for_openai(system_prompt, user_prompt)
    
def get_summary_from_openai(message):
    """
    Get a summary from OpenAI based on the provided message.
    """
    response = openai.chat.completions.create(model=MODEL, messages=message)
    return response.choices[0].message.content