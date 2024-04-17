#!/bin/bash

function readIni() {
    INIFILE=$1; SECTION=$2; ITEM=$3
    _readIni=`awk -F '=' '/\['$SECTION'\]/{a=1}a==1&&$1~/'$ITEM'/{print $2;exit}' $INIFILE`

    echo ${_readIni}
}

#示例
value=$(readIni config.ini ovs manager)
echo $value 

