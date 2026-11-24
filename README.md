# Pheli FM 95.0 — DJ Survival Challenge

A Django-powered weekly DJ survival competition for Pheli FM 95.0. Fans choose the DJ they want to keep in the competition. The DJ with more votes survives and faces a new challenger in the next weekly round.

## Phase 3: Server-side voting

- Votes are stored in the Django SQLite database, not in browser localStorage.
- All visitors see the same totals from the server.
- A browser session receives one vote per competition.
- A database-level unique constraint prevents the same session identity from voting twice in the same round.
- Votes are accepted only while the selected competition is open and within its scheduled start/end time.
- The public page refreshes shared totals automatically.
- Administrators can inspect recorded votes and totals in Django admin. Individual vote records cannot be created or deleted through the admin interface.

### Voting protection notes

The system uses an anonymous browser-session identity and stores only its SHA-256 hash with the vote. This is a practical first anti-duplicate measure, not verified identity or complete fraud prevention. Clearing browser cookies, using another browser/device, or automation can bypass session-based limits. For a high-stakes public competition, add verified mobile/email identity, rate limiting, monitoring and a clear voting policy before launch.

## Phase 2: Competition management

The password-protected Django admin area lets Pheli FM administrators:
- Add, edit, search and deactivate DJs.
- Store each DJ's name, short bio and photo URL.
- Create weekly competitions and select two different DJs.
- Set voting start and end dates/times.
- Open voting, close voting or mark a round completed.
- Manage one open competition at a time.

## Run locally on Windows

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver
```

Public website: http://127.0.0.1:8000/

Administrator dashboard: http://127.0.0.1:8000/admin/

If you already ran Phase 2, pull the latest changes and run `py manage.py migrate` to create the new Vote table. Your existing DJs and competitions remain in the local SQLite database.

## First-time competition setup

1. Sign in at `/admin/`.
2. Under **DJs**, add the two DJs for the first matchup. Add a full image URL if available.
3. Under **Weekly competitions**, create Week 1, select the two DJs, and set the start and end dates/times. Save it as Draft.
4. Select that competition in the list and choose **Open voting for selected competition** from the Actions menu.
5. The public home page will show the matchup. Use **Close voting for selected competition** when voting should stop.

Use South African local time (Africa/Johannesburg) when entering competition dates.

## Run automated tests

```powershell
py manage.py test competition
```

Tests cover server-side vote storage, duplicate vote rejection, shared totals across separate browser sessions, invalid choices and closed competitions.

## Database and deployment

Local development uses SQLite (db.sqlite3); no separate database server is required. The database file must be persisted and backed up. For a multi-instance production deployment, use PostgreSQL or another shared production database rather than a local SQLite file.

Before deploying, set a strong DJANGO_SECRET_KEY, set DJANGO_DEBUG=False, and set DJANGO_ALLOWED_HOSTS to the actual hostnames. Use HTTPS. Configure production session/cookie settings and reliable backups. Do not commit credentials or the production database file.
