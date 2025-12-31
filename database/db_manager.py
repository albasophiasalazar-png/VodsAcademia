import sqlite3
import hashlib
import os

DATABASE_PATH = "database/vodsacademia.db"

def get_connection():
    """Crea y retorna una conexión a la base de datos"""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Hashea una contraseña usando SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_database():
    """Inicializa la base de datos con todas las tablas"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabla de diplomados
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS diplomados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        descripcion TEXT,
        password_hash TEXT NOT NULL,
        activo INTEGER DEFAULT 1,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Tabla de módulos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS modulos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        diplomado_id INTEGER NOT NULL,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        orden INTEGER DEFAULT 0,
        FOREIGN KEY (diplomado_id) REFERENCES diplomados(id) ON DELETE CASCADE
    )
    """)
    
    # Tabla de clases (sesiones)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        modulo_id INTEGER NOT NULL,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        url_video TEXT NOT NULL,
        orden INTEGER DEFAULT 0,
        numero_sesion INTEGER,
        fecha_sesion DATE,
        duracion TEXT,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (modulo_id) REFERENCES modulos(id) ON DELETE CASCADE
    )
    """)
    
    # Tabla de usuarios admin
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios_admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        nombre_completo TEXT,
        activo INTEGER DEFAULT 1,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Crear usuario admin por defecto si no existe
    cursor.execute("SELECT COUNT(*) as count FROM usuarios_admin")
    if cursor.fetchone()['count'] == 0:
        default_password = hash_password("admin123")
        cursor.execute("""
        INSERT INTO usuarios_admin (usuario, password_hash, nombre_completo)
        VALUES (?, ?, ?)
        """, ("admin", default_password, "Administrador"))
        print("✅ Usuario admin creado - Usuario: admin, Contraseña: admin123")
    
    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada correctamente")

def migrate_database():
    """Aplica migraciones necesarias a la base de datos existente"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar si las columnas fecha_sesion y numero_sesion ya existen
    cursor.execute("PRAGMA table_info(clases)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Migración: Agregar fecha_sesion y numero_sesion si no existen
    if 'fecha_sesion' not in columns:
        print("🔄 Agregando columna fecha_sesion...")
        cursor.execute("ALTER TABLE clases ADD COLUMN fecha_sesion DATE")
        print("✅ Columna fecha_sesion agregada")
    
    if 'numero_sesion' not in columns:
        print("🔄 Agregando columna numero_sesion...")
        cursor.execute("ALTER TABLE clases ADD COLUMN numero_sesion INTEGER")
        print("✅ Columna numero_sesion agregada")
    
    conn.commit()
    conn.close()
    print("✅ Migraciones aplicadas correctamente")

# Funciones para usuarios admin
def verificar_admin(usuario, password):
    """Verifica las credenciales de un administrador"""
    conn = get_connection()
    cursor = conn.cursor()
    password_hash = hash_password(password)
    
    cursor.execute("""
    SELECT * FROM usuarios_admin 
    WHERE usuario = ? AND password_hash = ? AND activo = 1
    """, (usuario, password_hash))
    
    admin = cursor.fetchone()
    conn.close()
    return admin is not None

# Funciones para diplomados
def crear_diplomado(nombre, descripcion, password):
    """Crea un nuevo diplomado"""
    conn = get_connection()
    cursor = conn.cursor()
    password_hash = hash_password(password)
    
    try:
        cursor.execute("""
        INSERT INTO diplomados (nombre, descripcion, password_hash)
        VALUES (?, ?, ?)
        """, (nombre, descripcion, password_hash))
        conn.commit()
        diplomado_id = cursor.lastrowid
        conn.close()
        return diplomado_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def obtener_diplomados():
    """Obtiene todos los diplomados activos"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM diplomados WHERE activo = 1 ORDER BY nombre")
    diplomados = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return diplomados

def obtener_diplomado(diplomado_id):
    """Obtiene un diplomado por ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM diplomados WHERE id = ?", (diplomado_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def verificar_password_diplomado(diplomado_id, password):
    """Verifica la contraseña de un diplomado"""
    conn = get_connection()
    cursor = conn.cursor()
    password_hash = hash_password(password)
    
    cursor.execute("""
    SELECT * FROM diplomados 
    WHERE id = ? AND password_hash = ? AND activo = 1
    """, (diplomado_id, password_hash))
    
    diplomado = cursor.fetchone()
    conn.close()
    return diplomado is not None

def actualizar_diplomado(diplomado_id, nombre, descripcion, password=None):
    """Actualiza un diplomado"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if password:
        password_hash = hash_password(password)
        cursor.execute("""
        UPDATE diplomados 
        SET nombre = ?, descripcion = ?, password_hash = ?
        WHERE id = ?
        """, (nombre, descripcion, password_hash, diplomado_id))
    else:
        cursor.execute("""
        UPDATE diplomados 
        SET nombre = ?, descripcion = ?
        WHERE id = ?
        """, (nombre, descripcion, diplomado_id))
    
    conn.commit()
    conn.close()

def eliminar_diplomado(diplomado_id):
    """Desactiva un diplomado"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE diplomados SET activo = 0 WHERE id = ?", (diplomado_id,))
    conn.commit()
    conn.close()

