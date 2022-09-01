from django.db import models
from django.conf import settings

# Create your models here.


class Course(models.Model):
    
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.title

class Lesson(models.Model):

    title = models.CharField(max_length=100)
    number = models.IntegerField(blank=True, null=True)
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Progress(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='progress', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='lesson', on_delete=models.CASCADE)
    open = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'lesson']

    def __str__(self):
        return self.lesson.title
