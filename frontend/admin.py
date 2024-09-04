from django.contrib import admin

from .models import Settings, Game, Team, TeamMember, TryingInstruction


# Register your models here.
class SettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not Settings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Settings, SettingsAdmin)




class TeamInline(admin.TabularInline):
    model = Team
    extra = 1

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'state', 'winner')
    list_filter = ('state',)
    search_fields = ('winner__username',)
    inlines = [TeamInline]

class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1

class TryingInstructionInline(admin.TabularInline):
    model = TryingInstruction
    extra = 1

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'game')
    search_fields = ('name', 'code')
    list_filter = ('game',)
    inlines = [TeamMemberInline]



@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'team')
    search_fields = ('user__username', 'team__name')
    list_filter = ('team',)
    inlines = [TryingInstructionInline]

@admin.register(TryingInstruction)
class TryingInstructionAdmin(admin.ModelAdmin):
    list_display = ('team_member', 'instruction', 'team')
    search_fields = ('team_member__user__username', 'instruction', 'team_member__team__name')
    list_filter = ('team_member__team',)

    def team(self, obj):
        return obj.team_member.team
    team.short_description = 'Team'
