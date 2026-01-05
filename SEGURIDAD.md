# ⚠️ CONFIGURACIÓN DE SEGURIDAD

## Antes de subir a GitHub público

### ✅ Lo que YA está protegido:

1. **`.gitignore` configurado** - Excluye:
   - Base de datos (*.db)
   - Script de cambio de contraseña
   - Entorno virtual (.venv)
   
2. **Contraseñas hasheadas** - No se guardan en texto plano

### 🔴 ACCIONES REQUERIDAS antes de hacer push:

1. **Elimina el archivo con tu contraseña:**
   ```bash
   git rm --cached cambiar_password_admin.py
   ```

2. **Verifica que la base de datos NO esté en staging:**
   ```bash
   git status
   ```
   NO debe aparecer `database/vodsacademia.db`

3. **Primer commit seguro:**
   ```bash
   git add .
   git commit -m "Initial commit - VodsAcademia"
   git push origin main
   ```

### 🔐 Después de clonar (para otros usuarios):

1. Inicializar base de datos:
   ```bash
   python database/db_manager.py
   ```

2. Credenciales por defecto:
   - **Admin**: admin / admin123
   - **Cambiar INMEDIATAMENTE**

### 📝 Información que SÍ es segura compartir:

- ✅ Código fuente de la aplicación
- ✅ Estructura del proyecto
- ✅ Funciones de hash (SHA256)
- ✅ Lógica de autenticación

### ❌ Información que NUNCA se debe compartir:

- ❌ Base de datos con contraseñas reales
- ❌ Scripts con contraseñas hardcodeadas
- ❌ Contraseñas de diplomados de producción
- ❌ Información personal de estudiantes

### 🛡️ Recomendaciones adicionales:

1. **Para producción** - Considera usar:
   - Variables de entorno para configuración
   - Base de datos en servidor separado
   - HTTPS obligatorio
   - Autenticación de dos factores para admin

2. **Si tienes datos reales**:
   - Haz backup de tu base de datos actual
   - Crea una base de datos de demostración vacía
   - Nunca commitees datos personales

3. **En el README**:
   - Documenta cómo configurar desde cero
   - Advierte sobre cambiar contraseñas por defecto
   - Incluye sección de seguridad

### ✅ Checklist antes de hacer público:

- [ ] `.gitignore` incluye `*.db` y `cambiar_password_admin.py`
- [ ] No hay contraseñas reales en el código
- [ ] Base de datos NO está en el repositorio
- [ ] README incluye instrucciones de configuración
- [ ] README advierte sobre seguridad
- [ ] Has probado clonar en carpeta nueva y configurar desde cero

### 🚀 Para compartir versión de demostración:

Si quieres incluir datos de ejemplo, crea un script separado:

```python
# demo_setup.py
from database.db_manager import init_database, crear_diplomado, crear_modulo

init_database()
# Crea datos de ejemplo (NO reales)
crear_diplomado("Diplomado Demo", "Ejemplo de demostración", "demo123")
print("✅ Base de datos de demostración creada")
```

---

**RESUMEN**: El código es seguro para compartir, pero NUNCA subas:
- La base de datos (.db)
- Scripts con contraseñas reales
- Información personal o de producción
