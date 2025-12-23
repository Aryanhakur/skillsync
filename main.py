"""
Main module for skill extraction, job recommendation, and certification recommendation.
This module provides core functionality for the Skill Sync application.
"""
import os
import ast
import pandas as pd
import spacy
import requests
import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize spaCy model
try:
    nlp = spacy.load("output2")
except Exception as e:
    print(f"Error loading spaCy model: {e}")
    nlp = None

# Common tech skills for fallback when NLP model fails
COMMON_TECH_SKILLS = [
    "python", "java", "javascript", "html", "css", "react", "angular", "vue",
    "node.js", "express", "django", "flask", "spring", "hibernate", "sql",
    "mysql", "postgresql", "mongodb", "nosql", "aws", "azure", "gcp",
    "docker", "kubernetes", "jenkins", "git", "github", "gitlab", "ci/cd",
    "agile", "scrum", "jira", "confluence", "rest api", "graphql", "microservices",
    "machine learning", "artificial intelligence", "data science", "big data",
    "hadoop", "spark", "tensorflow", "pytorch", "keras", "nlp", "computer vision",
    "devops", "sre", "cloud computing", "serverless", "linux", "unix", "bash",
    "powershell", "c#", "c++", "ruby", "php", "swift", "kotlin", "go", "rust",
    "typescript", "jquery", "bootstrap", "sass", "less", "webpack", "babel",
    "redux", "vuex", "next.js", "nuxt.js", "gatsby", "rest",
    "oauth", "jwt", "authentication", "authorization", "security", "encryption",
    "testing", "unit testing", "integration testing", "e2e testing", "jest",
    "mocha", "chai", "selenium", "cypress", "puppeteer", "responsive design",
    "mobile development", "ios", "android", "react native", "flutter", "xamarin"
]

def extract_pdf_text(path):
    """
    Extract text from a PDF file.

    Args:
        path (str): Path to the PDF file

    Returns:
        str: Extracted text from the PDF
    """
    text = ''
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + '\n'
    return text


def extract_skills(text):
    """
    Extract skills from text using spaCy NER model or fallback to keyword matching.

    Args:
        text (str): Text to extract skills from

    Returns:
        str: Comma-separated list of skills
    """
    # If spaCy model is available, use it
    if nlp is not None:
        try:
            skills = []
            docs = nlp(text)
            for doc in docs.ents:
                skills.append(str.lower(doc.text))
            skills = list(set(skills))
            if skills:  # If skills were found
                return ', '.join(skills)
        except Exception as e:
            print(f"Error using spaCy model: {e}")
            # Fall through to the fallback method

    # Fallback method: Look for common tech skills in the text
    text_lower = text.lower()
    found_skills = []

    for skill in COMMON_TECH_SKILLS:
        if skill in text_lower:
            found_skills.append(skill)

    # If no skills found, return some default skills to avoid empty results
    if not found_skills:
        found_skills = ["python", "javascript", "html", "css", "sql"]

    return ', '.join(found_skills)


def one_hot_encode_skills(skills):
    """
    One-hot encode skills for association rule mining.

    Args:
        skills (str or pd.Series): Skills to encode

    Returns:
        pd.DataFrame: One-hot encoded skills
    """
    if isinstance(skills, str):  # If input is a single string
        skills = pd.Series([skills])  # Convert to Series

    # Split each entry by ", " and expand into separate rows
    skills_split = skills.str.get_dummies(sep=", ")
    return skills_split


def recommended_jobs(user_skills, job_listings):
    """
    Recommend jobs based on user skills using TF-IDF and cosine similarity.

    Args:
        user_skills (str): Comma-separated list of user skills
        job_listings (pd.DataFrame): DataFrame containing job listings with Skills column

    Returns:
        pd.DataFrame: Job listings sorted by similarity score
    """
    all_skills = [user_skills] + job_listings["Skills"].tolist()  # Combine user skills & job skills
    vectorizer = TfidfVectorizer()
    skill_vectors = vectorizer.fit_transform(all_skills)  # Convert text to numerical vectors
    cosine_sim = cosine_similarity(skill_vectors[0:1], skill_vectors[1:])  # Compare user skills with jobs
    job_listings["Similarity Score"] = cosine_sim[0]
    recommended_jobs = job_listings.sort_values(by="Similarity Score", ascending=False)
    return recommended_jobs


