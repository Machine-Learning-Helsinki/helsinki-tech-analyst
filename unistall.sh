## here we will unistall all the packages installed by the install.sh script

## Uninstalling oh-my-zsh
echo "Checking if The user has the docker installed or not"

command -v docker >/dev/null 2>&1 || { echo >&2 "Docker is not installed. Aborting."; exit 1; }

# Deleteing all the docker container here 
command docker rm -f $(docker ps -a -q)

# DELETEING ALL THE DOCKER IMAGES HERE
command docker rmi -f $(docker images -q)


if 