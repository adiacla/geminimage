import streamlit as st
import google.generativeai as genai

# Configuración de la API Key
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]  # Usa secretos de Streamlit
genai.configure(api_key=GOOGLE_API_KEY)

# Configuración del modelo Gemini
model = genai.GenerativeModel('gemini-pro')

# Función para generar respuestas del chatbot
def generate_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error al generar la respuesta: {str(e)}"

# Diseño de la aplicación Streamlit
# Crear dos columnas para el logo y el texto
col1, col2 = st.columns([1, 4])  # La primera columna es más pequeña

# Agregar logo en la primera columna
with col1:
    st.image("logo.png", width=80)  # Ajusta el tamaño del logo

# Agregar texto en la segunda columna
with col2:
    st.markdown("### Elaborado por Smart Regino Lab")  # Tamaño de encabezado ajustable

# Línea divisoria
st.divider()

# Inicializar el historial de chat en la sesión si no existe
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Mostrar el historial del chat primero
st.subheader("Historial del Chat")
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(f"**👤 Usuario:** {chat['content']}")
    elif chat["role"] == "model":
        st.markdown(f"**🤖 Gemini:** {chat['content']}")

# Separador para mejorar la apariencia
st.divider()

# Asegurar que la variable 'user_input' existe en session_state
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Entrada de texto para escribir el mensaje
user_input = st.text_input("Escribe tu mensaje aquí:", key="input_text", value=st.session_state.user_input)

# Botón para enviar mensaje
if st.button("Enviar"):
    if user_input:
        # Agregar el mensaje del usuario al historial
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Generar la respuesta del chatbot
        response_text = generate_response(user_input)

        # Agregar la respuesta del chatbot al historial
        st.session_state.chat_history.append({"role": "model", "content": response_text})

        # Limpiar el campo de entrada sin causar errores
        st.session_state.user_input = ""  
        
        # Forzar la recarga de la página para que se borre la entrada
        st.rerun()
    else:
        st.warning("Por favor, ingresa un mensaje.")
