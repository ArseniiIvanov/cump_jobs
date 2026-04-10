from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from jobs.models import Category, Employer, StudentProfile, Vacancy

class Command(BaseCommand):
    help = 'Заполняет БД тестовыми данными'

    def handle(self, *args, **kwargs):
        # Создаём категории
        categories = [
            ('IT и программирование', 'it'),
            ('Администрирование', 'admin'),
            ('Исследования', 'research'),
            ('Преподавание', 'teaching'),
            ('Маркетинг', 'marketing'),
        ]
        
        for name, slug in categories:
            cat, created = Category.objects.get_or_create(name=name, slug=slug)
            if created:
                self.stdout.write(f'✅ Создана категория: {name}')
        
        # Создаём работодателей
        employers_data = [
            ('IT-отдел университета', 'Разработка и поддержка сайтов и систем', 'it@university.ru', '+7(495)123-45-67'),
            ('Библиотека', 'Работа с документами и студентами', 'library@university.ru', '+7(495)234-56-78'),
            ('НИИ прикладных исследований', 'Научные проекты', 'research@university.ru', '+7(495)345-67-89'),
        ]
        
        employers = []
        for name, desc, email, phone in employers_data:
            emp, created = Employer.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'contact_email': email,
                    'contact_phone': phone
                }
            )
            employers.append(emp)
            if created:
                self.stdout.write(f'✅ Создан работодатель: {name}')
        
        # Создаём тестового студента
        user, created = User.objects.get_or_create(
            username='student',
            defaults={
                'email': 'student@example.com',
                'first_name': 'Иван',
                'last_name': 'Петров'
            }
        )
        if created:
            user.set_password('student123')
            user.save()
            self.stdout.write('✅ Создан пользователь: student (пароль: student123)')
        
        student, created = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                'faculty': 'Факультет информационных технологий',
                'year_of_study': 3,
                'phone': '+7(916)123-45-67',
                'bio': 'Ищу стажировку в IT сфере'
            }
        )
        if created:
            self.stdout.write('✅ Создан профиль студента')
        
        # Создаём вакансии
        vacancies_data = [
            ('Ассистент разработчика Python', employers[0], 'IT и программирование', 'part_time',
             'Помощь в разработке внутренних сервисов университета. Отличная возможность получить реальный опыт в коммерческой разработке.',
             'Знание Python, Django, SQL. Базовое понимание HTML/CSS.', 30000, 50000),
            ('Помощник библиотекаря', employers[1], 'Администрирование', 'part_time',
             'Работа с электронным и бумажным каталогами, помощь студентам в поиске литературы.',
             'Внимательность, знание MS Office, ответственность.', 20000, 25000),
            ('Лаборант-исследователь', employers[2], 'Исследования', 'internship',
             'Участие в научных проектах по анализу данных. Работа с реальными исследовательскими задачами.',
             'Аналитическое мышление, базовое знание статистики, желание учиться.', 15000, 25000),
            ('Ассистент преподавателя', employers[0], 'Преподавание', 'part_time',
             'Ведение семинарских занятий, проверка студенческих работ, помощь в подготовке материалов.',
             'Отличное знание Python, коммуникабельность, опыт обучения приветствуется.', 40000, 60000),
            ('SMM-менеджер', employers[1], 'Маркетинг', 'remote',
             'Ведение социальных сетей библиотеки: ВКонтакте, Telegram. Создание контента.',
             'Опыт работы с соцсетями, базовые навыки дизайна (Canha/Photoshop), грамотная речь.', 25000, 35000),
        ]
        
        for title, emp, cat_name, work_type, desc, req, sal_min, sal_max in vacancies_data:
            cat = Category.objects.get(name=cat_name)
            vac, created = Vacancy.objects.get_or_create(
                title=title,
                employer=emp,
                defaults={
                    'description': desc,
                    'requirements': req,
                    'category': cat,
                    'work_type': work_type,
                    'salary_min': sal_min,
                    'salary_max': sal_max,
                    'location': 'Москва, ул. Студенческая, д.1',
                    'status': 'active'
                }
            )
            if created:
                self.stdout.write(f'✅ Создана вакансия: {title}')
        
        self.stdout.write(self.style.SUCCESS('\n🎉 База данных успешно заполнена тестовыми данными!'))
        self.stdout.write(self.style.SUCCESS('👤 Логин: student, Пароль: student123'))