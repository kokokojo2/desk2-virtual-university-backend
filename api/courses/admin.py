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


class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'published_at', 'chapter', 'is_archived']
    readonly_fields = ['is_planned', 'created_at', 'edited_at']
    list_filter = ['is_archived', 'author__user']


class MaterialAdmin(PostAdmin):
    model = models.Material


class ChapterAdmin(admin.ModelAdmin):
    model = models.Chapter


admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.Material, MaterialAdmin)
admin.site.register(models.Chapter, ChapterAdmin)
