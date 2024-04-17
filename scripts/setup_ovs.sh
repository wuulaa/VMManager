#!/bin/bash

# 更新apt
apt-get update

# 安装依赖
apt-get install -y make gcc build-essential libssl-dev libcap-ng-dev python3.8 python3-pip autoconf automake libtool
pip3 install six

# Git clone
apt-get install -y git
git clone https://github.com/openvswitch/ovs.git

# Make
cd ovs
./boot.sh
./configure
make
make install

# 启动
cd /usr/local/share/openvswitch/scripts
./ovs-ctl start
sleep 2
./ovs-ctl start

# 设置manager
ovs-vsctl set-manager ptcp:6640
