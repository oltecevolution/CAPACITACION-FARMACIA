import streamlit as st
import os
from fpdf import FPDF

# --- CLASE DEL PDF PROFESIONAL ---
class GeneradorPDFPro(FPDF):
    def header(self):
        # Marco de la página
        self.rect(5, 5, 200, 287)
        
        # Logo institucional (si existe en la carpeta)
        if os.path.exists("logo.png"):
            self.image("logo.png", 10, 10, 30)
            self.set_x(45)
        else:
            self.set_x(10)
            
        self.set_font('Arial', 'B', 16)
        self.set_text_color(44, 62, 80)
        self.cell(0, 10, 'OLTEC EVOLUTION - SISTEMA DE EVALUACION', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, 'Reporte Oficial de Certificacion Tecnica', 0, 1, 'C')
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

# --- INICIALIZACIÓN DEL ESTADO GLOBAL DE LA SESIÓN (SESSION STATE) ---
if 'preguntas' not in st.session_state:
    st.session_state.preguntas = [
        {
            "pregunta": "¿Cuál es el resultado de aplicar la fórmula de dilución si C1=10%, V1=2L y V2=4L? Encuentre C2.",
            "opciones": ["C2 = 5%", "C2 = 2.5%", "C2 = 20%"],
            "respuesta_correcta": 0,
            "explicacion": "Usando C1 x V1 = C2 x V2 -> (10% * 2L) / 4L = 5%.",
            "imagen": None
        }
    ]
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

# --- CONFIGURACIÓN DE PÁGINA EN STREAMLIT ---
st.set_page_config(page_title="Oltec Evolution - CMS Web", layout="centered")

# --- BARRA LATERAL (SIDEBAR) & SEGURIDAD ---
st.sidebar.title("OLTEC EVOLUTION")
st.sidebar.write("Sistema de Capacitación Técnica")

# Sección oculta de administración en el Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Área de Administración")
clave_admin = st.sidebar.text_input("Contraseña de acceso:", type="password")

modo_admin = False
if clave_admin == "oltec123":
    modo_admin = st.sidebar.checkbox("Activar Modo Configuración 🛠️")
    if modo_admin:
        st.sidebar.success("Modo editor activado")
elif clave_admin:
    st.sidebar.error("Clave incorrecta")

# --- INTERFAZ DE CONFIGURACIÓN (SOLO SI SE AUTENTICA) ---
if modo_admin:
    st.title("🛠️ Panel de Configuración del Cuestionario")
    
    # 1. Ajustes del Cronómetro
    st.subheader("1. Parámetros de Evaluación")
    st.session_state.chk_cron = st.checkbox("Habilitar control de tiempo visual", value=st.session_state.chk_cron)
    
    # 2. Gestor de Fórmulas
    st.subheader("2. Banco de Fórmulas Rápidas")
    nueva_f = st.text_input("Agregar nueva fórmula al banco:")
    if st.button("Guardar Fórmula"):
        if nueva_f and nueva_f not in st.session_state.banco_formulas:
            st.session_state.banco_formulas.append(nueva_f)
            st.success("Fórmula guardada.")
            st.rerun()
            
    formula_seleccionada = st.selectbox("Fórmulas guardadas (Haz clic para copiar textualmente):", [""] + st.session_state.banco_formulas)
    if formula_seleccionada:
        st.info(f"Fórmula lista para copiar: `{formula_seleccionada}`")

    # 3. Formulario de Preguntas
    st.subheader("3. Diseñador de Preguntas")
    enunciado = st.text_area("Enunciado de la pregunta o cálculo matemático:", value=formula_seleccionada if formula_seleccionada else "")
    
    # Manejo dinámico de opciones mediante inputs en la web
    num_opciones = st.number_input("Número de opciones de respuesta:", min_value=2, max_value=10, value=3)
    opciones_inputs = []
    for i in range(num_opciones):
        opciones_inputs.append(st.text_input(f"Opción {i+1}:", key=f"opc_web_{i}"))
        
    correcta_idx = st.number_input("Índice de la respuesta correcta:", min_value=1, max_value=num_opciones, value=1) - 1
    explicacion = st.text_input("Justificación técnica (Feedback):")
    
    # Cargar Multimedia
    img_file = st.file_uploader("Adjuntar imagen de soporte:", type=["png", "jpg", "jpeg"])
    img_path = None
    if img_file:
        # Guarda la imagen temporalmente en el servidor local
        img_path = os.path.join("temp_media", img_file.name)
        os.makedirs("temp_media", exist_ok=True)
        with open(img_path, "wb") as f:
            f.write(img_file.getbuffer())
        st.image(img_file, width=200, caption="Vista previa cargada")

    if st.button("💾 GUARDAR PREGUNTA EN EL BANCO"):
        opc_limpias = [o.strip() for o in opciones_inputs if o.strip()]
        if enunciado and len(opc_limpias) >= 2:
            nueva_pregunta = {
                "pregunta": enunciado,
                "opciones": opc_limpias,
                "respuesta_correcta": correcta_idx,
                "explicacion": explicacion,
                "imagen": img_path
            }
            st.session_state.preguntas.append(nueva_pregunta)
            st.success("¡Pregunta añadida exitosamente al banco!")
            st.rerun()
        else:
            st.error("Por favor completa el enunciado y al menos 2 opciones.")

    # Lista de preguntas actuales para eliminar
    st.subheader("Cuestionarios en ejecución:")
    for idx, p in enumerate(st.session_state.preguntas):
        col1, col2 = st.columns([4, 1])
        col1.write(f"**{idx+1}.** {p['pregunta'][:60]}...")
        if col2.button("❌ Eliminar", key=f"del_{idx}"):
            st.session_state.preguntas.pop(idx)
            st.success("Pregunta eliminada.")
            st.rerun()

