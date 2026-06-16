# 🚀 Configuración de Base de Datos - ZOE

## ✅ Estado de Implementación

La plataforma ZOE ha sido **conectada exitosamente a la BD MySQL en XAMPP**.

### Componentes Implementados:

1. **app/config_db.py** ✅
   - Configuración de conexión a MySQL
   - Variables de entorno desde .env
   - Configuración de sesiones Flask
   - URL de conexión: `mysql+pymysql://root@localhost:3306/zoe`

2. **app/models.py** ✅
   - 10 modelos SQLAlchemy mapeados a 13 tablas
   - Relaciones many-to-many funcionando
   - Campos con valores NULL permitidos (compatible con datos existentes)

3. **app/main.py** ✅
   - Integración completa con SQLAlchemy
   - 40+ rutas actualizadas a consultas de BD
   - Función `init_db()` para inicializar tablas y datos
   - Manejo de sesiones mejorado con `werkzeug.security`

4. **.env** ✅
   - Archivo de configuración con credenciales
   - Variables: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

5. **test_db_connection.py** ✅
   - Script de prueba que verifica conexión
   - Muestra estadísticas de la BD
   - Resultado: ✅ CONEXIÓN EXITOSA

---

## 📊 Base de Datos Actual

### Información de Conexión:
- **Host**: localhost:3306
- **BD**: zoe
- **Usuario**: root
- **Contraseña**: (vacía - XAMPP por defecto)
- **Estado**: ✅ ACTIVA Y OPERATIVA

### Tablas (13):
```
✅ periodo_academico      (períodos académicos)
✅ usuario                 (14 usuarios - admin, profesores, estudiantes)
✅ materia                 (5 materias)
✅ grupo                   (5 grupos de estudiantes)
✅ tarea                   (5 tareas/asignaciones)
✅ entrega                 (entregas de tareas)
✅ recurso                 (recursos educativos)
✅ cronograma              (eventos/calendario)
✅ mensaje                 (sistema de mensajería)
✅ comunicado              (anuncios/comunicados)
✅ profesor_materia        (relación profesor-materia)
✅ estudiante_grupo        (relación estudiante-grupo)
✅ estudiante_materia      (relación estudiante-materia)
```

### Usuarios Existentes:
```
🔹 ADMIN: Carlos Mendoza (cmendoza@universidad.edu)
🔹 PROFESORES:
   - Laura Gómez (lgomez@universidad.edu)
   - Andrés Torres (atorres@universidad.edu)
   - Sofía Ramírez (sramirez@universidad.edu)
🔹 ESTUDIANTES: 10 usuarios de estudiantes registrados
```

---

## 🚀 Iniciar el Servidor

### Opción 1: Desde la raíz del proyecto
```bash
python app/main.py
```

### Opción 2: Desde la carpeta app
```bash
cd app
python main.py
```

### Acceder a la aplicación:
- **URL**: http://127.0.0.1:5000
- **Puerto**: 5000
- **Debug**: Activo (mode=development)

---

## 🔐 Credenciales de Prueba

### Login de ejemplo con usuarios existentes:
- **Email**: cmendoza@universidad.edu
- **Contraseña**: *contraseña hasheada en la BD*

*Nota: Las contraseñas están hasheadas. Para cambiarlas, usar werkzeug.security*

---

## 📝 Rutas Disponibles

### Públicas:
- `GET  /` - Página de inicio
- `GET  /programa-pop` - Información del programa
- `GET  /estructura` - Estructura de ZOE
- `GET  /ques` - ¿Qué es ZOE?

### Autenticación:
- `GET/POST /login` - Formulario de login
- `GET /logout` - Cerrar sesión

### Aplicación (requieren autenticación):
- `GET /dashboard` - Dashboard principal
- `GET /tareas` - Lista de tareas
- `GET /mensajeria` - Sistema de mensajes
- `GET /cronograma` - Cronograma/calendario
- `GET /recursos` - Recursos educativos
- `GET /informacion` - Comunicados
- `GET /materias` - Listado de materias
- `GET /grupos` - Listado de grupos
- `GET /usuarios` - Gestión de usuarios
- `GET /configuracion` - Configuración del sistema

### Formularios (CRUD):
- `GET/POST /formularios/crear-usuario`
- `GET/POST /formularios/crear-materia`
- `GET/POST /formularios/crear-grupo`
- `GET/POST /formularios/crear-tarea`
- `GET/POST /formularios/crear-recurso`
- `GET/POST /formularios/crear-periodo`

### APIs REST:
- `GET /api/materias` - Obtener materias en JSON
- `GET /api/grupos/<materia_id>` - Obtener grupos de una materia
- `GET /api/usuarios` - Obtener usuarios en JSON

### Health Check:
- `GET /health` - Verificar estado del servidor

---

## 🔧 Configuración Importante

### Variables de Entorno (.env):
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=zoe
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=zoe-desarrollo-cambiar-en-produccion
```

### Dependencias Instaladas:
```
✅ flask==3.0.0
✅ flask-sqlalchemy==3.1.1
✅ pymysql==1.1.0
✅ python-dotenv==1.0.0
✅ werkzeug==3.0.0 (incluye security)
```

---

## 📋 Próximos Pasos

### Fase 2: Migración a Jinja2
- [ ] Convertir HTML mock a templates dinámicos
- [ ] Pasar datos desde rutas a templates con {{ variable }}
- [ ] Utilizar {% for %} loops en lugar de HTML estático

### Fase 3: Mejoras Visuales
- [ ] Diseño moderno SaaS
- [ ] Bordes suaves, sombras discretas
- [ ] Tablas y formularios modernos
- [ ] Responsivo en móvil

### Fase 4: Funcionalidades Avanzadas
- [ ] Búsqueda y filtrado
- [ ] Paginación de resultados
- [ ] Upload de archivos
- [ ] Notificaciones en tiempo real

---

## ❓ Solución de Problemas

### Si XAMPP no está corriendo:
```
1. Abre XAMPP Control Panel
2. Haz clic en "Start" para Apache y MySQL
3. Verifica que MySQL esté activo en http://localhost/phpmyadmin
```

### Si la conexión falla:
```
1. Verifica credenciales en .env
2. Comprueba que la BD "zoe" existe
3. Ejecuta: python test_db_connection.py
4. Revisa los logs de MySQL en XAMPP
```

### Si hay error de módulos:
```bash
pip install -r requirements.txt
```

---

**Última actualización**: 2026-06-16  
**Estado**: ✅ OPERATIVO  
**Conexión BD**: ✅ EXITOSA  
