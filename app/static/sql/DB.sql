-- =============================================================================
-- ZOE — Base de datos completa y portable
-- Basado en tu dump real de XAMPP (zoe.sql, 04-08-2026), con tus datos.
-- Pensado para que cualquier compañero de equipo lo importe y le funcione
-- igual que en tu máquina, con el models.py actual del repo.
--
-- Cómo usarlo en XAMPP:
--   1. Abrí phpMyAdmin (http://localhost/phpmyadmin)
--   2. Pestaña SQL (arriba, sin seleccionar ninguna base primero)
--   3. Pegá TODO este archivo y ejecutá
--   4. Confirmá que tu .env tenga DB_NAME=zoe
-- =============================================================================

DROP DATABASE IF EXISTS zoe;
CREATE DATABASE zoe CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE zoe;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";

-- -----------------------------------------------------------------------------
-- 1. cohorte
-- Reemplaza a "periodo_academico". Una cohorte cubre los 2 años de un grupo
-- de estudiantes en el programa IB: décimo el primer año, once el segundo.
-- Ya NO genera cursos (ver nota en tabla `curso`): sí genera sus 4
-- especialidades (Especialidad.crear_paquete_por_defecto).
-- -----------------------------------------------------------------------------
CREATE TABLE `cohorte` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `activo` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `cohorte` (`id`, `nombre`, `fecha_inicio`, `fecha_fin`, `activo`) VALUES
(1, '25/26', '2025-08-01', '2027-06-30', 1);
ALTER TABLE `cohorte` AUTO_INCREMENT = 2;

-- -----------------------------------------------------------------------------
-- 1b. curso
-- CATÁLOGO GLOBAL, INDEPENDIENTE DE LA COHORTE: 1001-1004 (décimo) y
-- 1101-1104 (once). El mismo curso se reutiliza cohorte tras cohorte; NO
-- pertenece a ninguna. Quién está en qué curso, en qué cohorte, se resuelve
-- con usuario.curso_id + usuario.cohorte_id (ver tabla `usuario`).
-- No reemplaza a "grupo", que sigue existiendo para equipos de trabajo.
-- -----------------------------------------------------------------------------
CREATE TABLE `curso` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` int(11) NOT NULL,
  `nombre` varchar(100) DEFAULT NULL,
  `grado` int(11) NOT NULL,
  `seccion` int(11) NOT NULL,
  `activo` tinyint(1) DEFAULT 1,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_curso_codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `curso` (`codigo`, `nombre`, `grado`, `seccion`) VALUES
(1001, '1001', 10, 1), (1002, '1002', 10, 2), (1003, '1003', 10, 3), (1004, '1004', 10, 4),
(1101, '1101', 11, 1), (1102, '1102', 11, 2), (1103, '1103', 11, 3), (1104, '1104', 11, 4);
ALTER TABLE `curso` AUTO_INCREMENT = 9;

-- -----------------------------------------------------------------------------
-- 2. usuario
-- El estudiante tiene, de forma directa y explícita: cohorte, curso y
-- estado de matrícula BI (característica transversal, no un módulo aparte).
-- NOTA TÉCNICA: todo estudiante nuevo entra como NO_MATRICULADO; a futuro
-- se podría implementar otro flujo de admisión/matrícula inicial.
-- -----------------------------------------------------------------------------
CREATE TABLE `usuario` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `correo` varchar(255) NOT NULL,
  `contrasena_hash` varchar(255) NOT NULL,
  `rol` varchar(50) NOT NULL,
  `cohorte_id` int(11) DEFAULT NULL,
  `curso_id` int(11) DEFAULT NULL,
  `estado_matricula` ENUM('NO_MATRICULADO','EN_PROCESO','PENDIENTE','MATRICULADO','ACTIVO','RETIRADO','FINALIZADO','CANCELADO') DEFAULT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  `ultimo_login` datetime DEFAULT NULL,
  `activo` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `correo` (`correo`),
  KEY `cohorte_id` (`cohorte_id`),
  KEY `curso_id` (`curso_id`),
  CONSTRAINT `usuario_ibfk_1` FOREIGN KEY (`cohorte_id`) REFERENCES `cohorte` (`id`),
  CONSTRAINT `usuario_ibfk_2` FOREIGN KEY (`curso_id`) REFERENCES `curso` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `usuario` (`id`, `nombre`, `correo`, `contrasena_hash`, `rol`, `cohorte_id`, `curso_id`, `estado_matricula`, `creado_en`, `ultimo_login`, `activo`) VALUES
(2, 'María García', 'maria@example.com', 'scrypt:32768:8:1$Ff5qAiDFERgesG91$45fd7dedc88af0db0fac886b55694e472505f683dd03ca487c1d705ec52466e3f7b6c356ffa7eaa9df35823dd02d1448a3ab76fe1e1a0506be949d83361c99c3', 'profesor', 1, NULL, NULL, '2026-06-18 19:32:34', NULL, 1),
(5, 'Admin ZOE', 'admin@zoe.com', 'scrypt:32768:8:1$4lzdEy88sXQTDz6E$4056a47476c577cd3723892f9f726800206b90d400a0eede2cb68cba78ccc2b4f0d24b41a69240a31a5a156266e313974565dc45a3c6c4c36b183afefb12d02c', 'coordinador', NULL, NULL, NULL, NULL, NULL, 1),
(6, 'Santiago Aguilera', 'santiago@edu.com', 'scrypt:32768:8:1$fqnzVc6WbhpF9uuV$16672fe529db09ef9ba55d84486b26166863fee4531f970bce29a37b9bf083c732d756cbcf7992ee0f80ab25c93786546239a6611d329f38e5338b85dd8bbd54', 'estudiante', 1, 1, 'ACTIVO', NULL, NULL, 1),
(7, 'Jose Miguel Santana', 'Jose@prof.com', 'scrypt:32768:8:1$lMKTd7rAvFGcjXRa$bf6992cd33ca196e089d52030bc63e715ede82aafc35bcb5e57a8212c01698ea79fce39ad8aaacb879fe331f09981516665cbb71a90ce807c6d6373379761764', 'profesor', 1, NULL, NULL, NULL, NULL, 1);
ALTER TABLE `usuario` AUTO_INCREMENT = 9;

-- -----------------------------------------------------------------------------
-- 3. materia
-- CATÁLOGO GLOBAL, REUTILIZABLE: no pertenece a cohorte ni a curso. Se
-- conecta a un curso puntual (con su profesor) mediante `curso_materia`
-- (MATERIA -> ASIGNACIÓN ACADÉMICA -> CURSO + PROFESOR).
-- -----------------------------------------------------------------------------
CREATE TABLE `materia` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `materia` (`id`, `nombre`, `descripcion`, `creado_en`) VALUES
(1, 'Matemáticas', 'Cálculo y Álgebra lineal ', '2026-06-18 19:32:34'),
(2, 'Inglés', 'Lengua inglesa avanzada', '2026-06-18 19:32:34'),
(3, 'Programacion y Diseño de Software', '', NULL);
ALTER TABLE `materia` AUTO_INCREMENT = 4;

-- -----------------------------------------------------------------------------
-- 1c. curso_materia
-- Paquete de materias que se dictan en un curso, cada una con el profesor
-- asignado a dictarla en ESE curso específico.
-- -----------------------------------------------------------------------------
CREATE TABLE `curso_materia` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `curso_id` int(11) NOT NULL,
  `materia_id` int(11) NOT NULL,
  `profesor_id` int(11) DEFAULT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_curso_materia` (`curso_id`,`materia_id`),
  KEY `curso_id` (`curso_id`),
  KEY `materia_id` (`materia_id`),
  KEY `profesor_id` (`profesor_id`),
  CONSTRAINT `curso_materia_ibfk_1` FOREIGN KEY (`curso_id`) REFERENCES `curso` (`id`) ON DELETE CASCADE,
  CONSTRAINT `curso_materia_ibfk_2` FOREIGN KEY (`materia_id`) REFERENCES `materia` (`id`) ON DELETE CASCADE,
  CONSTRAINT `curso_materia_ibfk_3` FOREIGN KEY (`profesor_id`) REFERENCES `usuario` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `curso_materia` (`curso_id`, `materia_id`, `profesor_id`) VALUES
(1, 3, 7);

-- -----------------------------------------------------------------------------
-- 1e. especialidad
-- Programación de Software, Diseño Multimedia, Ambiental, Administración de
-- Empresas. Funciona como un curso (agrupa estudiantes de la cohorte) pero
-- por especialidad, con un solo profesor asignado. Se auto-generan las 4 al
-- crear la cohorte (ver Cohorte.guardar() en models.py).
-- -----------------------------------------------------------------------------
CREATE TABLE `especialidad` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `cohorte_id` int(11) NOT NULL,
  `profesor_id` int(11) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT 1,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_especialidad_cohorte_nombre` (`cohorte_id`,`nombre`),
  KEY `cohorte_id` (`cohorte_id`),
  KEY `profesor_id` (`profesor_id`),
  CONSTRAINT `especialidad_ibfk_1` FOREIGN KEY (`cohorte_id`) REFERENCES `cohorte` (`id`) ON DELETE CASCADE,
  CONSTRAINT `especialidad_ibfk_2` FOREIGN KEY (`profesor_id`) REFERENCES `usuario` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `especialidad` (`nombre`, `cohorte_id`) VALUES
('Programación de Software', 1), ('Diseño Multimedia', 1), ('Ambiental', 1), ('Administración de Empresas', 1);

-- -----------------------------------------------------------------------------
-- 1f. estudiante_especialidad
-- Estudiantes inscritos en una especialidad.
-- -----------------------------------------------------------------------------
CREATE TABLE `estudiante_especialidad` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL,
  `especialidad_id` int(11) NOT NULL,
  `unido_en` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_estudiante_especialidad` (`usuario_id`,`especialidad_id`),
  KEY `usuario_id` (`usuario_id`),
  KEY `especialidad_id` (`especialidad_id`),
  CONSTRAINT `estudiante_especialidad_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`) ON DELETE CASCADE,
  CONSTRAINT `estudiante_especialidad_ibfk_2` FOREIGN KEY (`especialidad_id`) REFERENCES `especialidad` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 4. tarea
