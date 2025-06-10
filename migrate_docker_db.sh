#!/bin/bash
# Run migrations inside Docker containers

echo "🐳 Migrating Docker databases..."

# Dev container
if docker ps | grep -q offer-creator-dev; then
    echo "Migrating dev container..."
    docker cp scripts/standardize-schema.py offer-creator-dev:/tmp/
    docker exec offer-creator-dev python /tmp/standardize-schema.py
fi

# Staging container  
if docker ps | grep -q offer-creator-staging; then
    echo "Migrating staging container..."
    docker cp scripts/standardize-schema.py offer-creator-staging:/tmp/
    docker exec offer-creator-staging python /tmp/standardize-schema.py
fi

echo "✅ Docker migrations complete"
