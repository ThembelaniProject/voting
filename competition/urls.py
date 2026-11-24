from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("api/competitions/<int:competition_id>/stats/", views.competition_stats, name="competition-stats"),
    path("api/competitions/<int:competition_id>/vote/", views.cast_vote, name="cast-vote"),
]
