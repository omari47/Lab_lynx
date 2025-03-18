from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import DashboardStatsAPI, RecentActivityAPI

router = DefaultRouter()
router.register(r'samples', views.SampleViewSet)
router.register(r'test-results', views.SampleTestResultViewSet)
router.register(r'labels', views.LabelViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('search/samples/', views.SampleSearchAPI.as_view(), name='sample-search'),
    path('dashboard-stats/', DashboardStatsAPI.as_view(), name='dashboard_stats'),
    path('recent-activities/', RecentActivityAPI.as_view(), name='recent_activities'),
    path('dashboard-stats/', DashboardStatsAPI.as_view(), name='dashboard_stats'),
    path('recent-activities/', RecentActivityAPI.as_view(), name='recent_activities'),
]