-- -----------------------------------------------------------------------------
-- -----------------------------------------------------------------------------
-- 4. tarea
-- Cada tarea pertenece a una ASIGNACIÓN ACADÉMICA puntual (curso_materia_id
-- = MATERIA + CURSO + PROFESOR), no solo a una materia. Así, "Matemáticas
-- en 1001" nunca se mezcla con "Matemáticas en 1002".
-- -----------------------------------------------------------------------------
CREATE TABLE `tarea` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `titulo` varchar(255) NOT NULL,
  `instrucciones` text DEFAULT NULL,
  `fecha_limite` date NOT NULL,
  `curso_materia_id` int(11) NOT NULL,
  `creado_por` int(11) NOT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `curso_materia_id` (`curso_materia_id`),
  KEY `creado_por` (`creado_por`),
  CONSTRAINT `tarea_ibfk_1` FOREIGN KEY (`curso_materia_id`) REFERENCES `curso_materia` (`id`) ON DELETE CASCADE,
  CONSTRAINT `tarea_ibfk_2` FOREIGN KEY (`creado_por`) REFERENCES `usuario` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
ALTER TABLE `tarea` AUTO_INCREMENT = 2;

-- -----------------------------------------------------------------------------
-- 5. entrega
-- FIX aplicado: fecha_entrega la manda siempre models.py (NOW()); antes se
-- insertaba sin ese campo y esta columna es NOT NULL sin default -> fallaba.
-- -----------------------------------------------------------------------------
CREATE TABLE `entrega` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tarea_id` int(11) NOT NULL,
  `estudiante_id` int(11) NOT NULL,
  `archivo_url` varchar(255) DEFAULT NULL,
  `archivo_nombre_original` varchar(255) DEFAULT NULL,
  `fecha_entrega` datetime NOT NULL,
  `estado` varchar(50) DEFAULT NULL,
  `calificacion` varchar(50) DEFAULT NULL,
  `comentario_profesor` text DEFAULT NULL,
  `fecha_limite` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tarea_id` (`tarea_id`),
  KEY `estudiante_id` (`estudiante_id`),
  CONSTRAINT `entrega_ibfk_1` FOREIGN KEY (`tarea_id`) REFERENCES `tarea` (`id`) ON DELETE CASCADE,
  CONSTRAINT `entrega_ibfk_2` FOREIGN KEY (`estudiante_id`) REFERENCES `usuario` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 6. grupo
