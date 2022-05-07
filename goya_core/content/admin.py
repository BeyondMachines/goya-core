from django.contrib import admin
from content.models import Advisory, RealLifeEvent

# Register your models here.

class AdvisoryModelAdmin(admin.ModelAdmin):
    readonly_fields = ('advisory_url',)
    list_display = ('advisory_title', 'advisory_published_time')


admin.site.register(Advisory, AdvisoryModelAdmin)

class RealLifeEventAdmin(admin.ModelAdmin):
    readonly_fields = ('event_url',)
    list_display = ('event_title', 'event_published_time')


admin.site.register(RealLifeEvent, RealLifeEventAdmin)