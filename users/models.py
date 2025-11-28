from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('SENIOR_INSTRUCTOR', 'Senior Instructor'),
        ('ADJUTANT', 'Adjutant'),
        ('SCHOOL_SERGEANT_MAJOR', 'School Sergeant Major'),
        ('CLASS_COMMANDER', 'Class Commander'),
        ('STUDENT', 'Student'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)

    def user_photo_path(instance, filename):
        uid = instance.id if instance and instance.id else 'unknown'
        return f'uploads/users/user_{uid}/{filename}'

    # allow any user to have a profile photo
    photo = models.FileField(upload_to=user_photo_path, null=True, blank=True)

class Class(models.Model):
    name = models.CharField(max_length=50)  # For storing class names like 'nduk-ict-02'
    class_commander = models.OneToOneField(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='commanded_class',
        limit_choices_to={'role': 'CLASS_COMMANDER'}
    )

    def __str__(self):
        return self.name

class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    class_group = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True)
    is_suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(null=True, blank=True)
    suspended_at = models.DateTimeField(null=True, blank=True)
    suspended_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='suspended_students')

    def student_photo_path(instance, filename):
        # store under media/uploads/students/user_<id>/filename
        user_id = instance.user.id if instance.user and instance.user.id else 'unknown'
        return f'uploads/students/user_{user_id}/{filename}'

    # Use FileField to avoid Pillow dependency in development; accepts images or files.
    photo = models.FileField(upload_to=student_photo_path, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.class_group}"

    class Meta:
        ordering = ['user__username']