def recommended_skills(user_skills, job_listings, skill_number=None):
    """
    Recommend skills based on job listings and user's existing skills.

    Args:
        user_skills (str): Comma-separated list of user skills
        job_listings (pd.DataFrame): DataFrame containing job listings with Skills column
        skill_number (int, optional): Number of skills to recommend. Defaults to 10 if None.

    Returns:
        list: List of recommended skills
    """
    user_skills = user_skills.split(", ")
    job_listings['Skills_list'] = job_listings['Skills'].apply(lambda x: x.split(", "))
    all_job_skills = [skill for skills_list in job_listings["Skills_list"] for skill in skills_list]
    skill_counts = Counter(all_job_skills)
    missing_skills = set(skill_counts.keys()) - set(user_skills)
    recommended_skills = sorted(missing_skills, key=lambda skill: skill_counts[skill], reverse=True)

    # Return top N suggested skills
    if skill_number is None:
        return recommended_skills[:10]
    else:
        return recommended_skills[:skill_number]

def get_certifications(specialization):
    """
    Get certification courses from Coursera based on skills.

    Args:
        specialization (str): Comma-separated list of skills or a single skill

    Returns:
        list: List of courses with [title, url, skill] format
    """
    courses = []
    limit_per_skill = 3  # Limit to exactly 3 certifications per skill

    # Check if specialization contains multiple skills (comma-separated)
    if ',' in specialization:
        # Split the skills and use all of them (up to 10) for better results
        skills = [skill.strip() for skill in specialization.split(',') if skill.strip()][:10]
        print(f"Searching for certifications for multiple skills: {skills}")

        # Search for each skill and combine results, limiting to exactly 3 per skill
        for skill in skills:
            print(f"Processing skill: {skill}")
            skill_courses = search_coursera_for_skill(skill)
            print(f"Found {len(skill_courses)} courses for skill: {skill}")

            # Limit to exactly 3 courses per skill
            limited_courses = skill_courses[:limit_per_skill]
            print(f"Using {len(limited_courses)} courses for skill: {skill}")

            # Add skill name as metadata to each course
            for course in limited_courses:
                # Add the skill as the third element in the course tuple
                if len(course) == 2:
                    course_with_skill = [course[0], course[1], skill]
                    courses.append(course_with_skill)
                else:
                    courses.append(course)

        # Remove duplicates while preserving order
        unique_courses = []
        seen_titles = set()
        for course in courses:
            if course[0] not in seen_titles:
                seen_titles.add(course[0])
                unique_courses.append(course)

        print(f"Total unique courses found: {len(unique_courses)}")
        return unique_courses  # Return all unique courses (should be up to 3 per skill)
    else:
        # Single skill/specialization search
        print(f"Searching for certifications for single skill: {specialization}")
        skill_courses = search_coursera_for_skill(specialization)

        # Limit to exactly 3 courses
        limited_courses = skill_courses[:limit_per_skill]
        print(f"Returning {len(limited_courses)} courses for single skill: {specialization}")

        return limited_courses


