echo "Here we will installed all the packages required for the development environment"

# ## Installing pip 
echo "Checking if the docker is installed or not"

command -v docker >/dev/null 2>&1 || { echo >&2 "Docker is not installed. Aborting.";  }

# Docker installation here

if [ -x "$(command -v apt-get)" ]; then
    echo "Debian-based system detected. Installing Docker using apt-get."
    sudo apt-get update
    sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
elif [ -x "$(command -v yum)" ]; then
    echo "Red Hat-based system detected. Installing Docker using yum."
    sudo yum install -y docker
    sudo systemctl start docker
    sudo systemctl enable docker
else
    echo "Unsupported OS. Please install Docker manually."
    exit 1
fi