"""
Views for the job_matcher app.

This module provides API endpoints for extracting skills from resumes,
recommending jobs, skills, and certifications, and fetching job links.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
import os
import sys
import pandas as pd
import requests
import logging
from .serializers import JobSerializer, JobLinkSerializer

# Configure logging
logger = logging.getLogger(__name__)

# Add the project root to the Python path to import main.py
sys.path.append(settings.BASE_DIR)

# Import functions from main.py with fallback implementations
try:
    from main import (
        extract_pdf_text,
        extract_skills,
        recommended_jobs,
        recommended_skills,
        get_certifications,
        get_job_links
    )
    logger.info("Successfully imported functions from main.py")
except ImportError as e:
    logger.error(f"Error importing functions from main.py: {e}")

    # Define fallback functions if imports fail
    def extract_pdf_text(path):
        """
        Fallback function to extract text from PDF.

        Args:
            path (str): Path to the PDF file

        Returns:
            str: Extracted text from the PDF
        """
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + '\n'
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""

    def extract_skills(text):
        """
        Fallback function to extract skills from text.

        Args:
            text (str): Text to extract skills from

        Returns:
            str: Comma-separated list of skills
        """
        common_skills = [
            "python", "java", "javascript", "html", "css", "react", "angular", "vue",
            "node.js", "express", "django", "flask", "spring", "hibernate", "sql",
            "mysql", "postgresql", "mongodb", "nosql", "aws", "azure", "gcp",
            "docker", "kubernetes", "jenkins", "git", "github", "gitlab", "ci/cd",
            "agile", "scrum", "jira", "confluence", "rest api", "graphql", "microservices"
        ]

        found_skills = []
        text_lower = text.lower()

        for skill in common_skills:
            if skill in text_lower:
                found_skills.append(skill)

        if not found_skills:
            found_skills = ["python", "javascript", "html", "css", "sql"]

        return ", ".join(found_skills)

    def recommended_jobs(user_skills, job_listings):
        """
        Fallback function to recommend jobs.

        Args:
            user_skills (str): User skills (unused in fallback)
            job_listings (pd.DataFrame): Job listings DataFrame

        Returns:
            pd.DataFrame: Top 5 jobs from the listings
        """
        # Suppress unused parameter warning
        _ = user_skills

        # Just return the first 5 jobs
        return job_listings.head(5)

    def recommended_skills(user_skills, job_listings, skill_number=None):
        """
        Fallback function to recommend skills.

        Args:
            user_skills (str): User skills (unused in fallback)
            job_listings (pd.DataFrame): Job listings (unused in fallback)
            skill_number (int, optional): Number of skills to return (unused in fallback)

        Returns:
            list: List of recommended skills
        """
        # Suppress unused parameter warnings
        _ = user_skills
        _ = job_listings
        _ = skill_number

        # Return default skills
        return ["python", "javascript", "react", "node.js", "sql"]

    def get_certifications(specialization):
        """
        Fallback function to get certifications.

        Args:
            specialization (str): Skill or specialization (unused in fallback)

        Returns:
            list: List of certification courses
        """
        # Suppress unused parameter warning
        _ = specialization

        # Return default certifications
        return [["Python Programming", "https://www.coursera.org/python"],
                ["Web Development", "https://www.coursera.org/webdev"]]

    def get_job_links(jobs_df):
        """
        Fallback function to get job links.

        Args:
            jobs_df (pd.DataFrame): DataFrame with job listings (unused in fallback)

        Returns:
            pd.DataFrame: Empty DataFrame with jobProvider and url columns
        """
        # Suppress unused parameter warning
        _ = jobs_df

        # Return empty DataFrame with required columns
        return pd.DataFrame(columns=['jobProvider', 'url'])


class ExtractSkillsView(APIView):
    """
    API view for extracting skills from a resume PDF file.

    Accepts a PDF file upload and returns extracted skills.
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        """
        Process a resume PDF file and extract skills.

        Args:
            request: HTTP request with resume file

        Returns:
            Response: JSON response with extracted skills or error message
        """
        # Check if resume file is provided
        if 'resume' not in request.FILES:
            logger.warning("Resume file not provided in request")
            return Response({"error": "No resume file provided"}, status=status.HTTP_400_BAD_REQUEST)

        resume_file = request.FILES['resume']
        file_path = None

        try:
            # Validate file type
            if not resume_file.name.lower().endswith('.pdf'):
                logger.warning(f"Invalid file type: {resume_file.name}")
                return Response({"error": "Only PDF files are supported"}, status=status.HTTP_400_BAD_REQUEST)

            # Create media directory if it doesn't exist
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            # Save the file temporarily
            file_path = os.path.join(settings.MEDIA_ROOT, resume_file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in resume_file.chunks():
                    destination.write(chunk)

            logger.info(f"Resume file saved temporarily at: {file_path}")

            # Extract text from PDF
            text = extract_pdf_text(file_path)
            if not text or len(text.strip()) == 0:
                raise ValueError("Could not extract text from PDF. The file may be corrupted or password-protected.")

            logger.info(f"Successfully extracted {len(text)} characters of text from PDF")

            # Extract skills from text
            skills = extract_skills(text)
            if not skills or len(skills.strip()) == 0:
                logger.warning("No skills found in the resume, using default skills")
                skills = "python, javascript, html, css, sql"
            else:
                logger.info(f"Successfully extracted skills: {skills}")

            return Response({"skills": skills}, status=status.HTTP_200_OK)

        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        finally:
            # Clean up temporary file
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"Temporary file removed: {file_path}")
                except Exception as e:
                    logger.error(f"Error removing temporary file: {str(e)}")


