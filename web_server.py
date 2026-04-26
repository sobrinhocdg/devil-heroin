from datetime import datetime
import os
import random

from flask import Flask, redirect, render_template_string, request, send_from_directory, url_for

from midi_generator import create_midi, clamp

app = Flask(__name__)
RELEASE_DIR = 'releases'

HTML_TEMPLATE = '''
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Gerador Dungeon Synth MIDI</title>
  <style>
    body { background: #111; color: #ddd; font-family: Arial, sans-serif; padding: 24px; }
    input, select, button { font-size: 1rem; padding: 10px; margin: 6px 0; width: 100%; max-width: 420px; }
    label { display: block; margin-top: 14px; }
    .card { background: #181818; border: 1px solid #333; padding: 20px; border-radius: 12px; max-width: 540px; }
    a { color: #7fc7ff; }
    .footer { margin-top: 20px; font-size: 0.9rem; color: #888; }
  </style>
</head>
<body>
  <h1>Gerador Dungeon Synth MIDI</h1>
  <div class="card">
    <form method="post" action="{{ url_for('generate') }}">
      <label for="title">Título do release</label>
      <input id="title" name="title" value="{{ title }}" required>

      <label for="tempo">Tempo (BPM)</label>
      <input id="tempo" name="tempo" type="number" min="40" max="90" value="{{ tempo }}" required>

      <label for="bars">Compassos</label>
      <input id="bars" name="bars" type="number" min="8" max="128" value="{{ bars }}" required>

      <label for="tracks">Tracks (1 a 12)</label>
      <input id="tracks" name="tracks" type="number" min="1" max="12" value="{{ tracks }}" required>

      <label for="seed">Seed (opcional)</label>
      <input id="seed" name="seed" value="{{ seed }}" placeholder="Deixe em branco para variar">

      <button type="submit">Gerar MIDI</button>
    </form>

    {% if generated_file %}
      <p>Arquivo gerado:</p>
      <p><a href="{{ url_for('download', filename=generated_file) }}">{{ generated_file }}</a></p>
    {% endif %}
  </div>

  <div class="card" style="margin-top:24px;">
    <h2>Últimos arquivos</h2>
    <ul>
      {% for item in recent_files %}
        <li><a href="{{ url_for('download', filename=item) }}">{{ item }}</a></li>
      {% endfor %}
    </ul>
  </div>

  <div class="footer">
    <p>Use o FL Studio para importar o MIDI e atribuir sintetizadores sombrios no Channel Rack.</p>
  </div>
</body>
</html>
'''


def list_recent_files(directory, count=10):
    if not os.path.isdir(directory):
        return []
    files = [f for f in os.listdir(directory) if f.lower().endswith('.mid')]
    files.sort(key=lambda name: os.path.getmtime(os.path.join(directory, name)), reverse=True)
    return files[:count]


@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE,
                                  title='afterrelease33',
                                  tempo=64,
                                  bars=32,
                                  tracks=8,
                                  seed='',
                                  generated_file=None,
                                  recent_files=list_recent_files(RELEASE_DIR, 10))


@app.route('/generate', methods=['POST'])
def generate():
    title = request.form.get('title', 'release_sombrio')
    tempo = int(request.form.get('tempo', 64))
    bars = int(request.form.get('bars', 32))
    tracks = int(request.form.get('tracks', 8))
    seed_raw = request.form.get('seed', '').strip()
    seed = int(seed_raw) if seed_raw.isdigit() else random.randint(0, 2**31 - 1)

    file_path = create_midi(title, clamp(tempo, 40, 90), clamp(bars, 8, 128), clamp(tracks, 1, 12), seed, RELEASE_DIR)
    filename = os.path.basename(file_path)
    return render_template_string(HTML_TEMPLATE,
                                  title=title,
                                  tempo=tempo,
                                  bars=bars,
                                  tracks=tracks,
                                  seed=seed_raw,
                                  generated_file=filename,
                                  recent_files=list_recent_files(RELEASE_DIR, 10))


@app.route('/downloads/<path:filename>')
def download(filename):
    return send_from_directory(RELEASE_DIR, filename, as_attachment=True)


if __name__ == '__main__':
    os.makedirs(RELEASE_DIR, exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
