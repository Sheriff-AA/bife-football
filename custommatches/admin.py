from django.contrib import admin
from .models import CustomMatch, CstmMatchEvent, CstmMatchPlayerStat, CstmMatchResult

# Register your models here.
admin.site.register(CustomMatch)
admin.site.register(CstmMatchEvent)
admin.site.register(CstmMatchPlayerStat)
admin.site.register(CstmMatchResult)
