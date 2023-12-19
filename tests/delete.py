import src.manage.domain_manage as domain_api
import src.storage.storage_api as storage_api
import libvirt

COUNT = 2

conn = libvirt.open("qemu:///system")
if not conn:
    raise SystemExit("Failed to open connection to qemu:///system")

for i in range(1,COUNT):
    domain_uuid = domain_api.get_uuid_by_name(conn, "domain1")
    domain_api.destroy_domain(conn, domain_uuid)
    domain_api.delete_domain(conn,domain_uuid)
    
for i in range(1,COUNT):
    storage_api.delete_rbd("libvirt-pool","domain1")