import streamlit as st
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import (
    verificar_admin, crear_diplomado, obtener_diplomados, actualizar_diplomado,
    eliminar_diplomado, crear_modulo, obtener_modulos, actualizar_modulo,
    eliminar_modulo, crear_clase, obtener_clases, actualizar_clase, eliminar_clase,
    mover_clase_a_modulo
)
from utils.helpers import extraer_url_de_iframe, formatear_fecha

st.set_page_config(
    page_title="Panel Admin - VodsAcademia",
    page_icon="👨‍💼",
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
    st.session_state.usuario_admin = None
    st.switch_page("app.py")

def login_admin():
    """Pantalla de login para administradores"""
    st.title("🔑 Panel de Administración")
    
    with st.form("login_form"):
        password = st.text_input("Contraseña de Administrador", type="password", placeholder="Ingresa la contraseña")
        submit = st.form_submit_button("Iniciar Sesión", type="primary", use_container_width=True)
        
        if submit:
            # Usuario por defecto es "admin"
            if verificar_admin("admin", password):
                st.session_state.tipo_usuario = 'admin'
                st.session_state.usuario_admin = "admin"
                st.success("✅ Sesión iniciada correctamente")
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")
    
    if st.button("← Volver al inicio"):
        st.switch_page("app.py")

def gestionar_diplomados():
    """Sección para gestionar diplomados"""
    st.header("📚 Gestión de Diplomados")
    
    # Inicializar contador para resetear formulario
    if 'form_diplomado_counter' not in st.session_state:
        st.session_state.form_diplomado_counter = 0
    
    # Crear nuevo diplomado
    with st.expander("➕ Crear Nuevo Diplomado", expanded=False):
        with st.form(f"form_nuevo_diplomado_{st.session_state.form_diplomado_counter}"):
            nombre = st.text_input("Nombre del Diplomado*")
            descripcion = st.text_area("Descripción")
            password = st.text_input("Contraseña de Acceso*", type="password")
            password_confirm = st.text_input("Confirmar Contraseña*", type="password")
            
            submit = st.form_submit_button("Crear Diplomado", type="primary")
            
            if submit:
                if not nombre or not password:
                    st.error("El nombre y la contraseña son obligatorios")
                elif password != password_confirm:
                    st.error("Las contraseñas no coinciden")
                else:
                    diplomado_id = crear_diplomado(nombre, descripcion, password)
                    if diplomado_id:
                        st.success(f"✅ Diplomado '{nombre}' creado correctamente")
                        st.session_state.form_diplomado_counter += 1
                        st.rerun()
                    else:
                        st.error("Ya existe un diplomado con ese nombre")
    
    # Listar diplomados existentes
    diplomados = obtener_diplomados()
    
    if diplomados:
        st.markdown("### Diplomados Existentes")
        
        for diplomado in diplomados:
            with st.expander(f"📖 {diplomado['nombre']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Descripción:** {diplomado['descripcion'] or 'Sin descripción'}")
                    st.markdown(f"**Fecha creación:** {diplomado['fecha_creacion']}")
                    
                    # Contar módulos y clases
                    modulos = obtener_modulos(diplomado['id'])
                    total_clases = sum(len(obtener_clases(m['id'])) for m in modulos)
                    st.markdown(f"**Módulos:** {len(modulos)} | **Clases:** {total_clases}")
                
                with col2:
                    if st.button("🗑️ Eliminar", key=f"del_dip_{diplomado['id']}"):
                        eliminar_diplomado(diplomado['id'])
                        st.success("Diplomado eliminado")
                        st.rerun()
                
                # Editar diplomado
                with st.form(f"form_edit_dip_{diplomado['id']}"):
                    st.markdown("**Editar Diplomado**")
                    nuevo_nombre = st.text_input("Nombre", value=diplomado['nombre'], key=f"nombre_{diplomado['id']}")
                    nueva_desc = st.text_area("Descripción", value=diplomado['descripcion'] or "", key=f"desc_{diplomado['id']}")
                    nueva_pass = st.text_input("Nueva Contraseña (dejar vacío para mantener)", type="password", key=f"pass_{diplomado['id']}")
                    
                    if st.form_submit_button("💾 Guardar Cambios"):
                        actualizar_diplomado(diplomado['id'], nuevo_nombre, nueva_desc, nueva_pass if nueva_pass else None)
                        st.success("Cambios guardados")
                        st.rerun()
    else:
        st.info("No hay diplomados creados aún.")

def gestionar_modulos():
    """Sección para gestionar módulos"""
    st.header("📑 Gestión de Módulos")
    
    diplomados = obtener_diplomados()
    
    if not diplomados:
        st.warning("Primero debes crear un diplomado")
        return
    
    # Seleccionar diplomado
    diplomado_opciones = {d['nombre']: d['id'] for d in diplomados}
    diplomado_seleccionado = st.selectbox(
        "Selecciona un Diplomado",
        options=list(diplomado_opciones.keys()),
        key="select_dip_modulo"
    )
    diplomado_id = diplomado_opciones[diplomado_seleccionado]
    
    # Inicializar contador para resetear formulario
    if 'form_modulo_counter' not in st.session_state:
        st.session_state.form_modulo_counter = 0
    
    # Crear nuevo módulo
    with st.expander("➕ Crear Nuevo Módulo", expanded=False):
        with st.form(f"form_nuevo_modulo_{st.session_state.form_modulo_counter}"):
            nombre = st.text_input("Nombre del Módulo*")
            descripcion = st.text_area("Descripción")
            orden = st.number_input("Orden", min_value=0, value=0, step=1)
            
            submit = st.form_submit_button("Crear Módulo", type="primary")
            
            if submit:
                if not nombre:
                    st.error("El nombre es obligatorio")
                else:
                    crear_modulo(diplomado_id, nombre, descripcion, orden)
                    st.success(f"✅ Módulo '{nombre}' creado correctamente")
                    st.session_state.form_modulo_counter += 1
                    st.rerun()
    
    # Listar módulos
    modulos = obtener_modulos(diplomado_id)
    
    if modulos:
        st.markdown("### Módulos Existentes")
        
        for modulo in modulos:
            with st.expander(f"📂 {modulo['nombre']} (Orden: {modulo['orden']})", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Descripción:** {modulo['descripcion'] or 'Sin descripción'}")
                    
                    # Contar clases
                    clases = obtener_clases(modulo['id'])
                    st.markdown(f"**Clases:** {len(clases)}")
                
                with col2:
                    if st.button("🗑️ Eliminar", key=f"del_mod_{modulo['id']}"):
                        eliminar_modulo(modulo['id'])
                        st.success("Módulo eliminado")
                        st.rerun()
                
                # Editar módulo
                with st.form(f"form_edit_mod_{modulo['id']}"):
                    st.markdown("**Editar Módulo**")
                    nuevo_nombre = st.text_input("Nombre", value=modulo['nombre'], key=f"nombre_mod_{modulo['id']}")
                    nueva_desc = st.text_area("Descripción", value=modulo['descripcion'] or "", key=f"desc_mod_{modulo['id']}")
                    nuevo_orden = st.number_input("Orden", value=modulo['orden'], min_value=0, key=f"orden_mod_{modulo['id']}")
                    
                    if st.form_submit_button("💾 Guardar Cambios"):
                        actualizar_modulo(modulo['id'], nuevo_nombre, nueva_desc, nuevo_orden)
                        st.success("Cambios guardados")
                        st.rerun()
    else:
        st.info("No hay módulos creados para este diplomado.")

def gestionar_clases():
    """Sección para gestionar clases"""
    st.header("🎥 Gestión de Clases")
    
    diplomados = obtener_diplomados()
    
    if not diplomados:
        st.warning("Primero debes crear un diplomado")
        return
    
    # Seleccionar diplomado
    diplomado_opciones = {d['nombre']: d['id'] for d in diplomados}
    diplomado_seleccionado = st.selectbox(
        "Selecciona un Diplomado",
        options=list(diplomado_opciones.keys()),
        key="select_dip_clase"
    )
    diplomado_id = diplomado_opciones[diplomado_seleccionado]
    
    modulos = obtener_modulos(diplomado_id)
    
    if not modulos:
        st.warning("Primero debes crear módulos para este diplomado")
        return
    
    # Seleccionar módulo
    modulo_opciones = {m['nombre']: m['id'] for m in modulos}
    modulo_seleccionado = st.selectbox(
        "Selecciona un Módulo",
        options=list(modulo_opciones.keys()),
        key="select_mod_clase"
    )
    modulo_id = modulo_opciones[modulo_seleccionado]
    
    # Inicializar contador para resetear formulario
    if 'form_clase_counter' not in st.session_state:
        st.session_state.form_clase_counter = 0
    
    # Crear sesiones masivas
    with st.expander("➕➕ Crear Sesiones Masivas", expanded=False):
        st.markdown("**Crea múltiples sesiones de una vez (sin descripción ni video)**")
        
        with st.form("form_sesiones_masivas"):
            col1, col2 = st.columns(2)
            
            with col1:
                cantidad_sesiones = st.number_input(
                    "¿Cuántas sesiones crear?*",
                    min_value=1,
                    max_value=50,
                    value=5,
                    step=1,
                    help="Número total de sesiones a crear"
                )
            
            with col2:
                numero_inicio = st.number_input(
                    "¿En qué número inician?*",
                    min_value=1,
                    value=1,
                    step=1,
                    help="Número de la primera sesión"
                )
            
            st.markdown(f"**Se crearán {cantidad_sesiones} sesiones: desde la {numero_inicio} hasta la {numero_inicio + cantidad_sesiones - 1}**")
            
            st.markdown("---")
            st.markdown("**Ingresa los datos para cada sesión:**")
            
            # Crear campos dinámicos para cada sesión
            sesiones_data = []
            for i in range(int(cantidad_sesiones)):
                numero_sesion = int(numero_inicio) + i
                st.markdown(f"### Sesión {numero_sesion}")
                
                col_fecha, col_titulo = st.columns(2)
                
                with col_fecha:
                    fecha = st.date_input(
                        f"Fecha",
                        key=f"fecha_masiva_{i}",
                        label_visibility="collapsed"
                    )
                
                with col_titulo:
                    titulo = st.text_input(
                        f"Título/Tema",
                        key=f"titulo_masiva_{i}",
                        placeholder=f"Título de la sesión {numero_sesion}",
                        label_visibility="collapsed"
                    )
                
                sesiones_data.append({
                    'numero': numero_sesion,
                    'fecha': fecha,
                    'titulo': titulo
                })
            
            submit_masivo = st.form_submit_button("✅ Crear Todas las Sesiones", type="primary")
            
            if submit_masivo:
                # Validar que todos tengan título
                sesiones_sin_titulo = [s['numero'] for s in sesiones_data if not s['titulo']]
                
                if sesiones_sin_titulo:
                    st.error(f"⚠️ Las siguientes sesiones no tienen título: {', '.join(map(str, sesiones_sin_titulo))}")
                else:
                    # Crear todas las sesiones
                    creadas = 0
                    errores = []
                    
                    for sesion in sesiones_data:
                        try:
                            # Crear con descripción indicando que el video se subirá próximamente
                            crear_clase(
                                modulo_id,
                                sesion['titulo'],
                                "La clase se subirá próximamente",
                                "",  # URL vacía
                                sesion['numero'],
                                str(sesion['fecha'])
                            )
                            creadas += 1
                        except Exception as e:
                            errores.append(f"Sesión {sesion['numero']}: {str(e)}")
                    
                    if creadas > 0:
                        st.success(f"✅ {creadas} sesiones creadas correctamente")
                    
                    if errores:
                        st.error("❌ Errores:\n" + "\n".join(errores))
                    
                    if creadas > 0:
                        st.rerun()
    
    # Crear nueva sesión/clase individual
    with st.expander("➕ Crear Nueva Sesión Individual", expanded=False):
        
        with st.form(f"form_nueva_clase_{st.session_state.form_clase_counter}"):
            col1, col2 = st.columns(2)
            
            with col1:
                numero_sesion = st.number_input("Número de Sesión*", min_value=1, value=1, step=1)
                fecha_sesion = st.date_input("Fecha de la Sesión*")
            
            with col2:
                        nombre = st.text_input("Título/Descripción*")
            
            descripcion = st.text_area("Descripción Adicional (opcional)")
            
            url_video_input = st.text_area(
                "Iframe",
                height=100
            )
            
            submit = st.form_submit_button("Crear Sesión", type="primary")
            
            if submit:
                if not nombre or not url_video_input or not fecha_sesion:
                    st.error("El título, fecha y URL del video son obligatorios")
                else:
                    # Extraer URL del iframe si es necesario
                    url_video = extraer_url_de_iframe(url_video_input)
                    
                    if not url_video.startswith('http'):
                        st.error("No se pudo extraer una URL válida. Verifica el iframe o URL que pegaste.")
                    else:
                        crear_clase(modulo_id, nombre, descripcion, url_video, numero_sesion, str(fecha_sesion))
                        st.success(f"✅ Sesión {numero_sesion} creada correctamente")
                        # Incrementar contador para limpiar formulario
                        st.session_state.form_clase_counter += 1
                        st.rerun()
    
    # Listar sesiones/clases
    clases = obtener_clases(modulo_id)
    
    if clases:
        st.markdown("### Sesiones Existentes")
        
        for clase in clases:
            fecha_mostrar = formatear_fecha(clase.get('fecha_sesion'))
            numero_mostrar = clase['numero_sesion'] if clase.get('numero_sesion') else clase['orden']
            
            with st.expander(f"📅 Sesión {numero_mostrar} - {clase['nombre']} ({fecha_mostrar})", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Fecha:** {fecha_mostrar}")
                    st.markdown(f"**Número de Sesión:** {numero_mostrar}")
                    st.markdown(f"**Descripción:** {clase['descripcion'] or 'Sin descripción'}")
                    st.markdown(f"**URL:** {clase['url_video'][:50]}...")
                
                with col2:
                    if st.button("🗑️ Eliminar", key=f"del_clase_{clase['id']}"):
                        eliminar_clase(clase['id'])
                        st.success("Sesión eliminada")
                        st.rerun()
                
                # Editar sesión/clase
                with st.form(f"form_edit_clase_{clase['id']}"):
                    st.markdown("**Editar Sesión**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        nuevo_numero = st.number_input("Número de Sesión", value=numero_mostrar, min_value=1, key=f"num_clase_{clase['id']}")
                        nueva_fecha = st.date_input("Fecha", value=None, key=f"fecha_clase_{clase['id']}")
                    with col2:
                        nuevo_nombre = st.text_input("Título", value=clase['nombre'], key=f"nombre_clase_{clase['id']}")
                    
                    nueva_desc = st.text_area("Descripción", value=clase['descripcion'] or "", key=f"desc_clase_{clase['id']}")
                    nueva_url_input = st.text_area(
                        "Iframe o URL Video", 
                        value=clase['url_video'], 
                        key=f"url_clase_{clase['id']}",
                        height=100
                    )
                    
                    if st.form_submit_button("💾 Guardar Cambios"):
                        # Extraer URL del iframe si es necesario
                        nueva_url = extraer_url_de_iframe(nueva_url_input)
                        fecha_final = str(nueva_fecha) if nueva_fecha else clase.get('fecha_sesion', '')
                        actualizar_clase(clase['id'], nuevo_nombre, nueva_desc, nueva_url, nuevo_numero, fecha_final)
                        st.success("Cambios guardados")
                        st.rerun()
    else:
        st.info("No hay clases creadas para este módulo.")
    
    # Mover sesiones entre módulos
    if clases:
        st.markdown("---")
        with st.expander("🔄 Mover Sesiones a Otro Módulo", expanded=False):
            st.markdown("**Selecciona las sesiones que deseas mover y el módulo destino**")
            
            # Selector de sesiones
            sesiones_opciones = {
                f"Sesión {c.get('numero_sesion', c['orden'])} - {c['nombre']} ({formatear_fecha(c.get('fecha_sesion'))})": c['id'] 
                for c in clases
            }
            
            sesiones_seleccionadas = st.multiselect(
                "Sesiones a mover",
                options=list(sesiones_opciones.keys()),
                key="sesiones_mover"
            )
            
            # Selector de módulo destino (excluyendo el actual)
            modulos_destino = [m for m in modulos if m['id'] != modulo_id]
            
            if modulos_destino:
                modulo_destino_opciones = {m['nombre']: m['id'] for m in modulos_destino}
                
                modulo_destino = st.selectbox(
                    "Mover a módulo",
                    options=list(modulo_destino_opciones.keys()),
                    key="modulo_destino"
                )
                
                if st.button("🔄 Mover Sesiones Seleccionadas", type="primary"):
                    if not sesiones_seleccionadas:
                        st.error("⚠️ Debes seleccionar al menos una sesión")
                    else:
                        nuevo_modulo_id = modulo_destino_opciones[modulo_destino]
                        movidas = 0
                        
                        for sesion_nombre in sesiones_seleccionadas:
                            clase_id = sesiones_opciones[sesion_nombre]
                            mover_clase_a_modulo(clase_id, nuevo_modulo_id)
                            movidas += 1
                        
                        st.success(f"✅ {movidas} sesión(es) movida(s) a '{modulo_destino}'")
                        st.rerun()
            else:
                st.warning("No hay otros módulos disponibles. Crea más módulos para poder mover sesiones.")

def main():
    """Función principal del panel admin"""
    
    # Verificar si hay sesión admin
    if st.session_state.get('tipo_usuario') != 'admin':
        login_admin()
        return
    
    # Header con navegación y logout
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title("Panel de Administración")
    with col2:
        st.markdown("")  # Espaciado
        if st.button("🚪 Cerrar Sesión"):
            logout()
    
    st.markdown("---")
    
    # Navegación principal con tabs
    if 'menu_admin' not in st.session_state:
        st.session_state.menu_admin = "Diplomados"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📚 Diplomados", type="primary" if st.session_state.menu_admin == "Diplomados" else "secondary", use_container_width=True):
            st.session_state.menu_admin = "Diplomados"
            st.rerun()
    
    with col2:
        if st.button("📑 Módulos", type="primary" if st.session_state.menu_admin == "Módulos" else "secondary", use_container_width=True):
            st.session_state.menu_admin = "Módulos"
            st.rerun()
    
    with col3:
        if st.button("🎥 Clases", type="primary" if st.session_state.menu_admin == "Clases" else "secondary", use_container_width=True):
            st.session_state.menu_admin = "Clases"
            st.rerun()
    
    st.markdown("---")
    
    # Contenido principal según la opción seleccionada
    opcion = st.session_state.menu_admin
    if opcion == "Diplomados":
        gestionar_diplomados()
    elif opcion == "Módulos":
        gestionar_modulos()
    elif opcion == "Clases":
        gestionar_clases()

if __name__ == "__main__":
    main()