class RecommendedJobsView(APIView):
    """
    API view for recommending jobs based on user skills.

    Accepts user skills and returns recommended jobs sorted by similarity.
    """
    def post(self, request):
        """
        Process user skills and return recommended jobs.

        Args:
            request: HTTP request with skills data

        Returns:
            Response: JSON response with recommended jobs or error message
        """
        # Check if skills are provided
        if 'skills' not in request.data:
            logger.warning("No skills provided in request")
            return Response({"error": "No skills provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_skills = request.data['skills']
            logger.info(f"Processing job recommendations for skills: {user_skills}")

            # Read job listings from absolute path
            job_listings_path = os.path.join(settings.BASE_DIR, 'Job_listings.csv')

            # Create a sample job listings file if it doesn't exist
            if not os.path.exists(job_listings_path):
                logger.warning(f"Job listings file not found at {job_listings_path}, creating sample data")
                sample_data = {
                    'id': ['1', '2', '3'],
                    'title': ['Software Engineer', 'Data Scientist', 'Web Developer'],
                    'company': ['Tech Co', 'Data Inc', 'Web LLC'],
                    'location': ['San Francisco', 'New York', 'Remote'],
                    'description': ['Software engineering role', 'Data science position', 'Web development job'],
                    'Skills': ['python, javascript', 'python, sql, machine learning', 'html, css, javascript, react']
                }
                pd.DataFrame(sample_data).to_csv(job_listings_path, index=False)
                logger.info("Created sample job listings file")

            # Load job listings
            job_listings = pd.read_csv(job_listings_path)
            logger.info(f"Loaded {len(job_listings)} job listings")

            # Get recommended jobs
            recommended = recommended_jobs(user_skills, job_listings)
            logger.info(f"Found {len(recommended)} recommended jobs")

            # Convert to list of dictionaries for serialization
            jobs_list = recommended.to_dict('records')

            # Serialize the data
            serializer = JobSerializer(jobs_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except pd.errors.EmptyDataError:
            logger.error("Empty job listings file")
            return Response(
                {"error": "Job listings file is empty"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Error processing job recommendations: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Error processing jobs: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RecommendedSkillsView(APIView):
    """
    API view for recommending skills based on user's existing skills.

    Accepts user skills and returns recommended skills to learn.
    """
    def post(self, request):
        """
        Process user skills and return recommended skills to learn.

        Args:
            request: HTTP request with skills data

        Returns:
            Response: JSON response with recommended skills or error message
        """
        # Check if skills are provided
        if 'skills' not in request.data:
            logger.warning("No skills provided in request")
            return Response({"error": "No skills provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_skills = request.data['skills']
            skill_count = request.data.get('skill_count', None)

            if skill_count and not isinstance(skill_count, int):
                try:
                    skill_count = int(skill_count)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid skill_count value: {skill_count}, using default")
                    skill_count = None

            logger.info(f"Processing skill recommendations for skills: {user_skills}")
            logger.info(f"Requested skill count: {skill_count}")

            # Read job listings from absolute path
            job_listings_path = os.path.join(settings.BASE_DIR, 'Job_listings.csv')

            # Create a sample job listings file if it doesn't exist
            if not os.path.exists(job_listings_path):
                logger.warning(f"Job listings file not found at {job_listings_path}, creating sample data")
                sample_data = {
                    'id': ['1', '2', '3'],
                    'title': ['Software Engineer', 'Data Scientist', 'Web Developer'],
                    'company': ['Tech Co', 'Data Inc', 'Web LLC'],
                    'location': ['San Francisco', 'New York', 'Remote'],
                    'description': ['Software engineering role', 'Data science position', 'Web development job'],
                    'Skills': ['python, javascript', 'python, sql, machine learning', 'html, css, javascript, react']
                }
                pd.DataFrame(sample_data).to_csv(job_listings_path, index=False)
                logger.info("Created sample job listings file")

            # Load job listings
            job_listings = pd.read_csv(job_listings_path)
            logger.info(f"Loaded {len(job_listings)} job listings")

            # Get recommended skills
            skills = recommended_skills(user_skills, job_listings, skill_count)
            logger.info(f"Found {len(skills)} recommended skills")

            return Response({"recommended_skills": skills}, status=status.HTTP_200_OK)

        except pd.errors.EmptyDataError:
            logger.error("Empty job listings file")
            return Response(
                {"error": "Job listings file is empty"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Error processing skill recommendations: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Error processing skills: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CertificationsView(APIView):
    """
    API view for fetching certification courses based on skills or specializations.

    Accepts a specialization parameter and returns relevant certification courses.
    """
    def get(self, request):
        """
        Process specialization parameter and return certification courses.

        Args:
            request: HTTP request with specialization parameter

        Returns:
            Response: JSON response with certification courses or error message
        """
        specialization = request.query_params.get('specialization', '')

        if not specialization:
            logger.warning("Empty specialization parameter in certification request")
            return Response(
                {"error": "No specialization provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(f"Certification request received with specialization: {specialization}")

        try:
            # Check if the specialization contains multiple skills (comma-separated)
            if ',' in specialization:
                logger.info(f"Multiple skills detected in certification request: {specialization}")

                # Clean up the skills - remove empty entries and trim whitespace
                skills = [skill.strip() for skill in specialization.split(',') if skill.strip()]
                logger.info(f"Processed skills for certification: {skills}")

                # If we have more than 10 skills, limit to first 10 to avoid too many API calls
                if len(skills) > 10:
                    skills = skills[:10]
                    logger.info(f"Limited to first 10 skills: {skills}")

                # Rejoin the skills with commas for the API call
                specialization = ', '.join(skills)
                logger.info(f"Final specialization string: {specialization}")

            # Get certifications from Coursera based on the skills
            certifications = get_certifications(specialization)
            logger.info(f"Found {len(certifications)} certifications for: {specialization}")

            # Transform the data for the frontend
            serialized_data = []
            for cert in certifications:
                if not isinstance(cert, (list, tuple)) or len(cert) < 2:
                    logger.warning(f"Invalid certification data format: {cert}")
                    continue

                cert_data = {"name": cert[0], "url": cert[1]}

                # If the certification has a skill attached (3rd element), include it
                if len(cert) > 2:
                    cert_data["skill"] = cert[2]

                serialized_data.append(cert_data)

            logger.info(f"Returning {len(serialized_data)} formatted certification entries")
            return Response(serialized_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in certification request: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Error fetching certifications: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class JobLinksView(APIView):
    """
    API view for fetching job application links.

    Accepts job IDs and returns links to apply for those jobs.
    """
    def post(self, request):
        """
        Process job IDs and return job application links.

        Args:
            request: HTTP request with job IDs

        Returns:
            Response: JSON response with job links or error message
        """
        if 'jobs' not in request.data:
            logger.warning("No jobs provided in request")
            return Response({"error": "No jobs provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validate job IDs
            job_ids = request.data['jobs']
            if not isinstance(job_ids, list):
                logger.warning(f"Invalid job IDs format: {type(job_ids)}")
                return Response({"error": "Jobs must be a list of IDs"}, status=status.HTTP_400_BAD_REQUEST)

            logger.info(f"Processing job links for {len(job_ids)} jobs")

            # Create a DataFrame with the job IDs
            jobs_df = pd.DataFrame({'id': job_ids})

            # Get job links
            job_links = get_job_links(jobs_df)
            logger.info(f"Found {len(job_links)} job links")

            # Convert to list of dictionaries
            links_list = job_links.to_dict('records')

            # Serialize the data
            serializer = JobLinkSerializer(links_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching job links: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Error fetching job links: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProxyJobsView(APIView):
    """
    API view for proxying job search requests to external job APIs.

    Accepts skills, location, and page parameters and returns job listings.
    """
    def post(self, request):
        """
        Process job search parameters and return job listings from external API.

        Args:
            request: HTTP request with search parameters

        Returns:
            Response: JSON response with job listings or error message
        """
        if 'skills' not in request.data:
            logger.warning("No skills provided in request")
            return Response({"error": "No skills provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Extract and validate parameters
            skills = request.data['skills']
            if not isinstance(skills, list):
                try:
                    # Try to convert string to list
                    if isinstance(skills, str):
                        skills = [s.strip() for s in skills.split(',')]
                    else:
                        skills = [str(skills)]
                except Exception:
                    logger.warning(f"Invalid skills format: {skills}")
                    return Response({"error": "Skills must be a list or comma-separated string"},
                                   status=status.HTTP_400_BAD_REQUEST)

            location = request.data.get('location', 'Worldwide')

            try:
                page = int(request.data.get('page', 1))
                if page < 1:
                    page = 1
            except (ValueError, TypeError):
                logger.warning(f"Invalid page parameter: {request.data.get('page')}, using default")
                page = 1

            logger.info(f"Searching for jobs with skills: {skills}, location: {location}, page: {page}")

            # Check if API key is configured
            if not hasattr(settings, 'FINDWORK_API_KEY') or not settings.FINDWORK_API_KEY:
                logger.error("FINDWORK_API_KEY not configured in settings")
                return Response(
                    {"error": "Job search API key not configured"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Call FindWork API
            api_url = 'https://findwork.dev/api/jobs/'
            headers = {
                'Authorization': f"Token {settings.FINDWORK_API_KEY}"
            }
            params = {
                'search': ' '.join(skills),
                'location': location,
                'page': page
            }

            logger.info(f"Calling external API: {api_url} with params: {params}")
            response = requests.get(api_url, headers=headers, params=params, timeout=15)
            response.raise_for_status()

            # Transform and return the jobs
            jobs_data = response.json()
            results = jobs_data.get('results', [])
            logger.info(f"Found {len(results)} jobs from external API")

            return Response(results, status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling external API: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Error calling external job search API: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Unexpected error in job search: {str(e)}", exc_info=True)
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
