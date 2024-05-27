"""Test cases for the views of the extraction app."""
import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse, resolve

from extraction.forms import (
    JourneyUploadForm,
    JourneySelectForm,
    FilterForm,
    ResultForm,
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
        self.url = reverse("choose_input_method")

    def test_view_get_request(self):
        """Test that the view URL exists and is accessible by passing a GET request."""
        response = self.client.get(self.url)
        resolver = resolve(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(resolver.func.view_class, JourneyInputSelectView)

    def test_view_post_request(self):
        """
        Test that a POST request to the view returns a method not allowed error.

        The JourneyInputSelectView is a simple TemplateView that does not handle POST request.
        """
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 405)

    def test_view_uses_correct_template(self):
        """Test that the view uses the correct template."""
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "choose_input_method.html")

    def test_view_context_data(self):
        """Test that the view doesn't pass any context data."""
        response = self.client.get(self.url)

        self.assertFalse("context_data_key" in response.context)


class JourneyUploadViewTests(TestCase):
    """Test cases for the JourneyUploadView."""

    def setUp(self):  # pylint: disable=invalid-name
        """Set up test client and URL."""
        self.client = Client()
        self.url = reverse("journey_upload")

    def test_view_get_request(self):
        """Test that the view URL exists and is accessible by passing a GET request."""
        response = self.client.get(self.url)
        resolver = resolve(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(resolver.func.view_class, JourneyUploadView)

    def test_view_uses_correct_template(self):
        """Test that the view uses the correct template."""
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "upload_journey.html")

    def test_view_uses_correct_form(self):
        """Test that the view uses the correct form."""
        response = self.client.get(self.url)

        self.assertIsInstance(response.context["form"], JourneyUploadForm)

    def test_view_context_data(self):
        """Test that the view doesn't pass any context data."""
        response = self.client.get(self.url)

        self.assertFalse("context_data_key" in response.context)

    def test_view_post_valid_form(self):
        """
        Test that posting a valid form with a file upload successfully creates
        a new model instance with the uploaded content and redirects to the correct success URL.
        """
        file_content = "This is a test Patient Journey."
        uploaded_file = SimpleUploadedFile("test.txt", file_content.encode("utf-8"))
        form_data = {"name": "Test Journey", "file": uploaded_file}

        response = self.client.post(self.url, data=form_data, format="multipart")
        mock_journey = PatientJourney.manager.first()

        self.assertEqual(
            response.status_code, 302
        )  # Response Code 302 means that the form was successfully submitted
        self.assertEqual(PatientJourney.manager.count(), 1)
        self.assertEqual(mock_journey.patient_journey, file_content)
        self.assertRedirects(
            response, reverse("journey_details", kwargs={"pk": mock_journey.id})
        )

    def test_view_post_invalid_form(self):
        """Test that posting an invalid form (without a file) returns the same page with a form error."""
        form_data = {}
        response = self.client.post(self.url, data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response=response,
            form="form",
            field="file",
            errors="This field is required.",
            msg_prefix="Invalid form submission",
        )


class JourneySelectViewTests(TestCase):
    """Test cases for the JourneySelectView."""

    def setUp(self):  # pylint: disable=invalid-name
        """Set up test client and URL."""
        self.client = Client()
        self.url = reverse("journey_select")

    def test_view_get_request(self):
        """Tests that the view URL exists and is accessible by passing a GET request."""
        response = self.client.get(self.url)
        resolver = resolve(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(resolver.func.view_class, JourneySelectView)

    def test_view_uses_correct_template(self):
        """Test that the view uses the correct template."""
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "select_journey.html")

    def test_view_uses_correct_form(self):
        """Test that the view uses the correct form."""
        response = self.client.get(self.url)

        self.assertIsInstance(response.context["form"], JourneySelectForm)

    def test_view_context_data(self):
        """Test that the view passes no context data."""
        response = self.client.get(self.url)

        self.assertFalse("context_data_key" in response.context)

    def test_view_post_valid_form(self):
        """
        Test that posting a valid form by selecting an existing Patient Journey redirects to the correct success URL.
        """
        mock_journey = PatientJourney.manager.create(
            name="Test Journey", patient_journey="This is a test Patient Journey."
        )
        form_data = {"selected_patient_journey": mock_journey.name}
        response = self.client.post(self.url, data=form_data, format="multipart")

        self.assertEqual(
            response.status_code, 302
        )  # Response Code 302 means that the form was successfully submitted
        self.assertEqual(mock_journey.name, form_data["selected_patient_journey"])
        self.assertRedirects(
            response, reverse("journey_details", kwargs={"pk": mock_journey.id})
        )

    def test_view_post_invalid_form(self):
        """Test that posting an invalid form (without selecting a file) returns the same page with a form error."""
        form_data = {}
        response = self.client.post(self.url, data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response=response,
            form="form",
            field="selected_patient_journey",
            errors="This field is required.",
            msg_prefix="Invalid form submission",
        )


