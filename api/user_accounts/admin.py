from django.contrib import admin
from .models import UserAccount, TeacherProfile, StudentProfile


class StudentProfileModelInline(admin.TabularInline):
    model = StudentProfile

    def has_delete_permission(self, request, obj=None):
        return False


class TeacherProfileModelInline(admin.TabularInline):
    model = TeacherProfile

    def has_delete_permission(self, request, obj=None):
        return False


class UserAccountAdmin(admin.ModelAdmin):
    model = UserAccount
    # list page
    list_display = ['first_name', 'last_name', 'email', 'department', 'registration_type', 'is_active']
    list_filter = ['department', 'is_active', 'registration_type']
    search_fields = ['first_name', 'last_name', 'email']

    # detail page
    readonly_fields = ['last_login', 'registration_type']
    exclude = ['password']

    def get_inlines(self, request, obj):
        try:
            profile_instance = obj.profile
            if isinstance(profile_instance, StudentProfile):
                return [StudentProfileModelInline]

            return [TeacherProfileModelInline]
        except AttributeError:
            return []


admin.site.register(UserAccount, UserAccountAdmin)