# --- VISTA DE LA EVALUACIÓN WEB (PARA LOS TRABAJADORES) ---
else:
    # FASE 1: INICIO Y CAPTURA DE DATOS
    if st.session_state.fase == 'inicio':
        st.title("📝 Plataforma de Capacitación - Oltec Evolution")
        st.subheader("Evaluación de Certificación Técnica")
        st.write("Por favor, introduzca sus datos de identidad para iniciar el examen.")
        
        nombre_input = st.text_input("Nombre Completo del Trabajador:")
        cedula_input = st.text_input("Cédula de Identidad / ID:")
        
        if st.button("🚀 COMENZAR EVALUACIÓN"):
            if nombre_input.strip() and cedula_input.strip():
                if len(st.session_state.preguntas) == 0:
                    st.error("No hay preguntas cargadas en el sistema por el administrador.")
                else:
                    st.session_state.nombre = nombre_input
                    st.session_state.cedula = cedula_input
                    st.session_state.indice_actual = 0
                    st.session_state.respuestas_usuario = []
                    st.session_state.fase = 'quiz'
                    st.rerun()
            else:
                st.warning("Debe ingresar obligatoriamente su Nombre y Cédula.")

    # FASE 2: CUESTIONARIO ACTIVO
    elif st.session_state.fase == 'quiz':
        p_actual = st.session_state.preguntas[st.session_state.indice_actual]
        total_p = len(st.session_state.preguntas)
        
        st.title("✏️ Evaluación en Curso")
        st.progress((st.session_state.indice_actual) / total_p)
        st.write(f"**Evaluado:** {st.session_state.nombre.upper()} | **C.I:** {st.session_state.cedula}")
        st.markdown(f"### Pregunta {st.session_state.indice_actual + 1} de {total_p}")
        
        # Mostrar control de tiempo estático si está activo
        if st.session_state.chk_cron:
            st.warning("⏱️ Esta evaluación está configurada bajo control de tiempo. Responda con agilidad.")
            
        # Contenedor de la Pregunta
        st.info(p_actual["pregunta"])
        
        # Imagen de Soporte
        if p_actual["imagen"] and os.path.exists(p_actual["imagen"]):
            st.image(p_actual["imagen"], use_container_width=True)
            
        # Opciones de respuesta
        seleccion = st.radio("Seleccione la alternativa correcta:", p_actual["opciones"], key=f"quiz_radio_{st.session_state.indice_actual}")
        
        if st.button("Validar y Continuar ➡️"):
            # Encontrar el índice de la opción seleccionada
            idx_seleccionada = p_actual["opciones"].index(seleccion)
            st.session_state.respuestas_usuario.append(idx_seleccionada)
            
            # Avanzar de pregunta
            if st.session_state.indice_actual + 1 < total_p:
                st.session_state.indice_actual += 1
            else:
                st.session_state.fase = 'resultados'
            st.rerun()

    # FASE 3: RESULTADOS & DESCARGA DEL PDF PROFESIONAL
    elif st.session_state.fase == 'resultados':
        st.title("🏁 Evaluación Finalizada")
        st.balloons()
        
        # Cálculos de notas
        buenas = sum(1 for i, r in enumerate(st.session_state.respuestas_usuario) if r == st.session_state.preguntas[i]["respuesta_correcta"])
        total = len(st.session_state.preguntas)
        calif = (buenas / total) * 100
        
        st.metric(label="Calificación Obtenida", value=f"{calif:.1f}%", delta=f"{buenas} de {total} Aciertos")
        
        st.write("Su evaluación ha sido procesada por el sistema central. Ya puede descargar su reporte oficial firmado en formato PDF.")

        # --- GENERACIÓN DEL PDF EN MEMORIA PARA LA WEB ---
        pdf = GeneradorPDFPro()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 10, " DATOS DEL EVALUADO", 0, 1, 'L', True)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 8, f"Nombre Completo: {st.session_state.nombre.upper()}", 0, 1)
        pdf.cell(0, 8, f"Cedula de Identidad: {st.session_state.cedula}", 0, 1)
        pdf.ln(4)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f" CALIFICACION FINAL: {calif:.1f}%", 0, 1, 'L', True)
        pdf.ln(5)
        
        for i, p in enumerate(st.session_state.preguntas):
            correcta = st.session_state.respuestas_usuario[i] == p["respuesta_correcta"]
            pdf.set_font("Arial", 'B', 10)
            pdf.set_text_color(0, 0, 0)
            p_clean = p['pregunta'].replace('¿', '').replace('?', '')
            pdf.multi_cell(0, 7, f"{i+1}. {p_clean}")
            
            pdf.set_font("Arial", '', 10)
            if correcta:
                pdf.set_text_color(39, 174, 96)
                pdf.cell(0, 6, "   Resultado de Respuesta: CORRECTA", 0, 1)
            else:
                pdf.set_text_color(192, 57, 43)
                pdf.cell(0, 6, f"   Resultado de Respuesta: INCORRECTA", 0, 1)
                pdf.set_text_color(44, 62, 80)
                sol = p['opciones'][p['respuesta_correcta']] if p['respuesta_correcta'] < len(p['opciones']) else "No respondida"
                pdf.cell(0, 6, f"   Solucion Teorica: {sol}", 0, 1)
                pdf.set_text_color(127, 140, 141)
                pdf.multi_cell(0, 6, f"   Feedback Tecnico: {p['explicacion']}")
            pdf.ln(3)
            
        # Guardado y preparación del botón de descarga web
        pdf_filename = f"temp_reporte_{st.session_state.cedula}.pdf"
        pdf.output(pdf_filename)
        
        with open(pdf_filename, "rb") as f:
            pdf_bytes = f.read()
            
        # Botón nativo de descarga en el navegador web
        st.download_button(
            label="📥 DESCARGAR REPORTE PROFESIONAL PDF",
            data=pdf_bytes,
            file_name=f"Reporte_Certificacion_{st.session_state.cedula}.pdf",
            mime="application/pdf"
        )
        
        # Limpieza del archivo temporal
        if os.path.exists(pdf_filename):
            os.remove(pdf_filename)
            
        if st.button("🔄 Realizar otra evaluación"):
            st.session_state.fase = 'inicio'
            st.session_state.respuestas_usuario = []
            st.session_state.indice_actual = 0
            st.rerun()