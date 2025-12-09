import streamlit as st
from openai import OpenAI
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

# --- CÓDIGO CSS PARA OCULTAR EL BADGE "CREATED BY" ---
hide_github_icon = """
    <style>
    /* 1. Ocultar menú y header estándar */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 2. Ocultar el badge específico de Streamlit Cloud (El de 'Created by') */
    /* Busca cualquier div cuya clase contenga la palabra 'viewerBadge' */
    div[class*="viewerBadge"] {
        display: none !important;
    }
    
    /* 3. (Opcional) Ajustar márgenes superiores para que no quede hueco */
    .block-container {
        padding-top: 0rem;
    }
    </style>
"""

st.markdown(hide_github_icon, unsafe_allow_html=True)

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="AeroDynamics Pro",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CONFIGURACIÓN DE API KEY ---
# Carga las claves del archivo .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 

# --- ESTILOS VISUALES (TEMA PINK) ---
def load_custom_css():
    st.markdown("""
    <style>
        /* 1. FONDO Y COLORES GLOBALES */
        .stApp {
            background-color: #0e1117;
            background-image: linear-gradient(180deg, rgba(20,0,10,0.8) 0%, rgba(14,17,23,1) 100%), 
                              url("https://www.nasa.gov/sites/default/files/thumbnails/image/edu_supersonic_research_lab_header.jpg");
            background-size: cover;
            background-attachment: fixed;
            color: #ffffff;
        }

        /* 2. TÍTULOS Y ENCABEZADOS */
        h1, h2, h3 {
            color: #ff2b70 !important; /* Rosa Neón */
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 800 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            /* text-shadow removed for flat style */
        }
        
        /* 3. INPUTS Y WIDGETS */
        .stTextInput input, .stNumberInput input {
            color: white !important;
            background-color: rgba(255, 43, 112, 0.05) !important;
            border: 1px solid #ff2b70 !important;
            border-radius: 8px !important;
        }
        div[data-baseweb="input"] {
            background-color: rgba(255, 43, 112, 0.05) !important;
            border: none !important;
        }
        label {
            color: #ffacc5 !important; /* Rosa pastel claro para etiquetas */
            font-weight: 600 !important;
        }

        /* 4. BOTONES */
        /* 4. BOTONES MODERNO PRO */
        .stButton > button {
            background-color: #ff2b70;
            color: white !important;
            border: 2px solid #ff2b70;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: 600;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            box-shadow: none !important;
        }
        .stButton > button:hover {
            background-color: transparent;
            color: #ff2b70 !important;
            border-color: #ff2b70;
            transform: translateY(-2px);
        }

        /* 5. TABS */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 10px 10px 0 0;
            color: white;
            padding: 10px 20px;
        }
        .stTabs [aria-selected="true"] {
            background-color: rgba(255, 43, 112, 0.2) !important;
            border-bottom: 2px solid #ff2b70 !important;
            color: #ff2b70 !important;
        }

        /* 6. CAJAS DE ALERTA Y MÉTRICAS */
        div[data-testid="stMetricValue"] {
            color: #ff2b70 !important;
        }
        
    </style>
    """, unsafe_allow_html=True)

load_custom_css()

# --- FUNCIONES DE CÁLCULO ---
def calcular_sustentacion(rho, v, area, cl):
    """Calcula la fuerza de sustentación: L = 1/2 * rho * v^2 * A * Cl"""
    return 0.5 * rho * (v ** 2) * area * cl

def generar_grafica_rendimiento(rho, v_actual, area, cl):
    """Genera datos para la curva de sustentación vs velocidad"""
    # Rango desde 0 hasta 1.5 veces la velocidad actual
    v_range = np.linspace(0, max(v_actual * 1.5, 10), 100)
    l_range = 0.5 * rho * (v_range ** 2) * area * cl
    
    df = pd.DataFrame({
        "Velocidad (m/s)": v_range,
        "Sustentación (N)": l_range
    })
    return df

# --- INTERFAZ DE USUARIO ---

# Encabezado
col_logo, col_title = st.columns([1.2, 4])
with col_logo:
    import base64
    # Usamos ruta relativa directa ya que confirmamos el CWD
    logo_file = "foto.svg"
    
    try:
        with open(logo_file, "r", encoding="utf-8") as f:
            svg_content = f.read()
            # 1. Reemplazamos los colores hexadecimales por el rosa corporativo
            # Nota: Aseguramos que coincide exactamente con lo que hay en el archivo
            svg_content = svg_content.replace('fill="#FEFEFD"', 'fill="#ff2b70"')
            svg_content = svg_content.replace('fill="#FDFDFC"', 'fill="#ff2b70"')
            
            # 2. Codificamos a Base64 para evitar problemas de renderizado HTML/Markdown
            b64_svg = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
            
        # 3. Mostramos como imagen HTML
        st.markdown(f"""
            <div style='display: flex; justify-content: center; align-items: center;'>
                <img src="data:image/svg+xml;base64,{b64_svg}" width="140" style="max-width: 100%;">
            </div>
        """, unsafe_allow_html=True)
        
    except FileNotFoundError:
        st.error(f"Error: No se encuentra '{logo_file}'")
    except Exception as e:
        st.error(f"Error cargando logo: {e}")

