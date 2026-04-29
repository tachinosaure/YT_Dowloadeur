import os
import re
import tempfile
import threading
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from yt_dlp import YoutubeDL

app = Flask(__name__)
app.secret_key = os.urandom(24)

YDL_OPTS_VIDEO = {
    'format': 'bestvideo[height<=1080]+bestaudio/best',
    'merge_output_format': 'mp4',
    'quiet': True,
    'no_warnings': True,
}

YDL_OPTS_AUDIO = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

URL_PATTERN = re.compile(r'https?://(www\.)?(youtube\.com|youtu\.be)/')


def validate_url(url):
    return bool(URL_PATTERN.search(url))


def cleanup(path):
    try:
        for f in os.listdir(path):
            try:
                os.remove(os.path.join(path, f))
            except OSError:
                pass
        os.rmdir(path)
    except OSError:
        pass


def download_file(url, mode, cookiefile=None):
    temp_dir = tempfile.mkdtemp(prefix='yt_dl_')
    outtmpl = os.path.join(temp_dir, '%(title).200s.%(ext)s')
    ydl_opts = (YDL_OPTS_AUDIO if mode == 'audio' else YDL_OPTS_VIDEO).copy()
    ydl_opts['outtmpl'] = outtmpl
    if cookiefile:
        ydl_opts['cookiefile'] = cookiefile

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if mode == 'audio':
                filename = os.path.splitext(filename)[0] + '.mp3'

        return filename, temp_dir
    except Exception:
        cleanup(temp_dir)
        raise


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/download', methods=['GET', 'POST'])
def download():
    temp_cookie_dir = None
    cookiefile = None

    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        mode = request.form.get('mode', 'video')
        cookies = request.files.get('cookies')

        if cookies and cookies.filename:
            temp_cookie_dir = tempfile.mkdtemp(prefix='yt_dl_cookies_')
            cookiefile = os.path.join(temp_cookie_dir, 'cookies.txt')
            cookies.save(cookiefile)
    else:
        url = request.args.get('url', '')
        mode = request.args.get('mode', 'video')

    if not url or not validate_url(url):
        flash('URL invalide ou manquante.', 'error')
        if temp_cookie_dir:
            cleanup(temp_cookie_dir)
        return redirect(url_for('index'))

    temp_dir = None
    try:
        filename, temp_dir = download_file(url, mode, cookiefile)
        return send_file(filename, as_attachment=True)
    except Exception as exc:
        error_message = str(exc)
        if 'Sign in to confirm you’re not a bot' in error_message:
            flash(
                'YouTube demande une connexion. Exportez vos cookies depuis votre navigateur et téléchargez-les ici.',
                'error'
            )
        else:
            flash(f'Erreur pendant le téléchargement : {error_message}', 'error')
        return redirect(url_for('index'))
    finally:
        if temp_dir:
            threading.Thread(target=cleanup, args=(temp_dir,), daemon=True).start()
        if temp_cookie_dir:
            threading.Thread(target=cleanup, args=(temp_cookie_dir,), daemon=True).start()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
