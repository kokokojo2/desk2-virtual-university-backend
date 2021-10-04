from django.db import models
from django.core import validators


class Faculty(models.Model):
    title = models.CharField(max_length=63,
                             unique=True,
                             validators=[validators.MinLengthValidator(2,'Please enter 2 or more characters')])
    description = models.TextField(null=True,
                                   #validators=[validators.MinLengthValidator(2, 'Please enter 2 or more characters')]
                                   )

    def __str__(self):
        return self.title


class Department(models.Model):
    title = models.CharField(max_length=63,
                             unique=True,
                             validators=[validators.MinLengthValidator(2,'Please enter 2 or more characters')])
    description = models.TextField(null=True,
                                   #validators=[validators.MinLengthValidator(2, 'Please enter 2 or more characters')]
                                   )
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Course(models.Model):
    title = models.CharField(max_length=127,
                             unique=False,
                             validators=[validators.MinLengthValidator(2,'Please enter 2 or more characters')])
    description = models.TextField(null=True,
                                   #validators=[validators.MinLengthValidator(2, 'Please enter 2 or more characters')]
                                   )
    department = models.ForeignKey(Department,on_delete=models.CASCADE)
    STATUSES = (
        ('O', 'Ongoing'),
        ('A', 'Archived'),
    )
    status = models.CharField(max_length=1, choices=STATUSES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CourseMember(models.Model):
    # user = models.ForeignKey(User,on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    STATUSES = (
        ('S', 'Student'),
        ('T', 'Teacher'),
        ('O', 'Owner'),
        ('A', 'Auditor'),
    )
    status = models.CharField(max_length=1, choices=STATUSES)


class Chapter(models.Model):
    title = models.CharField(max_length=31,
                             validators=[validators.MinLengthValidator(3,'Please enter 3 or more characters')])
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Task(models.Model):
    title = models.CharField(max_length=63,
                             validators=[validators.MinLengthValidator(4,'Please enter 4 or more characters')])
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    content = models.TextField()
    # author = models.ForeignKey(Teacher,on_delete=models.CASCADE)
    max_grade = models.PositiveSmallIntegerField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    post_date = models.DateTimeField()
    deadline = models.DateTimeField()

    def __str__(self):
        return self.title


class Attachment(models.Model):
    # task = models.ForeignKey(Task,on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')

    def __str__(self):
        return self.file.name


class StudentWork(models.Model):
    task = models.ForeignKey(Task,on_delete=models.CASCADE)
    # course_member = models.ForeignKey(CourseMember,on_delete=models.CASCADE)
    answer = models.TextField(null=True)
    STATUSES = (
        ('A', 'Assigned'),
        ('S', 'Submitted'),
        ('D', 'Deadline passed'),
        ('G', 'Graded'),
    )
    status = models.CharField(max_length=1, choices=STATUSES)
    # student_work.get_status_display()

    def __str__(self):
        return self.get_status_display()


class Grade(models.Model):
    description = models.CharField(max_length=127)
    work = models.ForeignKey(StudentWork, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
       # validators=[validators.MaxValueValidator(work.task.max_grade,'Grade can not be greater than maximum grade')]
    )
    # grader = models.ForeignKey(Teacher,on_delete=models.CASCADE)

