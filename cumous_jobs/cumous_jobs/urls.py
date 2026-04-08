"""
URL configuration for cumous_jobs project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Импортируем views из jobs для фронтенда
from jobs import views as jobs_views

schema_view = get_schema_view(
    openapi.Info(
        title="Campus Jobs API",
        default_version='v1',
        description="API для поиска работы и стажировок в кампусе",
        contact=openapi.Contact(email="support@campusjobs.ru"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-panel/', jobs_views.admin_dashboard_view, name='admin_dashboard'),
    path('api/admin/', include('jobs.admin_api_urls')),
    
    # API (префикс /api/)
    path('api/', include('jobs.api_urls')),  # создадим отдельный файл для API
    
    # Фронтенд страницы (без префикса)
    path('', jobs_views.index_view, name='index'),
    path('vacancy/<int:pk>/', jobs_views.vacancy_detail_view, name='vacancy_detail'),
    path('dashboard/', jobs_views.dashboard_view, name='dashboard'),
    path('profile/', jobs_views.profile_view, name='profile'),
    path('profile/edit/', jobs_views.profile_edit_view, name='profile_edit'),
    path('login/', jobs_views.login_view, name='login'),
    path('logout/', jobs_views.logout_view, name='logout'),
    path('reviews/', jobs_views.reviews_view, name='reviews'),

    # Документация
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)