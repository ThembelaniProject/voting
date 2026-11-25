from django.db.models import Count
from django.template.library import Library
from django.utils import timezone
from competition.models import Competition, DJ, Vote

register = Library()

@register.simple_tag
def pheli_dashboard():
    now = timezone.now()
    current = Competition.objects.filter(status=Competition.Status.OPEN).select_related("dj_one", "dj_two").first()
    history = Competition.objects.filter(status=Competition.Status.COMPLETED).select_related("winner", "eliminated_dj", "dj_one", "dj_two").order_by("-week_number")[:6]
    top_djs = DJ.objects.annotate(total_votes=Count("votes")).order_by("-total_votes", "name")[:5]
    if current:
        counts = {r["dj_id"]: r["total"] for r in current.votes.values("dj_id").annotate(total=Count("id"))}
        current.dj_one_vote_count = counts.get(current.dj_one_id, 0)
        current.dj_two_vote_count = counts.get(current.dj_two_id, 0)
        current.total_votes = current.dj_one_vote_count + current.dj_two_vote_count
    return {
        "total_djs": DJ.objects.count(),
        "active_djs": DJ.objects.filter(is_active=True, is_eliminated=False).count(),
        "total_competitions": Competition.objects.count(),
        "completed_competitions": Competition.objects.filter(status=Competition.Status.COMPLETED).count(),
        "total_votes": Vote.objects.count(),
        "current": current,
        "history": history,
        "top_djs": top_djs,
        "champion": DJ.objects.filter(is_champion=True).first(),
    }
