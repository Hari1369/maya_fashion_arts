from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render

from .forms import RegistrationForm, UserUpdateForm

User = get_user_model()


def superuser_required(view_func):
    @login_required(login_url="/admin/login/")
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_active or not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapped_view


def _user_rows(users, bound_user_id=None, bound_form=None):
    rows = []
    for user in users:
        form = (
            bound_form
            if user.pk == bound_user_id and bound_form is not None
            else UserUpdateForm(instance=user)
        )
        form_id = f"user-update-{user.pk}"
        for field in form.fields.values():
            field.widget.attrs["form"] = form_id
        rows.append((user, form, form_id))
    return rows


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "The user account has been created.")
            return redirect("core:dashboard")
    else:
        form = RegistrationForm()

    return render(request, "members/register.html", {"form": form})


@superuser_required
def user_details(request):
    users = User.objects.order_by("username")
    bound_user_id = None
    bound_form = None
    if request.method == "POST":
        action = request.POST.get("action")
        try:
            user_id = int(request.POST.get("user_id", ""))
        except ValueError:
            return HttpResponseBadRequest("A valid user ID is required.")
        user = users.filter(pk=user_id).first()
        if user is None:
            return HttpResponseBadRequest("The selected user does not exist.")

        if action == "update":
            bound_user_id = user.pk
            bound_form = UserUpdateForm(request.POST, instance=user)
            if bound_form.is_valid():
                bound_form.save()
                messages.success(request, f"Details for {user.username} were updated.")
                return redirect("members:userdetails")
        elif action == "delete":
            if user.pk == request.user.pk:
                messages.error(request, "You cannot delete your own account.")
                return redirect("members:userdetails")
            username = user.username
            user.delete()
            messages.success(request, f"User {username} was deleted.")
            return redirect("members:userdetails")
        else:
            return HttpResponseBadRequest("Unknown user action.")

    return render(
        request,
        "members/user_detail.html",
        {"user_rows": _user_rows(users, bound_user_id, bound_form)},
    )
