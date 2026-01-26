from django.contrib import admin
from .models import Tournament, Competition, CompetitionTeam

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "short_name",
        "tournament_type",
        "nationality",
        "owner_type",
        "is_active",
    )
    list_filter = ("tournament_type", "nationality", "owner_type", "is_active")
    search_fields = ("name", "short_name")
    def has_change_permission(self, request, obj=None):
        if obj and obj.owner_type == "SYSTEM":
            return request.user.is_superuser
        return True
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "tournament",
        "season",
        "start_date",
        "end_date",
        "owner_type",
        "is_active",
    )
    list_filter = ("tournament", "owner_type", "is_active")
    search_fields = ("name", "season")
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(CompetitionTeam)
class CompetitionTeamAdmin(admin.ModelAdmin):
    list_display = (
        "competition",
        "team",
        "added_at",
    )
    list_filter = ("competition",)
    search_fields = ("team__name", "competition__name")
    def has_delete_permission(self, request, obj=None):
        return False






