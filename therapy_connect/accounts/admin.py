from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserChangeForm, UserCreationForm


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = (
        "mobile_number",
        "first_name",
        "last_name",
        "is_admin",
        "role",
    )
    list_filter = (
        "is_admin",
        "role",
    )
    readonly_fields = ("last_login",)

    fieldsets = (
        (
            "Main",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "mobile_number",
                    "password",
                    "role",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_admin",
                    "is_staff",
                    "is_superuser",
                    "last_login",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "mobile_number",
                    "email",
                    "password1",
                    "password2",
                    "role",
                )
            },
        ),
    )

    search_fields = ("mobile_number", "first_name", "last_name")
    ordering = ("first_name",)
    filter_horizontal = ("groups", "user_permissions")

    def get_form(self, request, obj, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if not is_superuser:
            form.base_fields["is_superuser"].disabled = True
        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.exclude(is_superuser=True)
        return qs


admin.site.register(get_user_model(), UserAdmin)