-- -----------------------------------------------------------------------------
-- -----------------------------------------------------------------------------
-- 6. grupo
-- Agrupación de estudiantes INDEPENDIENTE del curso y opcionalmente ligada a
-- una materia (curso ≠ grupo: un curso puede tener varios grupos de estudio).
-- -----------------------------------------------------------------------------
CREATE TABLE `grupo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `materia_id` int(11) DEFAULT NULL,
  `curso_id` int(11) DEFAULT NULL,
  `cohorte_id` int(11) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT 1,
  `creado_por` int(11) NOT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `materia_id` (`materia_id`),
  KEY `curso_id` (`curso_id`),
  KEY `cohorte_id` (`cohorte_id`),
  KEY `creado_por` (`creado_por`),
  CONSTRAINT `grupo_ibfk_1` FOREIGN KEY (`materia_id`) REFERENCES `materia` (`id`) ON DELETE SET NULL,
  CONSTRAINT `grupo_ibfk_2` FOREIGN KEY (`creado_por`) REFERENCES `usuario` (`id`),
  CONSTRAINT `grupo_ibfk_3` FOREIGN KEY (`curso_id`) REFERENCES `curso` (`id`) ON DELETE SET NULL,
  CONSTRAINT `grupo_ibfk_4` FOREIGN KEY (`cohorte_id`) REFERENCES `cohorte` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `grupo` (`id`, `nombre`, `descripcion`, `materia_id`, `creado_por`, `creado_en`) VALUES
(1, 'Matemáticas A', NULL, 1, 2, '2026-06-18 19:32:34');
ALTER TABLE `grupo` AUTO_INCREMENT = 3;

-- -----------------------------------------------------------------------------
-- 7. estudiante_grupo
-- -----------------------------------------------------------------------------
CREATE TABLE `estudiante_grupo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL,
  `grupo_id` int(11) NOT NULL,
  `unido_en` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_estudiante_grupo` (`usuario_id`,`grupo_id`),
  KEY `usuario_id` (`usuario_id`),
  KEY `grupo_id` (`grupo_id`),
  CONSTRAINT `estudiante_grupo_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`) ON DELETE CASCADE,
  CONSTRAINT `estudiante_grupo_ibfk_2` FOREIGN KEY (`grupo_id`) REFERENCES `grupo` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- -----------------------------------------------------------------------------
-- Nota: la matrícula BI NO tiene historial. usuario.estado_matricula es la
-- ÚNICA fuente de verdad del estado actual de un estudiante (ver tabla
-- usuario más arriba). No existe tabla "matriculado" ni ninguna otra
-- estructura paralela que pueda contradecirla.
-- -----------------------------------------------------------------------------
-- 8. comunicado
-- -----------------------------------------------------------------------------
CREATE TABLE `comunicado` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `titulo` varchar(255) NOT NULL,
  `contenido` text DEFAULT NULL,
  `creado_por` int(11) NOT NULL,
  `publicado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  `activo` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`),
  KEY `creado_por` (`creado_por`),
  CONSTRAINT `comunicado_ibfk_1` FOREIGN KEY (`creado_por`) REFERENCES `usuario` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 10. recurso
-- -----------------------------------------------------------------------------
CREATE TABLE `recurso` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `titulo` varchar(255) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `url_archivo` varchar(255) DEFAULT NULL,
  `tipo` varchar(50) DEFAULT NULL,
  `materia_id` int(11) DEFAULT NULL,
  `curso_id` int(11) DEFAULT NULL,
  `curso_materia_id` int(11) DEFAULT NULL,
  `creado_por` int(11) NOT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `materia_id` (`materia_id`),
  KEY `curso_id` (`curso_id`),
  KEY `curso_materia_id` (`curso_materia_id`),
  KEY `creado_por` (`creado_por`),
  CONSTRAINT `recurso_ibfk_1` FOREIGN KEY (`materia_id`) REFERENCES `materia` (`id`) ON DELETE SET NULL,
  CONSTRAINT `recurso_ibfk_2` FOREIGN KEY (`creado_por`) REFERENCES `usuario` (`id`),
  CONSTRAINT `recurso_ibfk_3` FOREIGN KEY (`curso_id`) REFERENCES `curso` (`id`) ON DELETE SET NULL,
  CONSTRAINT `recurso_ibfk_4` FOREIGN KEY (`curso_materia_id`) REFERENCES `curso_materia` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 11. cronograma
-- -----------------------------------------------------------------------------
-- Nivel explícito del evento (institucional/cohorte/curso/asignación/grupo).
-- No obliga a ningún evento a tener materia: "Simulacro IB" es institucional,
-- "Entrega Matemáticas 1001" es de asignación académica (curso_materia_id).
CREATE TABLE `cronograma` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `titulo` varchar(255) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `fecha_evento` date NOT NULL,
  `tipo` varchar(50) DEFAULT NULL,
  `materia_id` int(11) DEFAULT NULL,
  `curso_id` int(11) DEFAULT NULL,
  `creado_por` int(11) NOT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `materia_id` (`materia_id`),
  KEY `curso_id` (`curso_id`),
  KEY `creado_por` (`creado_por`),
  CONSTRAINT `cronograma_ibfk_1` FOREIGN KEY (`materia_id`) REFERENCES `materia` (`id`) ON DELETE SET NULL,
  CONSTRAINT `cronograma_ibfk_2` FOREIGN KEY (`creado_por`) REFERENCES `usuario` (`id`),
  CONSTRAINT `cronograma_ibfk_3` FOREIGN KEY (`curso_id`) REFERENCES `curso` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `cronograma` (`id`, `titulo`, `descripcion`, `fecha_evento`, `tipo`, `materia_id`, `creado_por`, `creado_en`) VALUES
(1, 'Simulacro IB', '', '2026-07-15', 'examen', NULL, 5, NULL),
(2, 'Grados', '', '2026-11-26', 'actividad', NULL, 5, NULL);
ALTER TABLE `cronograma` AUTO_INCREMENT = 3;

-- -----------------------------------------------------------------------------
-- 12. mensaje
-- -----------------------------------------------------------------------------
CREATE TABLE `mensaje` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `remitente_id` int(11) NOT NULL,
  `destinatario_id` int(11) NOT NULL,
  `grupo_id` int(11) DEFAULT NULL,
  `asunto` varchar(255) NOT NULL,
  `cuerpo` text DEFAULT NULL,
  `enviado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  `leido` tinyint(1) DEFAULT 0,
  `eliminado_remitente` tinyint(1) DEFAULT 0,
  `eliminado_destinatario` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `remitente_id` (`remitente_id`),
  KEY `destinatario_id` (`destinatario_id`),
  KEY `idx_mensaje_grupo` (`grupo_id`),
  CONSTRAINT `fk_mensaje_grupo` FOREIGN KEY (`grupo_id`) REFERENCES `grupo` (`id`) ON DELETE SET NULL,
  CONSTRAINT `mensaje_ibfk_1` FOREIGN KEY (`remitente_id`) REFERENCES `usuario` (`id`),
  CONSTRAINT `mensaje_ibfk_2` FOREIGN KEY (`destinatario_id`) REFERENCES `usuario` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;

