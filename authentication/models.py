from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class SkillsHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills_history')
    skills = models.TextField()  # Stored as JSON string
    extracted_at = models.DateTimeField(auto_now_add=True)
    resume_name = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-extracted_at']
        verbose_name_plural = "Skills histories"

    def __str__(self):
        return f"{self.user.username}'s skills - {self.extracted_at.strftime('%Y-%m-%d %H:%M')}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a user profile when a new user is created."""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the user profile when the user is saved."""
    instance.profile.save()

class SavedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    job_apply_link = models.URLField(blank=True)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job_id')
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.user.username} - {self.title} at {self.company}"

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history')
    query = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    remote_only = models.BooleanField(default=False)
    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-searched_at']
        verbose_name_plural = "Search histories"

    def __str__(self):
        return f"{self.user.username} - {self.query}"
