from django.contrib import admin
from content.models import Advisory, RealLifeEvent, EventSummary, CandidateEvent, AwarenessMessage, AwarenessCategory, ScrapedEvent, InterestingEventCategory

# Register your models here.

class AdvisoryModelAdmin(admin.ModelAdmin):
    readonly_fields = ('advisory_url',)
    list_display = ('advisory_title', 'advisory_published_time')


admin.site.register(Advisory, AdvisoryModelAdmin)

class RealLifeEventAdmin(admin.ModelAdmin):
    readonly_fields = ('event_url',)
    list_display = ('event_title', 'event_url', 'event_published_time')


admin.site.register(RealLifeEvent, RealLifeEventAdmin)


class EventSummaryAdmin(admin.ModelAdmin):
    readonly_fields = ('summary_url',)
    list_display = ('summary_title', 'summary_published_time')


admin.site.register(EventSummary, EventSummaryAdmin)


class CandidateEventAdmin(admin.ModelAdmin):
    list_display = ('candidate_event_title', 'candidate_event_published_time','candidate_event_source_url','tag_list')

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())


admin.site.register(CandidateEvent, CandidateEventAdmin)


class AwarenessMessageAdmin(admin.ModelAdmin):
    list_display = ('awareness_message_title', 'awareness_category', 'awareness_message_published_time','tag_list')

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())


admin.site.register(AwarenessMessage, AwarenessMessageAdmin)


class AwarenessCategoryAdmin(admin.ModelAdmin):
    list_display = ('awareness_category', 'awareness_category_id')


admin.site.register(AwarenessCategory, AwarenessCategoryAdmin)


class InterestingEventCategoryAdmin(admin.ModelAdmin):
    list_display = ('interesting_event_category', 'interesting_event_category_category_id')


admin.site.register(InterestingEventCategory, InterestingEventCategoryAdmin)


class ScrapedEventAdmin(admin.ModelAdmin):
    readonly_fields = ('event_custom_id', 'event_url', 'event_source_url', 'event_additional_data')
    list_display = ('event_title', 'event_published_time', 'event_source')


admin.site.register(ScrapedEvent, ScrapedEventAdmin)

