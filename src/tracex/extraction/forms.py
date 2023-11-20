from django import forms


class JourneyForm(forms.Form):
    journey = forms.FileField(label="patient_journey")

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file:
            if not file.name.endswith(".txt"):
                raise forms.ValidationError("Please upload a valid .txt file.")
        return file
