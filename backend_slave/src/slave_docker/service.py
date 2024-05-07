from src.utils.response import APIResponse
from src.docker_manager.docker_manager import DockerManager
docker_manager = DockerManager()

#偷个懒，这里不做包装了
docker_service = docker_manager
