import src.domain_manager.guest as domain_api
import src.storage.storage_api as storage_api
import libvirt

COUNT = 1

conn = libvirt.open("qemu:///system")
if not conn:
    raise SystemExit("Failed to open connection to qemu:///system")

for i in range(1,COUNT+1):
    domain_uuid = domain_api.get_uuid_by_name(conn, "domain16")
    domain_api.destroy_domain(conn, domain_uuid)
    domain_api.delete_domain(conn,domain_uuid)
    
# for i in range(1,COUNT):
#     storage_api.delete_rbd("libvirt-pool","domain"+str(i))

# domain_uuid = domain_api.get_uuid_by_name(conn, "domain"+str(18))
# domain_api.destroy_domain(conn, domain_uuid)
# domain_api.delete_domain(conn,domain_uuid)
# storage_api.delete_rbd("libvirt-pool","domain"+str(16))   