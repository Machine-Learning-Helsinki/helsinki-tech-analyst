
# Installing all the required packages for the development environment

echo "Checking if The user has the docker installed or not"

command -v docker >/dev/null 2>&1 || { echo >&2 "Docker is not installed. Aborting."; exit 1; }

#!/usr/bin/env bash
echo "Here we will installed all the packages required for the development environment"

# Prompt for environment
read -r -p "Is this setup for production or development? [production/development]: " ENV_TYPE
ENV_TYPE=$(echo "${ENV_TYPE:-development}" | tr '[:upper:]' '[:lower:]')

if [[ "$ENV_TYPE" == "production" || "$ENV_TYPE" == "prod" || "$ENV_TYPE" == "p" ]]; then
  echo "Production environment selected"
  EXTRA_PKGS=""
  DOCKER_COMPOSE_FILE="./docker/docker-compose.yaml"
  if [ -f "$DOCKER_COMPOSE_FILE" ]; then
    # Prefer the docker compose plugin when available
    if docker compose version >/dev/null 2>&1; then
      docker compose -f "$DOCKER_COMPOSE_FILE" down -v
      docker compose -f "$DOCKER_COMPOSE_FILE" up -d --build
    else
      docker-compose -f "$DOCKER_COMPOSE_FILE" down -v
      docker-compose -f "$DOCKER_COMPOSE_FILE" up -d --build
    fi
  else
    echo "Compose file not found at $DOCKER_COMPOSE_FILE, falling back to default docker-compose.yml"
    if docker compose version >/dev/null 2>&1; then
      docker compose down -v
      docker compose up -d --build
    else
      docker-compose down -v
      docker-compose up -d --build
    fi
  fi
  
else
  echo "Development environment selected"
  # Add development helpers (adjust as needed)
  EXTRA_PKGS="docker-compose-plugin git"
fi

# ## Installing pip 
echo "Checking if docker is installed or not"

command -v docker >/dev/null 2>&1 || { echo >&2 "Docker is not installed. Proceeding to install.";  }

# Docker installation here

if [ -x "$(command -v apt-get)" ]; then
    echo "Debian-based system detected. Installing Docker using apt-get."
    sudo apt-get update
    sudo apt-get install -y docker.io $EXTRA_PKGS
    sudo systemctl start docker
    sudo systemctl enable docker
elif [ -x "$(command -v yum)" ]; then
    echo "Red Hat-based system detected. Installing Docker using yum."
    sudo yum install -y docker $EXTRA_PKGS
    sudo systemctl start docker
    sudo systemctl enable docker
else
    echo "Unsupported OS. Please install Docker manually."
    exit 1
fi

# ## Getting the docker image from the docker hub
echo "Pulling the Docker image for development environment"
# ...existing code...