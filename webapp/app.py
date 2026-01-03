from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, make_response
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import pymongo
import socket
from elasticsearch import Elasticsearch
from collections import defaultdict
import redis
import requests
from auth import init_auth_manager, login_required, api_login_required, check_auth, get_current_user

# Charger les variables d'environnement depuis .env manuellement
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key, value)

# Simple Flask application for Monitoring SaaS
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get('SECRET_KEY', 'devkey')

# Upload and data config
BASE_DIR = os.path.dirname(__file__)
# Store uploads in /app/uploads inside container (mounted as volume)
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'csv', 'json', 'txt', 'log'}

# MongoDB client
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
MONGO_DB = os.environ.get('MONGO_DB', 'monitoring')
MONGO_COLLECTION = os.environ.get('MONGO_COLLECTION', 'uploads')
try:
    mongo_client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    # trigger server selection to fail fast if unreachable
    mongo_client.server_info()
    mongo_db = mongo_client[MONGO_DB]
    uploads_col = mongo_db[MONGO_COLLECTION]
    users_col = mongo_db['users']  # Collection pour les utilisateurs
except Exception as e:
    # If Mongo is unavailable, set uploads_col to None and log via prints (Flask logging not configured here)
    uploads_col = None
    users_col = None
    print(f"Warning: cannot connect to MongoDB at {MONGO_URI}: {e}")

# Initialiser l'AuthManager avec la collection users
auth_manager = init_auth_manager(users_col)

# Elasticsearch client
ES_HOST = os.environ.get('ELASTICSEARCH_HOST', os.environ.get('ES_HOST', 'http://localhost:9200'))
try:
    es_client = Elasticsearch([ES_HOST], request_timeout=5)
    if es_client.ping():
        print(f"Connected to Elasticsearch at {ES_HOST}")
    else:
        es_client = None
        print(f"Warning: Elasticsearch ping failed at {ES_HOST}")
except Exception as e:
    es_client = None
    print(f"Warning: cannot connect to Elasticsearch at {ES_HOST}: {e}")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============================================
#  ROUTES D'AUTHENTIFICATION
# ============================================

@app.route('/login')
def login_page():
    """Page de connexion"""
    # Si déjà connecté, rediriger vers l'accueil
    if check_auth():
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/signup')
def signup_page():
    """Page d'inscription"""
    # Si déjà connecté, rediriger vers l'accueil
    if check_auth():
        return redirect(url_for('index'))
    return render_template('signup.html')


@app.route('/api/signup', methods=['POST'])
def api_signup():
    """API d'inscription - Crée un nouveau compte utilisateur"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not username or not email or not password:
            return jsonify({
                'success': False,
                'message': 'Tous les champs sont requis'
            }), 400
        
        if len(username) < 3:
            return jsonify({
                'success': False,
                'message': 'Le nom d\'utilisateur doit contenir au moins 3 caractères'
            }), 400
        
        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': 'Le mot de passe doit contenir au moins 6 caractères'
            }), 400
        
        # Créer l'utilisateur
        result = auth_manager.create_user(username, email, password)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur serveur: {str(e)}'
        }), 500


@app.route('/api/login', methods=['POST'])
def api_login():
    """API de connexion - Génère un token JWT"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        remember = data.get('remember', False)
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Nom d\'utilisateur et mot de passe requis'
            }), 400
        
        # Vérifier les credentials
        auth_result = auth_manager.verify_credentials(username, password)
        if not auth_result or not auth_result.get('valid'):
            return jsonify({
                'success': False,
                'message': 'Identifiants invalides'
            }), 401
        
        user_info = auth_result['user']
        
        # Générer le token
        token = auth_manager.generate_token(user_info)
        
        # Créer la réponse
        response = make_response(jsonify({
            'success': True,
            'message': 'Connexion réussie',
            'token': token,
            'user': user_info
        }))
        
        # Définir le cookie (expire dans 24h ou 30 jours si remember)
        max_age = 30 * 24 * 60 * 60 if remember else 24 * 60 * 60
        response.set_cookie(
            'access_token',
            token,
            max_age=max_age,
            httponly=True,
            secure=False,  # True en production avec HTTPS
            samesite='Lax'
        )
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur serveur: {str(e)}'
        }), 500


