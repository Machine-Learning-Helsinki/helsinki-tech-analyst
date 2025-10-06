#!/usr/bin/env bash
set -e

echo "🚀 Setting up development or production environment"

# Prompt for environment
read -r -p "Is this setup for production or development? [production/development]: " ENV_TYPE
ENV_TYPE=$(echo "${ENV_TYPE:-development}" | tr '[:upper:]' '[:lower:]')

# Function: Install Docker
install_docker() {
    echo "🔍 Checking if Docker is installed..."
    if ! command -v docker >/dev/null 2>&1; then
        echo "🐳 Docker not found. Installing Docker..."

        # Remove conflicting containerd
        sudo apt-get remove -y containerd containerd.io || true
        sudo apt-get update

        if [ -x "$(command -v apt-get)" ]; then
            echo "🟢 Debian-based system detected."
            sudo apt-get install -y ca-certificates curl gnupg lsb-release
            sudo mkdir -p /etc/apt/keyrings
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
            echo \
              "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
              https://download.docker.com/linux/ubuntu \
              $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        elif [ -x "$(command -v yum)" ]; then
            echo "🟠 Red Hat-based system detected."
            sudo yum install -y docker
        else
            echo "❌ Unsupported OS. Please install Docker manually."
            exit 1
        fi

        sudo systemctl enable docker
        sudo systemctl start docker
        echo "✅ Docker installed successfully."
    else
        echo "✅ Docker is already installed."
    fi
}

# Run Docker installation check
install_docker

# Environment setup
if [[ "$ENV_TYPE" =~ ^(production|prod|p)$ ]]; then
    echo "🌍 Production environment selected."
    mkdir -p ./dags ./logs ./plugins
    sudo chown -R 50000:0 ./dags ./logs ./plugins

    DOCKER_COMPOSE_FILE="./docker/docker-compose.yaml"
    if [ -f "$DOCKER_COMPOSE_FILE" ]; then
        echo "📦 Using compose file: $DOCKER_COMPOSE_FILE"
        if docker compose version >/dev/null 2>&1; then
            docker compose -f "$DOCKER_COMPOSE_FILE" down -v
            docker compose -f "$DOCKER_COMPOSE_FILE" up -d --build
        else
            docker-compose -f "$DOCKER_COMPOSE_FILE" down -v
            docker-compose -f "$DOCKER_COMPOSE_FILE" up -d --build
        fi
    else
        echo "⚠️ Compose file not found at $DOCKER_COMPOSE_FILE, using default."
        if docker compose version >/dev/null 2>&1; then
            docker compose down -v
            docker compose up -d --build
        else
            docker-compose down -v
            docker-compose up -d --build
        fi
    fi
else
    echo "💻 Development environment selected."
    sudo apt-get install -y git docker-compose-plugin
    echo "✅ Development environment setup complete."
fi
