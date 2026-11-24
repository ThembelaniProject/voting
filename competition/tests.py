import json
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Competition, DJ, Vote


class ServerSideVotingTests(TestCase):
    def setUp(self):
        self.dj_one = DJ.objects.create(name="Test DJ One")
        self.dj_two = DJ.objects.create(name="Test DJ Two")
        now = timezone.now()
        self.competition = Competition.objects.create(
            week_number=901,
            dj_one=self.dj_one,
            dj_two=self.dj_two,
            status=Competition.Status.OPEN,
            starts_at=now - timedelta(minutes=1),
            ends_at=now + timedelta(days=2),
        )
        self.vote_url = reverse("cast-vote", args=[self.competition.pk])
        self.stats_url = reverse("competition-stats", args=[self.competition.pk])

    def test_vote_is_saved_on_server_and_duplicate_is_rejected(self):
        self.client.get("/")
        response = self.client.post(
            self.vote_url,
            data=json.dumps({"choice": "dj1"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Vote.objects.filter(competition=self.competition).count(), 1)

        duplicate = self.client.post(
            self.vote_url,
            data=json.dumps({"choice": "dj2"}),
            content_type="application/json",
        )
        self.assertEqual(duplicate.status_code, 409)
        self.assertEqual(Vote.objects.filter(competition=self.competition).count(), 1)

    def test_different_browser_sessions_share_server_totals(self):
        first = self.client
        first.get("/")
        first.post(
            self.vote_url,
            data=json.dumps({"choice": "dj1"}),
            content_type="application/json",
        )

        second = self.client_class()
        second.get("/")
        second.post(
            self.vote_url,
            data=json.dumps({"choice": "dj2"}),
            content_type="application/json",
        )

        response = second.get(self.stats_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total"], 2)
        self.assertEqual(response.json()["dj1"], 1)
        self.assertEqual(response.json()["dj2"], 1)

    def test_voting_closed_rejects_new_vote(self):
        self.competition.status = Competition.Status.CLOSED
        self.competition.save()
        self.client.get("/")
        response = self.client.post(
            self.vote_url,
            data=json.dumps({"choice": "dj1"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Vote.objects.filter(competition=self.competition).count(), 0)

    def test_invalid_choice_is_rejected(self):
        self.client.get("/")
        response = self.client.post(
            self.vote_url,
            data=json.dumps({"choice": "someone-else"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
