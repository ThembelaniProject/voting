from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from .models import Competition, DJ


@transaction.atomic
def finalize_competition(competition_id):
    """Resolve a closed round and prepare the winner's next challenge."""
    competition = Competition.objects.select_for_update().select_related(
        "dj_one", "dj_two", "next_challenger"
    ).get(pk=competition_id)

    if competition.status != Competition.Status.CLOSED:
        raise ValidationError("Close voting before finalizing this competition.")
    if competition.winner_id or competition.eliminated_dj_id:
        raise ValidationError("This competition has already been finalized.")

    totals = {
        row["dj_id"]: row["total"]
        for row in competition.votes.values("dj_id").annotate(total=Count("id"))
    }
    one_votes = totals.get(competition.dj_one_id, 0)
    two_votes = totals.get(competition.dj_two_id, 0)
    if one_votes == two_votes:
        raise ValidationError(
            "The result is tied. Keep the round closed and resolve the tie before finalizing."
        )

    winner = competition.dj_one if one_votes > two_votes else competition.dj_two
    eliminated = competition.dj_two if winner.pk == competition.dj_one_id else competition.dj_one

    if competition.is_final:
        if competition.next_challenger_id:
            raise ValidationError("A final round cannot have a next challenger.")
        winner.is_champion = True
        winner.save(update_fields=["is_champion"])
    else:
        challenger = competition.next_challenger
        if challenger is None:
            raise ValidationError("Select a next challenger in this competition before finalizing.")
        if challenger.pk in (competition.dj_one_id, competition.dj_two_id):
            raise ValidationError("The next challenger must be a different DJ.")
        if not challenger.is_active or challenger.is_eliminated or challenger.is_champion:
            raise ValidationError("The selected challenger must be active and not previously eliminated.")

    eliminated.is_eliminated = True
    eliminated.is_champion = False
    eliminated.save(update_fields=["is_eliminated", "is_champion"])

    competition.winner = winner
    competition.eliminated_dj = eliminated
    competition.status = Competition.Status.COMPLETED
    competition.save(update_fields=["winner", "eliminated_dj", "status"])

    next_round = None
    if not competition.is_final:
        start = timezone.now()
        next_round = Competition.objects.create(
            week_number=Competition.objects.order_by("-week_number").values_list("week_number", flat=True).first() + 1,
            title=competition.title,
            dj_one=winner,
            dj_two=competition.next_challenger,
            status=Competition.Status.DRAFT,
            starts_at=start,
            ends_at=start + timedelta(days=7),
        )

    return {
        "competition": competition,
        "winner": winner,
        "eliminated": eliminated,
        "next_round": next_round,
        "votes": {competition.dj_one_id: one_votes, competition.dj_two_id: two_votes},
    }
