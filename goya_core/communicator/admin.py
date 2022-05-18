from django.contrib import admin

from communicator.models import Latest_Advisory, Latest_Event_Report, Advisories_Sent, Events_Sent, EventSummary_Sent, Latest_Awareness, Awareness_Sent

# Register your models here.

class Latest_AdvisoryAdmin(admin.ModelAdmin):
    list_display = ('advised_workspace', 'latest_advisory_time')


admin.site.register(Latest_Advisory, Latest_AdvisoryAdmin)

class Latest_Event_ReportAdmin(admin.ModelAdmin):
    list_display = ('advised_workspace', 'latest_event_report_time')


admin.site.register(Latest_Event_Report, Latest_Event_ReportAdmin)

class Latest_AwarenessAdmin(admin.ModelAdmin):
    list_display = ('advised_workspace', 'latest_awareness_time')


admin.site.register(Latest_Awareness, Latest_AwarenessAdmin)

class Advisories_SentAdmin(admin.ModelAdmin):
    list_display = ('advised_workspace', 'advisory_sent', 'advisory_sent_time')


admin.site.register(Advisories_Sent, Advisories_SentAdmin)


class Events_SentAdmin(admin.ModelAdmin):
    list_display = ('advised_workspace', 'event_sent', 'event_sent_time')


admin.site.register(Events_Sent, Events_SentAdmin)


class EventSummary_SentAdmin(admin.ModelAdmin):
    list_display = ('advised_workspace', 'event_summary_sent', 'event_summary_sent_time')


admin.site.register(EventSummary_Sent, EventSummary_SentAdmin)


class Awareness_SentAdmin(admin.ModelAdmin):
    list_display = ('advised_workspace', 'awareness_message_sent', 'awareness_message_sent_time')


admin.site.register(Awareness_Sent, Awareness_SentAdmin)
