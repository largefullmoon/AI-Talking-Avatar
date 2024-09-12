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
    return send_file(audio_file, as_attachment=True)

def text_to_speech(text):
    speech_file_path = "./speech.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text
    )
    response.stream_to_file(speech_file_path)
    return speech_file_path

def get_lip_move_steps(text):
    query = """
        Please provide a lip sync symbols for movement of my lips to the following following text.: '""" + text + """' by word.
        Please provide a main one lip sync symbol for each word. lip sync symbol should be one character.
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