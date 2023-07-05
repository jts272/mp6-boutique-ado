from django.contrib import messages
from django.shortcuts import get_object_or_404, render

from .forms import UserProfileForm
from .models import UserProfile


def profile(request):
    """Display the user's profile."""
    profile = get_object_or_404(UserProfile, user=request.user)

    # Populate form with current user's profile information
    form = UserProfileForm(instance=profile)

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")

    # Use related name on the order model to get order history
    orders = profile.orders.all()

    template = "profiles/profile.html"
    context = {
        # "profile": profile,
        "form": form,
        "orders": orders,
        # For profile update success message toasts
        "on_profile_page": True,
    }

    return render(request, template, context)
