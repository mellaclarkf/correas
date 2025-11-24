-- Crear base de datos
CREATE DATABASE IF NOT EXISTS defectos;
USE defectos;

-- -------------------------------------------------------
-- Tabla usuarios
-- -------------------------------------------------------
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL DEFAULT ''
) ENGINE=InnoDB;

-- -------------------------------------------------------
-- Tabla maquina
-- -------------------------------------------------------
CREATE TABLE maquina (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ubicacion VARCHAR(255),
    largo DOUBLE,
    direccion BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB;

-- -------------------------------------------------------
-- Tabla historial
-- -------------------------------------------------------
CREATE TABLE historial (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    image_path VARCHAR(500),
    eje_x INT,
    eje_y INT,
    largo INT,
    ancho INT,
    etiqueta VARCHAR(100),
    prediccion VARCHAR(100),
    modelo_correa VARCHAR(100),
    fecha_registro DATETIME,
    eje_x2 INT,
    eje_y2 INT,
    Tramo INT
) ENGINE=InnoDB;

-- -------------------------------------------------------
-- Tabla modelo
-- -------------------------------------------------------
CREATE TABLE modelo (
    id INT PRIMARY KEY,
    accuracy DOUBLE
) ENGINE=InnoDB;

-- -------------------------------------------------------
-- Tabla modelos_ml
-- -------------------------------------------------------
CREATE TABLE modelos_ml (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_modelo VARCHAR(255) NOT NULL,
    fecha_entrenamiento DATETIME NOT NULL,
    precision_modelo FLOAT NOT NULL,
    modelo_blob LONGBLOB,
    observacion TEXT,
    Id_User INT,
    activo BOOLEAN,
    CONSTRAINT fk_modelos_user FOREIGN KEY (Id_User) REFERENCES usuarios(id)
) ENGINE=InnoDB;

-- -------------------------------------------------------
-- Tabla tramo
-- -------------------------------------------------------
CREATE TABLE tramo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_maquina INT NOT NULL,
    numero_tramo INT NOT NULL,
    largo_tramo DOUBLE,
    nota TEXT,
    CONSTRAINT fk_tramo_maquina FOREIGN KEY (id_maquina) REFERENCES maquina(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- -------------------------------------------------------
-- Tabla reforzamientos
-- -------------------------------------------------------
CREATE TABLE reforzamientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha_reforzamiento DATETIME NOT NULL,
    modelo_id INT NOT NULL,
    precision_despues FLOAT,
    observacion TEXT,
    usuario_id INT NOT NULL,
    desde_id_defecto INT NOT NULL,
    hasta_id_defecto INT NOT NULL,
    CONSTRAINT fk_ref_modelo FOREIGN KEY (modelo_id) REFERENCES modelos_ml(id),
    CONSTRAINT fk_ref_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB;
