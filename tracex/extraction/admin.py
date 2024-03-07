"""Admin file for extraction app."""
from django.contrib import admin
from .models import Event, EventLog, PatientJourney, Prompt, Trace


class TraceInline(admin.TabularInline):  # or admin.StackedInline
    model = Trace
    extra = 0  # Controls the number of empty forms displayed for adding related objects


class EventInline(admin.TabularInline):  # or admin.StackedInline
    model = Event
    extra = 0  # Controls the number of empty forms displayed for adding related objects


@admin.register(PatientJourney)
class PatientJourneyAdmin(admin.ModelAdmin):
    inlines = [TraceInline]


@admin.register(Trace)
class TraceAdmin(admin.ModelAdmin):
    inlines = [EventInline]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass


admin.site.register(EventLog)
admin.site.register(Prompt)
