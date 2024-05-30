"""Implement forms for the tracex app."""
from django import forms

from tracex.logic.constants import (
    MODULES_REQUIRED,
    MODULES_OPTIONAL,
    EVENT_TYPES,
    LOCATIONS,
    ACTIVITY_KEYS,
)


class BaseEventForm(forms.Form):
    """
    Form to select common filters in project.

    Form Fields:
    modules_required -- Required modules for the trace extraction. Default defined in constants.
    modules_optional -- Optional modules for the trace extraction. Default defined in constants.
    event_types -- Event types for the trace extraction. Default defined in constants.
    locations -- Locations for the trace extraction. Default defined in constants.
    activity_key -- Activity key for the output dataframe and direct-follows-graph. Default defined in constants.
    """

    modules_required = forms.MultipleChoiceField(
        label="Required modules",
        choices=MODULES_REQUIRED,
        widget=forms.CheckboxSelectMultiple(),
        required=True,
        initial=[module[0] for module in MODULES_REQUIRED],
        disabled=True,
    )
    modules_optional = forms.MultipleChoiceField(
        label="Select additional modules",
        choices=MODULES_OPTIONAL,
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        initial=[module[0] for module in MODULES_OPTIONAL],
        help_text="If modules are deselected, the resulting dataframe will be filled with placeholders!",
    )
    event_types = forms.MultipleChoiceField(
        label="Select desired event types",
        choices=EVENT_TYPES,
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        initial=EVENT_TYPES[0][0],  # [event_type[0] for event_type in EVENT_TYPES],
        help_text="'N/A' only occurs, if 'Event Type Classifier' is not selected.",
    )
    locations = forms.MultipleChoiceField(
        label="Select desired locations",
        choices=LOCATIONS,
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        initial=[location[0] for location in LOCATIONS],
        help_text="'N/A' only occurs, if 'Location Extractor' is not selected.",
    )
    activity_key = forms.ChoiceField(
        label="Select activity key for output",
        choices=ACTIVITY_KEYS,
        widget=forms.RadioSelect(),
        required=True,
        initial=ACTIVITY_KEYS[0][
            0
        ],
    )

    def clean(self):
        """
        Validate the form by checking that at least one event type or location is selected.

        Raises:
            forms.ValidationError: If no event type or location is selected.

        Returns:
            dict: The cleaned data if the validation passes.
        """
        cleaned_data = super().clean()
        event_types = cleaned_data.get("event_types", [])
        locations = cleaned_data.get("locations", [])

        if not event_types and not locations:
            raise forms.ValidationError(
                "Please select at least one event type or one location.",
                code="no_event_type",
            )

        return cleaned_data

    def clean_event_types(self):
        """
        Validate event types by checking dependent choices.

        This method ensures that if one event type from a dependent group is selected,
        the other event type from the same group is also selected.

        Returns:
            list: The cleaned list of event types.

        Raises:
            ValidationError: If a dependent choice is missing.
        """
        event_types = self.cleaned_data["event_types"]
        dependent_choices = [
            ("Symptom Onset", "Symptom Offset"),
            ("Hospital Admission", "Hospital Discharge"),
        ]

        for choice_1, choice_2 in dependent_choices:
            self.validate_dependent_choices("event_types", choice_1, choice_2)

        return event_types

    def validate_dependent_choices(self, field, choice_1, choice_2):
        """Validate that two choices in a form field are either both selected or none of them.

        Args:
            field (str): The name of the field to validate.
            choice_1 (str): The first choice in the dependent pair.
            choice_2 (str): The second choice in the dependent pair.

        Raises:
            ValidationError: If one choice is selected while the other is not.
            """
        choices = self.cleaned_data.get(field, [])

        if (choice_1 in choices) ^ (choice_2 in choices):
            raise forms.ValidationError(
                f"{choice_1} and {choice_2} depend on each other. Please select both or none.",
                code="dependant_fields",
            )


class ApiKeyForm(forms.Form):
    """Form to enter the OpenAI API Key."""
    api_key = forms.CharField(
        label='Enter your OpenAI API Key',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'API Key'}),
        error_messages={
            'required': 'API Key cannot be empty.',
            'max_length': 'API Key cannot be longer than 100 characters.'
        }
    )

    def clean_api_key(self):
        """Check if API Key formation is valid."""
        api_key = self.cleaned_data.get('api_key')
        if not api_key or len(api_key.strip()) == 0:
            raise forms.ValidationError("API Key cannot be empty.")

        return api_key
