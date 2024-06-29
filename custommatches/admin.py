from django.contrib import admin
from .models import CustomMatch, CustomMatchEvent, CustomMatchPlayerStat, CustomMatchResult

# Register your models here.
admin.site.register(CustomMatch)
admin.site.register(CustomMatchEvent)
admin.site.register(CustomMatchPlayerStat)
admin.site.register(CustomMatchResult)
