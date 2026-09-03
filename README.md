# ZOE — Zona de Organización Estudiantil

Plataforma de gestión académica para el **Programa del Diploma del Bachillerato
Internacional (IB)**, desarrollada para el Colegio Técnico Digital Julio Flórez.

Backend en Flask puro (sin ORM, SQL directo), frontend en Jinja2 + CSS propio,
base de datos MySQL/MariaDB.

---

## Índice

1. [Modelo académico](#modelo-académico)
2. [Roles](#roles)
3. [Módulos del sistema](#módulos-del-sistema)
4. [Arquitectura técnica](#arquitectura-técnica)
5. [Instalación](#instalación)
6. [Estructura del proyecto](#estructura-del-proyecto)
7. [Base de datos](#base-de-datos)
8. [Permisos](#permisos)
9. [Eliminaciones y Foreign Keys](#eliminaciones-y-foreign-keys)
10. [Notas técnicas y decisiones de diseño](#notas-técnicas-y-decisiones-de-diseño)

---

## Modelo académico

ZOE se organiza alrededor de estas entidades y sus relaciones:

```
COHORTE
  → ciclo académico de dos años (décimo + once). Genera automáticamente
    sus 4 Especialidades al crearse.

CURSO
  → catálogo GLOBAL e INDEPENDIENTE de la cohorte: 1001-1004 (décimo) y
    1101-1104 (once). El mismo curso se reutiliza cohorte tras cohorte.

ESTUDIANTE (usuario con rol='estudiante')
  → pertenece a un CURSO y a una COHORTE (usuario.curso_id, usuario.cohorte_id)

MATRÍCULA BI
  → usuario.estado_matricula es la ÚNICA fuente de verdad del estado actual.
    NO existe historial de matrícula (decisión de diseño explícita).
    Estados: NO_MATRICULADO, EN_PROCESO, PENDIENTE, MATRICULADO, ACTIVO,
    RETIRADO, FINALIZADO, CANCELADO.
    Todo estudiante nuevo arranca en NO_MATRICULADO (parametrizable a
    futuro si se necesita otro flujo de admisión).

MATERIA
  → catálogo GLOBAL y reutilizable, sin pertenecer a cohorte ni curso.

ASIGNACIÓN ACADÉMICA (tabla curso_materia)
  → MATERIA + CURSO + PROFESOR. Un profesor puede dictar la misma materia
    en varios cursos; distintos cursos de la misma materia pueden tener
    distinto profesor. Es el contexto académico central del sistema.

GRUPO DE ESTUDIO
  → agrupación de estudiantes INDEPENDIENTE del curso (curso ≠ grupo).
    Puede tener contexto opcional (materia, curso, cohorte); si lo tiene,
    solo se pueden agregar estudiantes que pertenezcan a ese contexto.

TAREA
  → asociada a curso_materia_id (no a materia_id suelto), así
    "Matemáticas en 1001" nunca se mezcla con "Matemáticas en 1002".

ENTREGA
  → asociada a TAREA + ESTUDIANTE.

RECURSO
  → general/institucional, o académico específico (materia/curso/
    curso_materia_id opcionales).

CRONOGRAMA
  → eventos en 5 niveles: institucional, cohorte, curso, asignación
    académica (curso_materia_id) o grupo. El nivel se infiere solo según
    qué contexto se cargue.

ESPECIALIDAD
  → Programación de Software, Diseño Multimedia, Ambiental, Administración
    de Empresas. Funciona como un curso (agrupa estudiantes de la cohorte)
    pero con un solo profesor asignado.

VALORACIÓN
  → escala cualitativa IB/MEN: Bajo, Básico, Alto, Superior (no numérica).
    El boletín promedia en escala ordinal (1-4) ponderado por el % de cada
    actividad, y redondea al nivel más cercano.
```

---

## Roles

- **Coordinador**: control administrativo completo. Único rol que puede
  administrar Usuarios, Matrícula BI, Configuración y Parametrización.
- **Profesor**: gestiona únicamente sus propias asignaciones académicas
  (curso_materia donde es el profesor asignado) — sus tareas, entregas,
  recursos y cronograma de esas asignaciones. No puede ver ni administrar
  las de otro profesor, aunque sea la misma materia en otro curso.
- **Estudiante**: ve únicamente lo que corresponde a su curso, cohorte y
  matrícula — sus materias, tareas, valoraciones, recursos y grupos.

---

## Módulos del sistema

| Módulo | Ruta | Descripción |
|---|---|---|
| Dashboard | `/dashboard` | Panel de inicio según rol |
| Cohortes | dentro de `/configuracion` | CRUD de cohortes académicas |
| Cursos | `/cursos` | Catálogo de cursos, detalle por secciones (info/materias/profesores/estudiantes/grupos) |
| Especialidades | `/especialidades` | Programación, Diseño, Ambiental, Administración |
| Materias | `/materias` | Catálogo reutilizable, detalle con cursos donde se dicta |
| Usuarios | `/usuarios` | CRUD de usuarios, filtros combinables (rol/cohorte/curso/estado matrícula), paginado |
| Matrícula BI | `/matricula` | Estadísticas, filtros, cambio de estado — sin historial |
| Grupos de trabajo | `/grupos` | Agrupaciones de estudiantes independientes del curso |
| Tareas | `/tareas` | Ligadas a asignación académica (curso_materia), paginado |
| Valoraciones | `/valoraciones` | Libro de valoraciones Bajo/Básico/Alto/Superior |
| Recursos | `/recursos` | Material de apoyo, general o académico específico, paginado |
| Información (comunicados) | `/comunicados` | Avisos institucionales |
| Cronograma | `/cronograma` | Calendario en 5 niveles de contexto |
| Mensajería | `/mensajeria` | Mensajes directos entre usuarios |
| Archivo Histórico | `/archivo` | Proyectos archivados, búsqueda FULLTEXT, paginado |
| Reportes | `/reportes` | Estadísticas y reportes |
| Configuración | `/configuracion` | Usuarios/materias/grupos/cohortes — gestión del día a día |
| Parametrización | `/parametrizacion` | Módulos del sistema, roles y permisos, ajustes generales — solo coordinador |

---

## Arquitectura técnica

- **Backend**: Flask (Application Factory en `app/__init__.py`), 18 blueprints.
- **Base de datos**: MySQL/MariaDB, sin ORM — SQL directo vía `app/config_db.py`
  (patrón Singleton de conexión).
- **Frontend**: Jinja2 + CSS propio por módulo en `app/static/styles/aplicacion/`.
- **Autenticación**: sesión de Flask (`session['usuario_id']`, `session['rol']`).
- **Permisos**: sistema granular ROL → MÓDULO → ACCIÓN, fail-closed
  (ver sección [Permisos](#permisos)).

---

## Instalación

### Requisitos
- Python 3.10+
- MySQL o MariaDB corriendo localmente (ej. XAMPP)

### Pasos

```bash
# 1. Clonar e instalar dependencias
pip install -r requirements.txt

# 2. Base de datos
#    Abrí phpMyAdmin (http://localhost/phpmyadmin) → pestaña SQL
#    (sin seleccionar ninguna base primero) → pegá TODO
#    app/static/sql/DB.sql → ejecutá.
#    El script hace DROP DATABASE + CREATE DATABASE zoe, así que es
#    seguro re-ejecutarlo para partir de cero.

# 3. Variables de entorno (opcional, ya trae defaults para XAMPP local)
#    Crear app/.env si tu configuración difiere del default:
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=zoe

# 4. Ejecutar
python run.py
# App disponible en http://localhost:5000
```

---

## Estructura del proyecto

```
ZOE_APP/
├── run.py                       # Punto de entrada
├── requirements.txt
└── app/
    ├── __init__.py               # Application factory, registro de blueprints,
    │                              # context processor (modulo_visible, etc.)
    ├── config_db.py               # Conexión Singleton a MySQL/MariaDB
    ├── decorators.py              # login_required, roles_permitidos,
    │                              # modulo_requerido, accion_requerida,
    │                              # eliminacion_segura
    ├── models.py                  # TODAS las clases de modelo (POO, SQL directo)
    ├── blueprints/
    │   ├── auth/                  # Login/logout
    │   ├── dashboard/
    │   ├── cursos/                # CRUD curso + detalle por secciones
    │   ├── especialidades/
    │   ├── materias/              # CRUD + detalle (cursos donde se dicta)
    │   ├── usuarios/              # CRUD, filtros, paginación
    │   ├── matricula/             # Panel de Matrícula BI
    │   ├── grupos/
    │   ├── tareas/                # Ligadas a curso_materia_id
    │   ├── valoraciones/          # Libro de valoraciones
    │   ├── recursos/
    │   ├── comunicados/
    │   ├── cronograma/            # 5 niveles de contexto
    │   ├── mensajeria/
    │   ├── archivo/                # Archivo histórico, búsqueda FULLTEXT
    │   ├── reportes/
    │   ├── configuracion/          # Panel día a día (usuarios/materias/grupos/cohortes)
    │   └── parametrizacion/        # Módulos, permisos, ajustes generales
    ├── templates/aplicacion/       # Un subdirectorio por módulo, espejo de blueprints/
    └── static/
        ├── styles/aplicacion/      # Un .css por módulo + componentes compartidos
        └── sql/DB.sql              # Script completo de base de datos
```

---

## Base de datos

El script `app/static/sql/DB.sql` es la única fuente de verdad del esquema.
Hace `DROP DATABASE IF EXISTS zoe` + `CREATE DATABASE` con
`CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci` y `SET NAMES utf8mb4`
(importante: sin esto, tildes y "ñ" se corrompen al importar).

### Tablas principales (21 en total)

`cohorte`, `curso`, `usuario`, `materia`, `estudiante_grupo`,
`curso_materia`, `especialidad`, `estudiante_especialidad`, `tarea`,
`entrega`, `grupo`, `comunicado`, `recurso`, `cronograma`, `mensaje`,
`actividad_valorativa`, `valoracion_actividad`, `proyecto_archivado`,
`modulo_sistema`, `rol_permiso`, `configuracion_sistema`.

**No existen** (eliminadas deliberadamente durante la reestructuración):
`periodo_academico`, `estudiante_curso`, `estudiante_materia`,
`profesor_materia`, `matriculado`, `matricula_historial`.

---

## Permisos

Sistema granular **ROL → MÓDULO → ACCIÓN**, con **mínimo privilegio
(fail-closed)**: si no existe una fila explícita en `rol_permiso` para una
combinación rol+módulo+acción, se **deniega** (excepto Coordinador, que
siempre puede administrar todo).

Acciones soportadas por módulo (tabla `rol_permiso`, columna `accion`):
`ver`, `crear`, `editar`, `eliminar`, `asignar`, `calificar`,
`cambiar_estado`, `configurar`.

La protección existe **en backend**, en dos capas:

1. `@modulo_requerido('clave')` — el módulo debe estar activo
   (Parametrización → Módulos) y el rol debe tener `ver`.
2. `@accion_requerida('modulo', 'accion')` — el rol debe tener esa acción
   puntual habilitada. Aplicado en las rutas de creación, edición,
   eliminación y asignación de Cursos, Materias, Usuarios, Grupos, Tareas,
   Especialidades y Matrícula.

El Coordinador administra esta matriz completa desde
**Parametrización → Roles y permisos**.

---

## Eliminaciones y Foreign Keys

Cada relación tiene una política explícita y verificada contra una base de
datos real (no solo revisada en el código):

| Política | Se usa cuando... | Ejemplos |
|---|---|---|
| **CASCADE** | El hijo no tiene sentido sin el padre | `curso_materia → tarea → entrega`, `grupo → estudiante_grupo`, `curso → curso_materia` |
| **SET NULL** | La relación es opcional, el hijo sobrevive | `usuario.curso_id`, `recurso.materia_id/curso_id`, `cronograma.materia_id/curso_id/cohorte_id/grupo_id` |
| **RESTRICT** | Eliminar el padre perdería información importante | `usuario.cohorte_id`, `entrega.estudiante_id`, `actividad_valorativa.creado_por`, `proyecto_archivado.creado_por`, todas las FK `creado_por` hacia `usuario` |

Las rutas de eliminación (`@eliminacion_segura`) capturan errores de FK y
muestran un mensaje claro en vez de un error SQL crudo. Además, Curso,
Materia y Cohorte muestran **conteos reales de dependencias antes de
intentar eliminar** (ej: "Este curso tiene 8 estudiantes y 5 asignaciones
académicas").

---

## Notas técnicas y decisiones de diseño

- **Sin historial de matrícula**: decisión explícita. `usuario.estado_matricula`
  es la única fuente de verdad; no hay tabla ni log paralelo.
- **Curso y Materia son catálogos globales**: no dependen de cohorte. Se
  reutilizan año tras año; la cohorte es solo un filtro de contexto.
- **`curso_materia_id` es el contexto académico central**: Tareas, y
  opcionalmente Recursos y Cronograma, se anclan a la asignación completa
  (profesor+materia+curso), nunca solo a `materia_id`.
- **Grupo de estudio ≠ Curso**: un grupo puede tener contexto opcional de
  curso/materia/cohorte, y si lo tiene, solo admite estudiantes de ese
  contexto (`Grupo.es_compatible()`).
- **Encoding**: la conexión usa `utf8mb4`; `DB.sql` incluye `SET NAMES
  utf8mb4` para evitar corrupción de tildes/ñ al importar.

---

## Historial de la reestructuración

ZOE pasó por una reestructuración académica completa, validada contra una
base de datos MySQL/MariaDB real en cada fase (no solo revisión de código).
Resumen de lo implementado, de más antiguo a más reciente:

1. **Cohortes**: reemplazo del concepto de "período académico".
2. **Cursos independientes**: de estar atados a la cohorte pasaron a ser un
   catálogo global reutilizable (1001-1004/1101-1104).
3. **Materias 100% reutilizables**: se les quitó la dependencia de cohorte.
4. **Usuario/Estudiante**: `curso_id` y `estado_matricula` directos, con
   los 8 estados del proceso IB.
5. **Valoraciones cualitativas**: reemplazo de notas numéricas por la
   escala Bajo/Básico/Alto/Superior.
6. **Parametrización**: módulo nuevo para activar/desactivar módulos,
   gestionar permisos y ajustes generales — solo coordinador.
7. **Tareas/Entregas re-ancladas** a `curso_materia_id` (la asignación
   académica completa), cerrando fugas de datos entre cursos.
8. **Permisos granulares** módulo × acción, con verificación real en
   backend (no solo ocultar botones en el frontend).
9. **Recursos y Cronograma** con contexto académico opcional
   (general/institucional vs. específico de una asignación).
10. **Módulo de Matrícula BI** dedicado, con estadísticas y filtros —
    se descartó explícitamente llevar historial: `usuario.estado_matricula`
    es la única fuente de verdad.
11. **Paginación** en los listados que crecen sin límite: Usuarios,
    Archivo Histórico, Tareas, Grupos, Recursos, Cursos, Materias.
12. **Fail-closed en permisos**: se invirtió la regla por defecto de
    "permitir si no hay fila" a "denegar si no hay fila".
13. **Matriz de Foreign Keys revisada por completo** (CASCADE/SET
    NULL/RESTRICT según corresponda en cada relación) y **probada contra
    una base de datos real**, no solo en el código. Se encontraron y
    corrigieron bugs reales en este proceso:
    - `DB.sql` no traía `SET NAMES utf8mb4`, corrompiendo tildes/ñ en
      cualquier importación.
    - `estudiante_grupo` sin restricción `UNIQUE`, permitiendo duplicados.
    - `entrega.tarea_id` y `estudiante_grupo.grupo_id` sin `CASCADE`,
      bloqueando eliminaciones que debían limpiarse en cadena.
    - `actividad_valorativa.creado_por` y `proyecto_archivado.creado_por`
      en `CASCADE`: eliminar un profesor borraba en cascada las
      valoraciones (notas) de sus estudiantes y el archivo histórico.
      Corregido a `RESTRICT`.
14. **Validaciones académicas de backend**: un estudiante no puede entrar
    a un grupo restringido a un curso/cohorte al que no pertenece; un
    profesor no puede crear tareas sobre asignaciones académicas ajenas
    (verificado con pruebas reales, no solo revisión de código).
15. **Auditoría completa de las ~52 rutas POST** del sistema: se
    encontraron y corrigieron 8 rutas (Especialidades, Usuarios, Cursos)
    que tenían protección por rol pero no por acción granular.
