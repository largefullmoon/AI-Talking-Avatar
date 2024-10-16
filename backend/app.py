import os, openai
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
from dotenv import load_dotenv
from gtts import gTTS
from openai import OpenAI


client = OpenAI()


load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Adjust the origin to your React app's URL
cors = CORS(app, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST", "OPTIONS"])
app.app_context().push()
@app.route("/", methods=["get"])
def welcome():
    return "welcome"
import base64
@app.route('/upload', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    audio_file = request.files['audio']
    file_contents = audio_file.read()
    mp3_file = BytesIO(file_contents)
    mp3_file.name = audio_file.filename
    transcript = openai.audio.translations.create(model="whisper-1", file=mp3_file, response_format='text')
    response = get_openai_response(transcript)
    print(response)
    steps = get_lip_move_steps(response)
    print(steps)
    audio_file = text_to_speech(response)
    # return send_file(audio_file, as_attachment=True)
    # Convert audio file to Base64
    with open(audio_file, "rb") as audio:
        audio_base64 = base64.b64encode(audio.read()).decode('utf-8')
    
    # Return text and audio (in Base64 format) as JSON
    return jsonify({"text": response, "audio": audio_base64, 'steps': steps})

def text_to_speech(text):
    speech_file_path = "./speech.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=text
    )
    response.stream_to_file(speech_file_path)
    return speech_file_path

@app.route('/tts', methods=['POST'])
def tts():
    audio_file = text_to_speech(request.form['text'])
    return send_file(audio_file, as_attachment=True)
def get_lip_move_steps(text):
    query = """
        Please provide a lip sync symbols for movement of my lips to the following following text.: '""" + text + """' by word.
        Please provide a main one lip sync symbol and start time and end time and between_time time miri-seconds for each word. lip sync symbol should be on below visems array.
        Note: Every word's start and end time should be related all sentence's estimate time, between_time should be period from start_time and end_time
        Please describe the space of between another paragraph as "viseme_PP"
        This is visems array:
        ["mouthOpen",
        "viseme_PP",
        "viseme_FF",
        "Viseme_TH",
        "viseme_DD",
        "viseme_kk",
        "viseme_CH",
        "viseme_SS",
        "viseme_nn",
        "viseme_RR",
        "viseme_aa",
        "viseme_E",
        "viseme_I",
        "viseme_O",
        "viseme_U"]
        Please provide an only this JSON format. {word, lip_sync_symbol, start_time, end_time, between_time}
        Don't mention about texts like "```json```", and don't mention another unnecessary symbols and words. only return JSON.
    """
    try:
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": query}],
            stream=True,
        )
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
        return full_response
    except Exception as e:
        return e
def get_openai_response(user_input):
    try:
        # Define the OpenAI completion request
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": user_input}],
            stream=True,
        )
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
        return full_response

    except Exception as e:
        return e