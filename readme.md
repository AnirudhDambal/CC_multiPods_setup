# Voting Application

This is a distributed voting application that consists of multiple microservices working together to provide a complete voting system. The application allows users to cast votes and view real-time results.

## Architecture Overview

The application is built using a microservices architecture with the following components:

1. **Voting App** (`voting-app/`)
   - A Flask-based web application that allows users to cast votes
   - Runs on port 5000
   - Provides the user interface for voting

2. **Result App** (`result-app/`)
   - A Flask-based web application that displays voting results
   - Runs on port 5001
   - Shows real-time vote counts and statistics

3. **Database** (`db`)
   - PostgreSQL database (version 13)
   - Stores voting data
   - Runs on port 5432
   - Uses persistent volume for data storage

## Deployment Options

### Option 1: Docker Compose (Development)
```bash
# Build and start all services
docker-compose up --build

# Access the applications
Voting App: http://localhost:5000
Results App: http://localhost:5001
```

### Option 2: Kubernetes (Production)
```bash
# Start Minikube
minikube start --driver=docker
minikube addons enable metrics-server

# Build and deploy
eval $(minikube docker-env)
docker build -t result-app:latest ./result-app
docker build -t voting-app:latest ./voting-app

# Deploy to Kubernetes
kubectl apply -f k8s/

# Get service URLs
minikube service voting-app --url
minikube service result-app --url
```
   kubectlk get pods
   kubectl scale deployment result-app --replicas=1
## Project Structure

```
.
├── voting-app/          # Voting interface application
├── result-app/          # Results display application
├── k8s/                 # Kubernetes deployment configurations
├── docker-compose.yml   # Docker Compose configuration
├── requests.sh          # Script for making test requests
└── results.sh           # Script for checking results
```

## Development

### Prerequisites
- Docker and Docker Compose
- Kubernetes (for production deployment)
- Minikube (for local Kubernetes deployment)

### Environment Variables
- `FLASK_ENV`: Set to 'development' for local development
- `POSTGRES_USER`: Database username (default: postgres)
- `POSTGRES_PASSWORD`: Database password (default: postgres)
- `POSTGRES_DB`: Database name (default: votes)

## Testing

The project includes two shell scripts for testing:
- `requests.sh`: Simulates voting requests
- `results.sh`: Checks the voting results

## Monitoring

- Application logs are stored in `logs.txt`
- Kubernetes metrics server is enabled for production deployments

## Security Notes

- Default database credentials are used for development only
- In production, ensure to:
  - Use secure passwords
  - Enable HTTPS
  - Implement proper authentication
  - Secure database access


### Option 3:ansible (Development) 
  ansible-playbook -i hosts.ini ansible_setup.yml -K
