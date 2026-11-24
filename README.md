# Pheli FM 95.0 — DJ Survival Challenge

A database-free Phase 1 prototype for the Pheli FM 95.0 weekly DJ Survival Challenge. Pheli FM listeners choose the DJ they want to keep in the competition for another week. The DJ with more votes survives and faces a new challenger in the next weekly round; the other DJ is eliminated.

## Phase 1 stack

- Django
- HTML, CSS and vanilla JavaScript
- Browser localStorage for a one-vote-per-browser demonstration
- No database models or migrations required for the voting experience

## Run locally

```bash
py -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
py manage.py runserver
```

Open http://127.0.0.1:8000/.

## Demo behaviour

- Sample Week 01 battle with two placeholder demo DJs. Replace these with the confirmed Pheli FM contestants before launch.
- A fan can vote once per battle in that browser.
- Vote totals and percentages update immediately in the browser.
- The demo includes a voting deadline and a winner/survivor state when the deadline has passed.
- Reset demo votes using the **Reset demo vote** control.

## Important limitation

Browser localStorage is only for previewing the user experience. It is not secure, is not shared between devices, and can be cleared or manipulated. Real public voting requires server-side storage, identity/rate-limit controls and a database in a later phase.
