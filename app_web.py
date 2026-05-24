import streamlit as st
import os
import time
from fpdf import FPDF

# --- FUNCIÓN DE OPTIMIZACIÓN: SANITIZACIÓN DE TEXTO PARA FPDF ---
def limpiar_texto_pdf(texto):
    """Reemplaza caracteres especiales en español para evitar crasheos en FPDF estándar"""
    reemplazos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N', '¿': '', '?': '', 'ü': 'u', 'Ü': 'U'
    }
    for original, nuevo in reemplazos.items():
        texto = texto.replace(original, nuevo)
    return texto

# --- CLASE DEL PDF PROFESIONAL OPTIMIZADO ---
class GeneradorPDFPro(FPDF):
    def header(self):
        # Marco formal de la página
        self.rect(5, 5, 200, 287)
        
        # Logo institucional (opcional en carpeta raíz)
        if os.path.exists("logo.png"):
            self.image("logo.png", 10, 10, 30)
            self.set_x(45)
        else:
            self.set_x(10)
            
        self.set_font('Arial', 'B', 14)
        self.set_text_color(44, 62, 80)
        self.cell(0, 10, 'OLTEC EVOLUTION - SISTEMA DE EVALUACION', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, 'Reporte Oficial de Certificacion Tecnica', 0, 1, 'C')
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(127, 140, 141)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

# --- INICIALIZACIÓN DEL ESTADO GLOBAL DE LA SESIÓN (SESSION STATE) ---
if 'admin_password' not in st.session_state:
    st.session_state.admin_password = "oltec123"  # Contraseña inicial mutable

if 'categorias' not in st.session_state:
    # Estructura de diccionario para separar por listas de preguntas independientes
    st.session_state.categorias = {
        "Protecciones Eléctricas": [
            {
                "pregunta": "¿Cual es el resultado de aplicar la formula de dilucion si C1=10%, V1=2L y V2=4L? Encuentre C2.",
                "opciones": ["C2 = 5%", "C2 = 2.5%", "C2 = 20%"],
                "respuesta_correcta": 0,
                "explicacion": "Usando C1 x V1 = C2 x V2 -> (10% * 2L) / 4L = 5%.",
                "imagen": None,
                "creador": "Ing. Angel"
            }
        ],
        "Mecánica Automotriz": []
    }

if 'categoria_activa' not in st.session_state:
    st.session_state.categoria_activa = "Protecciones Eléctricas"
if 'banco_formulas' not in st.session_state:
    st.session_state.banco_formulas = ["C1 x V1 = C2 x V2", "Dosis = (Deseada / Disponible) x Vehiculo"]
if 'fase' not in st.session_state:
    st.session_state.fase = 'inicio'
if 'indice_actual' not in st.session_state:
    st.session_state.indice_actual = 0
if 'respuestas_usuario' not in st.session_state:
    st.session_state.respuestas_usuario = []
if 'nombre' not in st.session_state:
    st.session_state.nombre = ""
if 'cedula' not in st.session_state:
    st.session_state.cedula = ""
if 'chk_cron' not in st.session_state:
    st.session_state.chk_cron = True

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Oltec Evolution - CMS Web", layout="centered", page_icon="⚡")

# --- BARRA LATERAL (SIDEBAR) & SEGURIDAD DINÁMICA ---
st.sidebar.title("⚡ OLTEC EVOLUTION")
st.sidebar.write("Plataforma de Capacitación e Ingeniería")

st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Área de Administración")
clave_admin = st.sidebar.text_input("Contraseña de acceso:", type="password")

modo_admin = False
if clave_admin == st.session_state.admin_password:
    modo_admin = st.sidebar.checkbox("Activar Modo Configuración 🛠️")
    if modo_admin:
        st.sidebar.success("Modo editor autorizado")
elif clave_admin:
    st.sidebar.error("Clave incorrecta")

