from django.contrib import admin
from .models import Nationality, Stadium, Umpire, Player, Team

@admin.register(Nationality)
class NationalityAdmin(admin.ModelAdmin):
    list_display = ("name","code","is_active","id")
    search_fields = ("name", "code")
    list_filter = ("is_active",)

    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj = ...):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj = ...):
        return False

@admin.register(Stadium)
class StadiumAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "city",
        "nationality",
        "owner_type",
        "is_locked",
    )

    list_filter = ("owner_type","nationality")
    search_fields = ("name","city")

    def has_change_permission(self, request, obj = None):
        if obj and obj.owner_type == "SYSTEM":
            return request.user.is_superuser
        return True
    
    def has_delete_permission(self, request, obj = ...):
        return False

@admin.register(Umpire)
class UmpireAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "nationality",
        "owner_type",
        "is_locked",
    )

    list_filter = ("owner_type","nationality")
    search_fields = ("name",)

    def has_change_permission(self, request, obj = None):
        if obj and obj.owner_type == "SYSTEM":
            return request.user.is_superuser
        return True
    
    def has_delete_permission(self, request, obj = None):
        return False

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "nationality",
        "role",
        "owner_type",
        "is_locked",
    )

    list_filter = ("owner_type","nationality","role")
    search_fields = ("first_name","last_name")

    def has_change_permission(self, request, obj = None):
        if obj and obj.owner_type == "SYSTEM":
            return request.user.is_superuser
        return True
    
    """
    def has_delete_permission(self, request, obj = None):
        return False
    """

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "short_name",
        "team_type",
        "nationality",
        "owner_type",
        "is_locked",
    )

    list_filter = ("team_type","owner_type","nationality")
    search_fields = ("name","short_name")

    def has_change_permission(self, request, obj = None):
        if obj and obj.owner_type == "SYSTEM":
            return request.user.is_superuser
        return True
    
    def has_delete_permission(self, request, obj = None):
        return False