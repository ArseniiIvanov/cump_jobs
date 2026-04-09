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

class MyApplicationsView(generics.ListAPIView):
    """Список заявок текущего студента"""
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        student_profile = get_object_or_404(StudentProfile, user=self.request.user)
        return Application.objects.filter(student=student_profile).order_by('-applied_at')

class MyProfileView(generics.RetrieveUpdateAPIView):
    """Профиль текущего студента"""
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                'faculty': 'Не указан',
                'year_of_study': 1
            }
        )
        return profile

class MyNotificationsView(generics.ListAPIView):
    """Уведомления текущего студента"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        student_profile = get_object_or_404(StudentProfile, user=self.request.user)
        return Notification.objects.filter(student=student_profile).order_by('-created_at')[:20]

class CancelApplicationView(APIView):
    """Отмена заявки на вакансию"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, application_id):
        student_profile = get_object_or_404(StudentProfile, user=request.user)
        application = get_object_or_404(Application, id=application_id, student=student_profile)
        
        # Можно отменить только заявки в статусе 'pending' или 'reviewed'
        if application.status not in ['pending', 'reviewed']:
            return Response(
                {'error': f'Нельзя отменить заявку в статусе "{application.get_status_display()}"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Сохраняем название вакансии для уведомления
        vacancy_title = application.vacancy.title
        
        # Удаляем заявку
        application.delete()
        
        # Создаём уведомление об отмене
        Notification.objects.create(
            student=student_profile,
            title='Заявка отменена',
            message=f'Вы отменили заявку на вакансию "{vacancy_title}"',
            notification_type='status_change',
        )
        
        return Response(
            {'message': 'Заявка успешно отменена'},
            status=status.HTTP_200_OK
        )

class MyInterviewsView(generics.ListAPIView):
    """Список собеседований текущего студента"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        from .models import Interview
        student_profile = get_object_or_404(StudentProfile, user=self.request.user)
        # Получаем собеседования через заявки студента
        return Interview.objects.filter(
            application__student=student_profile,
            scheduled_date__gte=datetime.now()  # только будущие
        ).order_by('scheduled_date')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        from .serializers import InterviewSerializer
        serializer = InterviewSerializer(queryset, many=True)
        return Response(serializer.data)

# ========== Админские API ==========

class AdminVacancyListView(generics.ListCreateAPIView):
    """Список всех вакансий и создание новой (для админа)"""
    permission_classes = [IsAuthenticated]
    queryset = Vacancy.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return VacancyCreateUpdateSerializer
        return VacancyDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save()

class AdminVacancyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детали, редактирование, удаление вакансии (для админа)"""
    permission_classes = [IsAuthenticated]
    queryset = Vacancy.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return VacancyCreateUpdateSerializer
        return VacancyDetailSerializer

class AdminApplicationListView(generics.ListAPIView):
    """Список всех откликов (для админа)"""
    permission_classes = [IsAuthenticated]
    queryset = Application.objects.all().order_by('-applied_at')
    serializer_class = ApplicationSerializer

class AdminApplicationDetailView(APIView):
    """Детали отклика и изменение статуса (для админа)"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        application = get_object_or_404(Application, pk=pk)
        return Response(ApplicationSerializer(application).data)
    
    def patch(self, request, pk):
        application = get_object_or_404(Application, pk=pk)
        new_status = request.data.get('status')
        
        if new_status:
            application.status = new_status
            application.save()
            
            # Создаём уведомление студенту
            Notification.objects.create(
                student=application.student,
                title=f'Изменение статуса заявки: {application.vacancy.title}',
                message=f'Статус вашей заявки изменён на "{application.get_status_display()}"',
                notification_type='status_change',
                link=f'/dashboard/'
            )
            
            # Если статус "приглашение на собеседование" и есть данные о собеседовании
            if new_status == 'invited' and 'interview' in request.data:
                interview_data = request.data['interview']
                Interview.objects.update_or_create(
                    application=application,
                    defaults={
                        'scheduled_date': interview_data.get('scheduled_date'),
                        'location': interview_data.get('location', ''),
                        'is_online': interview_data.get('is_online', False),
                        'notes': interview_data.get('notes', '')
                    }
                )
                
                Notification.objects.create(
                    student=application.student,
                    title=f'Приглашение на собеседование: {application.vacancy.title}',
                    message=f'Вас пригласили на собеседование! Проверьте календарь.',
                    notification_type='interview_reminder',
                    link=f'/dashboard/'
                )
        
        return Response(ApplicationSerializer(application).data)

class AdminEmployerListView(generics.ListAPIView):
    """Список работодателей (для админа)"""
    permission_classes = [IsAuthenticated]
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer

class AdminCategoryListView(generics.ListAPIView):
    """Список категорий (для админа)"""
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# HTML страница админ-панели
@login_required
def admin_dashboard_view(request):
    """Админ-панель управления вакансиями"""
    # Проверка, что пользователь - админ (is_staff)
    if not request.user.is_staff:
        return redirect('/')
    return render(request, 'jobs/admin_dashboard.html')

# ========== Отзывы ==========

class ReviewEmployerListView(generics.ListAPIView):
    """Список отзывов о работодателях"""
    permission_classes = [AllowAny]
    serializer_class = ReviewEmployerSerializer
    queryset = ReviewEmployer.objects.all().order_by('-created_at')

class CreateReviewEmployerView(APIView):
    """Создание отзыва о работодателе (только для авторизованных студентов)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        student_profile = get_object_or_404(StudentProfile, user=request.user)
        employer_id = request.data.get('employer')
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')
        
        employer = get_object_or_404(Employer, id=employer_id)
        
        # Проверяем, не оставлял ли уже отзыв
        if ReviewEmployer.objects.filter(student=student_profile, employer=employer).exists():
            return Response(
                {'error': 'Вы уже оставляли отзыв о этом работодателе'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        review = ReviewEmployer.objects.create(
            student=student_profile,
            employer=employer,
            rating=rating,
            comment=comment
        )
        
        return Response(ReviewEmployerSerializer(review).data, status=status.HTTP_201_CREATED)

class ReviewStudentListView(generics.ListAPIView):
    """Список отзывов о студентах"""
    permission_classes = [AllowAny]
    serializer_class = ReviewStudentSerializer
    queryset = ReviewStudent.objects.all().order_by('-created_at')

class CreateReviewStudentView(APIView):
    """Создание отзыва о студенте (только для работодателей через админку)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Только для админов или специальных прав
        if not request.user.is_staff:
            return Response({'error': 'Доступ только для администрации'}, status=status.HTTP_403_FORBIDDEN)
        
        employer_id = request.data.get('employer')
        student_id = request.data.get('student')
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')
        
        employer = get_object_or_404(Employer, id=employer_id)
        student = get_object_or_404(StudentProfile, id=student_id)
        
        review = ReviewStudent.objects.create(
            employer=employer,
            student=student,
            rating=rating,
            comment=comment
        )
        
        return Response(ReviewStudentSerializer(review).data, status=status.HTTP_201_CREATED)

class EmployerReviewsView(generics.RetrieveAPIView):
    """Просмотр отзывов о конкретном работодателе"""
    permission_classes = [AllowAny]
    queryset = Employer.objects.all()
    serializer_class = EmployerWithReviewsSerializer

def reviews_view(request):
    """Страница отзывов о работодателях"""
    return render(request, 'jobs/reviews.html')

# HTML страницы (фронтенд)

def index_view(request):
    """Главная страница со списком вакансий"""
    return render(request, 'jobs/index.html')

def vacancy_detail_view(request, pk):
    """Страница деталей вакансии"""
    return render(request, 'jobs/vacancy_detail.html', {'vacancy_id': pk})

@login_required
def dashboard_view(request):
    """Личный кабинет студента"""
    return render(request, 'jobs/dashboard.html')

@login_required
def profile_view(request):
    """Профиль студента"""
    return render(request, 'jobs/profile.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверный логин или пароль')
    return render(request, 'jobs/login.html')

@login_required
def profile_edit_view(request):
    """Редактирование профиля студента"""
    return render(request, 'jobs/profile_edit.html')

def logout_view(request):
    logout(request)
    return redirect('/')