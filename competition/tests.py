import json
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Competition, DJ, Vote
from .services import finalize_competition


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
            self.vote_url, data=json.dumps({"choice": "dj1"}), content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Vote.objects.filter(competition=self.competition).count(), 1)
        duplicate = self.client.post(
            self.vote_url, data=json.dumps({"choice": "dj2"}), content_type="application/json"
        )
        self.assertEqual(duplicate.status_code, 409)
        self.assertEqual(Vote.objects.filter(competition=self.competition).count(), 1)

    def test_different_browser_sessions_share_server_totals(self):
        self.client.get("/")
        self.client.post(
            self.vote_url, data=json.dumps({"choice": "dj1"}), content_type="application/json"
        )
        second = self.client_class()
        second.get("/")
        second.post(
            self.vote_url, data=json.dumps({"choice": "dj2"}), content_type="application/json"
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
            self.vote_url, data=json.dumps({"choice": "dj1"}), content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Vote.objects.filter(competition=self.competition).count(), 0)

    def test_invalid_choice_is_rejected(self):
        self.client.get("/")
        response = self.client.post(
            self.vote_url, data=json.dumps({"choice": "someone-else"}), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)


class SurvivalProgressionTests(TestCase):
    def setUp(self):
        self.survivor = DJ.objects.create(name="Survivor DJ")
        self.loser = DJ.objects.create(name="Eliminated DJ")
        self.challenger = DJ.objects.create(name="Fresh Challenger")
        now = timezone.now()
        self.round = Competition.objects.create(
            week_number=1,
            dj_one=self.survivor,
            dj_two=self.loser,
            next_challenger=self.challenger,
            status=Competition.Status.CLOSED,
            starts_at=now - timedelta(days=7),
            ends_at=now,
        )
        for index in range(3):
            Vote.objects.create(
                competition=self.round, dj=self.survivor, voter_hash=f"survivor-{index}"
            )
        Vote.objects.create(competition=self.round, dj=self.loser, voter_hash="loser-1")

    def test_finalize_eliminates_loser_and_creates_next_draft_round(self):
        result = finalize_competition(self.round.pk)
        self.round.refresh_from_db()
        self.loser.refresh_from_db()
        self.assertEqual(self.round.status, Competition.Status.COMPLETED)
        self.assertEqual(self.round.winner, self.survivor)
        self.assertEqual(self.round.eliminated_dj, self.loser)
        self.assertTrue(self.loser.is_eliminated)
        next_round = result["next_round"]
        self.assertIsNotNone(next_round)
        self.assertEqual(next_round.week_number, 2)
        self.assertEqual(next_round.dj_one, self.survivor)
        self.assertEqual(next_round.dj_two, self.challenger)
        self.assertEqual(next_round.status, Competition.Status.DRAFT)

    def test_tie_does_not_eliminate_anyone(self):
        Vote.objects.create(competition=self.round, dj=self.loser, voter_hash="loser-2")
        Vote.objects.create(competition=self.round, dj=self.loser, voter_hash="loser-3")
        with self.assertRaises(ValidationError):
            finalize_competition(self.round.pk)
        self.loser.refresh_from_db()
        self.round.refresh_from_db()
        self.assertFalse(self.loser.is_eliminated)
        self.assertEqual(self.round.status, Competition.Status.CLOSED)

    def test_open_round_cannot_be_finalized(self):
        self.round.status = Competition.Status.OPEN
        self.round.save()
        with self.assertRaises(ValidationError):
            finalize_competition(self.round.pk)

    def test_final_round_crowns_winner_without_creating_next_round(self):
        self.round.is_final = True
        self.round.save()
        result = finalize_competition(self.round.pk)
        self.survivor.refresh_from_db()
        self.assertTrue(self.survivor.is_champion)
        self.assertIsNone(result["next_round"])
        self.assertEqual(Competition.objects.count(), 1)

    def test_eliminated_dj_cannot_be_next_challenger(self):
        self.challenger.is_eliminated = True
        self.challenger.save()
        with self.assertRaises(ValidationError):
            finalize_competition(self.round.pk)
        self.assertEqual(Competition.objects.count(), 1)
