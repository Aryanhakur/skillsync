from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    RegisterView, LogoutView, ChangePasswordView, UserDetailView, UpdateUserView,
    SavedJobListCreateView, SavedJobDetailView, SearchHistoryListView,
    SearchHistoryCreateView, SearchHistoryClearView, SkillsHistoryListView,
    SkillsHistoryCreateView, SkillsHistoryDetailView, SkillsHistoryClearView
)

urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # User profile endpoints
    path('user/', UserDetailView.as_view(), name='user_detail'),
    path('user/update/', UpdateUserView.as_view(), name='user_update'),
    path('user/change-password/', ChangePasswordView.as_view(), name='change_password'),

    # Saved jobs endpoints
    path('saved-jobs/', SavedJobListCreateView.as_view(), name='saved_jobs'),
    path('saved-jobs/<int:pk>/', SavedJobDetailView.as_view(), name='saved_job_detail'),

    # Search history endpoints
    path('search-history/', SearchHistoryListView.as_view(), name='search_history'),
    path('search-history/create/', SearchHistoryCreateView.as_view(), name='search_history_create'),
    path('search-history/clear/', SearchHistoryClearView.as_view(), name='search_history_clear'),

    # Skills history endpoints
    path('skills-history/', SkillsHistoryListView.as_view(), name='skills_history'),
    path('skills-history/<int:pk>/', SkillsHistoryDetailView.as_view(), name='skills_history_detail'),
    path('skills-history/create/', SkillsHistoryCreateView.as_view(), name='skills_history_create'),
    path('skills-history/clear/', SkillsHistoryClearView.as_view(), name='skills_history_clear'),
]
