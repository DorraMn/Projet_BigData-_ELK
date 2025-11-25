#!/bin/bash

# Script de test pour vérifier tous les services du projet Monitoring SaaS

echo "🔍 Vérification de l'état des services..."
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour tester un service
test_service() {
    local name=$1
    local url=$2
    local expected_code=$3
    
    if [ -z "$expected_code" ]; then
        expected_code=200
    fi
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$response" -eq "$expected_code" ]; then
        echo -e "${GREEN}✓${NC} $name - OK (HTTP $response)"
        return 0
    else
        echo -e "${RED}✗${NC} $name - ERREUR (HTTP $response, attendu $expected_code)"
        return 1
    fi
}

# Fonction pour tester avec authentification
test_service_auth() {
    local name=$1
    local url=$2
    local user=$3
    local pass=$4
    
    response=$(curl -s -o /dev/null -w "%{http_code}" -u "$user:$pass" "$url" 2>/dev/null)
    
    if [ "$response" -eq 200 ]; then
        echo -e "${GREEN}✓${NC} $name - OK (HTTP $response)"
        return 0
    else
        echo -e "${RED}✗${NC} $name - ERREUR (HTTP $response)"
        return 1
    fi
}

echo "📊 Services Web:"
test_service "Flask WebApp" "http://localhost:8000" 200
test_service "Kibana" "http://localhost:5601" 302
test_service_auth "Mongo Express" "http://localhost:8081" "admin" "admin123"

echo ""
echo "🔧 APIs:"
test_service "Elasticsearch" "http://localhost:9200" 200
test_service "Elasticsearch Health" "http://localhost:9200/_cluster/health" 200

echo ""
echo "📦 Services Docker:"
docker compose ps --format "table {{.Service}}\t{{.Status}}" | head -8

echo ""
echo "💾 MongoDB:"
doc_count=$(docker exec mongodb mongosh --quiet --eval "db.getSiblingDB('monitoring').uploads.countDocuments()" 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} MongoDB accessible - $doc_count documents dans monitoring.uploads"
else
    echo -e "${RED}✗${NC} MongoDB non accessible"
fi

echo ""
echo "🔴 Redis:"
redis_ping=$(docker exec redis redis-cli ping 2>/dev/null)
if [ "$redis_ping" = "PONG" ]; then
    echo -e "${GREEN}✓${NC} Redis accessible - PONG reçu"
else
    echo -e "${RED}✗${NC} Redis non accessible"
fi

echo ""
echo "📋 Résumé des URLs d'accès:"
echo "  • Flask WebApp:     http://localhost:8000"
echo "  • Kibana:           http://localhost:5601"
echo "  • Mongo Express:    http://localhost:8081 (admin/admin123)"
echo "  • Elasticsearch:    http://localhost:9200"
echo ""
echo "✨ Test terminé!"
