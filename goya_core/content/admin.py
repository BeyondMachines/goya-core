from django.contrib import admin
from content.models import Advisory

# Register your models here.

class AdvisoryModelAdmin(admin.ModelAdmin):
    readonly_fields = ('advisory_url',)
    list_display = ('advisory_title', 'advisory_published_time')


admin.site.register(Advisory, AdvisoryModelAdmin)
