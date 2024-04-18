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


#时间同步
apt -y install chrony

mv /etc/chrony/chrony.conf /etc/chrony/chrony.conf.bak

time_master="server ntp.aliyun.com iburst\nallow 192.168.201.34/24"

echo - e "$time_master" >> /etc/chrony/chrony.conf

service chrony restart

chronyc sources


#配置免密登录
ssh-keygen -t rsa -P ''

for ((i=1;i<=$((slaveNum+1));i++))
do
    curIP=$(readIni config.ini slave slave$i)
    ssh-copy-id -i .ssh/id_rsa.pub root@$curIP
done

#安装ceph基本安装包
apt install -y ceph-common

apt install -y cephadm

#初始化主节点
cephadm --image quay.io/ceph/ceph:v17.2 bootstrap --mon-ip $masterIP

#分发Ceph密钥
for ((i=1;i<=$((slaveNum+1));i++))
do
    curName=$(readIni config.ini slave hostname$i)
    ssh-copy-id -f -i /etc/ceph/ceph.pub $curName
done

#添加主机到集群
ceph orch host label add $masterName _admin
for ((i=1;i<=$((slaveNum+1));i++))
do
    curName=$(readIni config.ini slave hostname$i)
    curIP=$(readIni config.ini slave slave$i)
    ceph orch host add $curName $curIP
done

#添加磁盘
#ceph orch daemon add osd controller:/dev/sdc