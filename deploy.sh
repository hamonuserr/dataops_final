#!/bin/bash
# Quick deployment script for ML Platform

set -e

echo "🚀 ML Platform Quick Deployment Script"
echo "======================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker${NC}"

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose${NC}"

# Check disk space
available_space=$(df / | tail -1 | awk '{print $4}')
if [ "$available_space" -lt 10485760 ]; then  # 10GB in KB
    echo -e "${YELLOW}⚠️  Warning: Less than 10GB free disk space${NC}"
fi
echo -e "${GREEN}✅ Disk space${NC}"

echo ""
echo "🐳 Starting Docker containers..."
echo "This may take 2-3 minutes on first run..."
echo ""

# Start services
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
services=("postgres" "mlflow" "airflow-webserver" "diabetes-service" "prometheus" "grafana")

for service in "${services[@]}"; do
    if docker-compose ps "$service" 2>/dev/null | grep -q "Up"; then
        echo -e "${GREEN}✅ $service${NC}"
    else
        echo -e "${RED}❌ $service${NC}"
    fi
done

echo ""
echo "📊 Service URLs:"
echo "=================="
echo -e "MLflow:       ${GREEN}http://localhost:5000${NC}"
echo -e "Airflow:      ${GREEN}http://localhost:8080${NC} (admin/admin)"
echo -e "JupyterHub:   ${GREEN}http://localhost:8001${NC} (admin/admin)"
echo -e "LakeFS:       ${GREEN}http://localhost:8000${NC} (admin/admin123)"
echo -e "Prometheus:   ${GREEN}http://localhost:9090${NC}"
echo -e "Grafana:      ${GREEN}http://localhost:3000${NC} (admin/admin)"
echo -e "API Health:   ${GREEN}http://localhost:8000/health${NC}"
echo ""

echo "🧪 Testing API endpoint..."
sleep 2

if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ API is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  API health check pending (may take another moment)${NC}"
fi

echo ""
echo "📚 Next steps:"
echo "1. Check logs: docker-compose logs -f"
echo "2. Create MLflow prompts: python3 create_prompts.py"
echo "3. Access web UIs at the URLs above"
echo "4. Review deployment guide: DEPLOYMENT_GUIDE.md"
echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
