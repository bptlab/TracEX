"""This file contains the views for the event log testing environment app."""
from django.views.generic import FormView
from django.urls import reverse_lazy
from .forms import PatientJourneySelectForm
from extraction.models import PatientJourney
from extraction.logic.orchestrator import Orchestrator, ExtractionConfiguration

from extraction.logic.modules.module_activity_labeler import ActivityLabeler
from extraction.logic.modules.module_cohort_tagger import CohortTagger
from extraction.logic.modules.module_time_extractor_backup import TimeExtractorBackup
from extraction.logic.modules.module_location_extractor import LocationExtractor
from extraction.logic.modules.module_event_type_classifier import EventTypeClassifier
from extraction.logic.modules.module_patient_journey_preprocessor import Preprocessor
from extraction.logic.modules.module_event_log_comparator import EventLogComparator


class EventLogTestingOverviewView(FormView):
    form_class = PatientJourneySelectForm
    template_name = "testing_overview.html"
    success_url = reverse_lazy("journey_filter")

    def form_valid(self, form):
        selected_value = form.cleaned_data["selected_patient_journey"]
        patient_journey_entry = PatientJourney.manager.get(name=selected_value)
        configuration = ExtractionConfiguration(
            patient_journey=patient_journey_entry.patient_journey,
            modules={
                "preprocessing": Preprocessor,
                "activity_labeling": ActivityLabeler,
                "cohort_tagging": CohortTagger,
                "event_type_classification": EventTypeClassifier,
                "time_extraction": TimeExtractorBackup,
                "location_extraction": LocationExtractor,
                "event_log_comparator": EventLogComparator,
            },
        )
        Orchestrator(configuration=configuration)
        return super().form_valid(form)
