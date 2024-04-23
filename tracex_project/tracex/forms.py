"""Implementation of forms"""
from django import forms


class ApiKeyForm(forms.Form):
    """A form for inputting the OpenAI API key."""
    api_key = forms.CharField(
        label='Enter your OpenAI API Key',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'API Key'})
    )

    def clean_api_key(self):
        """Check if API Key formation is valid."""
        api_key = self.cleaned_data.get('api_key')
        if not api_key or len(api_key.strip()) == 0:
            raise forms.ValidationError("API Key cannot be empty.")

        return api_key