with col_title:
    st.markdown("<h1 style='margin-bottom: 0;'>AERODYNAMICS <span style='color: white; font-weight: 300;'>PRO</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #ffacc5; font-size: 1.2rem;'>PLATAFORMA INTELIGENTE DE CÁLCULO AERONÁUTICO</p>", unsafe_allow_html=True)

st.markdown("---")

# Sistema de Pestañas
tab_calculator, tab_ai = st.tabs(["CALCULADORA DE VUELO", "ASISTENTE IA"])

# --- PESTAÑA 1: CALCULADORA ---
with tab_calculator:
    # Layout de columnas para inputs y resultados
    col_inputs, col_results = st.columns([1, 1], gap="large")
    
    with col_inputs:
        st.subheader("1. Parámetros de Entrada")
        st.info("Introduce los datos físicos del avión y el entorno.")
        
        with st.container(border=True):
            rho = st.number_input("Densidad del Aire (kg/m³)", value=1.225, step=0.001, format="%.3f", help="1.225 es el estándar a nivel del mar.")
            velocity = st.number_input("Velocidad (m/s)", value=250.0, step=10.0, help="Velocidad relativa del aire.")
            area = st.number_input("Superficie Alar (m²)", value=122.0, step=1.0, help="Área total de las alas.")
            cl = st.number_input("Coeficiente de Sustentación (Cl)", value=0.5, step=0.1, help="Depende del ángulo de ataque y forma del perfil.")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("CALCULAR SUSTENTACIÓN"):
            calc_active = True
        else:
            calc_active = False

    with col_results:
        st.subheader("2. Análisis de Resultados")
        
        # Hacemos el cálculo reactivo (siempre se actualiza, pero destacamos al pulsar)
        lift = calcular_sustentacion(rho, velocity, area, cl)
        peso_soportado_kg = lift / 9.81
        
        # Tarjeta de Resultado Principal
        st.markdown(f"""
        <div style='background: rgba(255, 43, 112, 0.1); border: 2px solid #ff2b70; border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 20px;'>
            <h3 style='margin:0; color: #ffacc5; font-size: 1rem; text-transform: uppercase;'>Fuerza Generada</h3>
            <h1 style='margin:10px 0; color: #ffffff; font-size: 3.5rem;'>{lift:,.0f} N</h1>
            <p style='margin:0; color: #cccccc;'>Equivalente a levantar <b>{peso_soportado_kg:,.0f} kg</b></p>
        </div>
        """, unsafe_allow_html=True)

        # Gráfica
        st.markdown("##### 📈 Curva de Rendimiento")
        chart_df = generar_grafica_rendimiento(rho, velocity, area, cl)
        st.line_chart(chart_df.set_index("Velocidad (m/s)"), color="#ff2b70")
        
        # Interpretación Contextual
        if lift > 700000:
            st.success("✅ **CLASE HEAVY**: Sustentación suficiente para un avión comercial grande (ej. Boeing 737/Airbus A320).")
        elif lift > 10000:
            st.info("✅ **CLASE LIGHT**: Sustentación ideal para avionetas o jets privados pequeños.")
        else:
            st.warning("⚠️ **CLASE BAJA**: Sustentación limitada (Drones, RC o Ultraligeros).")

# --- PESTAÑA 2: ASISTENTE IA ---
with tab_ai:
    st.subheader("Consulta Técnica")

    # Prompt del Sistema (Profesional)
    system_prompt = """
    Eres un Asistente de Ingeniería Aeronáutica Avanzada.
    Actúas como consultor técnico para una plataforma de cálculo de aeronaves.
    
    Tus objetivos son:
    1. Proveer explicaciones técnicas precisas sobre aerodinámica y mecánica de fluidos.
    2. Interpretar los resultados de sustentación (Lift) y coeficientes.
    3. Mantener un tono estrictamente profesional, conciso y directo.
    
    REGLAS:
    - No uses saludos informales.
    - Usa formato LaTeX para ecuaciones.
    - No uses emojis en tus respuestas.
    - Si te preguntan sobre temas no aeronáuticos, declina cortésmente.
    """

    chat_container = st.container(border=True, height=400)
    
    # Inicializar el historial con el System Prompt
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": "Sistema listo. Introduzca su consulta técnica sobre aerodinámica."}
        ]

    # Mostrar mensajes (Ocultamos el mensaje 'system')
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] != "system":
                # Sin avatares (usa iconos por defecto profesionales)
                st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Introduzca su consulta técnica..."):
        if not OPENAI_API_KEY or "pega-tu-api-key" in OPENAI_API_KEY:
            st.error("Configuración de API Key requerida.")
        else:
            # 1. Guardar y mostrar mensaje usuario
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                st.chat_message("user").write(prompt)

            # 2. Llamada a OpenAI
            try:
                client = OpenAI(api_key=OPENAI_API_KEY)
                with chat_container:
                    with st.spinner("Procesando consulta..."):
                        # Filtramos los mensajes para enviar solo lo necesario y aseguramos el system prompt
                        messages_to_send = [{"role": "system", "content": system_prompt}]
                        messages_to_send.extend([m for m in st.session_state.messages if m["role"] != "system"])
                        
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=messages_to_send
                        )
                        rta = response.choices[0].message.content
                        
                # 3. Guardar y mostrar respuesta
                st.session_state.messages.append({"role": "assistant", "content": rta})
                with chat_container:
                    st.chat_message("assistant").write(rta)
            
            except Exception as e:

                st.error(f"Error de conexión con la IA: {e}")


