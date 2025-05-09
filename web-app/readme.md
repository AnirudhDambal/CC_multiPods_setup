# Voting Application Deployment

## Deployment Options

### Option 1: Kubernetes (Production)
```bash
# Start Minikube
minikube start --driver=docker
minikube addons enable metrics-server

# Build and deploy
eval $(minikube docker-env)
docker-compose build

#note if docker-compose build doesnt provide the image specified in k8s/ deploymensts section then appropraite commands ton be wriiten
kubectl apply -f k8s/

# Get URLs
minikube service voting-app --url
minikube service result-app --url
