import streamlit as st
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import init_database, migrate_database, obtener_diplomados, verificar_password_diplomado

# Configuración de la página
st.set_page_config(
    page_title="VodsAcademia - Plataforma de Videos",
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

# Inicializar la base de datos
init_database()
migrate_database()

# Intentar recuperar sesión desde query params
try:
    query_params = st.query_params
    if 'diplomado_id' in query_params and 'tipo' in query_params:
        if 'diplomado_id' not in st.session_state or not st.session_state.diplomado_id:
            st.session_state.diplomado_id = int(query_params['diplomado_id'])
            st.session_state.tipo_usuario = query_params['tipo']
except:
    pass

# Inicializar session state
if 'tipo_usuario' not in st.session_state:
    st.session_state.tipo_usuario = None
if 'diplomado_id' not in st.session_state:
    st.session_state.diplomado_id = None
if 'usuario_admin' not in st.session_state:
    st.session_state.usuario_admin = None

def logout():
    """Cierra la sesión actual"""
    st.session_state.tipo_usuario = None
    st.session_state.diplomado_id = None
    st.session_state.usuario_admin = None
    st.query_params.clear()
    st.rerun()

def main():
    """Función principal de la aplicación"""
    
    # Si ya hay sesión iniciada de admin, redirigir
    if st.session_state.tipo_usuario == 'admin':
        st.switch_page("pages/1_admin.py")
    
    # Si ya hay sesión iniciada de alumno, redirigir
    if st.session_state.tipo_usuario == 'alumno' and st.session_state.diplomado_id:
        st.switch_page("pages/2_alumno.py")
    
    # Botón de admin en la esquina superior
    col_space, col_admin = st.columns([9, 1])
    with col_admin:
        if st.button("🔑", help="Acceso Administración", key="btn_admin_top"):
            st.switch_page("pages/1_admin.py")
    
    # Header centrado
    st.title("🎓 VodsAcademia")
    st.markdown("### Calendario de Grabaciones - Academia Intra")
    
    st.markdown("---")
    
    # Acceso con contraseña del diplomado
    st.markdown("## 📚 Acceso a Diplomado")
    
    # Obtener diplomados disponibles
    diplomados = obtener_diplomados()
    
    if diplomados:
        # Centrar el formulario
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            diplomado_opciones = {d['nombre']: d['id'] for d in diplomados}
            
            diplomado_seleccionado = st.selectbox(
                "Selecciona tu Diplomado",
                options=list(diplomado_opciones.keys()),
                key="select_diplomado"
            )
            
            password = st.text_input(
                "Contraseña del Diplomado",
                type="password",
                key="password_diplomado"
            )
            
            st.markdown("")  # Espaciado
            
            if st.button("🔓 Ingresar", type="primary", use_container_width=True):
                if not password:
                    st.error("⚠️ Debes ingresar la contraseña")
                else:
                    diplomado_id = diplomado_opciones[diplomado_seleccionado]
                    if verificar_password_diplomado(diplomado_id, password):
                        st.session_state.tipo_usuario = 'alumno'
                        st.session_state.diplomado_id = diplomado_id
                        st.session_state.diplomado_autenticado = True
                        # Guardar en query params para persistencia
                        st.query_params['diplomado_id'] = str(diplomado_id)
                        st.query_params['tipo'] = 'alumno'
                        st.rerun()
                    else:
                        st.error("❌ Contraseña incorrecta")
    else:
        st.info("📭 No hay diplomados disponibles en este momento.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <small>VodsAcademia © 2025 - Academia Intra</small>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
