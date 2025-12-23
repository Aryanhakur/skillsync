# Skill Sync - Job Matching Platform

A platform that extracts skills from resumes and matches them with real-time job listings.

## Features

- Resume skill extraction
- Real-time job matching using RapidAPI
- Recommended skills based on job market trends
- Certification recommendations
- User authentication and history tracking

## Setup Instructions

### Backend Setup

1. Install Python dependencies:
   ```bash
   cd pythonmodel
   pip install -r requirements.txt
   ```

2. Configure environment variables:
   - Copy the `.env.example` file to `.env`
   - Update the API keys and other settings as needed

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Start the Django server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. Install Node.js dependencies:
   ```bash
   cd job-portal-frontend
   npm install
   ```

2. Start the Angular development server:
   ```bash
   ng serve
   ```

## Environment Variables

The application uses environment variables for configuration and API keys. These are stored in:

- Backend: `.env` file in the project root
- Frontend: `environment.ts` and `environment.prod.ts` files

### Important Environment Variables

- `RAPIDAPI_KEY`: Your RapidAPI key for job fetching
- `RAPIDAPI_HOST`: The RapidAPI host (default: jobs-api14.p.rapidapi.com)
- `FINDWORK_API_KEY`: Your FindWork API key (if used)
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to 'True' for development, 'False' for production

## API Usage Monitoring

The application includes API usage monitoring to help track and manage API calls:

- Frontend: Tracks API calls in localStorage
- Backend: Logs API calls to the console

## Caching

To reduce API calls and improve performance, the application implements caching:

- Job search results are cached for 1 hour by default
- Fallback job results are cached for 2 hours
- Cache duration can be configured in the environment settings

## Security Best Practices

- API keys are stored in environment variables, not hardcoded
- Sensitive data is not exposed to the frontend
- Authentication is required for sensitive operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
