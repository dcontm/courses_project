from rest_framework import serializers
from . import models



class LessonSerializer(serializers.ModelSerializer):

	class Meta:

		model =  models.Lesson
		fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):

	lessons = LessonSerializer(many=True, read_only=True)

	class Meta:

		model = models.Course
		fields = ['title', 'description', 'lessons']
    
class ProgressSerializer(serializers.ModelSerializer):

	class Meta:

		model =  models.Progress
		fields = '__all__'
