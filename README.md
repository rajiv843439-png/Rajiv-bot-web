# RAJIV TG BOTS

A mobile-friendly Telegram bot directory with search, category filtering, owner link, and a password-protected admin panel.

## Included

- 10 starter bot listings from the request
- Open Bot links to `https://t.me/<username>`
- Search and category filters
- Admin login at `/login`
- Add/edit/delete bot listings
- Optional public avatar image URL
- SQLite database (`bots.db`) created automatically
- `/health` health-check endpoint

## Important: set secrets first

The admin password previously shared in chat is **not included in this project**. Choose a new, unique password.

Set these environment variables before running/deploying:

- `ADMIN_PASSWORD` — required to enable admin login
- `SECRET_KEY` — long random value used to sign sessions
- `PORT` — optional; hosting providers usually set this automatically
- `DATABASE_PATH` — optional; use a persistent disk path if your host supports one
- `COOKIE_SECURE=1` — set this on HTTPS hosting

Never commit passwords or secret keys to GitHub.

## Run on Android / Termux

1. Install Python and Git from your usual trusted sources.
2. Extract this ZIP, then open a terminal in the `RAJIV_TG_BOTS` folder.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set secrets (replace the sample values; do not share them):

   ```bash
   export ADMIN_PASSWORD='choose-a-new-strong-password'
   export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
   python bot.py
   ```

5. Open `http://127.0.0.1:5000` on the same phone.
6. Open `/login` to sign in to the admin panel.

The website is only available while the Python process and device are running. For a public, 24/7 website, deploy the Flask app to a Python web host and use persistent storage for `bots.db`.

## GitHub and public hosting

GitHub stores the source code; **GitHub Pages cannot run this Flask/Python backend**. To run the admin panel and SQLite database, deploy to a Python-capable host. Upload `bot.py` and `requirements.txt`, set `ADMIN_PASSWORD` and `SECRET_KEY` as private environment variables in that host's dashboard, and use the start command:

```bash
python bot.py
```

For a production host, configure its provided HTTPS URL and persistent disk/database. If the host uses ephemeral storage, bot edits can be lost when the app restarts.

## Project files

- `bot.py` — complete Flask website and admin routes
- `requirements.txt` — Python dependency
- `README.md` — setup and deployment instructions

## Notes

- Telegram usernames are links; this site does not control the bots themselves.
- Avatar images are entered as public image URLs. Automatic Telegram profile-photo fetching is not configured in this standalone version.
- Use a unique admin password and keep the hosting environment variables private.
