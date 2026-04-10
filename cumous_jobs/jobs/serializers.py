from rest_framework import serializers
from .models import Category, Employer, Vacancy, Application, StudentProfile, Notification, Interview, ReviewEmployer, ReviewStudent

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = ['id', 'name', 'description', 'contact_email', 'contact_phone', 'logo']

class VacancySerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    employer_name = serializers.ReadOnlyField(source='employer.name')
    salary_display = serializers.ReadOnlyField()
    employer_average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Vacancy
        fields = ['id', 'title', 'description', 'requirements', 'category', 'category_name',
                  'employer', 'employer_name', 'work_type', 'salary_min', 'salary_max',
                  'salary_display', 'location', 'status', 'created_at', 'employer_average_rating']
    
    def get_employer_average_rating(self, obj):
        reviews = obj.employer.reviews.all()
        if reviews:
            return sum(r.rating for r in reviews) / len(reviews)
        return 0

class VacancyDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    employer = EmployerSerializer(read_only=True)
    salary_display = serializers.ReadOnlyField()
    
    class Meta:
        model = Vacancy
        fields = '__all__'

class VacancyCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления вакансий (для админа)"""
    class Meta:
        model = Vacancy
        fields = ['id', 'title', 'description', 'requirements', 'category', 'employer',
                  'work_type', 'salary_min', 'salary_max', 'location', 'status']
    
    def validate(self, data):
        # При создании проверяем наличие category и employer
        if self.instance is None:  # Это создание
            if not data.get('category'):
                raise serializers.ValidationError({"category": "Категория обязательна"})
            if not data.get('employer'):
                raise serializers.ValidationError({"employer": "Работодатель обязателен"})
        # При обновлении эти поля не обязательны
        return data

class ApplicationSerializer(serializers.ModelSerializer):
    vacancy_title = serializers.ReadOnlyField(source='vacancy.title')
    student_name = serializers.ReadOnlyField(source='student.user.get_full_name')
    student_username = serializers.ReadOnlyField(source='student.user.username')
    
    class Meta:
        model = Application
        fields = ['id', 'vacancy', 'vacancy_title', 'student', 'student_name', 'student_username',
                  'cover_letter', 'resume_version', 'status', 'applied_at', 'updated_at']
        read_only_fields = ['student', 'status', 'applied_at', 'updated_at']

class CreateApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['vacancy', 'cover_letter', 'resume_version']

class StudentProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    full_name = serializers.ReadOnlyField(source='user.get_full_name')
    email = serializers.ReadOnlyField(source='user.email')
    
    class Meta:
        model = StudentProfile
        fields = ['id', 'username', 'full_name', 'email', 'faculty', 'year_of_study', 
                  'phone', 'resume', 'bio', 'avatar', 'subscribe_notifications']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'is_read', 'created_at', 'link']

class InterviewSerializer(serializers.ModelSerializer):
    vacancy_title = serializers.ReadOnlyField(source='application.vacancy.title')
    vacancy_id = serializers.ReadOnlyField(source='application.vacancy.id')
    company_name = serializers.ReadOnlyField(source='application.vacancy.employer.name')
    
    class Meta:
        model = Interview
        fields = ['id', 'application', 'vacancy_title', 'vacancy_id', 'company_name',
                  'scheduled_date', 'location', 'notes', 'is_online']

class ReviewEmployerSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.user.get_full_name')
    student_username = serializers.ReadOnlyField(source='student.user.username')
    employer_name = serializers.ReadOnlyField(source='employer.name')
    
    class Meta:
        model = ReviewEmployer
        fields = ['id', 'student', 'student_name', 'student_username', 'employer', 'employer_name', 
                  'rating', 'comment', 'created_at']
        read_only_fields = ['student', 'created_at']

class ReviewStudentSerializer(serializers.ModelSerializer):
    employer_name = serializers.ReadOnlyField(source='employer.name')
    student_name = serializers.ReadOnlyField(source='student.user.get_full_name')
    
    class Meta:
        model = ReviewStudent
        fields = ['id', 'employer', 'employer_name', 'student', 'student_name', 
                  'rating', 'comment', 'created_at']
        read_only_fields = ['employer', 'created_at']

class EmployerWithReviewsSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    reviews = ReviewEmployerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Employer
        fields = ['id', 'name', 'description', 'contact_email', 'logo', 'average_rating', 'reviews_count', 'reviews']
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(r.rating for r in reviews) / len(reviews)
        return 0
    
    def get_reviews_count(self, obj):
        return obj.reviews.count()