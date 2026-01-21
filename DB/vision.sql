-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 21-01-2026 a las 13:44:05
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `vision`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `historial`
--

CREATE TABLE `historial` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `image_path` varchar(500) DEFAULT NULL,
  `eje_x` int(11) DEFAULT NULL,
  `eje_y` int(11) DEFAULT NULL,
  `eje_x2` int(11) DEFAULT NULL,
  `eje_y2` int(11) DEFAULT NULL,
  `largo` int(11) DEFAULT NULL,
  `ancho` int(11) DEFAULT NULL,
  `etiqueta` varchar(100) DEFAULT NULL,
  `prediccion` varchar(100) DEFAULT NULL,
  `modelo_correa` varchar(100) DEFAULT NULL,
  `fecha_registro` datetime DEFAULT NULL,
  `fecha_video` date DEFAULT NULL,
  `Tramo` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `historial`
--

INSERT INTO `historial` (`id`, `name`, `image_path`, `eje_x`, `eje_y`, `eje_x2`, `eje_y2`, `largo`, `ancho`, `etiqueta`, `prediccion`, `modelo_correa`, `fecha_registro`, `fecha_video`, `Tramo`) VALUES
(1, 'frame_000000.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000000.jpg', 850, 565, 894, 1078, 0, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:25', '2025-10-02', 1),
(2, 'frame_000002.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000002.jpg', 850, 323, 887, 886, 3, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:25', '2025-10-02', 1),
(3, 'frame_000004.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000004.jpg', 846, 82, 890, 641, 2, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:25', '2025-10-02', 1),
(4, 'frame_000009.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000009.jpg', 580, 17, 609, 117, 5, 0, NULL, 'CORTES', 'Correa A', '2025-10-02 11:12:25', '2025-10-02', 1),
(5, 'frame_000047.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000047.jpg', 858, 861, 897, 1079, 5, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:27', '2025-10-02', 1),
(6, 'frame_000049.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000049.jpg', 855, 585, 897, 1069, 0, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:27', '2025-10-02', 1),
(7, 'frame_000051.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000051.jpg', 852, 393, 894, 829, 2, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:27', '2025-10-02', 1),
(8, 'frame_000052.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000052.jpg', 851, 247, 894, 738, 5, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:27', '2025-10-02', 1),
(9, 'frame_000094.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000094.jpg', 857, 974, 891, 1079, 7, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:29', '2025-10-02', 1),
(10, 'frame_000096.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000096.jpg', 851, 716, 900, 1080, 9, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:29', '2025-10-02', 1),
(11, 'frame_000098.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000098.jpg', 849, 523, 900, 1078, 0, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:30', '2025-10-02', 1),
(12, 'frame_000099.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000099.jpg', 847, 358, 897, 956, 6, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:30', '2025-10-02', 1),
(13, 'frame_000099.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000099.jpg', 853, 818, 897, 970, 5, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:30', '2025-10-02', 1),
(14, 'frame_000101.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000101.jpg', 845, 135, 898, 559, 2, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:30', '2025-10-02', 1),
(15, 'frame_000101.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000101.jpg', 850, 563, 893, 734, 2, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:30', '2025-10-02', 1),
(16, 'frame_000146.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000146.jpg', 855, 850, 886, 1002, 5, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:32', '2025-10-02', 2),
(17, 'frame_000148.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000148.jpg', 852, 586, 885, 811, 2, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:32', '2025-10-02', 2),
(18, 'frame_000150.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000150.jpg', 851, 356, 883, 497, 9, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:32', '2025-10-02', 2),
(19, 'frame_000152.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000152.jpg', 852, 105, 882, 293, 8, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:32', '2025-10-02', 2),
(20, 'frame_000195.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000195.jpg', 854, 903, 882, 987, 2, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:34', '2025-10-02', 3),
(21, 'frame_000198.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000198.jpg', 850, 553, 880, 750, 1, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:34', '2025-10-02', 3),
(22, 'frame_000204.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000204.jpg', 578, 53, 602, 164, 0, 0, NULL, 'CORTES', 'Correa A', '2025-10-02 11:12:35', '2025-10-02', 3),
(23, 'frame_000208.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000208.jpg', 1350, 481, 1372, 719, 3, 0, NULL, 'CORTES', 'Correa A', '2025-10-02 11:12:35', '2025-10-02', 3),
(24, 'frame_000208.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000208.jpg', 1349, 742, 1371, 931, 7, 0, NULL, 'CORTES', 'Correa A', '2025-10-02 11:12:35', '2025-10-02', 3),
(25, 'frame_000243.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000243.jpg', 854, 957, 888, 1080, 8, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:36', '2025-10-02', 4),
(26, 'frame_000244.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000244.jpg', 849, 787, 892, 1080, 3, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:37', '2025-10-02', 4),
(27, 'frame_000245.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000245.jpg', 847, 683, 893, 1080, 5, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:37', '2025-10-02', 4),
(28, 'frame_000246.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000246.jpg', 845, 501, 891, 956, 2, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:37', '2025-10-02', 4),
(29, 'frame_000249.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000249.jpg', 842, 184, 886, 621, 2, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:37', '2025-10-02', 4),
(30, 'frame_000251.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000251.jpg', 843, 2, 888, 366, 3, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:37', '2025-10-02', 4),
(31, 'frame_000286.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000286.jpg', 856, 260, 880, 475, 0, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:39', '2025-10-02', 4),
(32, 'frame_000290.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000290.jpg', 855, 1006, 892, 1080, 7, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:39', '2025-10-02', 4),
(33, 'frame_000291.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000291.jpg', 850, 840, 897, 1080, 6, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:39', '2025-10-02', 4),
(34, 'frame_000294.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000294.jpg', 842, 486, 900, 1080, 8, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:39', '2025-10-02', 4),
(35, 'frame_000296.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000296.jpg', 841, 237, 896, 933, 8, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:39', '2025-10-02', 4),
(36, 'frame_000298.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000298.jpg', 840, 13, 896, 682, 5, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-02 11:12:39', '2025-10-02', 4),
(37, 'frame_000000.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000000.jpg', 850, 565, 894, 1078, 4, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:15:59', '2025-10-06', 1),
(38, 'frame_000002.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000002.jpg', 850, 323, 887, 886, 3, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:15:59', '2025-10-06', 1),
(39, 'frame_000004.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000004.jpg', 846, 82, 890, 641, 7, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:15:59', '2025-10-06', 1),
(40, 'frame_000009.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000009.jpg', 580, 17, 609, 117, 9, 0, NULL, 'CORTES', 'Correa A', '2025-10-06 23:15:59', '2025-10-06', 1),
(41, 'frame_000047.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000047.jpg', 858, 861, 897, 1079, 2, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:01', '2025-10-06', 1),
(42, 'frame_000049.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000049.jpg', 855, 585, 897, 1069, 7, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:01', '2025-10-06', 1),
(43, 'frame_000051.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000051.jpg', 852, 393, 894, 829, 8, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:01', '2025-10-06', 1),
(44, 'frame_000052.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000052.jpg', 851, 247, 894, 738, 0, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:01', '2025-10-06', 1),
(45, 'frame_000094.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000094.jpg', 857, 974, 891, 1079, 6, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:03', '2025-10-06', 1),
(46, 'frame_000096.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000096.jpg', 851, 716, 900, 1080, 7, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:04', '2025-10-06', 1),
(47, 'frame_000098.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000098.jpg', 849, 523, 900, 1078, 3, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:04', '2025-10-06', 1),
(48, 'frame_000099.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000099.jpg', 847, 358, 897, 956, 0, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:04', '2025-10-06', 1),
(49, 'frame_000099.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000099.jpg', 853, 818, 897, 970, 1, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:04', '2025-10-06', 1),
(50, 'frame_000101.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000101.jpg', 845, 135, 898, 559, 1, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:04', '2025-10-06', 1),
(51, 'frame_000101.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000101.jpg', 850, 563, 893, 734, 5, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:04', '2025-10-06', 1),
(52, 'frame_000146.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000146.jpg', 855, 850, 886, 1002, 8, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:06', '2025-10-06', 2),
(53, 'frame_000148.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000148.jpg', 852, 586, 885, 811, 7, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:06', '2025-10-06', 2),
(54, 'frame_000150.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000150.jpg', 851, 356, 883, 497, 4, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:06', '2025-10-06', 2),
(55, 'frame_000152.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000152.jpg', 852, 105, 882, 293, 9, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:06', '2025-10-06', 2),
(56, 'frame_000195.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000195.jpg', 854, 903, 882, 987, 7, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:08', '2025-10-06', 3),
(57, 'frame_000198.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000198.jpg', 850, 553, 880, 750, 9, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:09', '2025-10-06', 3),
(58, 'frame_000204.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000204.jpg', 578, 53, 602, 164, 9, 0, NULL, 'CORTES', 'Correa A', '2025-10-06 23:16:09', '2025-10-06', 3),
(59, 'frame_000208.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000208.jpg', 1350, 481, 1372, 719, 4, 0, NULL, 'CORTES', 'Correa A', '2025-10-06 23:16:09', '2025-10-06', 3),
(60, 'frame_000208.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000208.jpg', 1349, 742, 1371, 931, 6, 0, NULL, 'CORTES', 'Correa A', '2025-10-06 23:16:09', '2025-10-06', 3),
(61, 'frame_000243.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000243.jpg', 854, 957, 888, 1080, 9, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:11', '2025-10-06', 4),
(62, 'frame_000244.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000244.jpg', 849, 787, 892, 1080, 9, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:11', '2025-10-06', 4),
(63, 'frame_000245.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000245.jpg', 847, 683, 893, 1080, 3, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:11', '2025-10-06', 4),
(64, 'frame_000246.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000246.jpg', 845, 501, 891, 956, 3, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:11', '2025-10-06', 4),
(65, 'frame_000249.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000249.jpg', 842, 184, 886, 621, 4, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:11', '2025-10-06', 4),
(66, 'frame_000251.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000251.jpg', 843, 2, 888, 366, 1, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:11', '2025-10-06', 4),
(67, 'frame_000286.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000286.jpg', 856, 260, 880, 475, 5, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:13', '2025-10-06', 4),
(68, 'frame_000290.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000290.jpg', 855, 1006, 892, 1080, 6, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:13', '2025-10-06', 4),
(69, 'frame_000291.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000291.jpg', 850, 840, 897, 1080, 7, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:13', '2025-10-06', 4),
(70, 'frame_000294.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000294.jpg', 842, 486, 900, 1080, 7, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:13', '2025-10-06', 4),
(71, 'frame_000296.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000296.jpg', 841, 237, 896, 933, 3, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:13', '2025-10-06', 4),
(72, 'frame_000298.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000298.jpg', 840, 13, 896, 682, 9, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-06 23:16:13', '2025-10-06', 4),
(73, 'frame_000000.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000000.jpg', 850, 565, 894, 1078, 4, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 09:59:55', '2025-10-21', 1),
(74, 'frame_000002.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000002.jpg', 850, 323, 887, 886, 7, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 09:59:55', '2025-10-21', 1),
(75, 'frame_000004.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000004.jpg', 846, 82, 890, 641, 2, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 09:59:55', '2025-10-21', 1),
(76, 'frame_000009.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000009.jpg', 580, 17, 609, 117, 8, 0, NULL, 'CORTES', 'Correa A', '2025-10-21 09:59:55', '2025-10-21', 1),
(77, 'frame_000047.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000047.jpg', 858, 861, 897, 1079, 3, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 09:59:57', '2025-10-21', 1),
(78, 'frame_000049.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000049.jpg', 855, 585, 897, 1069, 0, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 09:59:57', '2025-10-21', 1),
(79, 'frame_000051.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000051.jpg', 852, 393, 894, 829, 7, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 09:59:57', '2025-10-21', 1),
(80, 'frame_000052.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000052.jpg', 851, 247, 894, 738, 0, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 09:59:57', '2025-10-21', 1),
(81, 'frame_000094.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000094.jpg', 857, 974, 891, 1079, 0, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 09:59:59', '2025-10-21', 1),
(82, 'frame_000096.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000096.jpg', 851, 716, 900, 1080, 3, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 09:59:59', '2025-10-21', 1),
(83, 'frame_000098.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000098.jpg', 849, 523, 900, 1078, 1, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 09:59:59', '2025-10-21', 1),
(84, 'frame_000099.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000099.jpg', 847, 358, 897, 956, 3, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 09:59:59', '2025-10-21', 1),
(85, 'frame_000099.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000099.jpg', 853, 818, 897, 970, 4, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 09:59:59', '2025-10-21', 1),
(86, 'frame_000101.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000101.jpg', 845, 135, 898, 559, 3, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 09:59:59', '2025-10-21', 1),
(87, 'frame_000101.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000101.jpg', 850, 563, 893, 734, 4, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 09:59:59', '2025-10-21', 1),
(88, 'frame_000146.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000146.jpg', 855, 850, 886, 1002, 6, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 10:00:02', '2025-10-21', 2),
(89, 'frame_000148.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000148.jpg', 852, 586, 885, 811, 3, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 10:00:02', '2025-10-21', 2),
(90, 'frame_000150.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000150.jpg', 851, 356, 883, 497, 6, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 10:00:02', '2025-10-21', 2),
(91, 'frame_000152.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000152.jpg', 852, 105, 882, 293, 2, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 10:00:02', '2025-10-21', 2),
(92, 'frame_000195.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000195.jpg', 854, 903, 882, 987, 7, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 10:00:04', '2025-10-21', 3),
(93, 'frame_000198.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000198.jpg', 850, 553, 880, 750, 5, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 10:00:04', '2025-10-21', 3),
(94, 'frame_000204.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000204.jpg', 578, 53, 602, 164, 5, 0, NULL, 'CORTES', 'Correa A', '2025-10-21 10:00:04', '2025-10-21', 3),
(95, 'frame_000208.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000208.jpg', 1350, 481, 1372, 719, 9, 0, NULL, 'CORTES', 'Correa A', '2025-10-21 10:00:05', '2025-10-21', 3),
(96, 'frame_000208.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000208.jpg', 1349, 742, 1371, 931, 3, 0, NULL, 'CORTES', 'Correa A', '2025-10-21 10:00:05', '2025-10-21', 3),
(97, 'frame_000243.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000243.jpg', 854, 957, 888, 1080, 3, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 10:00:06', '2025-10-21', 4),
(98, 'frame_000244.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000244.jpg', 849, 787, 892, 1080, 1, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 10:00:06', '2025-10-21', 4),
(99, 'frame_000245.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000245.jpg', 847, 683, 893, 1080, 9, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 10:00:06', '2025-10-21', 4),
(100, 'frame_000246.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000246.jpg', 845, 501, 891, 956, 7, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 10:00:07', '2025-10-21', 4),
(101, 'frame_000249.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000249.jpg', 842, 184, 886, 621, 0, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 10:00:07', '2025-10-21', 4),
(102, 'frame_000251.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000251.jpg', 843, 2, 888, 366, 3, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 10:00:07', '2025-10-21', 4),
(103, 'frame_000286.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000286.jpg', 856, 260, 880, 475, 3, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 10:00:09', '2025-10-21', 4),
(104, 'frame_000290.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000290.jpg', 855, 1006, 892, 1080, 9, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 10:00:09', '2025-10-21', 4),
(105, 'frame_000291.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000291.jpg', 850, 840, 897, 1080, 3, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 10:00:09', '2025-10-21', 4),
(106, 'frame_000294.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000294.jpg', 842, 486, 900, 1080, 2, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 10:00:09', '2025-10-21', 4),
(107, 'frame_000296.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000296.jpg', 841, 237, 896, 933, 4, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 10:00:09', '2025-10-21', 4),
(108, 'frame_000298.jpg', 'C:\\Users\\clark\\OneDrive\\Documentos\\Python\\ProyectoCorreoImagenes\\ProyectoInterfazCorreas5.0.2\\Imagenes\\frame_000298.jpg', 840, 13, 896, 682, 4, 0, NULL, 'DESGASTE', 'Correa A', '2025-10-21 10:00:09', '2025-10-21', 4);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `maquina`
--

CREATE TABLE `maquina` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `ubicacion` varchar(255) DEFAULT NULL,
  `largo` double DEFAULT NULL,
  `direccion` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `maquina`
--

INSERT INTO `maquina` (`id`, `nombre`, `ubicacion`, `largo`, `direccion`) VALUES
(1, 'Correa A', 'zona norte', 2400, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `modelo`
--

CREATE TABLE `modelo` (
  `id` int(11) NOT NULL,
  `accuracy` double DEFAULT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `nombre_modelo` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `modelo`
--

INSERT INTO `modelo` (`id`, `accuracy`, `fecha_creacion`, `nombre_modelo`) VALUES
(1, 75, '2025-08-28 16:33:40', 'Modelo0'),
(3, 99.5, '2025-08-28 17:36:56', 'Modelo6');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `modelos_ml`
--

CREATE TABLE `modelos_ml` (
  `id` int(11) NOT NULL,
  `nombre_modelo` varchar(255) NOT NULL,
  `fecha_entrenamiento` datetime NOT NULL,
  `precision_modelo` float NOT NULL,
  `modelo_blob` longblob DEFAULT NULL,
  `observacion` text DEFAULT NULL,
  `Id_User` int(11) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reforzamientos`
--

CREATE TABLE `reforzamientos` (
  `id` int(11) NOT NULL,
  `fecha_reforzamiento` datetime NOT NULL,
  `modelo_id` int(11) NOT NULL,
  `precision_despues` float DEFAULT NULL,
  `observacion` text DEFAULT NULL,
  `usuario_id` int(11) NOT NULL,
  `desde_id_defecto` int(11) NOT NULL,
  `hasta_id_defecto` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tramo`
--

CREATE TABLE `tramo` (
  `id` int(11) NOT NULL,
  `id_maquina` int(11) NOT NULL,
  `numero_tramo` int(11) NOT NULL,
  `largo_tramo` double DEFAULT NULL,
  `nota` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tramo`
--

INSERT INTO `tramo` (`id`, `id_maquina`, `numero_tramo`, `largo_tramo`, `nota`) VALUES
(1, 1, 1, 800, 'sdfdsf'),
(2, 1, 2, 600, 'dsfdf'),
(3, 1, 3, 300, 'dfdfdsf'),
(4, 1, 4, 700, 'fdsff');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL DEFAULT '',
  `es_admin` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `historial`
--
ALTER TABLE `historial`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `maquina`
--
ALTER TABLE `maquina`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `modelo`
--
ALTER TABLE `modelo`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `modelos_ml`
--
ALTER TABLE `modelos_ml`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_modelos_user` (`Id_User`);

--
-- Indices de la tabla `reforzamientos`
--
ALTER TABLE `reforzamientos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_ref_modelo` (`modelo_id`),
  ADD KEY `fk_ref_usuario` (`usuario_id`);

--
-- Indices de la tabla `tramo`
--
ALTER TABLE `tramo`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_tramo_maquina` (`id_maquina`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `historial`
--
ALTER TABLE `historial`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=109;

--
-- AUTO_INCREMENT de la tabla `maquina`
--
ALTER TABLE `maquina`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `modelo`
--
ALTER TABLE `modelo`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `modelos_ml`
--
ALTER TABLE `modelos_ml`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `reforzamientos`
--
ALTER TABLE `reforzamientos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tramo`
--
ALTER TABLE `tramo`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `modelos_ml`
--
ALTER TABLE `modelos_ml`
  ADD CONSTRAINT `fk_modelos_user` FOREIGN KEY (`Id_User`) REFERENCES `usuarios` (`id`);

--
-- Filtros para la tabla `reforzamientos`
--
ALTER TABLE `reforzamientos`
  ADD CONSTRAINT `fk_ref_modelo` FOREIGN KEY (`modelo_id`) REFERENCES `modelos_ml` (`id`),
  ADD CONSTRAINT `fk_ref_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`);

--
-- Filtros para la tabla `tramo`
--
ALTER TABLE `tramo`
  ADD CONSTRAINT `fk_tramo_maquina` FOREIGN KEY (`id_maquina`) REFERENCES `maquina` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
