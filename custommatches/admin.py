from django.contrib import admin
from .models import CustomMatch, CstmMatchEvent, CstmMatchPlayerStat

# Register your models here.
admin.site.register(CustomMatch)
admin.site.register(CstmMatchEvent)
admin.site.register(CstmMatchPlayerStat)
