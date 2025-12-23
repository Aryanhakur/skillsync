# Deploying Skill Sync to Render

This guide provides step-by-step instructions for deploying the Skill Sync application (Angular frontend and Django backend) to Render.

## Prerequisites

1. A [Render](https://render.com/) account
2. Your project code pushed to a GitHub repository

## Deployment Steps

### 1. Connect Your GitHub Repository to Render

1. Log in to your Render account
2. Click on "New" and select "Blueprint" from the dropdown menu
3. Connect your GitHub account if you haven't already
4. Select the repository containing your Skill Sync project
5. Click "Apply Blueprint"

Render will automatically detect the `render.yaml` file in your repository and create the services defined in it.

### 2. Configure Environment Variables

The `render.yaml` file already includes the basic environment variables needed for deployment. However, you may need to add additional variables:

1. Go to the Dashboard in Render
2. Select each service (backend and frontend)
3. Go to the "Environment" tab
4. Add any additional environment variables needed

### 3. Monitor Deployment

1. Render will automatically build and deploy your services
2. You can monitor the build and deployment process in the "Events" tab
3. Once deployment is complete, you can access your application using the provided URLs

### 4. Database Considerations

This deployment uses SQLite, which is suitable for academic showcase purposes. For a production application with multiple users, consider migrating to PostgreSQL, which is better supported by Render.

### 5. Troubleshooting

If you encounter any issues during deployment:

1. Check the build logs in the "Events" tab
2. Ensure all required environment variables are set
3. Verify that the `build.sh` script has execute permissions
4. Check that the paths in `render.yaml` match your project structure

## Post-Deployment

After successful deployment:

1. Test all features of your application
2. Update the frontend environment.prod.ts file if the backend URL changes
3. Set up monitoring and logging as needed

## Manual Deployment (Alternative)

If you prefer to deploy manually instead of using the Blueprint feature:

### Backend Deployment

1. In Render, create a new Web Service
2. Connect to your GitHub repository
3. Configure the service:
   - Name: skill-sync-backend
   - Runtime: Python
   - Build Command: `cd pythonmodel && chmod +x build.sh && ./build.sh`
   - Start Command: `cd pythonmodel && gunicorn job_api.wsgi:application`
4. Add the required environment variables
5. Click "Create Web Service"

### Frontend Deployment

1. In Render, create a new Web Service
2. Connect to your GitHub repository
3. Configure the service:
   - Name: skill-sync-frontend
   - Runtime: Node
   - Build Command: `cd pythonmodel/job-portal-frontend && npm install && npm run build`
   - Start Command: `cd pythonmodel/job-portal-frontend && npm run serve:ssr:job-portal-frontend`
4. Add the required environment variables
5. Click "Create Web Service"
