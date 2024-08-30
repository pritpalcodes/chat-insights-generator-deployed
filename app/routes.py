from flask import render_template, request, redirect, url_for, send_from_directory
from app import app
from app.utils import analyze_chat
import os

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'chat_file' not in request.files:
            return redirect(request.url)
        file = request.files['chat_file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            stats = analyze_chat(file_path)
            return redirect(url_for('results', stats=stats))
    return render_template('upload.html')

@app.route('/results')
def results():
    stats = request.args.get('stats')
    if stats:
        stats = eval(stats)  # Convert string representation of dict back to dict
        return render_template('results.html', stats=stats)
    return redirect(url_for('landing'))
