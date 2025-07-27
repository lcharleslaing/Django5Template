from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.conf import settings
from .models import File
from .forms import FileUploadForm
import os

# image views
def files(request):
    return render(request, 'files/files.html')

@login_required
def file_list(request):
    """Display list of uploaded files"""
    files = File.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')
    return render(request, 'files/file_list.html', {'files': files})

@login_required
def file_upload(request):
    """Handle file upload"""
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_obj = form.save(commit=False)
            file_obj.uploaded_by = request.user
            file_obj.save()
            messages.success(request, f'File "{file_obj.title}" uploaded successfully!')
            return redirect('files:file_list')
    else:
        form = FileUploadForm()

    return render(request, 'files/file_upload.html', {'form': form})

@login_required
def file_detail(request, file_id):
    """Display file details"""
    file_obj = get_object_or_404(File, id=file_id, uploaded_by=request.user)
    return render(request, 'files/file_detail.html', {'file': file_obj})

@login_required
def file_download(request, file_id):
    """Download a file"""
    file_obj = get_object_or_404(File, id=file_id, uploaded_by=request.user)

    # Check if file exists
    if not os.path.exists(file_obj.file.path):
        raise Http404("File not found")

    # Open and serve the file
    with open(file_obj.file.path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_obj.filename()}"'
        return response

@login_required
def file_delete(request, file_id):
    """Delete a file"""
    file_obj = get_object_or_404(File, id=file_id, uploaded_by=request.user)

    if request.method == 'POST':
        title = file_obj.title
        file_obj.delete()
        messages.success(request, f'File "{title}" deleted successfully!')
        return redirect('files:file_list')

    return render(request, 'files/file_delete.html', {'file': file_obj})
