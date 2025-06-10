#!/bin/bash
# Deploy to DigitalOcean Script
# Takes the staging instance and deploys it to DigitalOcean

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}DigitalOcean Deployment Script${NC}"
echo -e "${CYAN}==============================${NC}"
echo ""

# Check if staging is running and tested
echo -e "${YELLOW}Pre-deployment checks...${NC}"

# 1. Check staging is running
if ! docker ps | grep -q offer-creator-staging; then
    echo -e "${RED}❌ Staging instance not running!${NC}"
    echo "Run: ./scripts/two-stage-manager.sh start-staging"
    exit 1
fi

# 2. Run final tests on staging
echo -e "${BLUE}Running final tests on staging...${NC}"
if ! ./scripts/two-stage-manager.sh test-staging; then
    echo -e "${RED}❌ Staging tests failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Staging instance validated${NC}"

# 3. Create deployment package
echo -e "\n${YELLOW}Creating deployment package...${NC}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DEPLOY_DIR="deploy_${TIMESTAMP}"
mkdir -p $DEPLOY_DIR

# Copy necessary files
echo "Copying application files..."
cp -r app $DEPLOY_DIR/
cp -r core_app $DEPLOY_DIR/
cp -r templates $DEPLOY_DIR/
cp -r static $DEPLOY_DIR/
cp -r deployment $DEPLOY_DIR/
cp requirements.txt $DEPLOY_DIR/
cp run_flask_app.py $DEPLOY_DIR/
cp Procfile $DEPLOY_DIR/

# Create production config
cat > $DEPLOY_DIR/.env << EOF
FLASK_ENV=production
FLASK_DEBUG=0
GEMINI_API_KEY=${GEMINI_API_KEY}
DATABASE_URL=\${DATABASE_URL}
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
EOF

# Create app.yaml for DigitalOcean App Platform
cat > $DEPLOY_DIR/app.yaml << EOF
name: offer-creator-crm
region: sfo
services:
- name: web
  github:
    repo: endersclarity/offer-creator
    branch: main
    deploy_on_push: true
  build_command: pip install -r requirements.txt
  run_command: python run_flask_app.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 5000
  routes:
  - path: /
  envs:
  - key: FLASK_ENV
    value: production
  - key: PYTHONUNBUFFERED
    value: "1"
  - key: GEMINI_API_KEY
    type: SECRET
    value: ${GEMINI_API_KEY}
databases:
- name: offer-creator-db
  engine: PG
  version: "13"
  size: db-s-dev-database
  num_nodes: 1
EOF

echo -e "${GREEN}✅ Deployment package created: $DEPLOY_DIR${NC}"

# 4. Show deployment instructions
echo -e "\n${CYAN}Deployment Instructions:${NC}"
echo -e "${CYAN}=======================${NC}"
echo ""
echo "Option 1: DigitalOcean App Platform (Recommended)"
echo "  1. Push code to GitHub:"
echo "     git add ."
echo "     git commit -m 'Deploy staging to production'"
echo "     git push origin main"
echo ""
echo "  2. Create app on DigitalOcean:"
echo "     doctl apps create --spec $DEPLOY_DIR/app.yaml"
echo ""
echo "  3. Or use the web interface:"
echo "     https://cloud.digitalocean.com/apps/new"
echo ""
echo "Option 2: DigitalOcean Droplet (Manual)"
echo "  1. Create Ubuntu droplet"
echo "  2. SSH into droplet"
echo "  3. Install Python 3.11 and dependencies"
echo "  4. Copy $DEPLOY_DIR to droplet"
echo "  5. Run: python run_flask_app.py"
echo ""
echo -e "${YELLOW}Important: Set environment variables in DigitalOcean!${NC}"
echo "  - GEMINI_API_KEY"
echo "  - DATABASE_URL (if using managed database)"
echo "  - SECRET_KEY (use generated one from .env)"
echo ""
echo -e "${GREEN}Deployment package ready in: $DEPLOY_DIR/${NC}"