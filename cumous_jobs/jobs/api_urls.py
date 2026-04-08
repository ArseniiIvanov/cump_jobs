from django.urls import path
from . import views

urlpatterns = [
    path('vacancies/', views.VacancyListView.as_view(), name='vacancy-list'),
    path('vacancies/<int:pk>/', views.VacancyDetailView.as_view(), name='vacancy-detail'),
    path('apply/', views.ApplyToVacancyView.as_view(), name='apply'),
    path('my-applications/', views.MyApplicationsView.as_view(), name='my-applications'),
    path('my-profile/', views.MyProfileView.as_view(), name='my-profile'),
    path('my-notifications/', views.MyNotificationsView.as_view(), name='my-notifications'),
    path('reviews/employer/', views.ReviewEmployerListView.as_view(), name='reviews-employer'),
    path('reviews/employer/create/', views.CreateReviewEmployerView.as_view(), name='create-review-employer'),
    path('reviews/student/', views.ReviewStudentListView.as_view(), name='reviews-student'),
    path('reviews/student/create/', views.CreateReviewStudentView.as_view(), name='create-review-student'),
    path('employers/<int:pk>/reviews/', views.EmployerReviewsView.as_view(), name='employer-reviews'),
    path('my-interviews/', views.MyInterviewsView.as_view(), name='my-interviews'),
    path('cancel-application/<int:application_id>/', views.CancelApplicationView.as_view(), name='cancel-application'),  # ← новая строка
]
