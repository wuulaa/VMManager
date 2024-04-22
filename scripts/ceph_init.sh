#!/bib/bash

#以下命令整个集群只需要执行一次，创建默认池以及用户
ceph osd pool create libvirt-pool

rbd pool init libvirt-pool

ceph auth get-or-create client.libvirt mon 'profile rbd' osd 'profile rbd pool=libvirt-pool'

#用户授权，每一个节点都需要执行
ceph auth get-key client.libvirt | sudo tee client.libvirt.key
virsh secret-set-value --secret {3510c3cc-37bb-40c7-82cb-b93a6229d22d} --base64 $(cat client.libvirt.key) && rm client.libvirt.key