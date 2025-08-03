import os
import re
import time
from datetime import datetime, timedelta
from typing import Iterable, Optional, Dict, Any

import instaloader
from dateutil.parser import ParserError, parse as parse_date
from firebase_admin import credentials, firestore, initialize_app
from geopy.geocoders import Nominatim

# Add the Instagram usernames you want to monitor here
USERNAMES = [
    "houston_carmeets",
    "coffeeandcars",
    "eatsleepcarmeet",
    "houstonandcars",
]

CAR_MEET_KEYWORD = "car meet"

_GEOCODER = Nominatim(user_agent="meetz_scraper")

def extract_address(text: str) -> Optional[str]:
    """Return a simple street address found in text if present."""
    pattern = r"\d{1,5}\s+[\w\s\.]+,\s*[\w\s\.]+,\s*[A-Z]{2}"
    match = re.search(pattern, text)
    return match.group(0).strip() if match else None


def geocode(address: str) -> Optional[Dict[str, float]]:
    try:
        location = _GEOCODER.geocode(address)
    except Exception:
        location = None
    if location:
        return {"lat": location.latitude, "lng": location.longitude}
    return None


def extract_event_datetime(text: str) -> Optional[datetime]:
    """Return the first parseable datetime in ``text`` if present."""
    try:
        return parse_date(text, fuzzy=True)
    except (ParserError, ValueError):
        return None


class InstagramCarMeetScraper:
    """Fetch recent posts related to car meets from user accounts and save them to Firebase."""

    def __init__(self, firebase_key_path: str, username: str | None = None, password: str | None = None):
        self.loader = instaloader.Instaloader()
        if username and password:
            self.loader.login(username, password)

        cred = credentials.Certificate(firebase_key_path)
        initialize_app(cred)
        self.db = firestore.client()

    def fetch_recent_posts(self, since_days: int = 3) -> Iterable[Dict[str, Any]]:
        """Yield recent car-meet related posts within ``since_days`` days."""
        since = datetime.utcnow() - timedelta(days=since_days)

        for username in USERNAMES:
            profile = instaloader.Profile.from_username(self.loader.context, username)
            while True:
                try:
                    for post in profile.get_posts():
                        if post.date_utc < since:
                            break
                        caption = post.caption or ""
                        if CAR_MEET_KEYWORD not in caption.lower():
                            continue
                        address = extract_address(caption)
                        location = geocode(address) if address else None
                        event_time = extract_event_datetime(caption)
                        yield {
                            "shortcode": post.shortcode,
                            "url": f"https://www.instagram.com/p/{post.shortcode}/",
                            "caption": caption,
                            "taken_at": post.date_utc,
                            "likes": post.likes,
                            "username": username,
                            "address": address,
                            "location": location,
                            "event_time": event_time,
                        }
                    break
                except instaloader.exceptions.ConnectionException as exc:
                    message = str(exc)
                    if "please wait" in message.lower() or "401" in message:
                        print(
                            f"Rate limit hit for {username}: {message}. "
                            "Sleeping before retry."
                        )
                        time.sleep(600)
                        continue
                    print(f"Connection error for {username}: {message}. Skipping user.")
                    break

    def save_posts(self, posts: Iterable[Dict[str, Any]]):
        for post in posts:
            doc_ref = self.db.collection("instagram_posts").document(post["shortcode"])
            doc_ref.set(post)


def main() -> None:
    fb_key = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    if not fb_key:
        raise RuntimeError("Set FIREBASE_SERVICE_ACCOUNT env var to the path of your Firebase service account JSON.")

    insta_user = os.environ.get("INSTA_USERNAME")
    insta_pass = os.environ.get("INSTA_PASSWORD")

    scraper = InstagramCarMeetScraper(fb_key, insta_user, insta_pass)
    posts = scraper.fetch_recent_posts()
    scraper.save_posts(posts)


if __name__ == "__main__":
    main()
