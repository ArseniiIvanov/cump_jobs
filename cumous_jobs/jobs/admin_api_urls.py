from django.urls import path
from . import views

urlpatterns = [
    path('vacancies/', views.AdminVacancyListView.as_view(), name='admin-vacancies'),
    path('vacancies/<int:pk>/', views.AdminVacancyDetailView.as_view(), name='admin-vacancy-detail'),
    path('applications/', views.AdminApplicationListView.as_view(), name='admin-applications'),
    path('applications/<int:pk>/', views.AdminApplicationDetailView.as_view(), name='admin-application-detail'),
    path('employers/', views.AdminEmployerListView.as_view(), name='admin-employers'),
    path('categories/', views.AdminCategoryListView.as_view(), name='admin-categories'),
]