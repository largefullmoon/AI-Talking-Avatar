import os, openai
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
from dotenv import load_dotenv
from gtts import gTTS
from openai import OpenAI
import requests
import json
import time
from requests.adapters import HTTPAdapter
from difflib import SequenceMatcher
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
from elevenlabs.client import ElevenLabs
from elevenlabs import save

@app.route('/uploadVideo', methods=['POST'])
def uploadVideo():
    print("---------------------------------------------")
    # api_key = "sk_d08d647cbb6485f209bfc3461f869eb4e57f1750dba1f361"
    # # api_key = "sk_7e5b89695cddf2eb6550fe2d93fc9a670c1bb5fbad21dad0"
    # client = ElevenLabs(
    # api_key=api_key, # Defaults to ELEVEN_API_KEY
    # )
    # voice = client.clone(
    #     name="SampleVoice",
    #     description="An old American male voice with a slight hoarseness in his throat. Perfect for news",
    #     files=["./video.mp3"],
    # )

    # audio = client.generate(text="Hi! I'm a cloned voice!", voice=voice)

    # save(audio, './audio.mp3')
    # if voice_id:
        # text = "If you want to per   form voice cloning in real time (i.e., providing a new sample each time you call the text-to-speech (TTS) service), you will need to upload a new voice sample to ElevenLabs' API for each TTS request. ElevenLabs provides an API for creating and managing voice profiles, so you can dynamically upload a sample, get a unique voice_id, and then use that voice_id to generate speech from text."
        # synthesize_speech(text, voice_id)
        # time.sleep(10)
        # delete_voice(voice_id, api_key)
    audio_file = request.files['video']
    file_contents = audio_file.read()
    video_file = BytesIO(file_contents)
    video_file.name = audio_file.filename
    transcript = openai.audio.translations.create(model="whisper-1", file=video_file, response_format='text')
    return jsonify({"text": transcript})

def get_similarity_score(word, viseme):
    return SequenceMatcher(None, word.lower(), viseme.lower()).ratio()


@app.route('/upload', methods=['POST'])
def upload_audio():
    start_time = time.time()
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    audio_file = request.files['audio']
    file_contents = audio_file.read()
    mp3_file = BytesIO(file_contents)
    mp3_file.name = audio_file.filename
    transcript = openai.audio.translations.create(model="whisper-1", file=mp3_file, response_format='text')
    response = get_openai_response(transcript)
    # end_time = time.time()

    # # Calculate the total processing time
    # total_time = end_time - start_time
    # print(total_time)
    # # print(response)
    # api_url = "https://oliviaazure1.azurewebsites.net/ChatBotServiceRest.svc/GetAnswerNew"
    # user_id = "yassine"
    # bot_name = "yassine6991"
    # question = transcript
    # # Prepare query parameters
    # params = {
    #     "userID": user_id,
    #     "botName": bot_name,
    #     "question": question
    # }
    # try:
    #     # Send GET request to the API
    #     api_response = requests.get(api_url, params=params)
    #     # Check if the request was successful
    #     if api_response.status_code == 200:
    #         response = api_response.text
    # except Exception as e:
    #     return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    # end_time = time.time()

    # Calculate the total processing time
    # total_time = end_time - start_time
    # print(total_time)
    # steps = get_lip_move_steps(response)
    audio_file = text_to_speech(response)
    # Convert audio file to Base64
    with open(audio_file, "rb") as audio:
        audio_base64 = base64.b64encode(audio.read()).decode('utf-8')
    end_time = time.time()
    # Calculate the total processing time
    total_time = end_time - start_time
    print(total_time)
    audio_file = open(audio_file, "rb")
    transcript = client.audio.transcriptions.create(
        file=audio_file,
        model="whisper-1",
        response_format="verbose_json",
        timestamp_granularities=["word"]
    )
    # Match each word to the closest viseme
    words = transcript.words
    words = [word.to_dict() for word in words]
    visemes = [
        "mouthOpen", "viseme_PP", "viseme_FF", "Viseme_TH", "viseme_DD", "viseme_kk",
        "viseme_CH", "viseme_SS", "viseme_nn", "viseme_RR", "viseme_aa", "viseme_E",
        "viseme_I", "viseme_O", "viseme_U"
    ]
    for word_entry in words:
        word = word_entry['word']
        # Find the best-matched viseme
        best_match = max(visemes, key=lambda v: get_similarity_score(word, v))
        score = get_similarity_score(word, best_match)
        # Assign the best match to the word entry
        word_entry['viseme'] = best_match
        word_entry['similarity'] = round(score, 2)
    end_time = time.time()
    # Calculate the total processing time
    total_time = end_time - start_time
    print(total_time)
    # Return text and audio (in Base64 format) as JSON
    return jsonify({"text": response, "audio": audio_base64, 'steps': words})

def text_to_speech(text):
    speech_file_path = "./speech.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=text,
    )
    print(response, "response")
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
    user_input = "Please answer in 1 or 2 sentences brifely \n " + user_input + "\n Please don't use ' for response, such as you're, they're he's I'm"
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
import ssl

class SSLAdapter(HTTPAdapter):
    def __init__(self, ssl_version=None, **kwargs):
        self.ssl_version = ssl_version
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_version'] = self.ssl_version or ssl.PROTOCOL_TLSv1_2
        return super().init_poolmanager(*args, **kwargs)

session = requests.Session()
session.mount("https://", SSLAdapter(ssl.PROTOCOL_TLSv1_2))
