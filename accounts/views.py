from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import LoginForm, UserPasswordChangeForm, UserCreateForm, UserEditForm, AdminPasswordChangeForm
from employees.forms import PasswordResetRequestForm, SetNewPasswordForm

User = get_user_model()


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:index")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get("next", "dashboard:index")
            return redirect(next_url)
    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("accounts:login")


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html", {"page_title": "My Profile"})


@login_required
def change_password_view(request):
    form = UserPasswordChangeForm(request.user, request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect("accounts:profile")
    return render(request, "accounts/change_password.html", {"form": form, "page_title": "Change Password"})


@login_required
def user_list_view(request):
    if not (request.user.is_admin or request.user.is_it_admin or request.user.is_superuser):
        messages.error(request, "Access denied.")
        return redirect("dashboard:index")
    qs = User.objects.all().order_by("first_name", "last_name")
    search = request.GET.get('search', '')
    if search:
        qs = qs.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(username__icontains=search)
        )
    per_page = request.GET.get('per_page', '50')
    try:
        per_page = int(per_page)
        if per_page not in (20, 50, 100):
            per_page = 50
    except (ValueError, TypeError):
        per_page = 50
    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, "accounts/user_list.html", {
        "users": page_obj, "page_obj": page_obj, "search": search,
        "per_page": per_page, "page_title": "User Management"
    })


@login_required
def user_create_view(request):
    if not (request.user.is_admin or request.user.is_it_admin or request.user.is_superuser):
        messages.error(request, "Access denied.")
        return redirect("dashboard:index")
    form = UserCreateForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            messages.success(request, f"User {user.get_full_name()} created successfully.")
            return redirect("accounts:user_list")
    return render(request, "accounts/user_form.html", {"form": form, "page_title": "Create User", "action": "Create"})


@login_required
def user_edit_view(request, pk):
    if not (request.user.is_admin or request.user.is_it_admin or request.user.is_superuser):
        messages.error(request, "Access denied.")
        return redirect("dashboard:index")
    user_obj = get_object_or_404(User, pk=pk)
    form = UserEditForm(request.POST or None, instance=user_obj)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully.")
            return redirect("accounts:user_list")
    return render(request, "accounts/user_form.html", {
        "form": form, "page_title": "Edit User", "action": "Update", "user_obj": user_obj
    })


@login_required
def admin_change_password_view(request, pk):
    if not (request.user.is_admin or request.user.is_it_admin or request.user.is_superuser):
        messages.error(request, "Access denied.")
        return redirect("dashboard:index")
    user_obj = get_object_or_404(User, pk=pk)
    form = AdminPasswordChangeForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user_obj.set_password(form.cleaned_data['new_password1'])
            user_obj.save()
            messages.success(request, f"Password for {user_obj.get_full_name()} changed successfully.")
            return redirect("accounts:user_list")
    return render(request, "accounts/change_password_for_user.html", {
        "form": form,
        "user_obj": user_obj,
        "page_title": f"Change Password: {user_obj.get_full_name()}"
    })


def forgot_password_view(request):
    """Request a password reset. Always shows 'email sent' message to avoid revealing account existence."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    form = PasswordResetRequestForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email'].strip().lower()
        user = User.objects.filter(email__iexact=email).first()
        if user and user.is_active:
            # Generate secure token
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = request.build_absolute_uri(f'/accounts/reset-password/{uid}/{token}/')
            # Try to send email; silently ignore failures
            try:
                from django.core.mail import send_mail
                from core.models import SystemSettings
                settings_obj = SystemSettings.get_settings()
                from_name = settings_obj.email_from_name or 'IT Cadre System'
                send_mail(
                    subject='Password Reset — IT and Communication Cadre Tracking Database',
                    message=(
                        f"Hello {user.get_full_name()},\n\n"
                        f"You requested a password reset. Click the link below to set a new password:\n\n"
                        f"{reset_url}\n\n"
                        f"This link expires in 24 hours.\n\n"
                        f"If you did not request this, please ignore this email.\n\n"
                        f"— {from_name}"
                    ),
                    from_email=None,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception:
                pass  # Never reveal errors
        # Always show the same message — never reveal if email exists
        return render(request, 'accounts/forgot_password_sent.html', {})
    return render(request, 'accounts/forgot_password.html', {'form': form})


def password_reset_confirm_view(request, uidb64, token):
    """Confirm password reset with token from email."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        return render(request, 'accounts/password_reset_invalid.html', {})

    form = SetNewPasswordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user.set_password(form.cleaned_data['new_password1'])
        user.save()
        messages.success(request, 'Your password has been reset. Please sign in with your new password.')
        return redirect('accounts:login')

    return render(request, 'accounts/password_reset_confirm.html', {'form': form})


@login_required
def user_delete_view(request, pk):
    if not (request.user.is_admin or request.user.is_it_admin or request.user.is_superuser):
        messages.error(request, "Access denied.")
        return redirect("dashboard:index")
    user_obj = get_object_or_404(User, pk=pk)
    if user_obj == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect("accounts:user_list")
    if user_obj.is_superuser and not request.user.is_superuser:
        messages.error(request, "Only superusers can delete superuser accounts.")
        return redirect("accounts:user_list")
    if request.method == "POST":
        name = user_obj.get_full_name()
        user_obj.delete()
        messages.success(request, f"User {name} deleted successfully.")
        return redirect("accounts:user_list")
    return render(request, "accounts/user_confirm_delete.html", {
        "user_obj": user_obj,
        "page_title": f"Delete User: {user_obj.get_full_name()}"
    })
