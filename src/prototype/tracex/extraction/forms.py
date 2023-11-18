from django import forms


class JourneyForm(forms.Form):
    journey = forms.FileField(label="patient_journey")
