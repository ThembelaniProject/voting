from django.contrib import admin, messages
from django.utils import timezone

from .models import Competition, DJ, Vote


@admin.register(DJ)
class DJAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "bio")
    list_editable = ("is_active",)
    ordering = ("name",)


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ("week_number", "dj_one", "dj_two", "status", "vote_count", "starts_at", "ends_at")
    list_filter = ("status",)
    search_fields = ("title", "dj_one__name", "dj_two__name")
    ordering = ("-week_number",)
    actions = ("open_voting", "close_voting", "complete_competition")

    @admin.display(description="Recorded votes")
    def vote_count(self, obj):
        return obj.votes.count()

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


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("competition", "dj", "created_at")
    list_filter = ("competition", "dj")
    search_fields = ("competition__week_number", "dj__name")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    readonly_fields = ("competition", "dj", "voter_hash", "created_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
