import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

# Título e imagen de bienvenida
st.title("🌐 Traductor de Voz Inteligente")
st.markdown("#### 🗣️ ¡Dime lo que quieras traducir y escucha tu frase en el idioma que elijas!")
image = Image.open('traductorimg.png')
st.image(image, width=300)

# Sidebar con instrucciones
with st.sidebar:
    st.subheader("¿Cómo funciona?")
    st.write("1. Haz clic en 'Escuchar' para iniciar la grabación.")
    st.write("2. Pronuncia la frase que deseas traducir.")
    st.write("3. Selecciona los idiomas de entrada y salida.")
    st.write("4. Haz clic en 'Convertir' para obtener la traducción en audio.")

# Configuración del botón de reconocimiento de voz
st.write("**Pulsa el botón para iniciar la escucha:**")
stt_button = Button(label="🎤 Escuchar", width=300, height=50)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# Texto recibido del reconocimiento de voz
if result and "GET_TEXT" in result:
    input_text = result.get("GET_TEXT")
    st.markdown(f"**Texto recibido:** {input_text}")

# Creación de carpetas temporales para los audios
try:
    os.mkdir("temp")
except:
    pass

# Configuración de idiomas de entrada y salida
translator = Translator()
input_language = st.selectbox("Idioma de entrada:", ["Inglés", "Español", "Mandarín", "Japonés", "Francés"])
output_language = st.selectbox("Idioma de salida:", ["Inglés", "Español", "Mandarín", "Japonés", "Francés"])

# Acento de salida para inglés
if output_language == "Inglés":
    english_accent = st.selectbox("Seleccione el acento:", ["Defecto", "Estados Unidos", "Reino Unido", "Australia", "Canadá", "Irlanda", "Sudáfrica"])
else:
    english_accent = "Defecto"

# Mapeo de lenguajes
language_map = {
    "Inglés": "en", "Español": "es", "Mandarín": "zh-cn",
    "Japonés": "ja", "Francés": "fr"
}
input_language_code = language_map.get(input_language)
output_language_code = language_map.get(output_language)

# Mapeo de acentos
tld_map = {
    "Defecto": "com", "Estados Unidos": "com", "Reino Unido": "co.uk",
    "Australia": "com.au", "Canadá": "ca", "Irlanda": "ie", "Sudáfrica": "co.za"
}
tld = tld_map.get(english_accent, "com")

# Función para convertir texto a voz y guardar el audio
def text_to_speech(text, input_language, output_language, tld):
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, tld=tld)
    audio_file = f"temp/{text[:20]}.mp3"
    tts.save(audio_file)
    return audio_file, trans_text

# Botón para iniciar la traducción
if st.button("Convertir y Escuchar"):
    if input_text:
        audio_path, translated_text = text_to_speech(input_text, input_language_code, output_language_code, tld)
        audio_file = open(audio_path, "rb")
        audio_bytes = audio_file.read()
        
        # Despliegue de texto traducido y audio
        st.markdown("### 🔊 Escucha la traducción:")
        st.audio(audio_bytes, format="audio/mp3")
        st.markdown(f"**Traducción:** {translated_text}")

# Limpieza de archivos temporales
def clear_temp_files():
    temp_files = glob.glob("temp/*.mp3")
    for file in temp_files:
        os.remove(file)
        
clear_temp_files()

           


        
    


