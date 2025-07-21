# Meetz Event Scraper

This repository contains a simple Instagram scraper using [Instaloader](https://instaloader.github.io/) that collects recent car meet posts and stores them in Firebase Firestore.

## Requirements

- Python 3.10+
- `instaloader`
- `firebase-admin`

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

3. Run the scraper:

```bash
python scraper.py
```

The script pulls posts from predefined car meet related hashtags from the last seven days and saves them to the `instagram_posts` collection in Firestore. Run the script periodically (e.g., via cron) to keep the data updated.


