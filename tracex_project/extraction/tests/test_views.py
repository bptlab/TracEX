"""Test cases for the views of the extraction app."""
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse, resolve

from extraction.forms import (
    JourneyUploadForm,
)
from extraction.models import (
    PatientJourney,
)
from extraction.views import (
    JourneyInputSelectView,
    JourneyUploadView,
)


class JourneyInputSelectViewTests(TestCase):
    """Test cases for the JourneyInputSelectView."""

    def setUp(self):  # pylint: disable=invalid-name
        """Set up method that gets called everytime before tests are executed."""
        self.url = reverse('choose_input_method')

    def test_view_get_request(self):
        """Tests that the view URL exists and is accessible by passing a GET request."""
        response = self.client.get(self.url)
        resolver = resolve(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(resolver.func.view_class, JourneyInputSelectView)

    def test_view_post_request(self):
        """
        Test that a POST request to the view returns a method not allowed error since the JourneyInputSelectView
        is a simple TemplateView that does not handle POST request.
        """
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 405)

    def test_view_uses_correct_template(self):
        """Tests that the view uses the correct template."""
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'choose_input_method.html')

    def test_view_context_data(self):
        """Test that the view doesn't pass any context data."""
        response = self.client.get(self.url)

        self.assertFalse('context_data_key' in response.context)


class JourneyUploadViewTests(TestCase):
    """Test cases for the JourneyUploadView."""

    def setUp(self):  # pylint: disable=invalid-name
        """Set up method that gets called everytime before tests are executed."""
        self.client = Client()
        self.url = reverse('journey_upload')

    def test_view_get_request(self):
        """Tests that the view URL exists and is accessible by passing a GET request."""
        response = self.client.get(self.url)
        resolver = resolve(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(resolver.func.view_class, JourneyUploadView)

    def test_view_uses_correct_template(self):
        """Tests that the view uses the correct template."""
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'upload_journey.html')

    def test_view_uses_correct_form(self):
        """Tests that the view uses the correct form."""
        response = self.client.get(self.url)

        self.assertIsInstance(response.context['form'], JourneyUploadForm)

    def test_view_post_valid_form(self):
        """
        Test that posting a valid form with a file upload successfully creates
        a new model instance with the uploaded content and redirects to the correct success URL.
        """
        file_content = 'This is a test patient journey.'
        uploaded_file = SimpleUploadedFile('test.txt', file_content.encode('utf-8'))
        form_data = {'name': 'Test Journey', 'file': uploaded_file}

        response = self.client.post(self.url, form_data, format='multipart')
        # Response Code 200 means that the form validation failed and same view is rendered
        if response.status_code == 200:
            print(response.context['form'].errors)
        mock_journey = PatientJourney.manager.first()

        self.assertEqual(response.status_code, 302)  # Response Code 302 means that the form was successfully submitted
        self.assertEqual(PatientJourney.manager.count(), 1)
        self.assertEqual(mock_journey.patient_journey, file_content)
        self.assertRedirects(response, reverse('journey_details', kwargs={'pk': mock_journey.id}))
