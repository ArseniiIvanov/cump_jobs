from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db import models
from .models import (
    Vacancy, Application, StudentProfile, Notification, Interview,
    Category, Employer, ReviewEmployer, ReviewStudent
)
from .serializers import (
    VacancySerializer, VacancyDetailSerializer, VacancyCreateUpdateSerializer,
    ApplicationSerializer, CreateApplicationSerializer,
    StudentProfileSerializer, NotificationSerializer, InterviewSerializer,
    CategorySerializer, EmployerSerializer,
    ReviewEmployerSerializer, ReviewStudentSerializer, EmployerWithReviewsSerializer
)

# Create your views here.
class VacancyListView(generics.ListAPIView):
    """Список всех активных вакансий с фильтрацией"""
    serializer_class = VacancySerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Vacancy.objects.filter(status='active')
        
        # Поиск по ключевым словам
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search) |
                models.Q(requirements__icontains=search)
            )
        
        # Фильтр по категории
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Фильтр по типу работы
        work_type = self.request.query_params.get('work_type', None)
        if work_type:
            queryset = queryset.filter(work_type=work_type)
        
        return queryset

class VacancyDetailView(generics.RetrieveAPIView):
    """Детальная информация о вакансии"""
    queryset = Vacancy.objects.all()
    serializer_class = VacancyDetailSerializer
    permission_classes = [AllowAny]

class ApplyToVacancyView(APIView):
    """Подача заявки на вакансию"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = CreateApplicationSerializer(data=request.data)
        
        if serializer.is_valid():
            # Получаем или создаём профиль студента
            student_profile, created = StudentProfile.objects.get_or_create(
                user=request.user,
                defaults={
                    'faculty': 'Не указан',
                    'year_of_study': 1
                }
            )
            
            vacancy = serializer.validated_data['vacancy']
            
            # Проверяем, не подавал ли студент уже заявку
            if Application.objects.filter(student=student_profile, vacancy=vacancy).exists():
                return Response(
                    {'error': 'Вы уже подали заявку на эту вакансию'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                application = Application.objects.create(
                    student=student_profile,
                    vacancy=vacancy,
                    cover_letter=serializer.validated_data.get('cover_letter', ''),
                    resume_version=serializer.validated_data.get('resume_version')
                )
                
                # Создаём уведомление
                Notification.objects.create(
                    student=student_profile,
                    title='Заявка отправлена',
                    message=f'Ваша заявка на вакансию "{vacancy.title}" успешно отправлена',
                    notification_type='status_change',
                    link=f'/vacancy/{vacancy.id}/'
                )
                
                return Response(
                    ApplicationSerializer(application).data,
                    status=status.HTTP_201_CREATED
                )
            except IntegrityError:
                return Response(
                    {'error': 'Не удалось создать заявку'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



@login_required
def dashboard_view(request):
    """Личный кабинет студента"""
    return render(request, 'jobs/dashboard.html')