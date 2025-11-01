from django.db import models


class Course(models.Model):
    course_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    teacher = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.course_id} - {self.name}"


class Enrollment(models.Model):
    student = models.CharField(max_length=50)  # 記錄學生姓名
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    midterm_score = models.FloatField(null=True, blank=True)
    final_score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.student} - {self.course.name}"
