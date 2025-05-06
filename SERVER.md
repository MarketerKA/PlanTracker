# Server Deployment Instructions

## Prerequisites

- A server with Docker and Docker Compose installed
- SSL certificates for HTTPS
- GitHub repository with CI/CD setup

## Initial Setup

1. SSH into your server:
   ```
   ssh user@158.160.23.164
   ```

2. Create a deployment directory:
   ```
   mkdir -p $HOME/PlanTracker
   cd $HOME/PlanTracker
   ```

3. Clone the repository (or create the files manually):
   ```
   git clone https://github.com/yourusername/PlanTracker.git .
   ```

4. Create the required directories:
   ```
   mkdir -p nginx/conf.d nginx/ssl nginx/www
   ```

5. Create a `.env` file with your configurations:
   ```
   GITHUB_REPOSITORY=yourusername/PlanTracker
   SECRET_KEY=your_secret_key_here
   TELEGRAM_BOT_TOKEN=your_telegram_token_here
   ```

6. Set up SSL certificates:
   ```
   # Copy your SSL certificates
   cp /path/to/cert.pem nginx/ssl/
   cp /path/to/key.pem nginx/ssl/
   ```

7. Make the deployment script executable:
   ```
   chmod +x deploy.sh
   ```

## Automatic Deployment

The CI/CD workflow will automatically:
1. Test the code
2. Build Docker images
3. Push the images to GitHub Container Registry
4. Deploy to your server by running the `deploy.sh` script

## GitHub Secrets Required

Add these secrets to your GitHub repository:
- `SSH_USERNAME`: Your server SSH username
- `SSH_PRIVATE_KEY`: Your SSH private key for the server
- `SECRET_KEY`: App secret key
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token

## Manual Deployment

If you need to manually deploy:
```
cd $HOME/PlanTracker
./deploy.sh
```

## Troubleshooting

If you encounter issues:
1. Check Docker logs: `docker logs plantracker-frontend`
2. Check NGINX logs: `docker logs plantracker-nginx`
3. Ensure all environment variables are set correctly
4. Verify Docker images were pulled successfully: `docker images` 