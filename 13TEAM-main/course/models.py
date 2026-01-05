from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ROLE_CHOICES = (
        ("teacher", "教師"),
        ("student", "學生"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")
    full_name = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    def __str__(self):
        return self.full_name or self.user.username


class Course(models.Model):
    name = models.CharField(max_length=100)
    semester = models.CharField(max_length=20)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    midterm = models.FloatField(null=True, blank=True)
    final = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ("student", "course")

    def average(self):
        if self.midterm is not None and self.final is not None:
            return (self.midterm + self.final) / 2
        return None


class Comment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
    )

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"
