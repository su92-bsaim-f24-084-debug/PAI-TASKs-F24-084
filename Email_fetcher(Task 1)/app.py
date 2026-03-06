from flask import Flask, render_template, request
import requests
import re
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    emails = []
    url = ""

    if request.method == "POST":
        url = request.form["url"]

        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # find emails in raw html using regex
        raw_emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", response.text)

        # also check mailto links
        for a in soup.find_all("a", href=True):
            if "mailto:" in a["href"]:
                mail = a["href"].replace("mailto:", "").strip()
                raw_emails.append(mail)

        # remove duplicates
        emails = list(set(raw_emails))

    return render_template("index.html", emails=emails, url=url)


if __name__ == "__main__":
    app.run(debug=True)