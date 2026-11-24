# Pheli FM 95.0 — DJ Survival Challenge

A Django-powered weekly DJ survival competition for Pheli FM 95.0. Fans choose the DJ they want to keep in the competition. The DJ with more votes survives and faces a new challenger in the next weekly round.

## Phase 2: Competition management

The password-protected Django admin area lets Pheli FM administrators:
- Add, edit, search and deactivate DJs.
- Store each DJ's name, short bio and photo URL.
- Create weekly competitions and select two different DJs.
- Set voting start and end dates/times.
- Open voting, close voting or mark a round completed.
- Manage one open competition at a time.

The public home page displays the managed matchup and only enables voting while the round is open and within its scheduled time.

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

## First-time setup

1. Sign in at `/admin/` using the superuser account you created.
2. Under **DJs**, add the two DJs for the first matchup. Add a full image URL if available.
3. Under **Weekly competitions**, create Week 1, select the two DJs, and set the start and end date/time. Save it as Draft.
4. Select the competition in the list and choose **Open voting for selected competition** from the Actions menu.
5. The public home page will show the matchup. Use **Close voting for selected competition** when voting should stop.

Use South African local time (Africa/Johannesburg) when entering competition dates.

## Database

The admin dashboard uses a local SQLite file named `db.sqlite3`. No separate database server is required. Run `py manage.py migrate` after pulling updates to create or update the database schema.

## Important: public votes are still a preview

DJ and competition records are stored in SQLite. Public vote clicks are still stored only in each visitor's browser using localStorage. Those demo votes are not shared between visitors, are not secure against manipulation, and are not official competition results. Phase 3 will move voting to server-side storage and add abuse prevention before the site is used for a real public competition.

## Deployment security

Before deploying, set a strong `DJANGO_SECRET_KEY`, set `DJANGO_DEBUG=False`, and set `DJANGO_ALLOWED_HOSTS` to the actual hostnames. Do not commit credentials or a production database file. Use HTTPS in production.
