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

# Titulo e imagen de bienvenida
st.title("Traductor de Voz Inteligente")
st.markdown("#### 🗣️ Dime lo que quieras traducir y escucha tu frase en el idioma que elijas!")
image = Image.open('traductorimg.png')
st.image(image, width=300)

# Sidebar con instrucciones
with st.sidebar:
    st.subheader("¿Como funciona?")
    st.write("1. Haz clic en 'Escuchar' para iniciar la grabacion.")
    st.write("2. Pronuncia la frase que deseas traducir.")
    st.write("3. Selecciona los idiomas de entrada y salida.")
    st.write("4. Haz clic en 'Convertir' para obtener la traduccion en audio.")

# Configuracion del boton de reconocimiento de voz
st.write("**Pulsa el boton para iniciar la escucha:**")
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

# Creacion de carpetas temporales para los audios
try:
    os.mkdir("temp")
except:
    pass

# Configuracion de idiomas de entrada y salida
translator = Translator()
input_language = st.selectbox("Idioma de entrada:", ["Ingles", "Espanol", "Mandarin", "Japones", "Frances"])
output_language = st.selectbox("Idioma de salida:", ["Ingles", "Espanol", "Mandarin", "Japones", "Frances"])

# Mapeo de lenguajes
language_map = {
    "Ingles": "en", "Espanol": "es", "Mandarin": "zh-cn",
    "Japones": "ja", "Frances": "fr"
}
input_language_code = language_map.get(input_language)
output_language_code = language_map.get(output_language)

# Mapeo de acentos
tld = "com"

# Funcion para convertir texto a voz y guardar el audio
def text_to_speech(text, input_language, output_language, tld):
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, tld=tld)
    audio_file = f"temp/{text[:20]}.mp3"
    tts.save(audio_file)
    return audio_file, trans_text

# Boton para iniciar la traduccion
if st.button("Convertir y Escuchar"):
    if input_text:
        audio_path, translated_text = text_to_speech(input_text, input_language_code, output_language_code, tld)
        audio_file = open(audio_path, "rb")
        audio_bytes = audio_file.read()
        
        # Despliegue de texto traducido y audio
        st.markdown("### 🔊 Escucha la traduccion:")
        st.audio(audio_bytes, format="audio/mp3")
        st.markdown(f"**Traduccion:** {translated_text}")

# Limpieza de archivos temporales
def clear_temp_files():
    temp_files = glob.glob("temp/*.mp3")
    for file in temp_files:
        os.remove(file)
        
clear_temp_files()


           


        
    


