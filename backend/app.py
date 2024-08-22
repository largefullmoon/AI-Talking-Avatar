import os
import speech_recognition as sr
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pydub import AudioSegment

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Adjust the origin to your React app's URL
cors = CORS(app, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST", "OPTIONS"])
app.app_context().push()

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route("/", methods=["get"])
def welcome():
    return "welcome"

def convert_to_wav(file_path):
    """Convert audio file to .wav format using pydub"""
    sound = AudioSegment.from_mp3(file_path)
    wav_file_path = file_path.replace('.mp3', '.wav')
    sound.export(wav_file_path, format='wav')
    return wav_file_path

@app.route('/upload', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    filename = secure_filename(audio_file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    audio_file.save(file_path)

    # Convert the audio file to .wav format for speech recognition
    wav_file_path = convert_to_wav(file_path)

    # Recognize the speech using SpeechRecognition library
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_file_path) as source:
        audio = recognizer.record(source)
        try:
            transcription = recognizer.recognize_google(audio)
            return jsonify({'transcription': transcription})
        except sr.UnknownValueError:
            return jsonify({'error': 'Could not understand the audio'}), 400
        except sr.RequestError as e:
            return jsonify({'error': f'Speech recognition request failed: {e}'}), 500