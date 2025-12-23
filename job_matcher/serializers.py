from rest_framework import serializers

class JobSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    company = serializers.CharField()
    location = serializers.CharField()
    description = serializers.CharField()
    Skills = serializers.CharField()
    Similarity_Score = serializers.FloatField()
    employment_type = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    job_apply_link = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    employer_logo = serializers.CharField(required=False, allow_null=True, allow_blank=True)

class CertificationSerializer(serializers.Serializer):
    name = serializers.CharField()
    url = serializers.CharField()

class JobLinkSerializer(serializers.Serializer):
    jobProvider = serializers.CharField()
    url = serializers.CharField()
