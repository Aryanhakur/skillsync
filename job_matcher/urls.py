from django.urls import path
from . import views

urlpatterns = [
    path('extract-skills/', views.ExtractSkillsView.as_view(), name='extract-skills'),
    path('proxy-jobs/', views.ProxyJobsView.as_view(), name='proxy-jobs'),
    path('recommended-jobs/', views.RecommendedJobsView.as_view(), name='recommended-jobs'),
    path('recommended-skills/', views.RecommendedSkillsView.as_view(), name='recommended-skills'),
    path('certifications/', views.CertificationsView.as_view(), name='certifications'),
    path('job-links/', views.JobLinksView.as_view(), name='job-links'),
]
