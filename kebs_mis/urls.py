"""
URL configuration for kebs_mis project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from sample_mis import views
from sample_mis.api.views import recent_activities
from sample_mis.views import sample_api, data_management, export_samples_csv, generate_label_api
from django.contrib.auth import views as auth_views

urlpatterns = [

                  path('dashboard', views.dashboard, name='dashboard'),
                  # Authentication URLs
                  path('', views.login_view, name='login'),
                  path('accounts/logout/', views.logout_view, name='logout'),
                  path('accounts/register/', views.register, name='register'),



                  # sample management
                  path('sample-submission/', views.sample_submission, name='sample_submission'),
                  path('sample-tracking/', views.sample_tracking, name='sample_tracking'),
                  path('api/samples/', views.sample_api, name='sample_api'),
                  path('sample-details/<int:sample_id>/', views.sample_details, name='sample_details'),

                  # testing and labeling
                  path('test-results/<int:sample_id>/', views.test_results_detail, name='test_results_detail'),
                  path('generate-label/<int:sample_id>/', views.generate_label, name='generate-label'),
                  path('generate-label/', views.label_generation, name='label_generation'),
                  path('download-label/<int:label_id>/', views.download_label, name='download_label'),
                  path('samples/<int:sample_id>/test/', views.test_results, name='test_results'),
                  path("generate-label/", generate_label_api, name="generate_label"),
                  # Data Management
                  path('export-csv/', views.export_samples_csv, name='export_csv'),
                  path('testing-results/', views.testing_results, name='testing_results'),

                  # API Endpoints
                  path('api/', include('sample_mis.api.urls')),
                  path('api-auth/', include('rest_framework.urls')),

                  path('samples/<int:sample_id>/test/', views.test_results, name='test_results'),
                  path('samples/<int:sample_id>/label/', views.generate_label, name='generate_label'),
                  path('sample-details/<int:sample_id>/', views.sample_details, name='sample_details'),
                  # path('generate-label/', views.label_generation, name='label_generation'),
                  path('download-label/<int:label_id>/', views.download_label, name='download_label'),
                  path('download-label/<uuid:uuid>/', views.download_label, name='download_label'),

                  path('data-management/', data_management, name='data_management'),
                  path('export-data-csv/', export_samples_csv, name='export_data_csv'),
                  path('data-management/', views.data_management, name='data_management'),
                  path('api/recent-activities/', recent_activities, name='recent_activities'),
                  path('api/samples/', sample_api, name='sample_api'),

                  path('admin/', admin.site.urls),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
