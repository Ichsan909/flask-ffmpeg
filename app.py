from flask import Flask, render_template, request, redirect, url_for
import subprocess
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static/uploads"
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ffmpeg_process = None  # Variabel global untuk menyimpan proses ffmpeg


def start_stream(video_path, rtmp_url):
    global ffmpeg_process
    if ffmpeg_process is None:
        command = [
            "ffmpeg", "-re", "-stream_loop", "-1", "-i", video_path,
            "-c:v", "libx264", "-preset", "fast", "-b:v", "8000k",
            "-maxrate", "8000k", "-bufsize", "16000k",
            "-pix_fmt", "yuv420p", "-g", "60",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-f", "flv", rtmp_url
        ]

        print("Memulai streaming ke:", rtmp_url)
        ffmpeg_process = subprocess.Popen(command)


def stop_stream():
    global ffmpeg_process
    if ffmpeg_process is not None:
        print("Menghentikan streaming...")
        ffmpeg_process.terminate()
        ffmpeg_process = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'video' not in request.files:
        return "Tidak ada file yang dipilih!", 400
    file = request.files['video']
    if file.filename == '':
        return "File tidak valid!", 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    return redirect(url_for('index'))


@app.route('/start', methods=['POST'])
def start():
    rtmp_server = request.form.get("rtmp_server")
    stream_key = request.form.get("stream_key")
    
    if not rtmp_server or not stream_key:
        return "RTMP Server dan Stream Key harus diisi!", 400
    
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], os.listdir(app.config['UPLOAD_FOLDER'])[0])
    rtmp_url = f"{rtmp_server}/{stream_key}"
    start_stream(video_path, rtmp_url)
    
    return redirect(url_for('index'))


@app.route('/stop', methods=['POST'])
def stop():
    stop_stream()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
