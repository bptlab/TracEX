"""Admin file for extraction app."""
from django.contrib import admin
from extraction.models import Event, PatientJourney, Prompt, Trace, Cohort, Metric


class TraceInline(admin.TabularInline):
    """Inline for the Trace model, used to display the related Trace objects in the PatientJourney admin page."""

    model = Trace
    extra = 0  # Controls the number of empty forms displayed for adding related objects


class EventInline(admin.TabularInline):
    """Inline for the Event model, used to display the related Event objects in the Trace admin page."""

    model = Event
    extra = 0  # Controls the number of empty forms displayed for adding related objects


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
