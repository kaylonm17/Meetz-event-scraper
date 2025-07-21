import os
from datetime import datetime, timedelta

import instaloader
from firebase_admin import credentials, firestore, initialize_app

CAR_MEET_HASHTAGS = [
    "carmeet",
    "carmeetup",
    "cargathering",
]

class InstagramCarMeetScraper:
    """Fetch recent posts related to car meets and save them to Firebase."""

    def __init__(self, firebase_key_path: str, username: str | None = None, password: str | None = None):
        self.loader = instaloader.Instaloader()
        if username and password:
            self.loader.login(username, password)

        cred = credentials.Certificate(firebase_key_path)
        initialize_app(cred)
        self.db = firestore.client()

    def fetch_recent_posts(self, since_days: int = 7):
        since = datetime.utcnow() - timedelta(days=since_days)
        posts_to_save = []

        for hashtag in CAR_MEET_HASHTAGS:
            tag = instaloader.Hashtag.from_name(self.loader.context, hashtag)
            for post in tag.get_posts():
                if post.date_utc < since:
                    break
                caption = post.caption or ""
                posts_to_save.append(
                    {
                        "shortcode": post.shortcode,
                        "url": f"https://www.instagram.com/p/{post.shortcode}/",
                        "caption": caption,
                        "taken_at": post.date_utc.isoformat(),
                        "likes": post.likes,
                        "hashtag": hashtag,
                    }
                )
        return posts_to_save

    def save_posts(self, posts):
        for post in posts:
            doc_ref = self.db.collection("instagram_posts").document(post["shortcode"])
            doc_ref.set(post)


def main():
    fb_key = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    if not fb_key:
        raise RuntimeError(
            "Set FIREBASE_SERVICE_ACCOUNT env var to the path of your Firebase service account JSON."
        )

    insta_user = os.environ.get("INSTA_USERNAME")
    insta_pass = os.environ.get("INSTA_PASSWORD")

    scraper = InstagramCarMeetScraper(fb_key, insta_user, insta_pass)
    posts = scraper.fetch_recent_posts(7)
    scraper.save_posts(posts)


if __name__ == "__main__":
    main()
