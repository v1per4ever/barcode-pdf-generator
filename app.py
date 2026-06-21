import os
import csv
import zipfile
import tempfile
import shutil
from flask import Flask, request, render_template, send_file, jsonify
from werkzeug.utils import secure_filename
from generate_pdf import generate_from_csv

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.secret_key = 'super_secret_key'

def get_csv_preview(file_path):
    encodings = ['utf-8', 'utf-8-sig', 'cp1251', 'latin-1']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                reader = csv.DictReader(f)
                rows = [row for i, row in enumerate(reader) if i < 10]
                return rows
        except Exception:
            pass
    return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Нет файла'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400
    
    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        preview = get_csv_preview(filepath)
        return jsonify({'success': True, 'filepath': filepath, 'preview': preview})
        
    return jsonify({'error': 'Неверный формат файла. Нужен CSV.'}), 400

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    filepath = data.get('filepath')
    
    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'Файл не найден. Загрузите заново.'}), 400
        
    temp_dir = tempfile.mkdtemp()
    output_zip = os.path.join(app.config['UPLOAD_FOLDER'], 'barcodes.zip')
    
    try:
        # Генерируем PDF
        generated_files = generate_from_csv(filepath, temp_dir)
        
        # Создаем ZIP
        with zipfile.ZipFile(output_zip, 'w') as zipf:
            for file in generated_files:
                zipf.write(file, os.path.basename(file))
                
        return jsonify({'success': True, 'download_url': '/download'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

@app.route('/download')
def download():
    output_zip = os.path.join(app.config['UPLOAD_FOLDER'], 'barcodes.zip')
    if os.path.exists(output_zip):
        return send_file(output_zip, as_attachment=True, download_name='barcodes.zip')
    return "Файл не найден", 404

if __name__ == '__main__':
    import webbrowser
    from threading import Timer
    
    # Автоматически открываем браузер
    Timer(1.25, lambda: webbrowser.open('http://127.0.0.1:5000/')).start()
    app.run(debug=True, use_reloader=False)