class JourneyDetailViewTests(TestCase):
    """Test cases for the JourneyDetailView."""

    def setUp(self):  # pylint: disable=invalid-name
        """Set up test client, a mock Patient Journey and the URL."""
        self.client = Client()
        self.mock_journey = PatientJourney.manager.create(
            name="Test Journey", patient_journey="This is a test Patient Journey."
        )
        self.url = reverse("journey_details", kwargs={"pk": self.mock_journey.pk})

    def test_view_get_request(self):
        """Test that the view URL exists and is accessible by passing a GET request."""
        response = self.client.get(self.url)
        resolver = resolve(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(resolver.func.view_class, JourneyDetailView)

    def test_uses_correct_template(self):
        """Test that the view uses the correct template."""
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "journey_details.html")

    def test_view_context_data(self):
        """Test that the view passes the correct context data."""
        response = self.client.get(self.url)

        self.assertIn("patient_journey", response.context)
        self.assertEqual(response.context["patient_journey"], self.mock_journey)
        self.assertEqual(
            self.client.session.get("patient_journey_id"), self.mock_journey.id
        )

    def test_view_without_patient_journey(self):
        """Test that requesting a Patient Journey that does not exist returns a 404 error."""
        response = self.client.get(reverse("journey_details", kwargs={"pk": 999}))

        self.assertEqual(response.status_code, 404)

    def test_post_method_redirect(self):
        """Test that a POST request to the view redirects to the JourneyFilterView."""
        # Perform a GET request to set up session data
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.client.session["patient_journey_id"], self.mock_journey.id
        )

        # Perform a POST request to the same view
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("journey_filter"))


class JourneyFilterViewTests(TestCase):
    """Test cases for the JourneyFilterView."""

    fixtures = ["tracex_project/extraction/fixtures/prompts_fixture.json"]

    def setUp(self):  # pylint: disable=invalid-name
        """Set up test client, a mock Patient Journey, the URL and a factory that sends requests to the view."""
        self.client = Client()
        self.mock_journey = PatientJourney.manager.create(
            name="Test Journey", patient_journey="This is a test Patient Journey."
        )
        self.url = reverse("journey_filter")
        self.factory = RequestFactory()

    def test_view_get_request(self):
        """Test that the view URL exists and is accessible by passing a GET request."""
        response = self.client.get(self.url)
        resolver = resolve(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(resolver.func.view_class, JourneyFilterView)

    def test_uses_correct_template(self):
        """Test that the view uses the correct template."""
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "filter_journey.html")

    def test_view_uses_correct_form(self):
        """Test that the view uses the correct form."""
        response = self.client.get(self.url)

        self.assertIsInstance(response.context["form"], FilterForm)

    def test_get_context_data(self):
        """Test that the `is_comparing` context variable is added correctly in the `get_context_data` method."""
        request = self.factory.get(self.url)
        request.session = {}
        view = JourneyFilterView()
        view.request = request
        context = view.get_context_data()

        self.assertIn("is_comparing", context)

    def test_get_ajax(self):
        """
        Test the `get` method when an AJAX request is made.

        Ensure that the correct JSON response is returned with the progress and status information.
        """
        request = self.factory.get(self.url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        request.session = {"progress": 50, "status": "running"}
        view = JourneyFilterView()
        view.request = request
        response = view.get(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content), {"progress": 50, "status": "running"}
        )
