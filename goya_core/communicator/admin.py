from django.contrib import admin

from communicator.models import Latest_Advisory, Latest_Event_Report, Advisories_Sent, Events_Sent

# Register your models here.

class Latest_AdvisoryAdmin(admin.ModelAdmin):
    list_display = ('advised_workspace', 'latest_advisory_time')


admin.site.register(Latest_Advisory, Latest_AdvisoryAdmin)

class Latest_Event_ReportAdmin(admin.ModelAdmin):
    list_display = ('advised_workspace', 'latest_event_report_time')


admin.site.register(Latest_Event_Report, Latest_Event_ReportAdmin)


class Advisories_SentAdmin(admin.ModelAdmin):
    list_display = ('advised_workspace', 'advisory_sent', 'advisory_sent_time')


admin.site.register(Advisories_Sent, Advisories_SentAdmin)


class Events_SentAdmin(admin.ModelAdmin):
    list_display = ('advised_workspace', 'event_sent', 'event_sent_time')


admin.site.register(Events_Sent, Events_SentAdmin)