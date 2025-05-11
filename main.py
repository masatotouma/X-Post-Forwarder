import os
import json
import requests
import subprocess
from datetime import datetime

# Constants and other stuff

BEARER_TOKEN = os.environ.get("TWITTER_BEARER")
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
USERNAME = "MasatoTouma"
SOURCE = f"Twitter - @{USERNAME}"
SAVE_FILE = "last_seen.json"

### ACTUAL CODE ###

def get_user_id(username):
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()["data"]["id"]

def get_latest_tweet(user_id):
    url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results=5&tweet.fields=created_at"
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()["data"][0]

def send_to_discord(text, link):
    message = f"**New tweet from @{USERNAME}**\n{text}\n{link}"
    r = requests.post(WEBHOOK_URL, json={"content": message})
    print("Sent to Discord:", r.status_code)

def load_last_seen():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_last_seen(data):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ---------

if __name__ == "__main__":
    last_seen = load_last_seen()

    user_id = get_user_id(USERNAME)
    tweet = get_latest_tweet(user_id)
    tweet_id = tweet["id"]

    if last_seen.get(SOURCE) != tweet_id:
        print("New tweet detected.")
        tweet_url = f"https://twitter.com/{USERNAME}/status/{tweet_id}"
        send_to_discord(tweet["text"], tweet_url)
        last_seen[SOURCE] = tweet_id
        save_last_seen(last_seen)
    else:
        print("No new tweet.")
