from django.contrib import admin
from .models import MatchType, Match, Toss, PlayingXI, Innings
# Register your models here.
admin.site.register(MatchType)
admin.site.register(Match)
admin.site.register(Toss)
admin.site.register(PlayingXI)
admin.site.register(Innings)