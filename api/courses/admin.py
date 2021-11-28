from django.contrib import admin
from . import models


class DepartmentAdmin(admin.ModelAdmin):
    model = models.Department

    list_display = ['title', 'abbreviation', 'faculty']
    list_filter = ['faculty__abbreviation']
    search_fields = ['abbreviation']


class FacultyAdmin(admin.ModelAdmin):
    model = models.Faculty

    list_display = ['abbreviation', 'title']
    search_fields = ['abbreviation']


class GroupAdmin(admin.ModelAdmin):
    model = models.Group

    list_display = ['name', 'study_year', 'department', 'speciality']
    list_filter = ['study_year', 'department__abbreviation', 'speciality__title']
    search_fields = ['name']


class SpecialityAdmin(admin.ModelAdmin):
    model = models.Speciality

    list_display = ['title', 'code']
    search_fields = ['title', 'code']


class PositionAdmin(admin.ModelAdmin):
    model = models.Position
    search_fields = ['name']


class DegreeAdmin(admin.ModelAdmin):
    model = models.Degree
    search_fields = ['name']


admin.site.register(models.Faculty, FacultyAdmin)
admin.site.register(models.Department, DepartmentAdmin)
admin.site.register(models.Speciality, SpecialityAdmin)
admin.site.register(models.Position, PositionAdmin)
admin.site.register(models.Degree, DegreeAdmin)
admin.site.register(models.Group, GroupAdmin)



