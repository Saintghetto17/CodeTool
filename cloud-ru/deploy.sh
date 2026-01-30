#!/bin/bash

# Cloud.ru Deployment Script for Code Agent
# This script automates the deployment of Code Agent to Cloud.ru

set -e

echo "🚀 Code Agent - Cloud.ru Deployment Script"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REGISTRY="cr.cloud.ru"
REGISTRY_PATH="code-agent-registry"
IMAGE_NAME="code-agent"
IMAGE_TAG="1.0.0"
FULL_IMAGE="${REGISTRY}/${REGISTRY_PATH}/${IMAGE_NAME}:${IMAGE_TAG}"

# Functions
print_step() {
    echo -e "${BLUE}▶${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

check_requirements() {
    print_step "Checking requirements..."
    
    # Check docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found. Please install Docker first."
        exit 1
    fi
    print_success "Docker installed"
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        print_warning "kubectl not found. It's needed for Kubernetes deployment."
        echo "Install with: curl -LO https://dl.k8s.io/release/\$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    else
        print_success "kubectl installed"
    fi
    
    echo ""
}

build_image() {
    print_step "Building Docker image..."
    
    cd "$(dirname "$0")/.."
    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest .
    
    print_success "Image built successfully"
    echo ""
}

login_registry() {
    print_step "Logging into Cloud.ru Container Registry..."
    
    echo "Please enter your Cloud.ru credentials:"
    docker login ${REGISTRY}
    
    print_success "Logged in successfully"
    echo ""
}

push_image() {
    print_step "Tagging and pushing image to Cloud.ru..."
    
    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${FULL_IMAGE}
    docker tag ${IMAGE_NAME}:latest ${REGISTRY}/${REGISTRY_PATH}/${IMAGE_NAME}:latest
    
    docker push ${FULL_IMAGE}
    docker push ${REGISTRY}/${REGISTRY_PATH}/${IMAGE_NAME}:latest
    
    print_success "Image pushed successfully"
    echo ""
}

create_secrets() {
    print_step "Creating Kubernetes secrets..."
    
    if [ ! -f .env ]; then
        print_error ".env file not found. Please create it first."
        echo "Copy env.example to .env and fill in your credentials."
        exit 1
    fi
    
    # Source .env file
    export $(cat .env | xargs)
    
    # Create secret
    kubectl create secret generic code-agent-secrets \
        --from-literal=GITHUB_TOKEN="${GITHUB_TOKEN}" \
        --from-literal=GITHUB_REPO="${GITHUB_REPO}" \
        --from-literal=OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
        --from-literal=YANDEX_API_KEY="${YANDEX_API_KEY:-}" \
        --from-literal=YANDEX_FOLDER_ID="${YANDEX_FOLDER_ID:-}" \
        --from-literal=LLM_PROVIDER="${LLM_PROVIDER}" \
        --from-literal=MAX_ITERATIONS="${MAX_ITERATIONS:-5}" \
        --from-literal=LOG_LEVEL="${LOG_LEVEL:-INFO}" \
        --namespace=code-agent \
        --dry-run=client -o yaml | kubectl apply -f -
    
    print_success "Secrets created"
    echo ""
}

deploy_k8s() {
    print_step "Deploying to Kubernetes..."
    
    # Apply manifests
    kubectl apply -f k8s/deployment.yaml
    
    # Wait for deployment
    kubectl rollout status deployment/code-agent -n code-agent --timeout=5m
    
    print_success "Deployment complete"
    echo ""
}

show_status() {
    print_step "Checking deployment status..."
    echo ""
    
    echo "Pods:"
    kubectl get pods -n code-agent
    echo ""
    
    echo "Services:"
    kubectl get svc -n code-agent
    echo ""
    
    echo "Deployments:"
    kubectl get deployments -n code-agent
    echo ""
}

show_logs() {
    print_step "Recent logs:"
    kubectl logs -l app=code-agent -n code-agent --tail=20
}

# Main menu
show_menu() {
    echo ""
    echo "What would you like to do?"
    echo "1) Full deployment (build → push → deploy)"
    echo "2) Build image only"
    echo "3) Push image to registry"
    echo "4) Deploy to Kubernetes"
    echo "5) Update secrets"
    echo "6) Show status"
    echo "7) Show logs"
    echo "8) Exit"
    echo ""
}

# Main script
main() {
    check_requirements
    
    while true; do
        show_menu
        read -p "Enter your choice [1-8]: " choice
        
        case $choice in
            1)
                build_image
                login_registry
                push_image
                create_secrets
                deploy_k8s
                show_status
                ;;
            2)
                build_image
                ;;
            3)
                login_registry
                push_image
                ;;
            4)
                create_secrets
                deploy_k8s
                show_status
                ;;
            5)
                create_secrets
                ;;
            6)
                show_status
                ;;
            7)
                show_logs
                ;;
            8)
                echo "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid choice. Please try again."
                ;;
        esac
    done
}

# Run main
main