@app.route('/api/logout', methods=['POST'])
def api_logout():
    """API de déconnexion - Supprime le token"""
    response = make_response(jsonify({
        'success': True,
        'message': 'Déconnexion réussie'
    }))
    
    # Supprimer le cookie
    response.set_cookie('access_token', '', max_age=0)
    
    return response


@app.route('/api/verify-token', methods=['GET'])
def verify_token():
    """Vérifie si le token est valide"""
    user = get_current_user()
    
    if user:
        return jsonify({
            'success': True,
            'authenticated': True,
            'user': {
                'username': user['username'],
                'role': user['role']
            }
        })
    else:
        return jsonify({
            'success': False,
            'authenticated': False
        }), 401


# ============================================
#  ROUTES PROTÉGÉES
# ============================================

@app.route('/')
@login_required
def index():
    # Return the index template
    return render_template('index.html')


@app.route('/healthz')
def healthz():
    """Health check endpoint pour Docker (public, sans auth)"""
    return jsonify({'status': 'ok', 'service': 'webapp'}), 200


@app.route('/health')
@login_required
def health():
    """Page de health check pour tous les services"""
    return render_template('health.html')


@app.route('/search')
@login_required
def search():
    """Page de recherche personnalisée dans les logs"""
    return render_template('search.html')


@app.route('/api/health')
@api_login_required
def api_health():
    """API endpoint pour vérifier le statut de tous les services"""
    services = {}
    
    # Check Elasticsearch
    try:
        if es_client is not None and es_client.ping():
            cluster_health = es_client.cluster.health()
            services['elasticsearch'] = {
                'status': 'healthy',
                'url': ES_HOST,
                'cluster_status': cluster_health.get('status', 'unknown'),
                'nodes': cluster_health.get('number_of_nodes', 0),
                'response_time': 'OK'
            }
        else:
            services['elasticsearch'] = {
                'status': 'unhealthy',
                'url': ES_HOST,
                'error': 'Cannot ping Elasticsearch'
            }
    except Exception as e:
        services['elasticsearch'] = {
            'status': 'error',
            'url': ES_HOST,
            'error': str(e)
        }
    
    # Check MongoDB
    try:
        if uploads_col is not None:
            mongo_client.server_info()
            db_stats = mongo_db.command('dbStats')
            services['mongodb'] = {
                'status': 'healthy',
                'url': MONGO_URI,
                'database': MONGO_DB,
                'collections': db_stats.get('collections', 0),
                'data_size': db_stats.get('dataSize', 0)
            }
        else:
            services['mongodb'] = {
                'status': 'unhealthy',
                'url': MONGO_URI,
                'error': 'Connection not established'
            }
    except Exception as e:
        services['mongodb'] = {
            'status': 'error',
            'url': MONGO_URI,
            'error': str(e)
        }
    
    # Check Redis
    try:
        redis_host = os.environ.get('REDIS_HOST', 'localhost')
        redis_port = int(os.environ.get('REDIS_PORT', 6379))
        redis_client = redis.Redis(host=redis_host, port=redis_port, socket_connect_timeout=2)
        redis_info = redis_client.info()
        services['redis'] = {
            'status': 'healthy',
            'url': f'redis://{redis_host}:{redis_port}',
            'version': redis_info.get('redis_version', 'unknown'),
            'used_memory': redis_info.get('used_memory_human', 'unknown'),
            'connected_clients': redis_info.get('connected_clients', 0)
        }
    except Exception as e:
        redis_host = os.environ.get('REDIS_HOST', 'localhost')
        redis_port = int(os.environ.get('REDIS_PORT', 6379))
        services['redis'] = {
            'status': 'error',
            'url': f'redis://{redis_host}:{redis_port}',
            'error': str(e)
        }
    
    # Check Kibana
    try:
        kibana_host = os.environ.get('KIBANA_HOST', 'http://localhost:5601')
        kibana_response = requests.get(f'{kibana_host}/api/status', timeout=3)
        if kibana_response.status_code == 200:
            kibana_data = kibana_response.json()
            services['kibana'] = {
                'status': 'healthy',
                'url': kibana_host,
                'version': kibana_data.get('version', {}).get('number', 'unknown'),
                'state': kibana_data.get('status', {}).get('overall', {}).get('state', 'unknown')
            }
        else:
            services['kibana'] = {
                'status': 'unhealthy',
                'url': kibana_host,
                'error': f'HTTP {kibana_response.status_code}'
            }
    except Exception as e:
        kibana_host = os.environ.get('KIBANA_HOST', 'http://localhost:5601')
        services['kibana'] = {
            'status': 'error',
            'url': kibana_host,
            'error': str(e)
        }
    
    # Check Logstash
    try:
        logstash_host = os.environ.get('LOGSTASH_HOST', 'http://localhost:9600')
        logstash_response = requests.get(logstash_host, timeout=3)
        if logstash_response.status_code == 200:
            services['logstash'] = {
                'status': 'healthy',
                'url': logstash_host,
                'response': 'API responding'
            }
        else:
            services['logstash'] = {
                'status': 'unhealthy',
                'url': logstash_host,
                'error': f'HTTP {logstash_response.status_code}'
            }
    except Exception as e:
        logstash_host = os.environ.get('LOGSTASH_HOST', 'http://localhost:9600')
        services['logstash'] = {
            'status': 'error',
            'url': logstash_host,
            'error': str(e)
        }
    
    # Overall health
    healthy_count = sum(1 for s in services.values() if s.get('status') == 'healthy')
    total_count = len(services)
    
    return jsonify({
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'overall_status': 'healthy' if healthy_count == total_count else 'degraded',
        'healthy_services': healthy_count,
        'total_services': total_count,
        'services': services
    })


