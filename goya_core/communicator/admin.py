from django.contrib import admin

from communicator.models import Latest_Advisory

# Register your models here.

class Latest_AdvisoryAdmin(admin.ModelAdmin):
    list_display = ('advised_workspace', 'latest_advisory_time')


admin.site.register(Latest_Advisory, Latest_AdvisoryAdmin)