#!/bin/bash

function readIni() {
    INIFILE=$1; SECTION=$2; ITEM=$3
    _readIni=`awk -F '=' '/\['$SECTION'\]/{a=1}a==1&&$1~/'$ITEM'/{print $2;exit}' $INIFILE`

    echo ${_readIni}
}

masterIP=$(readIni config.ini master masterIP)
masterName=$(readIni config.ini master masterName)
slaveNum=$(readIni config.ini slave slaveNum)

hosts="$masterIP $masterName"
for ((i=1;i<=$((slaveNum+1));i++))
do
    curIP=$(readIni config.ini slave slave$i)
    curName=$(readIni config.ini slave hostname$i)
    hosts="$hosts \n $curIP $curName"
done

#配置hostname
echo -e "$hosts" >> /etc/hosts

#配置时间同步
apt -y install chrony

mv /etc/chrony/chrony.conf /etc/chrony/chrony.conf.bak

time_slave="server $masterIP iburst"

echo - e "$time_slave" >> /etc/chrony/chrony.conf

service chrony restart

chronyc sources

#安装ceph基本安装包
apt install -y ceph-common

apt install -y cephadm