@app.route('/upload', methods=['GET', 'POST'])
@login_required
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


@app.route('/api/stats')
@api_login_required
def api_stats():
    """API endpoint pour récupérer les statistiques en temps réel"""
    stats = {
        'total_logs': 0,
        'logs_today': 0,
        'errors': 0,
        'files_uploaded': 0,
        'timeline': []
    }
    
    try:
        # Statistiques Elasticsearch
        if es_client is not None:
            # Total logs
            result = es_client.count(index='logs-*')
            stats['total_logs'] = result.get('count', 0)
            
            # Logs récents (dernières 24h de données disponibles)
            # Au lieu de chercher "aujourd'hui", on cherche les logs récents basés sur les données existantes
            recent_query = {
                'size': 0,
                'aggs': {
                    'max_date': {'max': {'field': '@timestamp'}},
                    'min_date': {'min': {'field': '@timestamp'}}
                }
            }
            result_dates = es_client.search(index='logs-*', body=recent_query)
            max_date_ms = result_dates.get('aggregations', {}).get('max_date', {}).get('value', None)
            
            if max_date_ms:
                # Calculer 24h avant la date la plus récente
                from datetime import datetime, timedelta
                max_date = datetime.fromtimestamp(max_date_ms / 1000)
                one_day_before = max_date - timedelta(days=1)
                
                recent_logs_query = {
                    'query': {
                        'range': {
                            '@timestamp': {
                                'gte': one_day_before.isoformat()
                            }
                        }
                    }
                }
                result_recent = es_client.count(index='logs-*', body=recent_logs_query)
                stats['logs_today'] = result_recent.get('count', 0)
            else:
                stats['logs_today'] = 0
            
            # Erreurs (status failed)
            error_query = {
                'query': {
                    'match': {
                        'status': 'failed'
                    }
                }
            }
            result_errors = es_client.count(index='logs-*', body=error_query)
            stats['errors'] = result_errors.get('count', 0)
            
            # Timeline de toutes les données disponibles (au lieu de seulement 7 derniers jours)
            timeline_query = {
                'size': 0,
                'aggs': {
                    'logs_over_time': {
                        'date_histogram': {
                            'field': '@timestamp',
                            'calendar_interval': 'day',
                            'format': 'yyyy-MM-dd'
                        }
                    }
                }
            }
            result_timeline = es_client.search(index='logs-*', body=timeline_query)
            buckets = result_timeline.get('aggregations', {}).get('logs_over_time', {}).get('buckets', [])
            # Limiter à 30 derniers jours de données pour ne pas surcharger le graphe
            stats['timeline'] = [{'date': b['key_as_string'], 'count': b['doc_count']} for b in buckets[-30:]]
            
    except Exception as e:
        print(f"Error fetching Elasticsearch stats: {e}")
    
    # Fichiers uploadés depuis MongoDB
    if uploads_col is not None:
        try:
            stats['files_uploaded'] = uploads_col.count_documents({})
        except Exception as e:
            print(f"Error fetching MongoDB stats: {e}")
    
    return jsonify(stats)


