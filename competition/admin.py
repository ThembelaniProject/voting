from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.html import format_html

from .models import Competition, DJ, Vote
from .services import finalize_competition

admin.site.site_header = "Pheli FM 95.0 · Competition Control"
admin.site.site_title = "Pheli FM Admin"
admin.site.index_title = "Manage the DJ Survival Challenge"


@admin.register(DJ)
class DJAdmin(admin.ModelAdmin):
    list_display = ("photo_thumbnail", "name", "is_active", "is_eliminated", "is_champion", "created_at")
    list_display_links = ("name",)
    list_filter = ("is_active", "is_eliminated", "is_champion")
    search_fields = ("name", "bio")
    list_editable = ("is_active",)
    ordering = ("name",)
    list_per_page = 20
    readonly_fields = ("created_at", "photo_preview")
    fieldsets = (
        ("DJ profile", {"fields": ("name", "bio", "photo", "photo_url", "photo_preview")}),
        ("Competition status", {"fields": ("is_active", "is_eliminated", "is_champion")}),
        ("Record", {"fields": ("created_at",)}),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "photo" and field:
            field.label = "DJ image"
            field.help_text = "Choose File / Browse to select a photo from your device (JPG, PNG or WebP)."
            field.widget.attrs["accept"] = "image/jpeg,image/png,image/webp"
        if db_field.name == "photo_url" and field:
            field.label = "Legacy photo URL (optional)"
            field.help_text = "Uploaded DJ images take priority over this optional URL."
            field.widget.attrs["placeholder"] = "https://example.com/dj-photo.jpg"
        return field

    @admin.display(description="DJ photo")
    def photo_thumbnail(self, obj):
        source = obj.photo.url if obj.photo else obj.photo_url
        if not source:
            return format_html('<span class="ph-no-photo">No photo</span>')
        return format_html('<img src="{}" alt="{}" class="ph-dj-thumb">', source, obj.name)

    @admin.display(description="Photo preview")
    def photo_preview(self, obj):
        source = (obj.photo.url if obj.photo else obj.photo_url) if obj else ""
        if source:
            return format_html('<img src="{}" alt="{}" class="ph-dj-preview">', source, obj.name)
        return "Choose a photo and save to see its preview."


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ("week_number", "matchup", "status_badge", "vote_count", "countdown", "winner", "eliminated_dj", "starts_at", "ends_at")
    list_filter = ("status", "is_final")
    search_fields = ("title", "dj_one__name", "dj_two__name", "winner__name")
    ordering = ("-week_number",)
    date_hierarchy = "starts_at"
    list_per_page = 20
    readonly_fields = ("winner", "eliminated_dj", "created_at")
    actions = ("open_voting", "close_voting", "finalize_and_progress")
    fieldsets = (
        ("Weekly matchup", {"fields": ("week_number", "title", "dj_one", "dj_two")}),
        ("Voting schedule", {"fields": ("status", "starts_at", "ends_at")}),
        ("Next week setup", {"fields": ("next_challenger", "is_final")}),
        ("Final result", {"fields": ("winner", "eliminated_dj", "created_at")}),
    )

    @admin.display(description="Matchup")
    def matchup(self, obj):
        return format_html("<strong>{}</strong> <span class='ph-versus-label'>VS</span> <strong>{}</strong>", obj.dj_one.name, obj.dj_two.name)

    @admin.display(description="Status")
    def status_badge(self, obj):
        return format_html('<span class="ph-status ph-status-{}">{}</span>', obj.status, obj.get_status_display())

    @admin.display(description="Voting countdown")
    def countdown(self, obj):
        if obj.status != Competition.Status.OPEN:
            return "—"
        if obj.ends_at <= timezone.now():
            return format_html('<span class="ph-status ph-status-closed">Awaiting finalization</span>')
        return format_html('<span class="ph-countdown" data-ends-at="{}">Countdown active</span>', obj.ends_at.isoformat())

    @admin.display(description="Recorded votes")
    def vote_count(self, obj):
        return obj.votes.count()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "next_challenger":
            kwargs["queryset"] = DJ.objects.filter(is_active=True, is_eliminated=False, is_champion=False).order_by("name")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.action(description="Open voting for selected competition")
    def open_voting(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Select exactly one competition to open.", messages.ERROR)
            return
        competition = queryset.first()
        if competition.ends_at <= timezone.now():
            self.message_user(request, "Set a future voting end date before opening this competition.", messages.ERROR)
            return
        if competition.dj_one.is_eliminated or competition.dj_two.is_eliminated:
            self.message_user(request, "An eliminated DJ cannot enter a new competition.", messages.ERROR)
            return
        Competition.objects.exclude(pk=competition.pk).filter(status=Competition.Status.OPEN).update(status=Competition.Status.CLOSED)
        competition.status = Competition.Status.OPEN
        competition.save()
        self.message_user(request, f"Week {competition.week_number} is now open for voting.", messages.SUCCESS)

    @admin.action(description="Close voting for selected competition")
    def close_voting(self, request, queryset):
        updated = queryset.filter(status=Competition.Status.OPEN).update(status=Competition.Status.CLOSED)
        self.message_user(request, f"Closed voting for {updated} competition(s).", messages.SUCCESS)

    @admin.action(description="Finalize result, eliminate losing DJ and create next week")
    def finalize_and_progress(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Select exactly one closed competition to finalize.", messages.ERROR)
            return
        try:
            result = finalize_competition(queryset.first().pk)
        except (ValidationError, Competition.DoesNotExist) as exc:
            self.message_user(request, str(exc), messages.ERROR)
            return
        if result["next_round"]:
            message = (
                f"Week {result['competition'].week_number} finalized. "
                f"{result['winner'].name} survives; {result['eliminated'].name} is eliminated. "
                f"Week {result['next_round'].week_number} was created as Draft with "
                f"{result['next_round'].dj_two.name} as the new challenger. Open it when ready."
            )
        else:
            message = f"Season champion crowned: {result['winner'].name}. {result['eliminated'].name} has been eliminated."
        self.message_user(request, message, messages.SUCCESS)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("competition", "dj", "created_at")
    list_filter = ("competition", "dj")
    search_fields = ("dj__name",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 50
    readonly_fields = ("competition", "dj", "voter_hash", "created_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
