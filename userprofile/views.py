from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import UserProfileForm, UserUpdateForm, PasswordChangeForm

@login_required
def profile_view(request, username=None):
    """View user profile"""
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    # Get or create profile
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(user=user)
    
    # Get user's recent files and images
    recent_files = user.file_set.all().order_by('-uploaded_at')[:5] if hasattr(user, 'file_set') else []
    recent_images = user.image_set.all().order_by('-uploaded_at')[:5] if hasattr(user, 'image_set') else []
    
    context = {
        'profile_user': user,
        'profile': profile,
        'recent_files': recent_files,
        'recent_images': recent_images,
        'is_own_profile': user == request.user,
    }
    return render(request, 'userprofile/profile_view.html', context)

@login_required
def profile_edit(request):
    """Edit user profile"""
    # Get or create profile
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('userprofile:profile_view')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'userprofile/profile_edit.html', context)

@login_required
def password_change(request):
    """Change user password"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('userprofile:profile_view')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'userprofile/password_change.html', context)

@login_required
def profile_list(request):
    """List all user profiles (admin only)"""
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to view all profiles.")
        return redirect('userprofile:profile_view')
    
    profiles = UserProfile.objects.all().order_by('user__username')
    context = {
        'profiles': profiles,
    }
    return render(request, 'userprofile/profile_list.html', context)

@login_required
def avatar_remove(request):
    """Remove user avatar"""
    if request.method == 'POST':
        # Get or create profile
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        if profile.avatar and profile.has_avatar:
            # Delete the old avatar file
            if profile.avatar:
                profile.avatar.delete(save=False)
            profile.avatar = 'avatars/default.png'
            profile.save()
            messages.success(request, 'Avatar removed successfully!')
        else:
            messages.info(request, 'No custom avatar to remove.')
    
    return redirect('userprofile:profile_edit')
