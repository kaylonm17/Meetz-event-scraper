# Meetz Event Scraper

This repository contains a simple Instagram scraper using [Instaloader](https://instaloader.github.io/) that collects recent car meet posts from specified user accounts and stores them in Firebase Firestore. Captions are scanned for addresses which are geocoded so the Meetz app can drop pins on a map.

## Requirements

- Python 3.10+
- `instaloader`
- `firebase-admin`
- `geopy`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Create a Firebase project and generate a service account key JSON. Save the path to this file.
2. Export the following environment variables:

```bash
export FIREBASE_SERVICE_ACCOUNT=/path/to/serviceAccountKey.json
export INSTA_USERNAME=<your-instagram-username>
export INSTA_PASSWORD=<your-instagram-password>
```

3. Edit `scraper.py` and update the `USERNAMES` list with the Instagram accounts you want to monitor.

4. Run the scraper:

```bash
python scraper.py
```

The script fetches posts from the last seven days for each account, attempts to geocode addresses mentioned in captions, and saves results in the `instagram_posts` collection. Run the script daily (for example using cron) to keep the data up to date.
