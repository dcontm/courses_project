from . import models
from .  import serializers
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status



class CourseViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer



class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    
    queryset = models.Lesson.objects.all()

    def check_access(self, request, lesson):
        if lesson.number != 1:
            try:
                _prev = self.queryset.get(course=lesson.course, number=(lesson.number-1))
                _progress = models.Progress.objects.get(user=request.user, lesson=_prev)
            except ObjectDoesNotExist:
                return False
            if not _progress.completed:
                return False
            else:
                return True
        return True 
    
    def list(self, request):
        course_pk = request.query_params.get('course_pk')
        queryset = self.queryset
        if course_pk is not None:
            queryset = self.queryset.filter(course__pk=course_pk)
        serializer = serializers.LessonSerializer(queryset, many=True)
        return Response(serializer.data)
        
    def retrieve(self, request, pk=None, course_pk=None):
        queryset = self.queryset.filter(pk=pk)
        lesson = get_object_or_404(queryset, pk=pk)
        if self.check_access(request, lesson):
            serializer = serializers.LessonSerializer(lesson)
            return Response(serializer.data)
        else:
            return Response('Доступ закрыт. Завершите предыдущий урок.', status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False,  methods=['get'])
    def get_progress(self, request):
        data = models.Progress.objects.filter(user=request.user)
        serializer = serializers.ProgressSerializer(data, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        lesson = models.Lesson.objects.get(pk=pk)
        data = None
        try:
            data = models.Progress.objects.get(user=request.user, lesson=lesson)
        except ObjectDoesNotExist :
            data = models.Progress.objects.create(user=request.user, lesson=lesson, open = True)
        serializer = serializers.ProgressSerializer(data)
        return Response(serializer.data)
   
    @progress.mapping.put
    def change_progress(self, request, pk=None):
        lesson = models.Lesson.objects.get(pk=pk)
        progress = models.Progress.objects.get(user=request.user, lesson=lesson)
        progress.completed = True
        progress.save()
        return Response('Урок завершен!', status=status.HTTP_200_OK) 