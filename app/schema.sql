-- =============================================================================
-- ZOE — Esquema MySQL para XAMPP
-- Adaptado del diseño Oracle original.
-- Ejecutar en phpMyAdmin o consola MySQL.
-- =============================================================================

CREATE DATABASE IF NOT EXISTS zoe_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE zoe_db;

-- =============================================================================
-- PERÍODO ACADÉMICO
-- =============================================================================
CREATE TABLE periodo_academico (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(255) NOT NULL,
  fecha_inicio DATE NOT NULL,
  fecha_fin DATE NOT NULL,
  activo TINYINT(1) DEFAULT 1,
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- =============================================================================
-- USUARIO
-- =============================================================================
CREATE TABLE usuario (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(255) NOT NULL,
  correo VARCHAR(255) NOT NULL UNIQUE,
  contrasena_hash VARCHAR(255) NOT NULL,
  rol ENUM('estudiante', 'profesor', 'coordinador') NOT NULL DEFAULT 'estudiante',
  periodo_id INT,
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  ultimo_login TIMESTAMP NULL,
  activo TINYINT(1) DEFAULT 1,
  FOREIGN KEY (periodo_id) REFERENCES periodo_academico(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- =============================================================================
-- MATERIA
-- =============================================================================
CREATE TABLE materia (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(255) NOT NULL,
  tipo ENUM('regular', 'troncal') NOT NULL DEFAULT 'regular',
  descripcion TEXT,
  periodo_id INT,
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (periodo_id) REFERENCES periodo_academico(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- =============================================================================
-- PROFESOR_MATERIA (asignación de profesores a materias)
-- =============================================================================
CREATE TABLE profesor_materia (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  materia_id INT NOT NULL,
  FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE,
  FOREIGN KEY (materia_id) REFERENCES materia(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================================================
-- ESTUDIANTE_MATERIA
-- =============================================================================
CREATE TABLE estudiante_materia (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  materia_id INT NOT NULL,
  inscrito_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE,
  FOREIGN KEY (materia_id) REFERENCES materia(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================================================
-- TAREA
-- =============================================================================
CREATE TABLE tarea (
  id INT AUTO_INCREMENT PRIMARY KEY,
  titulo VARCHAR(255) NOT NULL,
  instrucciones TEXT,
  fecha_limite DATE NOT NULL,
  prioridad ENUM('alta', 'media', 'baja') DEFAULT 'media',
  materia_id INT NOT NULL,
  creado_por INT NOT NULL,
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (materia_id) REFERENCES materia(id) ON DELETE CASCADE,
  FOREIGN KEY (creado_por) REFERENCES usuario(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================================================
-- ENTREGA
-- =============================================================================
CREATE TABLE entrega (
  id INT AUTO_INCREMENT PRIMARY KEY,
  tarea_id INT NOT NULL,
  estudiante_id INT NOT NULL,
  archivo_url VARCHAR(500),
  fecha_entrega TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  estado ENUM('pendiente', 'en_revision', 'completada') DEFAULT 'pendiente',
  calificacion DECIMAL(5,2),
  comentario_profesor TEXT,
  FOREIGN KEY (tarea_id) REFERENCES tarea(id) ON DELETE CASCADE,
  FOREIGN KEY (estudiante_id) REFERENCES usuario(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================================================
-- CRONOGRAMA
-- =============================================================================
CREATE TABLE cronograma (
  id INT AUTO_INCREMENT PRIMARY KEY,
  titulo VARCHAR(255) NOT NULL,
  descripcion TEXT,
  fecha_evento DATE NOT NULL,
  tipo VARCHAR(50),
  materia_id INT,
  creado_por INT NOT NULL,
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (materia_id) REFERENCES materia(id) ON DELETE SET NULL,
  FOREIGN KEY (creado_por) REFERENCES usuario(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================================================
-- MENSAJE
-- =============================================================================
CREATE TABLE mensaje (
  id INT AUTO_INCREMENT PRIMARY KEY,
  remitente_id INT NOT NULL,
  destinatario_id INT NOT NULL,
  asunto VARCHAR(255),
  cuerpo TEXT NOT NULL,
  enviado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  leido TINYINT(1) DEFAULT 0,
  eliminado_remitente TINYINT(1) DEFAULT 0,
  eliminado_destinatario TINYINT(1) DEFAULT 0,
  FOREIGN KEY (remitente_id) REFERENCES usuario(id) ON DELETE CASCADE,
  FOREIGN KEY (destinatario_id) REFERENCES usuario(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================================================
-- RECURSO
-- =============================================================================
CREATE TABLE recurso (
  id INT AUTO_INCREMENT PRIMARY KEY,
  titulo VARCHAR(255) NOT NULL,
  descripcion TEXT,
  url_archivo VARCHAR(500),
  tipo ENUM('documento', 'presentacion', 'enlace', 'video') NOT NULL DEFAULT 'documento',
  materia_id INT,
  creado_por INT NOT NULL,
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (materia_id) REFERENCES materia(id) ON DELETE SET NULL,
  FOREIGN KEY (creado_por) REFERENCES usuario(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================================================
-- COMUNICADO
-- =============================================================================
CREATE TABLE comunicado (
  id INT AUTO_INCREMENT PRIMARY KEY,
  titulo VARCHAR(255) NOT NULL,
  contenido TEXT NOT NULL,
  creado_por INT NOT NULL,
  publicado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  activo TINYINT(1) DEFAULT 1,
  FOREIGN KEY (creado_por) REFERENCES usuario(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================================================
-- GRUPO (de estudio, por materia)
-- =============================================================================
CREATE TABLE grupo (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(255) NOT NULL,
  descripcion TEXT,
  materia_id INT NOT NULL,
  creado_por INT NOT NULL,
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (materia_id) REFERENCES materia(id) ON DELETE CASCADE,
  FOREIGN KEY (creado_por) REFERENCES usuario(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================================================
-- ESTUDIANTE_GRUPO
-- =============================================================================
CREATE TABLE estudiante_grupo (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  grupo_id INT NOT NULL,
  unido_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE,
  FOREIGN KEY (grupo_id) REFERENCES grupo(id) ON DELETE CASCADE
) ENGINE=InnoDB;