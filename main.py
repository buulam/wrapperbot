from flask import Flask, request
from dotenv import load_dotenv
import os
import whisper
import openai

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    html = '''
    <html>
        <head>
            <title>WrapperBot</title>
        </head>
        <body>
            <h1>Welcome to WrapperBot</h1>
            <p>Upload your video file to create a wrapper article.</p>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="video_file" accept="video/*">
                <input type="submit" value="Upload Video">
            </form>
        </body>
    </html>
    '''
    return html

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video_file' not in request.files:
        return "No file part", 400
    file = request.files['video_file']
    if file.filename == '':
        return "No selected file", 400
    uploads_dir = os.path.join(os.getcwd(), 'videos')
    os.makedirs(uploads_dir, exist_ok=True)
    file_path = os.path.join(uploads_dir, file.filename)
    file.save(file_path)
    print(f"Received file: {file.filename}")

    # Load Whisper model and transcribe
    model = whisper.load_model("base")  # You can use "tiny", "base", "small", "medium", or "large"
    result = model.transcribe(file_path)
    transcript = result["text"]

    # Manipulate transcript with ChatGPT
    openai.api_key = os.getenv("OPENAI_API_KEY")  # Set your API key in your environment
    prompt = f"Using the following transcript from a video, prepare a blog post about the contents of the Data Leakage Detection and Prevention script included in this notebook. This script was from an explainer video that was done in the style of 'Brightboard Lesson'. The blog post should focus on the challenges faced in the industry more than the solution being proposed. It needs to come off with less marketing and more technical solution:\n\n{transcript}"
    chat_response = openai.chat.completions.create(
        model="gpt-4o",  # or "gpt-4" if you have access
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    manipulated_transcript = chat_response.choices[0].message.content

    return (
        f"File '{file.filename}' uploaded successfully!<br><br>"
        f"<b>Transcript:</b><br>"
        f"<pre style='white-space: pre-wrap; word-break: break-word;'>{transcript}</pre><br><br>"
        f"<b>Manipulated Transcript (ChatGPT):</b><br>"
        f"<pre style='white-space: pre-wrap; word-break: break-word;'>{manipulated_transcript}</pre>"
    )
if __name__ == "__main__":
    app.run(debug=True)