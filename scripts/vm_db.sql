-- MySQL dump 10.13  Distrib 8.0.36, for Linux (x86_64)
--
-- Host: localhost    Database: vm_db
-- ------------------------------------------------------
-- Server version	8.0.36-0ubuntu0.20.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `guest`
--

DROP TABLE IF EXISTS `guest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `guest` (
  `uuid` varchar(64) NOT NULL COMMENT 'Guest UUID',
  `name` varchar(64) NOT NULL COMMENT 'Guest name',
  `user_uuid` varchar(64) NOT NULL COMMENT 'User UUID',
  `slave_name` varchar(64) NOT NULL COMMENT 'Node name',
  `title` varchar(64) DEFAULT NULL COMMENT 'Guest title',
  `description` varchar(64) DEFAULT NULL COMMENT 'Guest description',
  `status` varchar(64) NOT NULL COMMENT 'Guest status',
  `architecture` varchar(64) DEFAULT NULL COMMENT 'Guest architecture',
  `cpu` int DEFAULT NULL COMMENT 'CPU count',
  `max_cpu` int DEFAULT NULL COMMENT 'Max CPU count',
  `memory` int DEFAULT NULL COMMENT 'Memory size(MB)',
  `max_memory` int DEFAULT NULL COMMENT 'Max Memory size(MB)',
  `boot_option` varchar(64) DEFAULT NULL COMMENT 'Guest boot option, mapped to a volume',
  `spice_address` varchar(64) DEFAULT NULL COMMENT 'Guest SPICE address',
  `vnc_address` varchar(64) DEFAULT NULL COMMENT 'Guest VNC address, including ip, port and passwd',
  `parent_uuid` varchar(64) DEFAULT NULL COMMENT 'parent guest uuid',
  `children_list` varchar(64) DEFAULT NULL COMMENT 'children guest uuid list',
  `backups_list` varchar(64) DEFAULT NULL COMMENT 'backups uuid list, including ip, port and passwd',
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Primary Key',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `interface`
--

DROP TABLE IF EXISTS `interface`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `interface` (
  `name` varchar(64) NOT NULL COMMENT 'port name',
  `veth_name` varchar(64) DEFAULT NULL COMMENT 'port name within the virtual machine',
  `uuid` varchar(64) NOT NULL COMMENT 'interface UUID',
  `interface_type` enum('direct','network') NOT NULL COMMENT 'interface type, currently we only support ovs direct port',
  `status` enum('unbound','bound_unuse','bound_in_use') NOT NULL COMMENT 'status of a interface',
  `mac` varchar(64) DEFAULT NULL COMMENT 'mac address',
  `ip_address` varchar(64) DEFAULT NULL COMMENT 'ip address bond to the interface, could be null if net set yet',
  `gateway` varchar(64) DEFAULT NULL COMMENT 'ip gateway bond to the interface, could be null if net set yet',
  `xml` varchar(1024) DEFAULT NULL COMMENT 'xml string of a NIC/interface',
  `network_uuid` varchar(64) NOT NULL COMMENT 'UUID of the network this interface belongs to',
  `port_uuid` varchar(64) DEFAULT NULL COMMENT 'UUID of the ovs port this interface owns. This could be used to get the source name',
  `guest_uuid` varchar(64) DEFAULT NULL COMMENT 'UUID of the guest VM this interface belongs to',
  `slave_uuid` varchar(64) DEFAULT NULL COMMENT 'UUID of the slave node this interface is bound to',
  `user_uuid` varchar(64) DEFAULT NULL COMMENT 'UUID of the user this interface belongs to',
  `ip_modified` tinyint(1) NOT NULL COMMENT 'If interface ip is modified when domain is shutdown',
  `remove_from_domain` tinyint(1) NOT NULL COMMENT 'Should interface be removed from domain is shutdown',
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Primary Key',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `uuid` (`uuid`),
  UNIQUE KEY `mac` (`mac`),
  KEY `network_uuid` (`network_uuid`),
  CONSTRAINT `interface_ibfk_1` FOREIGN KEY (`network_uuid`) REFERENCES `network` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `network`
--

DROP TABLE IF EXISTS `network`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `network` (
  `uuid` varchar(64) NOT NULL COMMENT 'network UUID',
  `name` varchar(64) NOT NULL COMMENT 'network name',
  `address` varchar(64) NOT NULL COMMENT 'network address ,eg: 1.2.3.4/24',
  `user_uuid` varchar(64) DEFAULT NULL COMMENT 'UUID of the user this network belongs to',
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Primary Key',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `address` (`address`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `ovs_port`
--

DROP TABLE IF EXISTS `ovs_port`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ovs_port` (
  `uuid` varchar(64) NOT NULL COMMENT 'OVS port UUID',
  `name` varchar(64) NOT NULL COMMENT 'OVS port name',
  `vlan_tag` int DEFAULT NULL COMMENT 'OVS port tag',
  `slave_uuid` varchar(64) DEFAULT NULL COMMENT 'The UUID of slave this port belongs to.',
  `interface_uuid` varchar(64) DEFAULT NULL COMMENT 'The UUID of interface this port is bound to.',
  `port_type` enum('internal','vxlan') NOT NULL COMMENT 'ovs_port type, could be a vxlan port or a internal port',
  `remote_ip` varchar(64) DEFAULT NULL COMMENT 'remote ip addr if port is a vxlan port',
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Primary Key',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `pool`
--

DROP TABLE IF EXISTS `pool`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pool` (
  `uuid` varchar(64) NOT NULL COMMENT 'Pool UUID',
  `name` varchar(64) NOT NULL COMMENT 'Pool name',
  `status` tinyint(1) NOT NULL COMMENT 'The active state of the pool{down: 0, up: 1}',
  `allocation` int NOT NULL COMMENT 'Total pool capacity (MB)',
  `usage` int NOT NULL COMMENT 'Used capacity (MB)',
  `owner` varchar(64) NOT NULL COMMENT 'The user who owns this pool',
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Primary Key',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pool`
--

LOCK TABLES `pool` WRITE;
/*!40000 ALTER TABLE `pool` DISABLE KEYS */;
INSERT INTO `pool` VALUES ('d38681d3-07fd-41c7-b457-1667ef9354c7','volume-pool',0,20971520,3824640,'ZYQ',1);
/*!40000 ALTER TABLE `pool` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `slave`
--

DROP TABLE IF EXISTS `slave`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `slave` (
  `uuid` varchar(64) NOT NULL COMMENT 'Slave UUID',
  `name` varchar(64) NOT NULL COMMENT 'Slave name',
  `address` varchar(64) NOT NULL COMMENT 'Slave address, including ip and port',
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Primary Key',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `address` (`address`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `snapshot`
--

DROP TABLE IF EXISTS `snapshot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `snapshot` (
  `uuid` varchar(64) NOT NULL COMMENT 'Snapshot UUID',
  `name` varchar(64) NOT NULL COMMENT 'Snapshot name',
  `volume_uuid` varchar(64) NOT NULL COMMENT 'UUID of the snapshotted volume',
  `is_temp` tinyint(1) NOT NULL COMMENT 'Whether it was created temporarily due to cloning',
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Primary Key',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `volume_uuid` (`volume_uuid`),
  CONSTRAINT `snapshot_ibfk_1` FOREIGN KEY (`volume_uuid`) REFERENCES `volume` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=120 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `uuid` varchar(64) NOT NULL COMMENT 'User UUID',
  `name` varchar(64) NOT NULL COMMENT 'User name',
  `password` varchar(64) NOT NULL COMMENT 'User password, store encrypted str',
  `is_admin` tinyint(1) NOT NULL COMMENT 'whether a user is an admin',
  `token` varchar(512) DEFAULT NULL COMMENT 'token for jwt',
  `state` enum('online','offline') NOT NULL COMMENT 'user state, online or offline',
  `last_login` datetime DEFAULT NULL COMMENT 'last login datetime',
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Primary Key',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `password` (`password`),
  UNIQUE KEY `token` (`token`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `volume`
--

DROP TABLE IF EXISTS `volume`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `volume` (
  `uuid` varchar(64) NOT NULL COMMENT 'Volume UUID',
  `name` varchar(64) NOT NULL COMMENT 'Volume name',
  `status` smallint NOT NULL COMMENT 'The active state of the volume',
  `allocation` int NOT NULL COMMENT 'Total volume capacity (MB)',
  `parent_uuid` varchar(64) DEFAULT NULL COMMENT 'UUID of the cloned volume',
  `pool_uuid` varchar(64) NOT NULL COMMENT 'The UUID of poolwhere volume resides in',
  `guest_uuid` varchar(64) DEFAULT NULL COMMENT 'The UUID of guestusing this volume',
  `dev_order` smallint DEFAULT NULL COMMENT 'The order of device',
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Primary Key',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  UNIQUE KEY `name` (`name`),
  KEY `parent_uuid` (`parent_uuid`),
  KEY `pool_uuid` (`pool_uuid`),
  KEY `ix_volume_guest_uuid` (`guest_uuid`),
  CONSTRAINT `volume_ibfk_1` FOREIGN KEY (`parent_uuid`) REFERENCES `volume` (`uuid`),
  CONSTRAINT `volume_ibfk_2` FOREIGN KEY (`pool_uuid`) REFERENCES `pool` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=89 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `volume`
--

LOCK TABLES `volume` WRITE;
/*!40000 ALTER TABLE `volume` DISABLE KEYS */;
INSERT INTO `volume` VALUES ('8388ad7f-e58b-4d94-bf41-6e95b23d0d4a','template',0,20480,NULL,'d38681d3-07fd-41c7-b457-1667ef9354c7',NULL,NULL,1);
/*!40000 ALTER TABLE `volume` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-04-18 14:58:09