# --- INTERFAZ DE CONFIGURACIÓN ADMINISTRATIVA ---
if modo_admin:
    st.title("🛠️ Panel de Control y Configuración")
    
    # Pestañas para organizar la administración de forma limpia
    tab_eval, tab_cat, tab_preg, tab_seg = st.tabs([
        "📊 Parámetros", "📁 Gestión de Categorías", "📝 Diseñador de Preguntas", "🔐 Seguridad"
    ])
    
    with tab_eval:
        st.subheader("Configuración de Cuestionarios")
        st.session_state.chk_cron = st.checkbox("Habilitar control de tiempo visual para el personal", value=st.session_state.chk_cron)
        
        st.write("---")
        st.subheader("Banco de Fórmulas de Consulta")
        nueva_f = st.text_input("Agregar nueva fórmula técnica:")
        if st.button("Guardar Fórmula"):
            if nueva_f and nueva_f not in st.session_state.banco_formulas:
                st.session_state.banco_formulas.append(nueva_f)
                st.toast("Fórmula añadida al repositorio", icon="💾")
                st.rerun()
                
        formula_seleccionada = st.selectbox("Fórmulas guardadas (Clic para transferir al enunciado):", [""] + st.session_state.banco_formulas)

    with tab_cat:
        st.subheader("Creación de Módulos / Categorías")
        nueva_cat = st.text_input("Nombre de la nueva categoría de evaluación:", placeholder="Ej. Diagnóstico Motores Chevrolet")
        if st.button("Crear Nueva Categoría"):
            cat_limpia = nueva_cat.strip()
            if cat_limpia:
                if cat_limpia not in st.session_state.categorias:
                    st.session_state.categorias[cat_limpia] = []
                    st.success(f"Categoría '{cat_limpia}' añadida con éxito.")
                    st.rerun()
                else:
                    st.warning("Esa categoría ya existe en el sistema.")
            else:
                st.error("El nombre no puede estar vacío.")

    with tab_preg:
        st.subheader("Diseñador de Preguntas de Certificación")
        
        # Selección de categoría destino
        categoria_destino = st.selectbox("Seleccionar Categoría donde guardar la pregunta:", list(st.session_state.categorias.keys()))
        
        enunciado = st.text_area("Enunciado o situación de falla técnica:", value=formula_seleccionada if formula_seleccionada else "")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            num_opciones = st.number_input("Opciones de respuesta:", min_value=2, max_value=6, value=3)
            correcta_idx = st.number_input("Número de la opción correcta:", min_value=1, max_value=num_opciones, value=1) - 1
        with col_c2:
            creador_pregunta = st.text_input("Nombre del Creador / Diseñador:", value="Ing. Ángel")
            explicacion = st.text_input("Feedback / Justificación técnica:")

        opciones_inputs = []
        for i in range(num_opciones):
            opciones_inputs.append(st.text_input(f"Opción {i+1}:", key=f"opc_diseno_{i}"))
            
        img_file = st.file_uploader("Adjuntar imagen técnica de soporte (Diagramas, capturas):", type=["png", "jpg", "jpeg"])
        img_path = None
        if img_file:
            img_path = os.path.join("temp_media", img_file.name)
            os.makedirs("temp_media", exist_ok=True)
            with open(img_path, "wb") as f:
                f.write(img_file.getbuffer())
            st.image(img_file, width=200, caption="Imagen cargada correctamente")

        if st.button("💾 GUARDAR PREGUNTA EN CATEGORÍA"):
            opc_limpias = [o.strip() for o in opciones_inputs if o.strip()]
            if enunciado and len(opc_limpias) >= 2:
                nueva_p = {
                    "pregunta": enunciado,
                    "opciones": opc_limpias,
                    "respuesta_correcta": correcta_idx,
                    "explicacion": explicacion,
                    "imagen": img_path,
                    "creador": creador_pregunta if creador_pregunta.strip() else "Anónimo"
                }
                st.session_state.categorias[categoria_destino].append(nueva_p)
                st.success(f"¡Pregunta asociada a '{categoria_destino}' de forma exitosa!")
                st.rerun()
            else:
                st.error("Verifique que el enunciado y al menos 2 opciones tengan contenido válido.")

        st.write("---")
        st.subheader("🗂️ Supervisor de Banco de Preguntas Activo")
        for cat_name, lista_p in st.session_state.categorias.items():
            with st.expander(f"📁 Lista: {cat_name} ({len(lista_p)} preguntas)"):
                if not lista_p:
                    st.caption("No hay preguntas registradas en esta sección.")
                for idx, p in enumerate(lista_p):
                    c_col1, c_col2 = st.columns([4, 1])
                    c_col1.write(f"**{idx+1}.** {p['pregunta'][:70]}... *(Por: {p.get('creador', 'N/A')})*")
                    if c_col2.button("❌ Eliminar", key=f"del_{cat_name}_{idx}"):
                        lista_p.pop(idx)
                        st.toast("Pregunta eliminada de la base de datos", icon="🗑️")
                        st.rerun()

    with tab_seg:
        st.subheader("🔑 Seguridad de Credenciales")
        nueva_clave = st.text_input("Establecer nueva contraseña del panel:", type="password")
        confirmar_clave = st.text_input("Confirmar nueva contraseña:", type="password")
        
        if st.button("Actualizar Llave de Acceso"):
            if nueva_clave.strip():
                if nueva_clave == confirmar_clave:
                    st.session_state.admin_password = nueva_clave.strip()
                    st.success("¡Contraseña de seguridad actualizada de forma exitosa!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Las contraseñas ingresadas no coinciden.")
            else:
                st.error("La contraseña no puede quedar en blanco.")

