"""
Script para cambiar la contraseña del administrador
"""
from database.db_manager import get_connection, hash_password

def cambiar_password_admin(nueva_password):
    """Cambia la contraseña del usuario admin"""
    conn = get_connection()
    cursor = conn.cursor()
    
    password_hash = hash_password(nueva_password)
    
    cursor.execute("""
    UPDATE usuarios_admin 
    SET password_hash = ? 
    WHERE usuario = 'admin'
    """, (password_hash,))
    
    conn.commit()
    
    if cursor.rowcount > 0:
        print(f"✅ Contraseña de admin actualizada correctamente")
        print(f"   Usuario: admin")
        print(f"   Nueva contraseña: {nueva_password}")
    else:
        print("❌ No se encontró el usuario admin")
    
    conn.close()

if __name__ == "__main__":
    # Nueva contraseña
    nueva_password = "2!fkYgD&"
    cambiar_password_admin(nueva_password)
