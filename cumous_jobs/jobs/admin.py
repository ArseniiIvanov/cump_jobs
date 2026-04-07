from django.contrib import admin
from .models import (
    Category, Employer, StudentProfile, Vacancy, Application,
    Interview, Notification, SavedVacancy, ReviewEmployer, ReviewStudent
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'contact_phone')

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'faculty', 'year_of_study', 'phone')
    list_filter = ('faculty', 'year_of_study')

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'category', 'work_type', 'status', 'created_at')
    list_filter = ('status', 'work_type', 'category', 'employer')
    search_fields = ('title', 'description')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'vacancy', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('student__user__username', 'vacancy__title')

@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('application', 'scheduled_date', 'is_online')
    list_filter = ('is_online', 'scheduled_date')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')

@admin.register(SavedVacancy)
class SavedVacancyAdmin(admin.ModelAdmin):
    list_display = ('student', 'vacancy', 'saved_at')

@admin.register(ReviewEmployer)
class ReviewEmployerAdmin(admin.ModelAdmin):
    list_display = ('student', 'employer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')

@admin.register(ReviewStudent)
class ReviewStudentAdmin(admin.ModelAdmin):
    list_display = ('employer', 'student', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')