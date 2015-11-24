-- MySQL dump 10.13  Distrib 5.5.23, for Win32 (x86)
--
-- Host: localhost    Database: WFM
-- ------------------------------------------------------
-- Server version	5.5.23

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `client`
--

DROP TABLE IF EXISTS `client`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `client` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `longitude` double DEFAULT NULL,
  `latitude` double DEFAULT NULL,
  `IS_BASE` tinyint(1) DEFAULT '0',
  `address` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `client`
--

LOCK TABLES `client` WRITE;
/*!40000 ALTER TABLE `client` DISABLE KEYS */;
INSERT INTO `client` VALUES (1,'Гончаров А.В.',30.350544,59.999623,0,'2-й Муринский проспект, 39'),(2,'Петренко Л.Н',30.283422,59.940608,0,'Волжский переулок, 13'),(3,'Глинка С.А.',30.298571,59.923732,0,'улица Глинки, 15'),(4,'Абакумов В.Д.',30.302444,59.863053,0,'Новоизмайловский проспект, 17'),(5,'Нержин Е.Ф.',30.40057,59.869613,0,'улица Турку, 22к3'),(6,'Рубин И.Я.',30.258731,60.003064,0,'Гаккелевская улица, 29'),(7,'Прянчиков Р.М.',30.30995,59.99105,0,'Ланское шоссе, 25'),(8,'Сологдин Д.Н.',30.385513,60.017815,0,'улица Вавиловых, 4к1'),(9,'Прохоров О.О.',30.345645,59.99742,0,'Институтский проспект, 4к1'),(10,'Белов К.Г.',30.385362,59.945648,0,'Очаковская улица, 6'),(11,'base',30.311116,59.913881,1,NULL);
/*!40000 ALTER TABLE `client` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `distance`
--

DROP TABLE IF EXISTS `distance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `distance` (
  `CLIENT_FROM` int(11) NOT NULL,
  `CLIENT_TO` int(11) NOT NULL,
  `distance` double NOT NULL,
  PRIMARY KEY (`CLIENT_FROM`,`CLIENT_TO`),
  KEY `CLIENT_TO` (`CLIENT_TO`),
  CONSTRAINT `DISTANCE_ibfk_1` FOREIGN KEY (`CLIENT_FROM`) REFERENCES `client` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `DISTANCE_ibfk_2` FOREIGN KEY (`CLIENT_TO`) REFERENCES `client` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `distance`
--

LOCK TABLES `distance` WRITE;
/*!40000 ALTER TABLE `distance` DISABLE KEYS */;
INSERT INTO `distance` VALUES (1,2,0.9),(1,3,1.1),(1,4,1.9),(1,5,1.8),(1,6,0.6),(1,7,0.3),(1,8,0.4),(1,9,0.1),(1,10,0.8),(1,11,1.2),(2,1,0.9),(2,3,0.3),(2,4,1.1),(2,5,1.3),(2,6,0.9),(2,7,0.7),(2,8,1.3),(2,9,0.9),(2,10,0.7),(2,11,0.4),(3,1,1.1),(3,2,0.3),(3,4,0.8),(3,5,1),(3,6,1.1),(3,7,0.9),(3,8,1.4),(3,9,1.1),(3,10,0.7),(3,11,0.2),(4,1,1.9),(4,2,1.1),(4,3,0.8),(4,5,0.7),(4,6,2),(4,7,1.8),(4,8,2.2),(4,9,1.9),(4,10,1.3),(4,11,0.7),(5,1,1.8),(5,2,1.3),(5,3,1),(5,4,0.7),(5,6,2.1),(5,7,1.8),(5,8,2.1),(5,9,1.8),(5,10,1.1),(5,11,0.9),(6,1,0.6),(6,2,0.9),(6,3,1.1),(6,4,2),(6,5,2.1),(6,7,0.4),(6,8,0.9),(6,9,0.6),(6,10,1.2),(6,11,1.3),(7,1,0.3),(7,2,0.7),(7,3,0.9),(7,4,1.8),(7,5,1.8),(7,6,0.4),(7,8,0.6),(7,9,0.3),(7,10,0.8),(7,11,1.1),(8,1,0.4),(8,2,1.3),(8,3,1.4),(8,4,2.2),(8,5,2.1),(8,6,0.9),(8,7,0.6),(8,9,0.4),(8,10,1),(8,11,1.5),(9,1,0.1),(9,2,0.9),(9,3,1.1),(9,4,1.9),(9,5,1.8),(9,6,0.6),(9,7,0.3),(9,8,0.4),(9,10,0.8),(9,11,1.2),(10,1,0.8),(10,2,0.7),(10,3,0.7),(10,4,1.3),(10,5,1.1),(10,6,1.2),(10,7,0.8),(10,8,1),(10,9,0.8),(10,11,0.7),(11,1,1.2),(11,2,0.4),(11,3,0.2),(11,4,0.7),(11,5,0.9),(11,6,1.3),(11,7,1.1),(11,8,1.5),(11,9,1.2),(11,10,0.7);
/*!40000 ALTER TABLE `distance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `task`
--

DROP TABLE IF EXISTS `task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `task` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `CLIENT_ID` int(11) DEFAULT NULL,
  `TASK_TYPE_ID` int(11) DEFAULT NULL,
  `START_ARRIVE` int(11) DEFAULT NULL,
  `END_ARRIVE` int(11) DEFAULT NULL,
  `PRIORITY` int(11) DEFAULT NULL,
  `OPEN_TASK_DATE` date DEFAULT NULL,
  `CLOSE_TASK_DATE` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `CLIENT_ID` (`CLIENT_ID`),
  KEY `TASK_TYPE_ID` (`TASK_TYPE_ID`)
) ENGINE=MyISAM AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task`
--

LOCK TABLES `task` WRITE;
/*!40000 ALTER TABLE `task` DISABLE KEYS */;
INSERT INTO `task` VALUES (1,1,1,9,12,5,NULL,NULL),(2,2,2,14,17,5,NULL,NULL),(3,3,1,10,13,4,NULL,NULL),(4,4,4,9,16,3,NULL,NULL),(5,5,1,11,15,3,NULL,NULL),(8,8,1,9,13,4,NULL,NULL),(6,6,5,15,18,5,NULL,NULL),(9,9,3,15,17,5,NULL,NULL);
/*!40000 ALTER TABLE `task` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `task_type`
--

DROP TABLE IF EXISTS `task_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `task_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `task_type` varchar(200) DEFAULT NULL,
  `task_time` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task_type`
--

LOCK TABLES `task_type` WRITE;
/*!40000 ALTER TABLE `task_type` DISABLE KEYS */;
INSERT INTO `task_type` VALUES (1,'Подключение к интернету',1),(2,'Подключение к интернету;Настройка маршрутизатора',1.6),(3,'Настройка маршрутизатора',0.6),(4,'Подключение оптоволокна',0.5),(5,'Настройка маршрутизатора;Подключение оптоволокна',1.1),(6,'Подключение к интернету;Подключение оптоволокна',1.5);
/*!40000 ALTER TABLE `task_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `worker`
--

DROP TABLE IF EXISTS `worker`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `worker` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `skill` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `worker`
--

LOCK TABLES `worker` WRITE;
/*!40000 ALTER TABLE `worker` DISABLE KEYS */;
INSERT INTO `worker` VALUES (1,'Петров З.К.','Подключение к интернету;Настройка маршрутизатора'),(2,'Тихонов В.М.','Подключение к интернету;Подключение оптоволокна'),(3,'Смирнов Г.Т.','Настройка маршрутизатора;Подключение оптоволокна');
/*!40000 ALTER TABLE `worker` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2013-05-21 18:38:22
