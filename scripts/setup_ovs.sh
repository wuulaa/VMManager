#!/bin/bash

function readIni() {
    INIFILE=$1; SECTION=$2; ITEM=$3
    _readIni=`awk -F '=' '/\['$SECTION'\]/{a=1}a==1&&$1~/'$ITEM'/{print $2;exit}' $INIFILE`

    echo ${_readIni}
}

manager=$(readIni ./config.ini ovs manager)
echo $manager 

# 更新apt
apt-get update

# 安装依赖
apt-get install -y make gcc build-essential libssl-dev libcap-ng-dev python3.8 python3-pip autoconf automake libtool
pip3 install six

# Git clone
apt-get install -y git

cd ../
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
ovs-vsctl set-manager $manager
