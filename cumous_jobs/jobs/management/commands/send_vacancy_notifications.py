from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from jobs.models import StudentProfile, Vacancy
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Отправляет уведомления о новых вакансиях подписанным студентам'
    
    def handle(self, *args, **kwargs):
        # Получаем вакансии за последние 24 часа
        yesterday = datetime.now() - timedelta(days=1)
        new_vacancies = Vacancy.objects.filter(created_at__gte=yesterday, status='active')
        
        if not new_vacancies:
            self.stdout.write('Новых вакансий нет')
            return
        
        # Получаем подписанных студентов
        subscribed_students = StudentProfile.objects.filter(subscribe_notifications=True)
        
        for student in subscribed_students:
            # Здесь можно добавить фильтрацию по интересам студента
            # Пока отправляем всем подписанным
            
            # Создаём уведомление в БД
            from jobs.models import Notification
            Notification.objects.create(
                student=student,
                title='Новые вакансии!',
                message=f'Появилось {new_vacancies.count()} новых вакансий. Зайдите на сайт, чтобы посмотреть!',
                notification_type='new_vacancy',
                link='/'
            )
            
            # Здесь можно добавить отправку email
            # send_mail(...)
        
        self.stdout.write(self.style.SUCCESS(f'Уведомления отправлены {subscribed_students.count()} студентам'))