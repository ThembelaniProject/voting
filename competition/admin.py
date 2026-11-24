from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Competition, DJ


@admin.register(DJ)
class DJAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "bio")
    list_editable = ("is_active",)
    ordering = ("name",)


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ("week_number", "dj_one", "dj_two", "status", "starts_at", "ends_at")
    list_filter = ("status",)
    search_fields = ("title", "dj_one__name", "dj_two__name")
    ordering = ("-week_number",)
    actions = ("open_voting", "close_voting", "complete_competition")

    @admin.action(description="Open voting for selected competition")
    def open_voting(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Select exactly one competition to open.", messages.ERROR)
            return
        competition = queryset.first()
        if competition.ends_at <= timezone.now():
            self.message_user(request, "Set a future voting end date before opening this competition.", messages.ERROR)
            return
        Competition.objects.exclude(pk=competition.pk).filter(status=Competition.Status.OPEN).update(
            status=Competition.Status.CLOSED
        )
        competition.status = Competition.Status.OPEN
        competition.save()
        self.message_user(request, f"Week {competition.week_number} is now open for voting.", messages.SUCCESS)

    @admin.action(description="Close voting for selected competition")
    def close_voting(self, request, queryset):
        updated = queryset.filter(status=Competition.Status.OPEN).update(status=Competition.Status.CLOSED)
        self.message_user(request, f"Closed voting for {updated} competition(s).", messages.SUCCESS)

    @admin.action(description="Mark selected competition as completed")
    def complete_competition(self, request, queryset):
        updated = queryset.exclude(status=Competition.Status.DRAFT).update(status=Competition.Status.COMPLETED)
        self.message_user(request, f"Marked {updated} competition(s) as completed.", messages.SUCCESS)