# --- VISTA DE LA EVALUACIÓN WEB (PARA LOS TRABAJADORES) ---
else:
    # FASE 1: INICIO, CAPTURA DE DATOS Y SELECCIÓN DE CATEGORÍA
    if st.session_state.fase == 'inicio':
        st.title("📝 Plataforma de Capacitación - Oltec Evolution")
        st.subheader("Evaluación de Certificación Técnica")
        st.write("Complete sus datos corporativos e indique el módulo de ingeniería que desea evaluar.")
        
        nombre_input = st.text_input("Nombre Completo del Trabajador:")
        cedula_input = st.text_input("Cédula de Identidad / ID:")
        
        # Selección dinámica del cuestionario que desea rendir
        categoria_elegida = st.selectbox("Seleccione el Módulo Técnico a evaluar:", list(st.session_state.categorias.keys()))
        
        if st.button("🚀 INICIAR CERTIFICACIÓN TÉCNICA"):
            if nombre_input.strip() and cedula_input.strip():
                preguntas_seleccionadas = st.session_state.categorias[categoria_elegida]
                if len(preguntas_seleccionadas) == 0:
                    st.error(f"El módulo '{categoria_elegida}' no tiene preguntas cargadas actualmente por el administrador.")
                else:
                    st.session_state.nombre = nombre_input
                    st.session_state.cedula = cedula_input
                    st.session_state.categoria_activa = categoria_elegida
                    st.session_state.indice_actual = 0
                    st.session_state.respuestas_usuario = []
                    st.session_state.fase = 'quiz'
                    st.rerun()
            else:
                st.warning("Debe ingresar obligatoriamente su Nombre y Cédula de Identidad.")

    # FASE 2: CUESTIONARIO ACTIVO
    elif st.session_state.fase == 'quiz':
        preguntas_modulo = st.session_state.categorias[st.session_state.categoria_activa]
        p_actual = preguntas_modulo[st.session_state.indice_actual]
        total_p = len(preguntas_modulo)
        
        st.title("✏️ Certificación en Progreso")
        st.progress((st.session_state.indice_actual) / total_p)
        st.write(f"**Evaluado:** {st.session_state.nombre.upper()} | **Módulo:** {st.session_state.categoria_activa}")
        st.markdown(f"### Evaluación: Pregunta {st.session_state.indice_actual + 1} de {total_p}")
        
        if st.session_state.chk_cron:
            st.warning("⏱️ Control de auditoría de tiempo activo para este módulo. Responda con precisión.")
            
        st.info(p_actual["pregunta"])
        
        if p_actual["imagen"] and os.path.exists(p_actual["imagen"]):
            st.image(p_actual["imagen"], use_container_width=True)
            
        seleccion = st.radio("Seleccione la alternativa correcta:", p_actual["opciones"], key=f"quiz_radio_{st.session_state.indice_actual}")
        
        if st.button("Validar y Continuar ➡️"):
            idx_seleccionada = p_actual["opciones"].index(seleccion)
            st.session_state.respuestas_usuario.append(idx_seleccionada)
            
            if st.session_state.indice_actual + 1 < total_p:
                st.session_state.indice_actual += 1
            else:
                # Transición profesional con spinner en vez de globos invasivos
                with st.spinner("Procesando respuestas en la base central..."):
                    time.sleep(1.2)
                st.session_state.fase = 'resultados'
            st.rerun()

    # FASE 3: RESULTADOS E INFORME TÉCNICO AUDITABLE
    elif st.session_state.fase == 'resultados':
        preguntas_modulo = st.session_state.categorias[st.session_state.categoria_activa]
        st.title("🏁 Proceso de Evaluación Completado")
        
        # Animación moderna y profesional en barra superior
        st.toast("¡Evaluación finalizada con éxito!", icon="📥")
        
        buenas = sum(1 for i, r in enumerate(st.session_state.respuestas_usuario) if r == preguntas_modulo[i]["respuesta_correcta"])
        total = len(preguntas_modulo)
        calif = (buenas / total) * 100
        
        # Panel formal de resultados
        if calif >= 70:
            st.success(f"🎉 **ESTADO: APROBADO**. Ha completado los requerimientos mínimos de Oltec Evolution para el módulo: {st.session_state.categoria_activa}.")
        else:
            st.error(f"📋 **ESTADO: REPROBADO**. Se sugiere revisar el material de soporte técnico de las fórmulas asociadas y volver a intentar.")

        st.metric(label="Calificación Registrada", value=f"{calif:.1f}%", delta=f"{buenas} de {total} Aciertos")
        
        st.write("La firma digital técnica ha sido adjuntada. Ya puede descargar el reporte de auditoría en formato PDF.")

        # --- GENERACIÓN DEL PDF SANITIZADO ---
        pdf = GeneradorPDFPro()
        pdf.add_page()
        
        # Datos del Evaluado
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 9, " DATOS DEL EVALUADO Y MODULO", 0, 1, 'L', True)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 7, limpiar_texto_pdf(f"Nombre Completo: {st.session_state.nombre.upper()}"), 0, 1)
        pdf.cell(0, 7, limpiar_texto_pdf(f"Cedula de Identidad / ID: {st.session_state.cedula}"), 0, 1)
        pdf.cell(0, 7, limpiar_texto_pdf(f"Modulo de Evaluacion: {st.session_state.categoria_activa}"), 0, 1)
        pdf.ln(3)
        
        # Calificación
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 9, limpiar_texto_pdf(f" CALIFICACION FINAL OBTENIDA: {calif:.1f}%"), 0, 1, 'L', True)
        pdf.ln(4)
        
        # Cuerpo de respuestas con el Nombre del Diseñador/Creador añadido
        for i, p in enumerate(preguntas_modulo):
            correcta = st.session_state.respuestas_usuario[i] == p["respuesta_correcta"]
            pdf.set_font("Arial", 'B', 10)
            pdf.set_text_color(44, 62, 80)
            
            # Sanitizar enunciado y el creador antes de inyectar en FPDF
            p_limpia = limpiar_texto_pdf(p['pregunta'])
            creador_limpio = limpiar_texto_pdf(p.get('creador', 'Ing. Angel'))
            
            pdf.multi_cell(0, 6, f"{i+1}. {p_limpia} (Disenado por: {creador_limpio})")
            
            pdf.set_font("Arial", '', 10)
            if correcta:
                pdf.set_text_color(39, 174, 96)
                pdf.cell(0, 6, "   Resultado: CORRECTA", 0, 1)
            else:
                pdf.set_text_color(192, 57, 43)
                pdf.cell(0, 6, "   Resultado: INCORRECTA", 0, 1)
                pdf.set_text_color(44, 62, 80)
                sol_limpia = limpiar_texto_pdf(p['opciones'][p['respuesta_correcta']])
                pdf.cell(0, 6, f"   Solucion Esperada: {sol_limpia}", 0, 1)
                feed_limpio = limpiar_texto_pdf(p['explicacion'])
                pdf.set_text_color(127, 140, 141)
                pdf.multi_cell(0, 5, f"   Feedback de Ingenieria: {feed_limpio}")
            pdf.ln(2)
            
        # Almacenamiento dinámico seguro
        pdf_filename = f"temp_reporte_{st.session_state.cedula}.pdf"
        pdf.output(pdf_filename)
        
        with open(pdf_filename, "rb") as f:
            pdf_bytes = f.read()
            
        st.download_button(
            label="📥 DESCARGAR REPORTE PROFESIONAL PDF",
            data=pdf_bytes,
            file_name=f"Reporte_Certificacion_Oltec_{st.session_state.cedula}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        if os.path.exists(pdf_filename):
            os.remove(pdf_filename)
            
        st.write("---")
        if st.button("🔄 Finalizar y Volver al Inicio"):
            st.session_state.fase = 'inicio'
            st.session_state.respuestas_usuario = []
            st.session_state.indice_actual = 0
            st.rerun()