# Funciones para módulos
def crear_modulo(diplomado_id, nombre, descripcion, orden):
    """Crea un nuevo módulo"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO modulos (diplomado_id, nombre, descripcion, orden)
    VALUES (?, ?, ?, ?)
    """, (diplomado_id, nombre, descripcion, orden))
    conn.commit()
    modulo_id = cursor.lastrowid
    conn.close()
    return modulo_id

def obtener_modulos(diplomado_id):
    """Obtiene todos los módulos de un diplomado"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM modulos 
    WHERE diplomado_id = ? 
    ORDER BY orden, nombre
    """, (diplomado_id,))
    modulos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return modulos

def actualizar_modulo(modulo_id, nombre, descripcion, orden):
    """Actualiza un módulo"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE modulos 
    SET nombre = ?, descripcion = ?, orden = ?
    WHERE id = ?
    """, (nombre, descripcion, orden, modulo_id))
    conn.commit()
    conn.close()

def eliminar_modulo(modulo_id):
    """Elimina un módulo"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM modulos WHERE id = ?", (modulo_id,))
    conn.commit()
    conn.close()

# Funciones para clases (sesiones)
def crear_clase(modulo_id, nombre, descripcion, url_video, numero_sesion, fecha_sesion):
    """Crea una nueva clase/sesión"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO clases (modulo_id, nombre, descripcion, url_video, numero_sesion, fecha_sesion, orden)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (modulo_id, nombre, descripcion, url_video, numero_sesion, fecha_sesion, numero_sesion))
    conn.commit()
    clase_id = cursor.lastrowid
    conn.close()
    return clase_id

def obtener_clases(modulo_id):
    """Obtiene todas las clases de un módulo ordenadas por fecha"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM clases 
    WHERE modulo_id = ? 
    ORDER BY fecha_sesion DESC, numero_sesion DESC
    """, (modulo_id,))
    clases = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return clases

def obtener_clase(clase_id):
    """Obtiene una clase por ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clases WHERE id = ?", (clase_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def actualizar_clase(clase_id, nombre, descripcion, url_video, numero_sesion, fecha_sesion):
    """Actualiza una clase/sesión"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE clases 
    SET nombre = ?, descripcion = ?, url_video = ?, numero_sesion = ?, fecha_sesion = ?, orden = ?
    WHERE id = ?
    """, (nombre, descripcion, url_video, numero_sesion, fecha_sesion, numero_sesion, clase_id))
    conn.commit()
    conn.close()

def eliminar_clase(clase_id):
    """Elimina una clase"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clases WHERE id = ?", (clase_id,))
    conn.commit()
    conn.close()

def mover_clase_a_modulo(clase_id, nuevo_modulo_id):
    """Mueve una clase a otro módulo"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE clases 
    SET modulo_id = ? 
    WHERE id = ?
    """, (nuevo_modulo_id, clase_id))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
    migrate_database()
