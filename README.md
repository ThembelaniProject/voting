# Pheli FM 95.0 — DJ Survival Challenge

A Django-powered weekly DJ survival competition for Pheli FM 95.0. Fans choose the DJ they want to keep in the competition. The DJ with more votes survives and faces a fresh challenger in the next weekly round.

## Phase 4: automatic elimination and weekly progression

1. Create the weekly matchup and open voting from Django admin.
2. When voting ends, use **Close voting** in the competition list.
3. Edit the closed competition and select a fresh **Next challenger**. The selected DJ must be active and not eliminated.
4. If this is the season's final matchup, tick **Is final** instead and leave Next challenger blank.
5. Return to the competition list, select the closed round, and run **Finalize result, eliminate losing DJ and create next week**.
6. The app counts the votes. The DJ with more votes survives; the other DJ is marked eliminated. A new Draft round is created automatically with the survivor against the selected challenger.
7. Open the new Draft round when its schedule is ready. For a final round, the winner is marked as the season champion.

A tied result is deliberately not finalized: no DJ is eliminated and no next round is created. Administrators must resolve the tie according to the station's published competition rules before taking further action. A round must be closed before it can be finalized. The generated next round starts as Draft with a seven-day schedule; an administrator should review its dates before opening it.

The public website now displays completed round results and the season champion.

## Phase 3: server-side voting

- Votes are stored in the Django database, not browser localStorage.
- All visitors see the same totals from the server.
- A browser session receives one vote per competition.
- A database-level unique constraint prevents the same session identity from voting twice in the same round.
- Votes are accepted only while the selected competition is open and within its scheduled start/end time.
- The public page refreshes shared totals automatically.
- Administrators can inspect recorded votes and totals in Django admin. Individual vote records cannot be created or deleted through the admin interface.

### Voting protection notes

The system uses an anonymous browser-session identity and stores only its SHA-256 hash with the vote. This is a practical first anti-duplicate measure, not verified identity or complete fraud prevention. Clearing browser cookies, using another browser/device, or automation can bypass session-based limits. For a high-stakes public competition, add verified mobile/email identity, rate limiting, monitoring and a clear voting policy before launch.

## Phase 2: competition management

The password-protected Django admin area lets Pheli FM administrators add, edit, search and deactivate DJs; create weekly competitions; select two different DJs; set dates; and open or close voting.

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

If you already have a local database, pull the latest changes and run `py manage.py migrate`. The new migrations add the survival fields without deleting existing DJs, competitions or votes.

## Run automated tests

```powershell
py manage.py test competition
```

Tests cover server-side voting, duplicate vote rejection, shared totals, closed competitions, automatic elimination, tie handling, champion selection and next-round creation.

## Database and deployment

Local development uses SQLite (`db.sqlite3`); no separate database server is required. The database file must be persisted and backed up. For a multi-instance production deployment, use PostgreSQL or another shared production database rather than a local SQLite file.

Before deploying, set a strong `DJANGO_SECRET_KEY`, set `DJANGO_DEBUG=False`, set `DJANGO_ALLOWED_HOSTS` to the actual hostnames, use HTTPS, configure secure session/cookie settings and reliable backups. Do not commit credentials or the production database file.
