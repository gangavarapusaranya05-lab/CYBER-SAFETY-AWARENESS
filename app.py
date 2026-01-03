from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

def check_link(url):
    """Check if a link is reachable and return its quality."""
    try:
        start = time.time()
        response = requests.get(url, timeout=5)
        elapsed = time.time() - start
        if response.status_code == 200:
            return "Good" if elapsed < 1.5 else "Moderate"
        else:
            return "Broken"
    except:
        return "Broken"

def get_links(topic, max_links=15):
    """Scrape Bing and categorize the links."""
    query = topic.replace(' ', '+')
    url = f"https://www.bing.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    good_links, moderate_links = [], []

    for item in soup.find_all("li", {"class": "b_algo"}):
        a_tag = item.find("a")
        if a_tag and a_tag["href"].startswith("http"):
            link = a_tag["href"]
            status = check_link(link)
            if status == "Good":
                good_links.append(link)
            elif status == "Moderate":
                moderate_links.append(link)
            if len(good_links) + len(moderate_links) >= max_links:
                break

    return good_links, moderate_links

@app.route("/", methods=["GET", "POST"])
def index():
    good_links, moderate_links = [], []
    topic = ""
    if request.method == "POST":
        topic = request.form.get("topic")
        good_links, moderate_links = get_links(topic)
    return render_template("index.html", topic=topic, good_links=good_links, moderate_links=moderate_links)

if __name__ == "__main__":
    app.run(debug=True)
