# DJ Battle — Weekly Fan Voting

A database-free Phase 1 prototype for a weekly DJ survival competition. Fans choose the DJ they want to stay for another week. The DJ with the most votes survives and faces a new challenger in the next round.

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

- Sample Week 01 battle with two demo DJs.
- A fan can vote once per battle in that browser.
- Vote totals and percentages update immediately in the browser.
- The demo includes a voting deadline and a winner/survivor state when the deadline has passed.
- Reset demo votes using the **Reset demo vote** control.

## Important limitation

Browser localStorage is only for previewing the user experience. It is not secure, is not shared between devices, and can be cleared or manipulated. Real public voting requires server-side storage, identity/rate-limit controls and a database in a later phase.
