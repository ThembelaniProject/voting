from django.shortcuts import render
from django.utils import timezone

from .models import Competition


def home(request):
    now = timezone.now()
    competition = Competition.objects.filter(status=Competition.Status.OPEN).first()
    if competition is None:
        competition = Competition.objects.exclude(status=Competition.Status.DRAFT).first()

    voting_open = bool(
        competition
        and competition.status == Competition.Status.OPEN
        and competition.starts_at <= now < competition.ends_at
    )

    if competition is None:
        competition_status = "No active round"
    elif competition.status == Competition.Status.OPEN and now >= competition.ends_at:
        competition_status = "Voting closed"
    elif competition.status == Competition.Status.OPEN and now < competition.starts_at:
        competition_status = "Scheduled"
    else:
        competition_status = competition.get_status_display()

    return render(request, "index.html", {
        "competition": competition,
        "competition_status": competition_status,
        "voting_open": voting_open,
        "deadline_iso": competition.ends_at.isoformat() if competition else "",
        "week_number": competition.week_number if competition else None,
    })
