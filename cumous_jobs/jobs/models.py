from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from datetime import datetime

class Category(models.Model):
    """Категория вакансии (например: IT, администрирование, исследования)"""
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='URL')
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    
    def __str__(self):
        return self.name

class Employer(models.Model):
    """Работодатель (кафедра, отдел, компания)"""
    name = models.CharField(max_length=200, verbose_name='Название организации')
    description = models.TextField(blank=True, verbose_name='Описание')
    contact_email = models.EmailField(verbose_name='Email для связи')
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    logo = models.ImageField(upload_to='employers/', blank=True, null=True, verbose_name='Логотип')
    
    class Meta:
        verbose_name = 'Работодатель'
        verbose_name_plural = 'Работодатели'
    
    def __str__(self):
        return self.name

class StudentProfile(models.Model):
    """Профиль студента"""
    YEAR_CHOICES = [
        (1, '1 курс'),
        (2, '2 курс'),
        (3, '3 курс'),
        (4, '4 курс'),
        (5, '5 курс'),
        (6, 'Магистратура'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile', verbose_name='Пользователь')
    faculty = models.CharField(max_length=200, verbose_name='Факультет')
    year_of_study = models.IntegerField(choices=YEAR_CHOICES, verbose_name='Курс')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    resume = models.FileField(
        upload_to='resumes/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'doc'])],
        verbose_name='Резюме'
    )
    bio = models.TextField(blank=True, verbose_name='О себе')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    subscribe_notifications = models.BooleanField(default=True, verbose_name='Подписка на новые вакансии')

    class Meta:
        verbose_name = 'Профиль студента'
        verbose_name_plural = 'Профили студентов'
    
    def __str__(self):
        return f"{self.user.username} - {self.faculty}"

class Vacancy(models.Model):
    """Вакансия"""
    WORK_TYPE_CHOICES = [
        ('full_time', 'Полная занятость'),
        ('part_time', 'Частичная занятость'),
        ('internship', 'Стажировка'),
        ('remote', 'Удалённая работа'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('closed', 'Закрыта'),
        ('draft', 'Черновик'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    requirements = models.TextField(verbose_name='Требования')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='vacancies', verbose_name='Категория')
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name='vacancies', verbose_name='Работодатель')
    work_type = models.CharField(max_length=20, choices=WORK_TYPE_CHOICES, verbose_name='Тип работы')
    salary_min = models.IntegerField(blank=True, null=True, verbose_name='Зарплата от')
    salary_max = models.IntegerField(blank=True, null=True, verbose_name='Зарплата до')
    location = models.CharField(max_length=200, blank=True, verbose_name='Место работы')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def salary_display(self):
        if self.salary_min and self.salary_max:
            return f"{self.salary_min:,} - {self.salary_max:,} ₽"
        elif self.salary_min:
            return f"от {self.salary_min:,} ₽"
        elif self.salary_max:
            return f"до {self.salary_max:,} ₽"
        return "Не указана"

class Application(models.Model):
    """Заявка студента на вакансию"""
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('reviewed', 'Просмотрено'),
        ('invited', 'Приглашение на собеседование'),
        ('rejected', 'Отказ'),
        ('accepted', 'Принят'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='applications', verbose_name='Студент')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='applications', verbose_name='Вакансия')
    cover_letter = models.TextField(blank=True, verbose_name='Сопроводительное письмо')
    resume_version = models.FileField(
        upload_to='application_resumes/',
        blank=True,
        null=True,
        verbose_name='Резюме для этой заявки'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    applied_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата подачи')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-applied_at']
        unique_together = ['student', 'vacancy']  # Студент не может подать две заявки на одну вакансию
    
    def __str__(self):
        return f"{self.student.user.username} -> {self.vacancy.title}"

class Interview(models.Model):
    """Собеседование"""
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='interview', verbose_name='Заявка')
    scheduled_date = models.DateTimeField(verbose_name='Дата и время собеседования')
    location = models.CharField(max_length=300, blank=True, verbose_name='Место проведения (или ссылка)')
    notes = models.TextField(blank=True, verbose_name='Заметки')
    is_online = models.BooleanField(default=False, verbose_name='Онлайн собеседование')
    
    class Meta:
        verbose_name = 'Собеседование'
        verbose_name_plural = 'Собеседования'
    
    def __str__(self):
        return f"Собеседование: {self.application.vacancy.title} - {self.scheduled_date}"

class Notification(models.Model):
    """Уведомление для студента"""
    TYPE_CHOICES = [
        ('status_change', 'Изменение статуса заявки'),
        ('new_vacancy', 'Новая вакансия'),
        ('interview_reminder', 'Напоминание о собеседовании'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='notifications', verbose_name='Студент')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    message = models.TextField(verbose_name='Сообщение')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Тип')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    link = models.CharField(max_length=500, blank=True, verbose_name='Ссылка')
    
    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.user.username}: {self.title}"

class SavedVacancy(models.Model):
    """Избранные вакансии"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='saved_vacancies', verbose_name='Студент')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='saved_by', verbose_name='Вакансия')
    saved_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата сохранения')
    
    class Meta:
        verbose_name = 'Избранная вакансия'
        verbose_name_plural = 'Избранные вакансии'
        unique_together = ['student', 'vacancy']
    
    def __str__(self):
        return f"{self.student.user.username} сохранил {self.vacancy.title}"

class ReviewEmployer(models.Model):
    """Отзыв студента о работодателе"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='reviews_employer', verbose_name='Студент')
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name='reviews', verbose_name='Работодатель')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name='Оценка (1-5)')
    comment = models.TextField(verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Отзыв о работодателе'
        verbose_name_plural = 'Отзывы о работодателях'
    
    def __str__(self):
        return f"{self.student.user.username} -> {self.employer.name}: {self.rating}★"

class ReviewStudent(models.Model):
    """Отзыв работодателя о студенте"""
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name='reviews_student', verbose_name='Работодатель')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='reviews_employer_given', verbose_name='Студент')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name='Оценка (1-5)')
    comment = models.TextField(verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Отзыв о студенте'
        verbose_name_plural = 'Отзывы о студентах'
    
    def __str__(self):
        return f"{self.employer.name} -> {self.student.user.username}: {self.rating}★"

