"""Test cases for the views of the extraction app."""
import json

from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse, resolve

from extraction.forms import (
    JourneyUploadForm,
    JourneySelectForm,
    FilterForm,
    ResultForm
)
from extraction.models import (
    PatientJourney,
)
from extraction.views import (
    JourneyInputSelectView,
    JourneyUploadView,
    JourneySelectView,
    JourneyDetailView,
    JourneyFilterView,
    ResultView,
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

    def test_view_context_data(self):
        """Test that the view doesn't pass any context data."""
        response = self.client.get(self.url)

        self.assertFalse('context_data_key' in response.context)

    def test_view_post_valid_form(self):
        """
        Test that posting a valid form with a file upload successfully creates
        a new model instance with the uploaded content and redirects to the correct success URL.
        """
        file_content = 'This is a test patient journey.'
        uploaded_file = SimpleUploadedFile('test.txt', file_content.encode('utf-8'))
        form_data = {'name': 'Test Journey', 'file': uploaded_file}

        response = self.client.post(self.url, data=form_data, format='multipart')
        mock_journey = PatientJourney.manager.first()

        self.assertEqual(response.status_code, 302)  # Response Code 302 means that the form was successfully submitted
        self.assertEqual(PatientJourney.manager.count(), 1)
        self.assertEqual(mock_journey.patient_journey, file_content)
        self.assertRedirects(response, reverse('journey_details', kwargs={'pk': mock_journey.id}))

    def test_view_post_invalid_form(self):
        """Tests that posting an invalid form (without a file) returns the same page with a form error."""
        form_data = {}
        response = self.client.post(self.url, data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'file', 'This field is required.')


class JourneySelectViewTests(TestCase):
    """Test cases for the JourneySelectView."""

    def setUp(self):  # pylint: disable=invalid-name
        """Set up method that gets called everytime before tests are executed."""
        self.client = Client()
        self.url = reverse('journey_select')

    def test_view_get_request(self):
        """Tests that the view URL exists and is accessible by passing a GET request."""
        response = self.client.get(self.url)
        resolver = resolve(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(resolver.func.view_class, JourneySelectView)

    def test_view_uses_correct_template(self):
        """Tests that the view uses the correct template."""
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'select_journey.html')

    def test_view_uses_correct_form(self):
        """Tests that the view uses the correct form."""
        response = self.client.get(self.url)

        self.assertIsInstance(response.context['form'], JourneySelectForm)

    def test_view_context_data(self):
        """Test that the view passes no context data."""
        response = self.client.get(self.url)

        self.assertFalse('context_data_key' in response.context)

    def test_view_post_valid_form(self):
        """
        Test that posting a valid form by selecting an existing patient journey redirects to the correct success URL.
        """
        mock_journey = PatientJourney.manager.create(name='Test Journey',
                                                     patient_journey='This is a test patient journey.')
        form_data = {'selected_patient_journey': mock_journey.name}
        response = self.client.post(self.url, data=form_data, format='multipart')

        self.assertEqual(response.status_code, 302)  # Response Code 302 means that the form was successfully submitted
        self.assertEqual(mock_journey.name, form_data['selected_patient_journey'])
        self.assertRedirects(response, reverse('journey_details', kwargs={'pk': mock_journey.id}))

    def test_view_post_invalid_form(self):
        """Tests that posting an invalid form (without selecting a file) returns the same page with a form error."""
        form_data = {}
        response = self.client.post(self.url, data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'selected_patient_journey', 'This field is required.')


class JourneyDetailViewTests(TestCase):
    """Test cases for the JourneyDetailView."""

    def setUp(self):  # pylint: disable=invalid-name
        """Set up method that gets called everytime before tests are executed."""
        self.client = Client()
        self.mock_journey = PatientJourney.manager.create(name='Test Journey',
                                                          patient_journey='This is a test patient journey.')
        self.url = reverse('journey_details', kwargs={'pk': self.mock_journey.pk})

    def test_view_get_request(self):
        """Tests that the view URL exists and is accessible by passing a GET request."""
        response = self.client.get(self.url)
        resolver = resolve(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(resolver.func.view_class, JourneyDetailView)

    def test_uses_correct_template(self):
        """Tests that the view uses the correct template."""
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'journey_details.html')

    def test_view_context_data(self):
        """Test that the view passes the correct context data."""
        response = self.client.get(self.url)

        self.assertIn('patient_journey', response.context)
        self.assertEqual(response.context['patient_journey'], self.mock_journey)
        self.assertEqual(self.client.session.get('patient_journey_id'), self.mock_journey.id)

    def test_view_without_patient_journey(self):
        """Test that requesting a patient journey that does not exist returns a 404 error."""
        response = self.client.get(reverse('journey_details', kwargs={'pk': 999}))

        self.assertEqual(response.status_code, 404)

    def test_post_method_redirect(self):
        """Test that a POST request to the view redirects to the same page."""
        # Perform a GET request to set up session data
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session['patient_journey_id'], self.mock_journey.id)

        # Perform a POST request to the same view
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('journey_filter'))


