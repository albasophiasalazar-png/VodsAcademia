import streamlit as st
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import obtener_diplomado, obtener_modulos, obtener_clases, verificar_password_modulo
from utils.helpers import formatear_fecha

st.set_page_config(
    page_title="Mis Clases - VodsAcademia",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ocultar completamente el sidebar con CSS y centrar títulos
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="collapsedControl"] {
            display: none;
        }
        h1, h2, h3 {
            text-align: center;
        }
        .stMarkdown h1 {
            padding: 1rem 0;
        }
        .stMarkdown h2 {
            padding: 0.8rem 0;
        }
        .stMarkdown h3 {
            padding: 0.5rem 0;
        }
    </style>
""", unsafe_allow_html=True)

def logout():
    """Cierra la sesión"""
    st.session_state.tipo_usuario = None
    st.session_state.diplomado_id = None
    st.query_params.clear()
    st.switch_page("app.py")



def main():
    """Función principal de la vista de alumno"""
    
    # Intentar recuperar sesión desde query params si no hay en session_state
    if not st.session_state.get('tipo_usuario'):
        try:
            query_params = st.query_params
            if 'diplomado_id' in query_params and 'tipo' in query_params:
                st.session_state.diplomado_id = int(query_params['diplomado_id'])
                st.session_state.tipo_usuario = query_params['tipo']
        except:
            pass
    
    # Verificar si hay sesión de alumno
    if st.session_state.get('tipo_usuario') != 'alumno':
        st.warning("⚠️ Debes iniciar sesión primero")
        if st.button("← Volver al inicio"):
            st.switch_page("app.py")
        return
    
    # Obtener información del diplomado
    diplomado_id = st.session_state.diplomado_id
    diplomado = obtener_diplomado(diplomado_id)
    
    if not diplomado:
        st.error("Error: Diplomado no encontrado")
        logout()
        return
    
    # Header con título y botón de cerrar sesión
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title(f"🎓 {diplomado['nombre']}")
        if diplomado['descripcion']:
            st.markdown(diplomado['descripcion'])
    with col2:
        st.markdown("")  # Espaciado
        if st.button("🚪 Cerrar Sesión"):
            logout()
    
    st.markdown("---")
    
    # Contenido principal
    modulos = obtener_modulos(diplomado_id)
    
    if not modulos:
        st.info("📭 No hay módulos disponibles en este diplomado aún.")
        return
    
    # Selector de módulos en el contenido principal
    st.markdown("### 📚 Selecciona un Módulo")
    
    # Inicializar session_state para módulos autenticados
    if 'modulos_autenticados' not in st.session_state:
        st.session_state.modulos_autenticados = set()
    
    # Almacenar el módulo seleccionado en session_state
    if 'modulo_seleccionado' not in st.session_state:
        st.session_state.modulo_seleccionado = modulos[0]['id']
    
    # Crear tabs o botones para módulos
    modulo_nombres = [f"📂 {m['nombre']}" for m in modulos]
    modulo_ids = [m['id'] for m in modulos]
    
    # Encontrar el índice del módulo actual
    try:
        idx_actual = modulo_ids.index(st.session_state.modulo_seleccionado)
    except ValueError:
        idx_actual = 0
        st.session_state.modulo_seleccionado = modulo_ids[0]
    
    # Crear columnas para los módulos
    num_modulos = len(modulos)
    cols_modulos = st.columns(num_modulos if num_modulos <= 5 else 5)
    
    for idx, (modulo, col) in enumerate(zip(modulos, cols_modulos if num_modulos <= 5 else cols_modulos * (num_modulos // 5 + 1))):
        if idx < num_modulos:
            with col:
                clases_count = len(obtener_clases(modulo['id']))
                es_seleccionado = modulo['id'] == st.session_state.modulo_seleccionado
                esta_autenticado = modulo['id'] in st.session_state.modulos_autenticados
                
                # Mostrar icono de candado si no está autenticado
                icono = "📂" if esta_autenticado else "🔒"
                
                if st.button(
                    f"{icono} {modulo['nombre']}\n({clases_count} clases)",
                    key=f"btn_mod_{modulo['id']}",
                    type="primary" if es_seleccionado else "secondary",
                    use_container_width=True
                ):
                    st.session_state.modulo_seleccionado = modulo['id']
                    # Resetear la clase seleccionada al cambiar de módulo
                    if 'clase_seleccionada' in st.session_state:
                        del st.session_state.clase_seleccionada
                    st.rerun()
    
    st.markdown("---")
    
    # Obtener módulo seleccionado
    modulo_actual = None
    for m in modulos:
        if m['id'] == st.session_state.modulo_seleccionado:
            modulo_actual = m
            break
    
    if not modulo_actual:
        modulo_actual = modulos[0]
        st.session_state.modulo_seleccionado = modulo_actual['id']
    
    # Verificar si el módulo está autenticado
    modulo_autenticado = modulo_actual['id'] in st.session_state.modulos_autenticados
    
    # Mostrar información del módulo
    st.markdown(f"## 📂 {modulo_actual['nombre']}")
    
    if modulo_actual['descripcion']:
        st.markdown(f"*{modulo_actual['descripcion']}*")
    
    st.markdown("---")
    
    # Si el módulo no está autenticado, mostrar formulario de contraseña
    if not modulo_autenticado:
        st.markdown("### 🔐 Autenticación Requerida")
        st.info("Este módulo requiere contraseña para acceder a su contenido.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            password_modulo = st.text_input(
                "Contraseña del Módulo",
                type="password",
                key=f"pass_mod_{modulo_actual['id']}"
            )
            
            if st.button("🔓 Desbloquear Módulo", type="primary", use_container_width=True):
                if not password_modulo:
                    st.error("⚠️ Debes ingresar la contraseña")
                else:
                    if verificar_password_modulo(modulo_actual['id'], password_modulo):
                        st.session_state.modulos_autenticados.add(modulo_actual['id'])
                        st.success("✅ Módulo desbloqueado")
                        st.rerun()
                    else:
                        st.error("❌ Contraseña incorrecta")
        
        # Mostrar solo las fechas de las sesiones (sin contenido)
        st.markdown("---")
        st.markdown("### 📅 Sesiones Programadas (Vista Previa)")
        st.info("🔒 Desbloquea el módulo para acceder al contenido completo de las sesiones")
        
        clases = obtener_clases(modulo_actual['id'])
        
        if clases:
            for clase in clases:
                fecha_mostrar = formatear_fecha(clase.get('fecha_sesion'))
                numero_sesion = clase.get('numero_sesion', clase.get('orden', ''))
                
                col_fecha, col_nombre = st.columns([1, 3])
                with col_fecha:
                    st.markdown(f"**📅 {fecha_mostrar}**")
                with col_nombre:
                    st.markdown(f"**Sesión {numero_sesion}:** {clase['nombre']}")
        else:
            st.info("📭 No hay sesiones disponibles en este módulo aún.")
        
        return
    
    # Si el módulo está autenticado, mostrar el contenido completo
    # Obtener clases del módulo
    clases = obtener_clases(modulo_actual['id'])
    
    if not clases:
        st.info("📭 No hay sesiones disponibles en este módulo aún.")
        return
    
    # Mostrar lista de sesiones como calendario
    st.markdown("### 📅 Sesiones Programadas")
    
    for clase in clases:
        fecha_mostrar = formatear_fecha(clase.get('fecha_sesion'))
        numero_sesion = clase.get('numero_sesion', clase.get('orden', ''))
        
        # Crear fila con información de la sesión y botón
        col_info, col_boton = st.columns([4, 1])
        
        with col_info:
            st.markdown(f"**Sesión {numero_sesion}: {clase['nombre']}**")
            st.markdown(f"📅 {fecha_mostrar}")
            if clase['descripcion']:
                st.markdown(f"*{clase['descripcion']}*")
        
        with col_boton:
            # Verificar si hay URL de video
            if clase['url_video'] and clase['url_video'].strip():
                url_video = clase['url_video'].strip()
                # Crear botón HTML personalizado que abre en nueva pestaña
                button_html = f"""
                    <div style="display: flex; align-items: center; height: 100%; padding-top: 8px;">
                        <a href="{url_video}" target="_blank" style="text-decoration: none; width: 100%;">
                            <button style="
                                background-color: #FF4B4B;
                                color: white;
                                padding: 10px 20px;
                                font-size: 16px;
                                font-weight: 600;
                                border: none;
                                border-radius: 8px;
                                cursor: pointer;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                transition: all 0.3s ease;
                                width: 100%;
                            " onmouseover="this.style.backgroundColor='#E63946'; this.style.transform='scale(1.05)';" 
                               onmouseout="this.style.backgroundColor='#FF4B4B'; this.style.transform='scale(1)';">
                                🎬 Ver Grabación
                            </button>
                        </a>
                    </div>
                """
                st.markdown(button_html, unsafe_allow_html=True)
            else:
                st.markdown("<div style='padding-top: 8px;'><em>📹 Próximamente</em></div>", unsafe_allow_html=True)
        
        st.markdown("---")

if __name__ == "__main__":
    main()
