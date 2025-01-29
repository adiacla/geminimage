import pyttsx3
import re
import speech_recognition as sr
import streamlit as st
import google.generativeai as genai
import threading

# Configuración de la API Key
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]  # Usa secretos de Streamlit
genai.configure(api_key=GOOGLE_API_KEY)

# Configuración del modelo Gemini
model = genai.GenerativeModel('gemini-pro')

# Inicializar el motor TTS (Text to Speech)
engine = pyttsx3.init()

# Verificar las voces disponibles y establecer una
voices = engine.getProperty('voices')

# Usar la primera voz disponible (puedes probar otras si prefieres)
engine.setProperty('voice', voices[0].id)  # Puedes cambiar el índice si prefieres otra voz
engine.setProperty('rate', 150)  # Velocidad de la voz
engine.setProperty('volume', 1)  # Volumen máximo (0.0 a 1.0)

# Variable de control para evitar múltiples ejecuciones de runAndWait
is_speaking = False

# Función para limpiar Markdown
def remove_markdown(text):
    clean_text = re.sub(r"([*_]{1,3}|`{1,3}|!\[.*?\]\(.*?\)|\[.*?\]\(.*?\))", "", text)
    return clean_text

# Función para generar respuestas del chatbot
def generate_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error al generar la respuesta: {str(e)}"

# Función para convertir texto a voz en un hilo separado
def text_to_speech_thread(text):
    global is_speaking
    if is_speaking:
        return  # Si ya estamos hablando, no hacer nada

    clean_text = remove_markdown(text)
    is_speaking = True

    # Usar un hilo separado para que no interfiera con el ciclo de ejecución
    def speak():
        engine.say(clean_text)
        engine.runAndWait()  # Ejecutar la acción de hablar

    t = threading.Thread(target=speak)
    t.start()
    t.join()  # Esperar a que termine antes de continuar
    is_speaking = False

# Función para capturar audio y convertirlo en texto
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Hablando... espera un momento...")
        recognizer.adjust_for_ambient_noise(source)  # Ajuste para ruido ambiente
        audio = recognizer.listen(source)
        try:
            # Usamos Google Speech Recognition para convertir a texto
            text = recognizer.recognize_google(audio, language="es-ES")
            return text
        except sr.UnknownValueError:
            return "No pude entender el audio."
        except sr.RequestError:
            return "Error al conectar con el servicio de reconocimiento."

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

# Opción para capturar voz
if st.button("Hablar"):
    user_input = speech_to_text()  # Captura la voz y la convierte en texto
    st.session_state.user_input = user_input
    st.text_area("Texto Capturado", user_input, height=200)  # Mostrar el texto capturado
    
    if user_input:  # Si se capturó un texto válido
        # Agregar el mensaje del usuario al historial
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Generar la respuesta del chatbot
        response_text = generate_response(user_input)

        # Agregar la respuesta del chatbot al historial
        st.session_state.chat_history.append({"role": "model", "content": response_text})

        # Mostrar el texto antes de convertirlo a voz
        st.markdown(f"**🤖 Gemini:** {response_text}")

        # Convertir la respuesta a voz usando un hilo separado
        text_to_speech_thread(response_text)

        # Limpiar el campo de entrada sin causar errores
        st.session_state.user_input = ""  

        # Forzar la recarga de la página para que se borre la entrada
        st.rerun()

    else:
        st.warning("No se pudo capturar voz.")
