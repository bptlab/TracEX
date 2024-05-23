"""
Provide class-based views for the tracex app.

Views:
TracexLandingPage -- View for the landing page of the tracex app.
ResetApiKey -- View for the resetting the API key.
DownloadXesView -- View for the download of XES file(s).
"""
import os
import traceback
import zipfile
from tempfile import NamedTemporaryFile
from typing import List

from django.views import View
from django.http import HttpResponse, FileResponse
from django.views.generic import TemplateView, RedirectView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from tracex.forms import ApiKeyForm


class TracexLandingPage(TemplateView):
    """View for the landing page of the tracex app."""

    template_name = "landing_page.html"

    def get(self, _request, *args, **kwargs):
        """Handle GET requests by initializing a form for API key entry and adding it to the context."""
        context = self.get_context_data(**kwargs)
        context['form'] = ApiKeyForm()

        return self.render_to_response(context)

    def post(self, request):
        """Handle POST requests by processing a submitted form containing an API key."""
        form = ApiKeyForm(request.POST)
        if form.is_valid():
            api_key = form.cleaned_data['api_key']
            os.environ['OPENAI_API_KEY'] = api_key

            return redirect('landing_page')
        else:
            context = self.get_context_data()
            context['form'] = form

            return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        """Return context data and adds a flag indicating whether an API key is set."""
        context = super().get_context_data(**kwargs)
        api_key = os.getenv('OPENAI_API_KEY')
        context['prompt_for_key'] = not bool(api_key)

        return context


class ResetApiKey(RedirectView):
    """View for resetting the API key."""

    url = reverse_lazy("landing_page")

    def get(self, request, *args, **kwargs):
        """Handle GET requests by deleting the API key from the environment and redirecting to the landing page."""
        try:
            del os.environ['OPENAI_API_KEY']
        except KeyError as e:
            return render(
                self.request,
                'error_page.html',
                {'type': type(e).__name__,'error_traceback': traceback.format_exc()}
            )

        return super().get(request, *args, **kwargs)


class DownloadXesView(View):
    """View for the downloading of XES file(s)."""

    def post(self, request, *args, **kwargs):
        """
        Process a POST request to download specified trace types as XES files.

        Validates trace types and returns the appropriate file response.
        """
        trace_types = self.get_trace_types(request)
        if not trace_types:
            return HttpResponse("No file type specified.", status=400)

        files_to_download = self.collect_files(request, trace_types)
        if files_to_download is None:
            return HttpResponse("One or more files could not be found.", status=404)

        if len(files_to_download) == 1:
            return self.single_file_response(files_to_download[0])

        return self.zip_files_response(files_to_download)

    @staticmethod
    def get_trace_types(request):
        """Retrieves a list of trace types from the POST data."""

        return request.POST.getlist("trace_type[]")

    def collect_files(self, request, trace_types: List[str]):
        """Collects file for the specified trace types to download, checking for their existence."""
        files_to_download = []
        for trace_type in trace_types:
            file_path = self.process_trace_type(request, trace_type)
            if file_path:
                if os.path.exists(file_path):
                    files_to_download.append(file_path)
                else:
                    return None

        return files_to_download

    @staticmethod
    def process_trace_type(request, trace_type):
        """Process and provide the XES files to be downloaded based on the trace type."""

    # pylint: disable=consider-using-with
    @staticmethod
    def single_file_response(file_path):
        """Prepare a single XES file for download."""
        file_name = os.path.basename(file_path)
        response = FileResponse(open(file_path, "rb"), as_attachment=True)
        response["Content-Disposition"] = f'attachment; filename="{file_name}"'

        return response

    @staticmethod
    def zip_files_response(files_to_download):
        """Prepare a ZIP file for multiple files to download."""
        with NamedTemporaryFile(mode="w+b", suffix=".zip", delete=False) as temp_zip:
            with zipfile.ZipFile(temp_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file_path in files_to_download:
                    file_name = os.path.basename(file_path)
                    zipf.write(file_path, arcname=file_name)

            response = FileResponse(open(temp_zip.name, "rb"), as_attachment=True)
            response["Content-Disposition"] = 'attachment; filename="downloaded_files.zip"'

        os.remove(temp_zip.name)

        return response
