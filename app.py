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


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        mode = request.form.get('mode', 'video')

        if not url:
            flash('Veuillez saisir une URL YouTube valide.', 'error')
            return redirect(url_for('index'))

        if not validate_url(url):
            flash('Veuillez utiliser une URL YouTube valide.', 'error')
            return redirect(url_for('index'))

        return redirect(url_for('download', mode=mode, url=url))

    return render_template('index.html')


@app.route('/download')
def download():
    url = request.args.get('url', '')
    mode = request.args.get('mode', 'video')

    if not url or not validate_url(url):
        flash('URL invalide ou manquante.', 'error')
        return redirect(url_for('index'))

    temp_dir = tempfile.mkdtemp(prefix='yt_dl_')
    outtmpl = os.path.join(temp_dir, '%(title).200s.%(ext)s')
    ydl_opts = (YDL_OPTS_AUDIO if mode == 'audio' else YDL_OPTS_VIDEO).copy()
    ydl_opts['outtmpl'] = outtmpl

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if mode == 'audio':
                filename = os.path.splitext(filename)[0] + '.mp3'

        return send_file(filename, as_attachment=True)
    except Exception as exc:
        flash(f'Erreur pendant le téléchargement : {exc}', 'error')
        return redirect(url_for('index'))
    finally:
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

        threading.Thread(target=cleanup, args=(temp_dir,), daemon=True).start()


if __name__ == '__main__':
    app.run(host='', port=, debug=True)
