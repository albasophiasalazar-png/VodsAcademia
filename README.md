# VodsAcademia

Sistema de gestión de videos para diplomados de Academia Intra.

## Características

- **Autenticación por diplomado**: Cada diplomado tiene su contraseña única
- **Panel de administración**: Gestiona diplomados, módulos y clases
- **Videos protegidos**: Embed de OneDrive que evita descargas
- **Organización por módulos**: Clases organizadas por módulos dentro de cada diplomado

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
streamlit run app.py
```

## Roles

- **Admin**: Usuario y contraseña para gestionar todo el contenido
- **Alumno**: Acceso con contraseña específica del diplomado

## Base de datos

SQLite con las siguientes tablas:
- `diplomados`: Información de cada diplomado
- `modulos`: Módulos dentro de cada diplomado
- `clases`: Clases con URLs de videos de OneDrive
- `usuarios_admin`: Credenciales de administradores
