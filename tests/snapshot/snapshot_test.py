from src.snapshot.snapshot import SnapShot

snap = SnapShot("libvirt-pool", "rbd-with-net")
# print(snap.get_image())
print(snap.query_snaps())
print(snap.is_snap_exits("rbd-with-net"))
# print(snap.create_snap("image1_snap1"))
# print(snap.is_snap_protected("image1_snap1"))
# snap.protect_snap("image1_snap1")
# snap.clone_snap("rbd3-network", "libvirt-pool", "test_clone_image2")
print(snap.get_children_list("rbd-with-net"))