import docker
import pprint

from docker.models.networks import Network
import docker.models.containers
import docker.types
client = docker.from_env()
# client.containers.run(image="dorowu/ubuntu-desktop-lxde-vnc", network="none", name="ttttt",ports={"80/tcp":26080},detach=True)
container: docker.models.containers.Container = client.containers.list(filters={"name":"redis"})[0]
# print(container.stats(decode=True, stream=True))
# network = client.networks.get("o247vphxgs4q", verbose=True, scope="swarm")
# token = client.swarm.attrs["JoinTokens"]["Manager"]
# print(token)

status = container.stats(decode=True).__next__()
# cpu_delta = status.get("cpu_stats").get("cpu_usage").get("total_usage") - status.get("precpu_stats").get("cpu_usage").get("total_usage")
# print(cpu_delta)
print(status.get("cpu_stats"))
print(status.get("memory_stats"))
print(status.get("networks"))
# client.swarm.init(default_addr_pool=["50.0.0.0/24"])


# ipam_pool = docker.types.IPAMPool(subnet="50.0.1.0/24")
# ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
# network:Network =client.networks.create("aaaaa", driver="overlay",ipam=ipam_config,attachable=True)
