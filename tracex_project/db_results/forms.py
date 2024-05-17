"""Implementation of forms for the database result app."""
from django import forms
from django.utils.safestring import mark_safe

from extraction.models import PatientJourney
from extraction.models import Cohort
from tracex.forms import BaseEventForm


class PatientJourneySelectForm(forms.Form):
    """Form for selecting a patient journey."""

    selected_patient_journey = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        """Initializes the PatientJourneySelectForm."""
        super().__init__(*args, **kwargs)
        self.fields[
            "selected_patient_journey"
        ].choices = self.get_patient_journey_choices()

    def get_patient_journey_choices(self):
        """Retrieves the available patient journey choices with existing metrics from the database."""
        patient_journeys = PatientJourney.manager.exclude(
            trace__events__metrics__activity_relevance__isnull=True,
            trace__events__metrics__timestamp_correctness__isnull=True,
            trace__events__metrics__correctness_confidence__isnull=True,
        ).distinct()
        choices = [(pj.name, pj.name) for pj in patient_journeys]

        return choices


class EvaluationForm(BaseEventForm):
    """Form for evaluating the extraction result."""

    min_age = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={"id": "min-age"}),
    )
    max_age = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={"id": "max-age"}),
    )
    none_age = forms.BooleanField(
        label=mark_safe("<i>Include elements with None values</i>"),
        required=False,
        widget=forms.CheckboxInput(),
    )
    sex = forms.MultipleChoiceField(
        label="Sex:",
        choices=[],
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    condition = forms.MultipleChoiceField(
        label="Condition:",
        choices=[],
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    preexisting_condition = forms.MultipleChoiceField(
        label="Preexisting Condition:",
        choices=[],
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    origin = forms.MultipleChoiceField(
        label="Origin:",
        choices=[],
        widget=forms.CheckboxSelectMultiple(attrs={"class": "origin-checkbox"}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Initializes the EvaluationForm."""
        config = kwargs.get("initial", None)
        super().__init__(*args, **kwargs)

        self.label_suffix = ""

        if config:
            self.fields["min_age"].initial = config.get("min_age")
            self.fields["max_age"].initial = config.get("max_age")

        self.fields["condition"].choices = self.get_choices("condition")
        self.fields["preexisting_condition"].choices = self.get_choices(
            "preexisting_condition"
        )
        self.fields["origin"].choices = self.get_choices("origin")
        self.fields["sex"].choices = self.get_choices("sex")

    @staticmethod
    def get_choices(category):
        """Get all choices available in the database for a given category."""
        choices = Cohort.manager.values_list(category, flat=True).distinct()
        none_info_text = mark_safe("<i>Include elements with None values</i>")
        choices = [
            (
                "None" if choice is None else choice,
                none_info_text if choice is None else choice,
            )
            for choice in choices
        ]
        # sort by name, but put None values at the end
        return sorted(choices, key=lambda x: (x[0] == "None", x[1]))