@app.route('/api/search')
@api_login_required
def api_search():
    """API endpoint pour rechercher dans les logs Elasticsearch"""
    # Récupérer les paramètres de recherche
    query_text = request.args.get('query', '').strip()
    level = request.args.get('level', '').strip()
    service = request.args.get('service', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()
    page = int(request.args.get('page', 1))
    page_size = 50
    
    # Construire la requête Elasticsearch
    must_conditions = []
    
    # Recherche texte libre
    if query_text:
        must_conditions.append({
            'multi_match': {
                'query': query_text,
                'fields': ['message', 'product', 'customer_name', 'payment_type'],
                'type': 'best_fields',
                'fuzziness': 'AUTO'
            }
        })
    
    # Filtre par niveau (status)
    if level:
        must_conditions.append({
            'match': {
                'status': level
            }
        })
    
    # Filtre par service
    if service:
        must_conditions.append({
            'match': {
                'service': service
            }
        })
    
    # Filtre par plage de dates
    if date_from or date_to:
        date_range = {}
        if date_from:
            date_range['gte'] = date_from
        if date_to:
            date_range['lte'] = date_to
        
        must_conditions.append({
            'range': {
                '@timestamp': date_range
            }
        })
    
    # Si aucun filtre, afficher tous les logs
    if not must_conditions:
        es_query = {
            'query': {
                'match_all': {}
            }
        }
    else:
        es_query = {
            'query': {
                'bool': {
                    'must': must_conditions
                }
            }
        }
    
    # Ajouter tri et pagination
    es_query['sort'] = [{'@timestamp': {'order': 'desc'}}]
    es_query['from'] = (page - 1) * page_size
    es_query['size'] = page_size
    
    # Exécuter la recherche
    results = {
        'success': False,
        'total': 0,
        'page': page,
        'page_size': page_size,
        'total_pages': 0,
        'logs': [],
        'query_params': {
            'query': query_text,
            'level': level,
            'service': service,
            'date_from': date_from,
            'date_to': date_to
        }
    }
    
    try:
        if es_client is not None:
            response = es_client.search(index='logs-*', body=es_query)
            
            total_hits = response['hits']['total']['value']
            results['success'] = True
            results['total'] = total_hits
            results['total_pages'] = (total_hits + page_size - 1) // page_size
            
            # Extraire les logs
            for hit in response['hits']['hits']:
                source = hit['_source']
                log_entry = {
                    'timestamp': source.get('@timestamp', ''),
                    'level': source.get('status', source.get('level', 'info')),
                    'service': source.get('service', 'unknown'),
                    'message': source.get('message', ''),
                    'product': source.get('product', ''),
                    'customer': source.get('customer_name', ''),
                    'payment_type': source.get('payment_type', ''),
                    'amount': source.get('amount', ''),
                    'category': source.get('category', '')
                }
                results['logs'].append(log_entry)
            
            # Sauvegarder l'historique de recherche dans MongoDB
            if uploads_col is not None:
                try:
                    history_collection = mongo_db['search_history']
                    history_entry = {
                        'timestamp': datetime.utcnow(),
                        'query_text': query_text,
                        'level': level,
                        'service': service,
                        'date_from': date_from,
                        'date_to': date_to,
                        'results_count': total_hits,
                        'ip_address': request.remote_addr
                    }
                    history_collection.insert_one(history_entry)
                except Exception as e:
                    print(f"Error saving search history: {e}")
        
        else:
            results['error'] = 'Elasticsearch client not available'
    
    except Exception as e:
        results['error'] = str(e)
        print(f"Search error: {e}")
    
    return jsonify(results)


@app.route('/dashboard')
@login_required
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
