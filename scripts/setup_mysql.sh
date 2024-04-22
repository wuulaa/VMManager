#!/bin/bash

apt-get install -y mysql-server


ROOT_USER=root
ROOT_PASSWORD=kunpeng920
VM_USER=vm_manager
VM_PASSWORD=kunpeng920

# 执行 SQL 语句
mysql -u$ROOT_USER << EOF
alter user 'root'@'localhost' identified with mysql_native_password by '$ROOT_PASSWORD';
flush privileges;
create user '$VM_USER'@'localhost' identified by '$VM_PASSWORD';
create database vm_db;
grant all privileges on vm_db.* to '$VM_USER'@'localhost' with grant option;
flush privileges;
EOF

mysql -u$ROOT_USER -p$ROOT_PASSWORD vm_db < vm_db.sql