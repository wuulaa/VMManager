import docker
import pprint

import docker.models
import docker.models.containers
import docker.types
client = docker.from_env()
# client.containers.run(image="dorowu/ubuntu-desktop-lxde-vnc", network="none", name="ttttt",ports={"80/tcp":26080},detach=True)
container: docker.models.containers.Container = client.containers.list(filters={"name":"bb2"})[0]
# print(container.stats(decode=True, stream=True))
# network = client.networks.get("o247vphxgs4q", verbose=True, scope="swarm")
# token = client.swarm.attrs["JoinTokens"]["Manager"]
# print(token)
status = container.stats(decode=True)
cpu_delta = status.get("cpu_stats").get("cpu_usage").get("total_usage") - status.get("precpu_stats").get("cpu_usage").get("total_usage")