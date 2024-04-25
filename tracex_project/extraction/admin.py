"""Admin file for extraction app."""
from django.contrib import admin
from extraction.models import Event, PatientJourney, Prompt, Trace, Cohort, Metric


class TraceInline(admin.TabularInline):
    """Inline for the Trace model, used to display the related Trace objects in the PatientJourney admin page."""

    model = Trace
    extra = 0  # Controls the number of empty forms displayed for adding related objects


class EventInline(admin.TabularInline):
    model = Event
    extra = 0
    readonly_fields = (
        "metrics_activity_relevance",
        "metrics_timestamp_correctness",
        "metrics_correctness_confidence",
    )

    def metrics_activity_relevance(self, obj):
        return obj.metrics.activity_relevance if hasattr(obj, "metrics") else "-"

    def metrics_timestamp_correctness(self, obj):
        return obj.metrics.timestamp_correctness if hasattr(obj, "metrics") else "-"

    def metrics_correctness_confidence(self, obj):
        return obj.metrics.correctness_confidence if hasattr(obj, "metrics") else "-"


@admin.register(PatientJourney)
class PatientJourneyAdmin(admin.ModelAdmin):
    """Admin page for the PatientJourney model."""

    inlines = [TraceInline]


@admin.register(Trace)
class TraceAdmin(admin.ModelAdmin):
    """Admin page for the Trace model."""

    inlines = [EventInline]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin page for the Event model."""


admin.site.register(Metric)
admin.site.register(Prompt)
admin.site.register(Cohort)