-- =============================================================================
-- FIN — cohortes, cursos, especialidades, matriculados y demás tablas del
-- sistema, con datos de ejemplo (2 usuarios profesor, 1 estudiante,
-- 1 coordinador, 3 materias, 1 grupo, 2 eventos de cronograma).
-- =============================================================================

-- =============================================================================
-- MIGRACIÓN: Valoraciones por actividad (escala Bajo/Básico/Alto/Superior) + Archivo Histórico
-- No borra nada existente. Ejecutar en phpMyAdmin -> pestaña SQL (base `zoe`).
-- =============================================================================

USE zoe;

-- Valoración mínima de aprobación, configurable por materia.
-- Escala cualitativa IB/MEN: Bajo < Básico < Alto < Superior (default Básico).
ALTER TABLE materia
    ADD COLUMN valoracion_minima_aprobatoria ENUM('Bajo','Básico','Alto','Superior') NOT NULL DEFAULT 'Básico';

-- Actividades valorativas que el profesor define libremente por materia
CREATE TABLE actividad_valorativa (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    materia_id  INT NOT NULL,
    nombre      VARCHAR(200) NOT NULL,
    tipo        VARCHAR(50) NOT NULL DEFAULT 'otro',
    porcentaje  DECIMAL(5,2) NOT NULL,
    fecha       DATE DEFAULT NULL,
    creado_por  INT NOT NULL,
    creado_en   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (materia_id) REFERENCES materia(id) ON DELETE CASCADE,
    FOREIGN KEY (creado_por) REFERENCES usuario(id) ON DELETE RESTRICT,
    INDEX idx_actividad_materia (materia_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Valoración de cada estudiante en cada actividad: Bajo, Básico, Alto o Superior
-- (no numérica). El promedio ponderado del boletín se calcula en la app,
-- mapeando cada nivel a un ordinal 1-4 y redondeando al nivel más cercano.
CREATE TABLE valoracion_actividad (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    actividad_id   INT NOT NULL,
    estudiante_id  INT NOT NULL,
    valor          ENUM('Bajo','Básico','Alto','Superior') DEFAULT NULL,
    comentario     TEXT,
    calificado_en  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (actividad_id) REFERENCES actividad_valorativa(id) ON DELETE CASCADE,
    FOREIGN KEY (estudiante_id) REFERENCES usuario(id) ON DELETE RESTRICT,
    UNIQUE KEY uq_actividad_estudiante (actividad_id, estudiante_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Archivo histórico de proyectos de cohortes anteriores, con búsqueda FULLTEXT
CREATE TABLE proyecto_archivado (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    titulo          VARCHAR(200) NOT NULL,
    descripcion     TEXT,
    autor           VARCHAR(200) DEFAULT NULL,
    materia_id      INT NULL,
    cohorte_id      INT NULL,
    url_archivo     VARCHAR(255) DEFAULT NULL,
    palabras_clave  VARCHAR(255) DEFAULT NULL,
    creado_por      INT NOT NULL,
    creado_en       DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (materia_id) REFERENCES materia(id) ON DELETE SET NULL,
    FOREIGN KEY (cohorte_id) REFERENCES cohorte(id) ON DELETE SET NULL,
    FOREIGN KEY (creado_por) REFERENCES usuario(id) ON DELETE RESTRICT,
    FULLTEXT KEY ft_proyecto_busqueda (titulo, descripcion, palabras_clave)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- MIGRACIÓN: Parametrización (módulos, permisos por rol, configuración base)
-- Panel exclusivo del coordinador para activar/desactivar módulos, restringir
-- el acceso por rol y editar ajustes generales del sistema sin tocar código.
-- =============================================================================

-- Módulos del sistema que se pueden activar/desactivar. No incluye
-- Dashboard/Usuarios/Configuración/Parametrización: son el núcleo y no se apagan.
CREATE TABLE modulo_sistema (
    clave        VARCHAR(50) PRIMARY KEY,
    nombre       VARCHAR(100) NOT NULL,
    descripcion  VARCHAR(255) DEFAULT NULL,
    activo       TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO modulo_sistema (clave, nombre, descripcion, activo) VALUES
('tareas', 'Tareas', 'Asignación y entrega de tareas', 1),
('materias', 'Materias', 'Catálogo de materias por cohorte', 1),
('cursos', 'Cursos', 'Cursos 1001-1004 / 1101-1104', 1),
('especialidades', 'Especialidades', 'Programación, Diseño, Ambiental, Administración', 1),
('grupos', 'Grupos de trabajo', 'Equipos de trabajo dentro de una materia', 1),
('valoraciones', 'Valoraciones', 'Libro de valoraciones Bajo/Básico/Alto/Superior', 1),
('archivo', 'Archivo Histórico', 'Proyectos archivados de cohortes anteriores', 1),
('recursos', 'Recursos', 'Material de apoyo compartido', 1),
('comunicados', 'Información', 'Comunicados y avisos', 1),
('cronograma', 'Cronograma', 'Calendario de eventos académicos', 1),
('mensajeria', 'Mensajería', 'Mensajes directos entre usuarios', 1),
('reportes', 'Reportes', 'Reportes y estadísticas', 1);

-- Matriz rol x módulo. Si no hay fila para una combinación, se asume
-- permitido=1 (fail-open), así que solo hace falta insertar las restricciones.
-- Matriz ROL x MÓDULO x ACCIÓN. Si no hay fila para una combinación, se
-- asume permitido=1 (fail-open), así que solo hace falta insertar las
-- restricciones. modulo_clave NO tiene FK a modulo_sistema porque también
-- cubre módulos núcleo no desactivables (usuarios, matricula).
CREATE TABLE rol_permiso (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    rol           VARCHAR(50) NOT NULL,
    modulo_clave  VARCHAR(50) NOT NULL,
    accion        VARCHAR(30) NOT NULL DEFAULT 'ver',
    permitido     TINYINT(1) NOT NULL DEFAULT 1,
    UNIQUE KEY uq_rol_modulo_accion (rol, modulo_clave, accion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Permisos por defecto (mínimo privilegio: lo que NO está acá queda
-- DENEGADO — ver ModuloSistema/RolPermiso en models.py). El coordinador
-- siempre puede todo (no necesita filas). Estos valores reproducen el
-- comportamiento real que ya tenía la app antes de este cambio.
INSERT INTO rol_permiso (rol, modulo_clave, accion, permitido) VALUES
-- Visibilidad de módulo (ver) — profesor ve todo lo académico
('profesor', 'tareas', 'ver', 1), ('profesor', 'materias', 'ver', 1),
('profesor', 'cursos', 'ver', 1), ('profesor', 'especialidades', 'ver', 1),
('profesor', 'grupos', 'ver', 1), ('profesor', 'valoraciones', 'ver', 1),
('profesor', 'archivo', 'ver', 1), ('profesor', 'recursos', 'ver', 1),
('profesor', 'comunicados', 'ver', 1), ('profesor', 'cronograma', 'ver', 1),
('profesor', 'mensajeria', 'ver', 1), ('profesor', 'reportes', 'ver', 1),
('profesor', 'matricula', 'ver', 1),
-- Visibilidad de módulo (ver) — estudiante solo lo que le corresponde
('estudiante', 'tareas', 'ver', 1), ('estudiante', 'materias', 'ver', 1),
('estudiante', 'valoraciones', 'ver', 1), ('estudiante', 'archivo', 'ver', 1),
('estudiante', 'recursos', 'ver', 1), ('estudiante', 'comunicados', 'ver', 1),
('estudiante', 'cronograma', 'ver', 1), ('estudiante', 'mensajeria', 'ver', 1),
('estudiante', 'reportes', 'ver', 1),
-- Acciones del profesor sobre Tareas (ya podía hacer esto)
('profesor', 'tareas', 'crear', 1), ('profesor', 'tareas', 'editar', 1),
('profesor', 'tareas', 'eliminar', 1), ('profesor', 'tareas', 'calificar', 1),
-- Acciones del profesor sobre Grupos (solo puede crear, no editar/eliminar/asignar)
('profesor', 'grupos', 'crear', 1);

CREATE TABLE configuracion_sistema (
    clave          VARCHAR(100) PRIMARY KEY,
    valor          TEXT,
    tipo           VARCHAR(20) NOT NULL DEFAULT 'texto',
    descripcion    VARCHAR(255) DEFAULT NULL,
    actualizado_en DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO configuracion_sistema (clave, valor, tipo, descripcion) VALUES
('nombre_institucion', 'Colegio Julio Flórez', 'texto', 'Nombre de la institución, usado en encabezados y reportes'),
('correo_soporte', 'soporte@zoeapp.edu.co', 'texto', 'Correo de contacto para soporte técnico'),
('programa', 'Bachillerato Internacional (IB)', 'texto', 'Nombre del programa académico'),
('cohorte_activa_id', '1', 'numero', 'ID de la cohorte que se muestra por defecto en los filtros'),
('permitir_autoregistro', '0', 'booleano', 'Si los estudiantes pueden crear su propia cuenta sin invitación');