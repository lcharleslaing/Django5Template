from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Image
from .forms import ImageUploadForm

@login_required
def image_list(request):
    """Display list of uploaded images"""
    images = Image.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')
    return render(request, 'images/image_list.html', {'images': images})

@login_required
def image_upload(request):
    """Handle image upload"""
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_obj = form.save(commit=False)
            image_obj.uploaded_by = request.user
            image_obj.save()
            messages.success(request, f'Image "{image_obj.title}" uploaded successfully!')
            return redirect('images:image_list')
    else:
        form = ImageUploadForm()

    return render(request, 'images/image_upload.html', {'form': form})

@login_required
def image_detail(request, image_id):
    """Display image details"""
    image_obj = get_object_or_404(Image, id=image_id, uploaded_by=request.user)
    return render(request, 'images/image_detail.html', {'image': image_obj})

@login_required
def image_delete(request, image_id):
    """Delete an image"""
    image_obj = get_object_or_404(Image, id=image_id, uploaded_by=request.user)

    if request.method == 'POST':
        title = image_obj.title
        image_obj.delete()
        messages.success(request, f'Image "{title}" deleted successfully!')
        return redirect('images:image_list')

    return render(request, 'images/image_delete.html', {'image': image_obj})

# Keep the original view for backward compatibility
def images(request):
    return render(request, 'images/images.html')
