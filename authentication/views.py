from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .serializers import (
    UserSerializer, RegisterSerializer, ChangePasswordSerializer,
    UpdateUserSerializer, SavedJobSerializer, SearchHistorySerializer,
    SkillsHistorySerializer
)
from .models import SavedJob, SearchHistory, SkillsHistory

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.get_object()
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({"old_password": ["Wrong password."]},
                            status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({"detail": "Password updated successfully"},
                        status=status.HTTP_200_OK)

class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

class UpdateUserView(generics.UpdateAPIView):
    serializer_class = UpdateUserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

class SavedJobListCreateView(generics.ListCreateAPIView):
    serializer_class = SavedJobSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SavedJobDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = SavedJobSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user)

class SearchHistoryListView(generics.ListAPIView):
    serializer_class = SearchHistorySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return SearchHistory.objects.filter(user=self.request.user)

class SearchHistoryCreateView(generics.CreateAPIView):
    serializer_class = SearchHistorySerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SearchHistoryClearView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request):
        SearchHistory.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SkillsHistoryListView(generics.ListAPIView):
    serializer_class = SkillsHistorySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return SkillsHistory.objects.filter(user=self.request.user)

class SkillsHistoryCreateView(generics.CreateAPIView):
    serializer_class = SkillsHistorySerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SkillsHistoryDetailView(generics.RetrieveAPIView):
    serializer_class = SkillsHistorySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return SkillsHistory.objects.filter(user=self.request.user)

class SkillsHistoryClearView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request):
        SkillsHistory.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
