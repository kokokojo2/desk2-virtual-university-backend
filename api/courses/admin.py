from django.contrib import admin
from . import models
from utils.admin import ReadOnlyInlineMixin


class CourseMemberInline(admin.TabularInline):
    model = models.CourseMember
    readonly_fields = ['user']
    extra = 0


class ChapterInline(ReadOnlyInlineMixin, admin.TabularInline):
    model = models.Chapter
    fields = ['title', 'created_at']
    readonly_fields = ['created_at']
    show_change_link = True


class PostInline(ReadOnlyInlineMixin, admin.TabularInline):
    fields = ['title', 'published_at', 'is_archived']
    show_change_link = True


class MaterialInline(PostInline):
    model = models.Material


class TaskInline(PostInline):
    model = models.Task


class ChapterAdmin(admin.ModelAdmin):
    inlines = [MaterialInline, TaskInline]
    model = models.Chapter

    list_display = ['title', 'created_at', 'course']
    list_filter = ['course__title']


class CourseAdmin(admin.ModelAdmin):
    model = models.Course
    inlines = [CourseMemberInline, ChapterInline]
    list_display = ['title', 'department', 'speciality', 'status', 'owner']
    list_filter = ['department', 'speciality', 'status']
    search_fields = ['owner__first_name', 'owner__last_name', 'title']


class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'published_at', 'chapter', 'is_archived']
    readonly_fields = ['created_at', 'edited_at']
    list_filter = ['is_archived', 'author__user']


class MaterialAdmin(PostAdmin):
    model = models.Material


class TaskAdmin(PostAdmin):
    model = models.Task


admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.Material, MaterialAdmin)
admin.site.register(models.Chapter, ChapterAdmin)
admin.site.register(models.Task, TaskAdmin)
