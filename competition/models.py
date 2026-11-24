from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class DJ(models.Model):
    name = models.CharField(max_length=100, unique=True)
    bio = models.CharField(max_length=240, blank=True)
    photo_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    is_eliminated = models.BooleanField(default=False)
    is_champion = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "DJ"
        verbose_name_plural = "DJs"

    def __str__(self):
        return self.name


class Competition(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        OPEN = "open", "Voting open"
        CLOSED = "closed", "Voting closed"
        COMPLETED = "completed", "Completed"

    week_number = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=140, default="Pheli FM DJ Survival Challenge")
    dj_one = models.ForeignKey(DJ, on_delete=models.PROTECT, related_name="first_rounds")
    dj_two = models.ForeignKey(DJ, on_delete=models.PROTECT, related_name="second_rounds")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    starts_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField()
    next_challenger = models.ForeignKey(
        DJ, on_delete=models.PROTECT, related_name="scheduled_challenges",
        blank=True, null=True, help_text="Choose the fresh DJ who will challenge the winner next week."
    )
    is_final = models.BooleanField(
        default=False, help_text="Tick this only when this is the final round of the season."
    )
    winner = models.ForeignKey(
        DJ, on_delete=models.PROTECT, related_name="competition_wins", blank=True, null=True
    )
    eliminated_dj = models.ForeignKey(
        DJ, on_delete=models.PROTECT, related_name="competition_eliminations", blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-week_number"]
        verbose_name = "Weekly competition"

    def clean(self):
        super().clean()
        if self.dj_one_id and self.dj_two_id and self.dj_one_id == self.dj_two_id:
            raise ValidationError("A DJ cannot compete against themselves.")
        if self.ends_at and self.starts_at and self.ends_at <= self.starts_at:
            raise ValidationError("The voting end date must be after the start date.")
        if self.status == self.Status.OPEN:
            other_open = Competition.objects.filter(status=self.Status.OPEN).exclude(pk=self.pk)
            if other_open.exists():
                raise ValidationError("Only one weekly competition can be open at a time.")
        if self.next_challenger_id and self.next_challenger_id in (self.dj_one_id, self.dj_two_id):
            raise ValidationError("The next challenger must be different from the current contestants.")
        if self.is_final and self.next_challenger_id:
            raise ValidationError("A final round cannot have a next challenger.")

    def __str__(self):
        return f"Week {self.week_number}: {self.dj_one} vs {self.dj_two}"


class Vote(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name="votes")
    dj = models.ForeignKey(DJ, on_delete=models.PROTECT, related_name="votes")
    voter_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["competition", "voter_hash"], name="uniq_vote_session_round")
        ]
        indexes = [models.Index(fields=["competition", "dj"], name="vote_comp_dj_idx")]

    def __str__(self):
        return f"{self.dj} · Week {self.competition.week_number}"
