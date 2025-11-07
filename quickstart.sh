#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Banner
echo -e "${PURPLE}"
cat << "EOF"
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║           🚀 Task Manager Pro - Quick Start                ║
║                                                            ║
║     Production DevOps Project with Vault & Keycloak       ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${BLUE}Choose deployment mode:${NC}"
echo ""
echo "  1) 🐳 Local Development (Docker Compose)"
echo "  2) ☸️  Kubernetes Cluster"
echo "  3) 📖 Show Documentation"
echo "  4) ❌ Exit"
echo ""
read -p "Select option [1-4]: " choice

case $choice in
  1)
    echo ""
    echo -e "${GREEN}=== Starting Local Development ===${NC}"
    echo ""
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
      echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
      exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
      echo -e "${RED}❌ Docker Compose not found. Please install Docker Compose first.${NC}"
      exit 1
    fi
    
    echo -e "${BLUE}📦 Starting services...${NC}"
    docker-compose up -d
    
    echo ""
    echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
    sleep 10
    
    # Wait for Vault
    echo -e "${BLUE}   Waiting for Vault...${NC}"
    until curl -s http://localhost:8200/v1/sys/health > /dev/null 2>&1; do
      sleep 2
    done
    echo -e "${GREEN}   ✓ Vault is ready${NC}"
    
    # Wait for Keycloak
    echo -e "${BLUE}   Waiting for Keycloak...${NC}"
    until curl -s http://localhost:8080 > /dev/null 2>&1; do
      sleep 2
    done
    echo -e "${GREEN}   ✓ Keycloak is ready${NC}"
    
    # Wait for Backend
    echo -e "${BLUE}   Waiting for Backend...${NC}"
    until curl -s http://localhost:8000/health > /dev/null 2>&1; do
      sleep 2
    done
    echo -e "${GREEN}   ✓ Backend is ready${NC}"
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║           ✨ Development Environment Ready! ✨            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}📍 Services:${NC}"
    echo "   • Frontend:  http://localhost:3000"
    echo "   • Backend:   http://localhost:8000"
    echo "   • API Docs:  http://localhost:8000/api/docs"
    echo "   • Vault:     http://localhost:8200 (token: root)"
    echo "   • Keycloak:  http://localhost:8080 (admin/admin)"
    echo ""
    echo -e "${BLUE}🔑 Default Credentials:${NC}"
    echo "   • Username: admin"
    echo "   • Password: admin123"
    echo ""
    echo -e "${YELLOW}⚠️  Next Steps:${NC}"
    echo "   1. Configure Keycloak realm: http://localhost:8080/admin"
    echo "      - Create realm: task-manager"
    echo "      - Create client: task-manager-api"
    echo "      - See: docs/KEYCLOAK_SETUP.md"
    echo ""
    echo "   2. Setup Vault secrets:"
    echo "      export VAULT_ADDR=http://localhost:8200"
    echo "      export VAULT_TOKEN=root"
    echo "      ./vault-config/setup-vault-with-keycloak.sh"
    echo ""
    echo "   3. Open http://localhost:3000 and login!"
    echo ""
    echo -e "${BLUE}📚 Documentation:${NC}"
    echo "   • Quick Reference:  docs/QUICK_REFERENCE.md"
    echo "   • Full Guide:       docs/DEPLOYMENT_EXTERNAL_SERVICES.md"
    echo "   • Keycloak Setup:   docs/KEYCLOAK_SETUP.md"
    echo ""
    echo -e "${BLUE}🛠️  Useful Commands:${NC}"
    echo "   • View logs:        docker-compose logs -f"
    echo "   • Stop services:    docker-compose down"
    echo "   • Restart:          docker-compose restart"
    echo "   • Connect to DB:    docker-compose exec postgres psql -U taskuser -d taskdb"
    echo ""
    ;;
    
  2)
    echo ""
    echo -e "${GREEN}=== Kubernetes Deployment ===${NC}"
    echo ""
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
      echo -e "${RED}❌ kubectl not found. Please install kubectl first.${NC}"
      exit 1
    fi
    
    # Check cluster
    if ! kubectl cluster-info &> /dev/null; then
      echo -e "${RED}❌ Cannot connect to Kubernetes cluster.${NC}"
      exit 1
    fi
    
    echo -e "${BLUE}📋 Kubernetes Cluster:${NC}"
    kubectl cluster-info
    echo ""
    
    read -p "Continue with deployment? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      exit 0
    fi
    
    # Check Vault
    echo ""
    echo -e "${BLUE}🔐 Vault Configuration${NC}"
    if [ -z "$VAULT_ADDR" ]; then
      read -p "Enter Vault address (e.g., http://192.168.1.100:8200): " VAULT_ADDR
      export VAULT_ADDR
    fi
    
    if [ -z "$VAULT_TOKEN" ]; then
      read -sp "Enter Vault token: " VAULT_TOKEN
      echo ""
      export VAULT_TOKEN
    fi
    
    # Test Vault
    if ! vault status > /dev/null 2>&1; then
      echo -e "${RED}❌ Cannot connect to Vault at $VAULT_ADDR${NC}"
      exit 1
    fi
    echo -e "${GREEN}✓ Vault connected${NC}"
    
    # Setup Vault
    echo ""
    echo -e "${BLUE}🔧 Setting up Vault secrets...${NC}"
    if [ -f "vault-config/setup-vault-with-keycloak.sh" ]; then
      chmod +x vault-config/setup-vault-with-keycloak.sh
      ./vault-config/setup-vault-with-keycloak.sh
    else
      echo -e "${YELLOW}⚠️  Vault setup script not found. Please run manually.${NC}"
    fi
    
    # Create namespace
    echo ""
    echo -e "${BLUE}📦 Creating namespace...${NC}"
    kubectl create namespace task-manager --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply manifests
    echo ""
    echo -e "${BLUE}🚀 Deploying to Kubernetes...${NC}"
    kubectl apply -f k8s/base/
    
    echo ""
    echo -e "${BLUE}⏳ Waiting for pods to be ready...${NC}"
    kubectl wait --for=condition=ready pod -l app=task-manager -n task-manager --timeout=300s || true
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              ✨ Deployment Complete! ✨                   ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}📊 Status:${NC}"
    kubectl get pods -n task-manager
    echo ""
    kubectl get svc -n task-manager
    echo ""
    kubectl get ingress -n task-manager
    echo ""
    echo -e "${BLUE}📚 Next Steps:${NC}"
    echo "   1. Check deployment: kubectl get pods -n task-manager"
    echo "   2. View logs: kubectl logs -n task-manager -l component=api --tail=100"
    echo "   3. Setup Ingress DNS"
    echo "   4. Configure Keycloak redirect URIs"
    echo ""
    echo "   See: docs/DEPLOYMENT_EXTERNAL_SERVICES.md"
    echo ""
    ;;
    
  3)
    echo ""
    echo -e "${GREEN}=== Documentation ===${NC}"
    echo ""
    echo -e "${BLUE}📚 Available Documentation:${NC}"
    echo ""
    echo "  📖 README.md"
    echo "     Main project overview and introduction"
    echo ""
    echo "  🚀 docs/QUICK_REFERENCE.md"
    echo "     Quick start guide (50 minutes)"
    echo ""
    echo "  📋 docs/DEPLOYMENT_EXTERNAL_SERVICES.md"
    echo "     Complete deployment guide with external Vault & Keycloak"
    echo ""
    echo "  🔐 docs/KEYCLOAK_SETUP.md"
    echo "     Detailed Keycloak SSO configuration"
    echo ""
    echo "  ✅ CHECKLIST.md"
    echo "     Production readiness checklist"
    echo ""
    echo "  🛠️  CHEATSHEET.md"
    echo "     All useful commands in one place"
    echo ""
    echo -e "${BLUE}📁 Project Structure:${NC}"
    echo ""
    echo "  backend/          - Python FastAPI application"
    echo "  frontend/         - React application"
    echo "  k8s/              - Kubernetes manifests"
    echo "  vault-config/     - Vault setup scripts"
    echo "  docs/             - Documentation"
    echo ""
    echo -e "${BLUE}🎓 Learn More:${NC}"
    echo ""
    echo "  • Architecture:     See README.md"
    echo "  • Local Dev:        docker-compose up -d"
    echo "  • Production:       See docs/DEPLOYMENT_EXTERNAL_SERVICES.md"
    echo "  • Troubleshooting:  See docs/DEPLOYMENT_EXTERNAL_SERVICES.md#troubleshooting"
    echo ""
    ;;
    
  4)
    echo ""
    echo -e "${BLUE}👋 Goodbye!${NC}"
    echo ""
    exit 0
    ;;
    
  *)
    echo -e "${RED}Invalid option${NC}"
    exit 1
    ;;
esac

echo -e "${PURPLE}═══════════════════════════════════════════════════════════${NC}"
echo ""
