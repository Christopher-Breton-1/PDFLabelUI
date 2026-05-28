#!/bin/bash

# function to check and install docker
install_docker() {
  echo "docker not found. installing docker..."
  if command -v apt &>/dev/null; then
    sudo apt update
    sudo apt install -y docker.io
  elif command -v yum &>/dev/null; then
    sudo yum install -y docker
  else
    echo "unsupported package manager. please install docker manually."
    exit 1
  fi
  sudo systemctl start docker
  sudo systemctl enable docker
  echo "docker installed successfully."
}

# function to check and install docker compose
install_docker_compose() {
  echo "docker-compose not found. installing docker-compose..."
  if command -v curl &>/dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "docker-compose installed successfully."
  else
    echo "curl not found. please install docker-compose manually."
    exit 1
  fi
}

# function to check if a command exists
command_exists() {
  command -v "$1" &>/dev/null
}

# try to run docker-compose up
echo "attempting to launch the app..."
if ! docker compose up -d --build; then
  echo "docker-compose failed. checking for docker and docker-compose installation..."

  # check for docker
  if ! command_exists docker; then
    install_docker
  fi

  # check for docker-compose
  if ! command_exists docker compose; then
    install_docker_compose
  fi

  # retry docker-compose up
  echo "retrying to launch the app..."
  if ! docker compose up -d --build; then
    echo "failed to launch the app after installation. please check for issues."
    exit 1
  fi
fi

echo "app launched successfully."
