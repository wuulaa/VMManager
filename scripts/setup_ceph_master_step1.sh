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
    hosts="$hosts\n$curIP $curName"
done

#配置hostname
echo -e "$hosts" >> /etc/hosts


#时间同步
apt -y install chrony

mv /etc/chrony/chrony.conf /etc/chrony/chrony.conf.bak

time_master="server ntp.aliyun.com iburst \nallow 192.168.201.34/24"

echo -e "$time_master" >> /etc/chrony/chrony.conf

service chrony restart

chronyc sources