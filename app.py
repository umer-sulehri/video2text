from flask import Flask, render_template, request, send_file, jsonify
import openai
import os
from moviepy.editor import VideoFileClip
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
from werkzeug.utils import secure_filename
import magic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'video': {'mp4', 'avi', 'mov', 'mkv'},
    'audio': {'wav', 'mp3', 'ogg', 'm4a'}
}

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please create a .env file with your API key.")

def allowed_file(filename, file_type):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS[file_type]

def is_valid_file_type(file_path, expected_type):
    """Check if file is of expected type using file extension and magic numbers"""
    # First check file extension
    if not allowed_file(file_path, expected_type):
        return False
    
    # Then check magic numbers
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(file_path)
    
    if expected_type == 'video':
        return 'video' in file_type
    elif expected_type == 'audio':
        return 'audio' in file_type or file_type.startswith('video')  # Some audio files might be detected as video
    return False

def video_to_audio(video_path):
    """Convert video to audio"""
    if not is_valid_file_type(video_path, 'video'):
        raise ValueError("Invalid video file. Please upload a valid video file (mp4, avi, mov, mkv)")
    
    video = VideoFileClip(video_path)
    audio = video.audio
    
    if audio is None:
        raise ValueError("No audio track found in the video file")
    
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.wav')
    audio.write_audiofile(output_path)
    
    video.close()
    audio.close()
    
    return output_path

def audio_to_text(audio_path):
    """Convert audio to text using OpenAI Whisper API"""
    if not is_valid_file_type(audio_path, 'audio'):
        raise ValueError("Invalid audio file. Please upload a valid audio file (wav, mp3, ogg, m4a)")
    
    with open(audio_path, 'rb') as audio_file:
        transcript = openai.Audio.transcribe(
            "whisper-1",
            audio_file
        )
        return transcript['text']

def video_to_text(video_path):
    """Convert video to text by first converting to audio then to text"""
    audio_path = video_to_audio(video_path)
    text = audio_to_text(audio_path)
    
    # Clean up temporary files
    if os.path.exists(audio_path):
        os.remove(audio_path)
    return text

def summarize_text(text):
    """Summarize text using OpenAI GPT model"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Please provide a concise summary of the following text:"},
            {"role": "user", "content": text}
        ],
        max_tokens=150
    )
    return response.choices[0].message['content']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    conversion_type = request.form.get('conversion_type')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    try:
        result = {}
        
        if conversion_type == 'video_to_audio':
            output_path = video_to_audio(file_path)
            return send_file(output_path, as_attachment=True, download_name='converted_audio.wav')
        
        elif conversion_type == 'audio_to_text':
            text = audio_to_text(file_path)
            result['text'] = text
            
        elif conversion_type == 'video_to_text':
            text = video_to_text(file_path)
            result['text'] = text
            
        # If text was generated and summarization is requested
        if 'text' in result and request.form.get('summarize') == 'true':
            result['summary'] = summarize_text(result['text'])
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

@app.route('/summarize', methods=['POST'])
def summarize():
    text = request.json.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        summary = summarize_text(text)
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 