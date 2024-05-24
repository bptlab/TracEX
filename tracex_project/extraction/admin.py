"""Admin file for extraction app."""
from django.contrib import admin
from typing import Union
from extraction.models import Event, PatientJourney, Prompt, Trace, Cohort, Metric


class CohortInline(admin.StackedInline):
    """
    Django admin interface for the Cohort model.

    This inline admin interface is used to manage Cohort instances directly from the Trace admin page.
    No extra blank forms are displayed for adding new Cohort instances, and deletion of Cohort instances
    from the Trace admin page is not allowed.

    Attributes:
        model: Specifies the model that this inline admin interface is for.
        extra: Defines how many extra blank forms are displayed on the admin page when a new Trace is created.
        can_delete: Determines whether the deletion of instances of the model is allowed from the admin interface.
    """

    model = Cohort
    extra = 0
    can_delete = False


class TraceInline(admin.TabularInline):
    """
    Django admin interface for the Trace model.

    This inline admin interface is used to manage Trace instances directly from the PatientJourney admin page.
    No extra blank forms are displayed for adding new Trace instances.

    Attributes:
        model: Specifies the model that this inline admin interface is for.
        extra: Defines how many extra blank forms are displayed on the admin page when a new PatientJourney is created.
    """

    model = Trace
    extra = 0  # Controls the number of empty forms displayed for adding related objects


class EventInline(admin.TabularInline):
    """
    Django admin interface for the Event model.

    This inline admin interface is used to manage Event instances directly from the Trace admin page.
    No extra blank forms are displayed for adding new Event instances. Certain fields related to metrics
    are read-only.

    Attributes:
        model: Specifies the model that this inline admin interface is for.
        extra: Defines how many extra blank forms are displayed on the admin page when a new Trace is created.
        readonly_fields: Specifies which fields on the admin interface are read-only.
    """

    model = Event
    extra = 0
    readonly_fields = (
        "metrics_activity_relevance",
        "metrics_timestamp_correctness",
        "metrics_correctness_confidence",
    )

    @staticmethod
    def metrics_activity_relevance(obj: Event) -> Union[str, int]:
        """Returns the activity relevance metric for the event."""
        return obj.metrics.activity_relevance if hasattr(obj, "metrics") else "-"

    @staticmethod
    def metrics_timestamp_correctness(obj: Event) -> Union[str, int]:
        """Returns the timestamp correctness metric for the event."""
        return obj.metrics.timestamp_correctness if hasattr(obj, "metrics") else "-"

    @staticmethod
    def metrics_correctness_confidence(obj: Event) -> Union[str, int]:
        """Returns the correctness confidence metric for the event."""
        return obj.metrics.correctness_confidence if hasattr(obj, "metrics") else "-"


@admin.register(PatientJourney)
class PatientJourneyAdmin(admin.ModelAdmin):
    """Django admin interface for managing PatientJourney instances and related Trace instances."""

    inlines = [TraceInline]


@admin.register(Trace)
class TraceAdmin(admin.ModelAdmin):
    """Django admin interface for managing Trace instances and related Cohort and Event instances."""

    inlines = [CohortInline, EventInline]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Django admin interface for managing Event instances."""


admin.site.register(Metric)
admin.site.register(Prompt)
admin.site.register(Cohort)
