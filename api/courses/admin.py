from django.contrib import admin
from . import models


class CourseMemberInline(admin.TabularInline):
    model = models.CourseMember
    readonly_fields = ['user']
    extra = 0


class CourseAdmin(admin.ModelAdmin):
    model = models.Course
    inlines = [CourseMemberInline]
    list_display = ['title', 'department', 'speciality', 'status', 'owner']
    list_filter = ['department', 'speciality', 'status']
    search_fields = ['owner__first_name', 'owner__last_name', 'title']


admin.site.register(models.Course, CourseAdmin)
