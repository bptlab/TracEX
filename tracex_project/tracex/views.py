"""
Provide class-based views for the tracex app.

Views:
TracexLandingPage -- View for the landing page of the tracex app.
ResetApiKey -- View for the resetting the API key.
DownloadXesView -- View for the download of XES file(s).
"""
import os
import zipfile
from tempfile import NamedTemporaryFile

from django.views import View
from django.http import HttpResponse, FileResponse
from django.views.generic import TemplateView, RedirectView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from tracex.forms import ApiKeyForm


class TracexLandingPage(TemplateView):
    """View for the landing page of the tracex app."""
    template_name = "landing_page.html"

    def get(self, _request, *_args, **kwargs):
        """Handle GET requests by initializing a form for API key entry and adding it to the context."""
        form = ApiKeyForm()
        context = self.get_context_data(**kwargs)
        context['form'] = form

        return self.render_to_response(context)

    def post(self, request):
        """Handles POST requests by processing a submitted form containing an API key.
        If valid, saves the API key to the environment and redirects to the landing page;
        otherwise, renders the form with errors."""
        form = ApiKeyForm(request.POST)
        if form.is_valid():
            api_key = form.cleaned_data['api_key']
            os.environ['OPENAI_API_KEY'] = api_key  # This sets it for the current process only
            return redirect('landing_page')

        return render(request, self.template_name, {'form': form})

    def get_context_data(self, **kwargs):
        """Retrieves and returns the base context data enhanced with the presence check for the API key.
        Indicates if a prompt for the API key is needed based on its absence."""
        context = super().get_context_data(**kwargs)
        self.request.session.flush()
        api_key = os.getenv('OPENAI_API_KEY')
        context['prompt_for_key'] = not bool(api_key)

        return context


class ResetApiKey(RedirectView):
    """View for resetting the API key."""

    url = reverse_lazy("landing_page")

    def get(self, request, *args, **kwargs):
        """Handles GET requests by deleting the API key from the environment and redirecting to the landing page."""
        del os.environ['OPENAI_API_KEY']

        return super().get(request, *args, **kwargs)


class DownloadXesView(View):
    """View for the download of on or more XES files."""

    def post(self, request, *_args, **_kwargs):
        """
        Process a POST request to download specified trace types as XES files.

        Validates trace types and returns the appropriate file response.
        """
        trace_types = self.get_trace_types(request)
        if not trace_types:
            return HttpResponse("No file type specified.", status=400)

        files_to_download = self.collect_files(request, trace_types)
        if files_to_download is None:  # Check for None explicitly to handle error scenario
            return HttpResponse("One or more files could not be found.", status=404)

        if len(files_to_download) == 1:
            return self.single_file_response(files_to_download[0])

        return self.zip_files_response(files_to_download)

    @staticmethod
    def get_trace_types(request):
        """Retrieves a list of trace types from the POST data."""

        return request.POST.getlist("trace_type[]")

    def collect_files(self, request, trace_types):
        """Collects file for the specified trace types to download, checking for their existence."""
        files_to_download = []
        for trace_type in trace_types:
            file_path = self.process_trace_type(request, trace_type)
            if file_path:
                if os.path.exists(file_path):
                    files_to_download.append(file_path)
                else:
                    return None  # Return None if any file path is invalid

        return files_to_download

    @staticmethod
    def process_trace_type(request, trace_type):
        """Process and provide the XES files to be downloaded based on the trace type."""

    # pylint: disable=consider-using-with
    @staticmethod
    def single_file_response(file_path):
        """Prepare a file if there is only a single XES file."""
        file = open(file_path, "rb")
        response = FileResponse(file, as_attachment=True)
        response[
            "Content-Disposition"
        ] = f'attachment; filename="{os.path.basename(file_path)}"'

        return response

    @staticmethod
    def zip_files_response(files_to_download):
        """Prepare a ZIP file if there are multiple XES files to download."""
        temp_zip = NamedTemporaryFile(mode="w+b", suffix=".zip", delete=False)
        zipf = zipfile.ZipFile(temp_zip, "w", zipfile.ZIP_DEFLATED)
        for file_path in files_to_download:
            zipf.write(file_path, arcname=os.path.basename(file_path))
        zipf.close()
        temp_zip_path = temp_zip.name
        temp_zip.close()

        file = open(temp_zip_path, "rb")
        response = FileResponse(file, as_attachment=True)
        response[
            "Content-Disposition"
        ] = 'attachment; filename="downloaded_xes_files.zip"'

        return response
