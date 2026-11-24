from django.shortcuts import render
from django.utils import timezone

from .models import Competition


def home(request):
    competition = Competition.objects.filter(status=Competition.Status.OPEN).first()
    if competition is None:
        competition = Competition.objects.exclude(status=Competition.Status.DRAFT).first()

    voting_open = bool(
        competition
        and competition.status == Competition.Status.OPEN
        and competition.starts_at <= timezone.now() < competition.ends_at
    )
    deadline_iso = competition.ends_at.isoformat() if competition else ""
    return render(request, "index.html", {
        "competition": competition,
        "voting_open": voting_open,
        "deadline_iso": deadline_iso,
        "week_number": competition.week_number if competition else None,
    })