class JourneyFilterViewTests(TestCase):
    """Test cases for the JourneyFilterView."""

    fixtures = ["tracex_project/extraction/fixtures/prompts_fixture.json"]

    @staticmethod
    def dummy_get_response():
        """This is a dummy function to satisfy the get_response parameter of the SessionMiddleware."""
        return None

    def setUp(self):  # pylint: disable=invalid-name
        """Set up method that gets called everytime before tests are executed."""
        self.client = Client()
        self.mock_journey = PatientJourney.manager.create(name='Test Journey',
                                                          patient_journey='This is a test patient journey.')
        self.url = reverse('journey_filter')
        self.factory = RequestFactory()

    def test_view_get_request(self):
        """Tests that the view URL exists and is accessible by passing a GET request."""
        response = self.client.get(self.url)
        resolver = resolve(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(resolver.func.view_class, JourneyFilterView)

    def test_uses_correct_template(self):
        """Tests that the view uses the correct template."""
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'filter_journey.html')

    def test_view_uses_correct_form(self):
        """Tests that the view uses the correct form."""
        response = self.client.get(self.url)

        self.assertIsInstance(response.context['form'], FilterForm)

    def test_get_context_data(self):
        """Test that the `is_comparing` context variable is added correctly in the `get_context_data` method."""
        request = self.factory.get(self.url)
        request.session = {}
        view = JourneyFilterView()
        view.request = request
        context = view.get_context_data()

        self.assertIn('is_comparing', context)

    # Non-deterministic test since orchestrator is executed
    def test_form_valid(self):
        """Test that a valid form submission redirects to the correct URL."""
        form_data = {
            'modules_required': ['activity_labeling'],
            'modules_optional': ['preprocessing', 'event_type_classification'],
            'event_types': ['Symptom Onset', 'Symptom Offset'],
            'locations': ['Home', 'Hospital', 'Doctors', 'N/A'],
            'activity_key': 'event_type',
        }
        # Set up session data
        session = self.client.session
        session['is_comparing'] = False
        session.save()

        # Submit the form using the test client
        response = self.client.post(self.url, data=form_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('result'))

    def test_get_ajax(self):
        """
        Test the `get` method when an AJAX request is made.
        Ensure that the correct JSON response is returned with the progress and status information.
        """
        request = self.factory.get(self.url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.session = {'progress': 50, 'status': 'running'}
        view = JourneyFilterView()
        view.request = request
        response = view.get(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'progress': 50, 'status': 'running'})


class ResultViewTests(TestCase):
    """Test cases for the ResultView."""
    def setUp(self):  # pylint: disable=invalid-name
        """Set up method that gets called everytime before tests are executed."""
        self.client = Client()
        self.mock_journey = PatientJourney.manager.create(name='Test Journey',
                                                          patient_journey='This is a test patient journey.')
        self.session = self.client.session
        self.session['selected_modules'] = ['activity_labeling']
        self.session.save()
        self.url = reverse('result')

    def test_view_get_request(self):
        """Tests that the view URL exists and is accessible by passing a GET request."""
        response = self.client.get(self.url)
        resolver = resolve(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(resolver.func.view_class, ResultView)

    def test_uses_correct_template(self):
        """Tests that the view uses the correct template."""
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'result.html')

    def test_uses_correct_form(self):
        """Tests that the view uses the correct form."""
        response = self.client.get(self.url)

        self.assertIsInstance(response.context['form'], ResultForm)

    def test_get_form_kwargs(self):
        """Tests that correct form kwargs are passed to the form."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        form = response.context['form']

        self.assertIsInstance(form, ResultForm)
        self.assertEqual((form.initial['selected_modules']), self.session['selected_modules'])

    def test_get_context_data(self):
        """Tests that the view fetches the correct context data."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        context = response.context

        self.assertIn('form', context)
        self.assertIsInstance(context['form'], ResultForm)
        self.assertIn('journey', context)
        self.assertEqual(context['journey'], self.mock_journey.patient_journey)
        self.assertIn('dfg_img', context)
        self.assertIn('trace_table', context)
        self.assertIn('all_dfg_img', context)
        self.assertIn('event_log_table', context)
