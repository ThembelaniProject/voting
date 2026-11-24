import hashlib
import json
import secrets

from django.db import IntegrityError, transaction
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .models import Competition, DJ, Vote


def _vote_totals(competition):
    counts = {
        row["dj_id"]: row["total"]
        for row in Vote.objects.filter(competition=competition).values("dj_id").annotate(total=Count("id"))
    }
    one = counts.get(competition.dj_one_id, 0)
    two = counts.get(competition.dj_two_id, 0)
    return {
        "dj1": one,
        "dj2": two,
        "total": one + two,
        "dj1_percent": round(one / (one + two) * 100, 1) if one + two else 0,
        "dj2_percent": round(two / (one + two) * 100, 1) if one + two else 0,
    }


def _is_open(competition, now=None):
    now = now or timezone.now()
    return (
        competition.status == Competition.Status.OPEN
        and competition.starts_at <= now < competition.ends_at
    )


@ensure_csrf_cookie
def home(request):
    if not request.session.get("vote_identity"):
        request.session["vote_identity"] = secrets.token_urlsafe(32)
        request.session.set_expiry(60 * 60 * 24 * 30)

    now = timezone.now()
    competition = Competition.objects.filter(status=Competition.Status.OPEN).select_related(
        "dj_one", "dj_two"
    ).first()
    if competition is None:
        competition = Competition.objects.exclude(status=Competition.Status.DRAFT).select_related(
            "dj_one", "dj_two", "winner", "eliminated_dj"
        ).first()

    voting_open = bool(competition and _is_open(competition, now))
    if competition is None:
        competition_status = "No active round"
    elif competition.status == Competition.Status.OPEN and now >= competition.ends_at:
        competition_status = "Voting closed"
    elif competition.status == Competition.Status.OPEN and now < competition.starts_at:
        competition_status = "Scheduled"
    else:
        competition_status = competition.get_status_display()

    totals = _vote_totals(competition) if competition else {
        "dj1": 0, "dj2": 0, "total": 0, "dj1_percent": 0, "dj2_percent": 0
    }
    already_voted = False
    if competition:
        identity = request.session.get("vote_identity")
        if identity:
            voter_hash = hashlib.sha256(identity.encode("utf-8")).hexdigest()
            already_voted = Vote.objects.filter(competition=competition, voter_hash=voter_hash).exists()

    history = Competition.objects.filter(status=Competition.Status.COMPLETED).select_related(
        "winner", "eliminated_dj"
    ).order_by("-week_number")[:8]
    champion = DJ.objects.filter(is_champion=True).first()

    return render(request, "index.html", {
        "competition": competition,
        "competition_status": competition_status,
        "voting_open": voting_open,
        "deadline_iso": competition.ends_at.isoformat() if competition else "",
        "week_number": competition.week_number if competition else None,
        "vote_totals": totals,
        "already_voted": already_voted,
        "round_history": history,
        "champion": champion,
    })


@require_GET
def competition_stats(request, competition_id):
    try:
        competition = Competition.objects.get(pk=competition_id)
    except Competition.DoesNotExist:
        return JsonResponse({"error": "Competition not found."}, status=404)

    totals = _vote_totals(competition)
    identity = request.session.get("vote_identity")
    already_voted = False
    if identity:
        voter_hash = hashlib.sha256(identity.encode("utf-8")).hexdigest()
        already_voted = Vote.objects.filter(competition=competition, voter_hash=voter_hash).exists()

    return JsonResponse({
        **totals,
        "voting_open": _is_open(competition),
        "already_voted": already_voted,
        "status": competition.status,
    })


@require_POST
def cast_vote(request, competition_id):
    try:
        payload = json.loads(request.body or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid request body."}, status=400)

    choice = payload.get("choice")
    if choice not in ("dj1", "dj2"):
        return JsonResponse({"error": "Choose one of the two competing DJs."}, status=400)

    try:
        competition = Competition.objects.select_related("dj_one", "dj_two").get(pk=competition_id)
    except Competition.DoesNotExist:
        return JsonResponse({"error": "Competition not found."}, status=404)

    if not _is_open(competition):
        return JsonResponse({"error": "Voting is not open for this competition."}, status=403)

    identity = request.session.get("vote_identity")
    if not identity:
        identity = secrets.token_urlsafe(32)
        request.session["vote_identity"] = identity
        request.session.set_expiry(60 * 60 * 24 * 30)

    voter_hash = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    selected_dj = competition.dj_one if choice == "dj1" else competition.dj_two

    try:
        with transaction.atomic():
            Vote.objects.create(
                competition=competition,
                dj=selected_dj,
                voter_hash=voter_hash,
            )
    except IntegrityError:
        return JsonResponse({
            "error": "A vote has already been submitted from this browser for this round.",
            "already_voted": True,
        }, status=409)

    return JsonResponse({
        "message": f"Your vote for {selected_dj.name} has been recorded.",
        **_vote_totals(competition),
        "already_voted": True,
    }, status=201)
