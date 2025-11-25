from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import pymongo
import socket

# Simple Flask application for Monitoring SaaS
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get('SECRET_KEY', 'devkey')

# Upload and data config
BASE_DIR = os.path.dirname(__file__)
# Store uploads under project-relative ./data/uploads for persistence across containers
UPLOAD_FOLDER = os.path.abspath(os.path.join(BASE_DIR, '..', 'data', 'uploads'))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'csv', 'json', 'txt', 'log'}

# MongoDB client
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://mongodb:27017')
MONGO_DB = os.environ.get('MONGO_DB', 'monitoring')
MONGO_COLLECTION = os.environ.get('MONGO_COLLECTION', 'uploads')
try:
    mongo_client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    # trigger server selection to fail fast if unreachable
    mongo_client.server_info()
    mongo_db = mongo_client[MONGO_DB]
    uploads_col = mongo_db[MONGO_COLLECTION]
except Exception as e:
    # If Mongo is unavailable, set uploads_col to None and log via prints (Flask logging not configured here)
    uploads_col = None
    print(f"Warning: cannot connect to MongoDB at {MONGO_URI}: {e}")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    # Return the index template
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')

    # POST (file upload)
    if 'file' not in request.files:
        msg = 'No file part'
        if request.is_json:
            return jsonify({'error': msg}), 400
        flash(msg)
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        msg = 'No selected file'
        if request.is_json:
            return jsonify({'error': msg}), 400
        flash(msg)
        return redirect(request.url)

    if not allowed_file(file.filename):
        msg = 'Invalid file format. Allowed: ' + ','.join(sorted(ALLOWED_EXTENSIONS))
        if request.is_json:
            return jsonify({'status': 'error', 'error': msg}), 400
        flash(msg)
        return redirect(request.url)

    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    # Save file to disk
    try:
        file.stream.seek(0)
        file.save(save_path)
    except Exception as e:
        msg = f'Error saving file: {e}'
        if request.is_json:
            return jsonify({'status': 'error', 'error': msg}), 500
        flash(msg)
        return redirect(request.url)

    # Gather metadata
    try:
        size = os.path.getsize(save_path)
    except Exception:
        size = None

    mtype = file.mimetype or ''
    upload_time = datetime.utcnow().isoformat() + 'Z'
    status = 'saved'

    metadata = {
        'filename': filename,
        'size': size,
        'uploaded_at': upload_time,
        'type': mtype,
        'extension': filename.rsplit('.', 1)[1].lower() if '.' in filename else '',
        'status': status,
        'uploader_host': socket.gethostname(),
    }

    # Store metadata in MongoDB if available
    inserted_id = None
    if uploads_col is not None:
        try:
            res = uploads_col.insert_one(metadata)
            inserted_id = str(res.inserted_id)
            metadata['_id'] = inserted_id
        except Exception as e:
            # record error in metadata but do not fail the upload itself
            metadata['status'] = 'error_saving_metadata'
            metadata['meta_error'] = str(e)
    else:
        metadata['status'] = 'mongo_unavailable'

    # Read first 10 lines for preview (text preview)
    preview_lines = []
    try:
        with open(save_path, 'r', encoding='utf-8', errors='replace') as f:
            for i, line in enumerate(f):
                if i >= 10:
                    break
                preview_lines.append(line.rstrip('\n'))
    except Exception as e:
        preview_lines = [f'Error reading file: {e}']

    response = {'status': 'success', 'metadata': metadata, 'preview': preview_lines}

    # If AJAX/JS expects JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return jsonify(response)

    # Otherwise render template with preview and metadata
    return render_template('upload.html', preview=preview_lines, filename=filename, metadata=metadata)


@app.route('/dashboard')
def dashboard():
    # Get statistics from MongoDB
    stats = {
        'total_uploads': 0,
        'success_uploads': 0,
        'error_uploads': 0,
        'uploads': []
    }
    
    if uploads_col is not None:
        try:
            # Total uploads
            stats['total_uploads'] = uploads_col.count_documents({})
            
            # Success uploads
            stats['success_uploads'] = uploads_col.count_documents({
                'status': {'$in': ['saved', 'processed']}
            })
            
            # Error uploads
            stats['error_uploads'] = uploads_col.count_documents({
                'status': 'error'
            })
            
            # Recent uploads (last 10)
            stats['uploads'] = list(uploads_col.find().sort('uploaded_at', -1).limit(10))
            
        except Exception as e:
            print(f"Error fetching dashboard stats: {e}")
    
    return render_template('dashboard.html', **stats)


if __name__ == '__main__':
    port = int(os.environ.get('FLASK_RUN_PORT', 8000))
    app.run(host='0.0.0.0', port=port)
