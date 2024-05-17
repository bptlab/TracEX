"""Test cases for the views of the extraction app."""
from django.test import TestCase
from django.urls import reverse


class JourneyInputSelectViewTests(TestCase):
    """Test cases for the JourneyInputSelectView."""
    def test_view_get_request(self):
        """Tests that the view URL exists and is accessible by passing a GET request."""
        response = self.client.get(reverse("choose_input_method"))

        self.assertEqual(response.status_code, 200)

    def test_view_post_request(self):
        """
        Test that a POST request to the view returns a method not allowed error since the JourneyInputSelectView
        is a simple TemplateView that does not handle POST request.
        """
        response = self.client.post(reverse('choose_input_method'))

        self.assertEqual(response.status_code, 405)

    def test_view_uses_correct_template(self):
        """Tests that the view uses the correct template."""
        response = self.client.get(reverse("choose_input_method"))

        self.assertTemplateUsed(response, "choose_input_method.html")

    def test_view_context_data(self):
        """Test that the view doesn't pass any context data."""
        response = self.client.get(reverse('choose_input_method'))

        self.assertFalse('context_data_key' in response.context)