def search_coursera_for_skill(skill):
    """
    Search Coursera for courses related to a specific skill.

    Args:
        skill (str): Skill to search for

    Returns:
        list: List of courses with [title, url] format
    """
    print(f"Searching Coursera for: {skill}")
    skill_courses = []

    if not skill or len(skill.strip()) == 0:
        print("Empty skill provided, skipping search")
        return []

    # Construct the URL with the skill as the query parameter
    url = f"https://www.coursera.org/search?query={skill}&sortBy=BEST_MATCH"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }

    try:
        print(f"Making request to: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract course links - try different class patterns as Coursera might change them
        links = soup.find_all('a', class_='cds-119 cds-113 cds-115 cds-CommonCard-titleLink css-vflzcf cds-142')

        # If no links found with the first pattern, try alternative patterns
        if not links:
            links = soup.find_all('a', class_=lambda c: c and 'CommonCard-titleLink' in c)

        # If still no links, try a more generic approach
        if not links:
            links = soup.find_all('a', href=lambda h: h and '/learn/' in h)

        print(f"Found {len(links)} potential course links")

        for link in links:
            # Try to extract course title and URL
            title = None
            if hasattr(link, 'h3') and link.h3 and link.h3.string:
                title = link.h3.string
            elif link.get('aria-label'):
                title = link.get('aria-label')
            elif link.text:
                title = link.text.strip()

            if title and link.get('href'):
                href = link['href']
                # Ensure URL is absolute
                if not href.startswith('http'):
                    href = "https://www.coursera.org" + href

                course = [title, href]
                skill_courses.append(course)

        print(f"Successfully extracted {len(skill_courses)} courses for skill: {skill}")
        return skill_courses

    except requests.exceptions.RequestException as e:
        print(f"Request error searching Coursera for {skill}: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error searching Coursera for {skill}: {e}")
        return []


def get_job_links(recommended_jobs):
    """
    Extract job application links from recommended jobs DataFrame.

    Args:
        recommended_jobs (pd.DataFrame): DataFrame containing recommended jobs with jobProviders column

    Returns:
        pd.DataFrame: DataFrame with jobProvider and url columns
    """
    job_links_df = pd.DataFrame(columns=['jobProvider', 'url'])

    if 'jobProviders' not in recommended_jobs.columns:
        print("Warning: 'jobProviders' column not found in recommended_jobs DataFrame")
        return job_links_df

    for i in recommended_jobs['jobProviders']:
        try:
            li = ast.literal_eval(i)
            row = pd.DataFrame(data=li[:2], columns=['jobProvider', 'url'])
            job_links_df = pd.concat([job_links_df, row], ignore_index=True)
        except (ValueError, SyntaxError) as e:
            print(f"Error parsing job provider data: {e}")

    return job_links_df


def fetch_paginated_jobs(api_url, params, headers=None, max_pages=5):
    """
    Fetch paginated job listings from an API.

    Args:
        api_url (str): API endpoint URL
        params (dict): Query parameters
        headers (dict, optional): Request headers
        max_pages (int, optional): Maximum number of pages to fetch. Defaults to 5.

    Returns:
        list: List of job listings
    """
    all_jobs = []
    next_page = ""  # Initialize nextPage as empty

    for page_num in range(max_pages):  # Limit number of pages to fetch
        if next_page:  # Add nextPage token only if it exists
            params["nextPage"] = next_page

        try:
            response = requests.get(api_url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()

            jobs = data.get("jobs", [])  # Extract job data
            if not jobs:
                print(f"No jobs found on page {page_num + 1}")
                break

            all_jobs.extend(jobs)
            print(f"Fetched {len(jobs)} jobs from page {page_num + 1}")

            # Get nextPage token for next request
            next_page = data.get("nextPage")  # Adjust based on API response

            if not next_page:  # Stop if no more pages
                print("No more pages available")
                break

        except requests.exceptions.RequestException as e:
            print(f"Error fetching jobs on page {page_num + 1}: {e}")
            break

    print(f"Total jobs fetched: {len(all_jobs)}")
    return all_jobs

# API configuration
API_URL = "https://jobs-api14.p.rapidapi.com/v2/list"

DEFAULT_PARAMS = {
    "query": "",
    "location": "India",
    "autoTranslateLocation": "true",
    "remoteOnly": "false",
    "employmentTypes": "fulltime;parttime;intern;contractor"
}

DEFAULT_HEADERS = {
    "x-rapidapi-key": os.environ.get('RAPIDAPI_KEY', '726bb03d58mshefcca0953ad0d7ap1b6e63jsn054dc3c55e8a'),
    "x-rapidapi-host": os.environ.get('RAPIDAPI_HOST', 'jobs-api14.p.rapidapi.com')
}


def load_job_listings(file_path="Job_listings.csv"):
    """
    Load job listings from CSV file and extract skills from descriptions.

    Args:
        file_path (str, optional): Path to the CSV file. Defaults to "Job_listings.csv".

    Returns:
        pd.DataFrame: DataFrame containing job listings with extracted skills
    """
    try:
        jobs_df = pd.read_csv(file_path)
        listings = pd.DataFrame(jobs_df)

        # Extract skills from job descriptions if not already present
        if 'Skills' not in listings.columns:
            listings['Skills'] = listings['description'].apply(lambda x: extract_skills(x))

        return listings
    except Exception as e:
        print(f"Error loading job listings: {e}")
        # Return empty DataFrame with required columns
        return pd.DataFrame(columns=['id', 'title', 'company', 'location', 'description', 'Skills'])


def main():
    """
    Main function to demonstrate the functionality of the module.
    """
    # Load job listings
    listings = load_job_listings()

    # Extract text from resume
    try:
        text = extract_pdf_text("specialised2vansh.pdf")
        skills_text = extract_skills(text)

        print('The user has the Following Skills: \n')
        for skill in skills_text.split(', '):
            print(skill)

        # Get recommended jobs
        print('\nThe Following Jobs match the user profile and are sorted by similarity: ')
        rec_jobs = recommended_jobs(skills_text, listings)
        print(rec_jobs[['id', 'title', 'Similarity Score']])

        # Get recommended skills
        print('\nThe following Skills can be added to the user resume:')
        rec_skills = recommended_skills(skills_text, listings)
        for skill in rec_skills:
            print(skill)

        # Get certifications
        courses = get_certifications(rec_jobs['title'].iloc[0] if not rec_jobs.empty else "python")
        courses_df = pd.DataFrame(data=courses, columns=['Course', 'Link', 'Skill'] if len(courses) > 0 and len(courses[0]) > 2 else ['Course', 'Link'])
        print('\nThe user can get the following certifications:')
        print(courses_df)

        # Get job links
        print("\nHere are the links to the Job listings:")
        jobs_links = get_job_links(rec_jobs)
        print(jobs_links)

    except Exception as e:
        print(f"Error in main function: {e}")


if __name__ == "__main__":
    main()
