#!/bin/bash

apt-get install -y git python3.8 python3-pip novnc redis python-is-python3 docker
apt-get install -y qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virtinst virt-manager

pip install -r requirements.txt