from courses.models import Faculty,Department,Course,\
    CourseMember,Task,Grade,Chapter,Attachment,StudentWork
from django.contrib.auth.models import User, Group
from rest_framework import serializers


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ('title', 'description')


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('title', 'description', 'faculty')


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('title', 'description', 'department','status','created_at')


class CourseMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMember
        fields = ('course', 'status')


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('title', 'chapter', 'content',
                  'max_grade', 'created_at', 'edited_at',
                  'post_date', 'deadline')


class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ('title', 'description', 'course')


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ('task', 'file')


class StudentWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentWork
        fields = ('task', 'answer', 'status', 'course_member')


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ('work', 'description', 'amount')