"""
Main JARVIS Application
Web interface for interacting with JARVIS modules
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import os
import threading
import time
from datetime import datetime

from config.logging_config import get_logger
from config.settings import SERVER_CONFIG, APP_CONFIG, MODULES_CONFIG
from modules.assistant_core import JarvisAssistantCore

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize logger
logger = get_logger('WebApp')

# Initialize JARVIS Assistant
jarvis = JarvisAssistantCore()

# Global variables
speech_results = []
speech_active = False


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html', 
                         app_config=APP_CONFIG,
                         modules=MODULES_CONFIG)


@app.route('/speech-to-text')
def speech_to_text_page():
    """Speech to Text module page"""
    return render_template('speech_to_text.html', 
                         app_config=APP_CONFIG)


@app.route('/text-to-speech')
def text_to_speech_page():
    """Text to Speech module page"""
    return render_template('text_to_speech.html', 
                         app_config=APP_CONFIG)


@app.route('/datetime')
def datetime_page():
    """DateTime module page"""
    return render_template('datetime.html', 
                         app_config=APP_CONFIG)


@app.route('/calendar')
def calendar_page():
    """Calendar module page"""
    return render_template('calendar.html', 
                         app_config=APP_CONFIG)


@app.route('/api/modules/status')
def get_modules_status():
    """Get status of all modules"""
    try:
        status = jarvis.get_module_status()
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        logger.error(f"Error getting module status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/speech/listen-once', methods=['POST'])
def listen_once():
    """Listen for speech once"""
    try:
        data = request.get_json() or {}
        timeout = data.get('timeout', 10)
        
        if not jarvis.is_module_available('speech_to_text'):
            return jsonify({
                'success': False,
                'error': 'Speech to Text module not available'
            }), 400
        
        # Start listening
        result = jarvis.start_speech_recognition(continuous=False)
        
        return jsonify({
            'success': True,
            'data': {
                'text': result,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error in listen_once: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/speech/start-continuous', methods=['POST'])
def start_continuous_listening():
    """Start continuous speech recognition"""
    global speech_active, speech_results
    
    try:
        if not jarvis.is_module_available('speech_to_text'):
            return jsonify({
                'success': False,
                'error': 'Speech to Text module not available'
            }), 400
        
        if speech_active:
            return jsonify({
                'success': False,
                'error': 'Continuous listening already active'
            }), 400
        
        # Clear previous results
        speech_results = []
        speech_active = True
        
        # Start continuous listening with custom callback
        def speech_callback(text):
            global speech_results
            speech_results.append({
                'text': text,
                'timestamp': datetime.now().isoformat()
            })
            # Keep only last 50 results
            if len(speech_results) > 50:
                speech_results = speech_results[-50:]
        
        stt_module = jarvis.modules['speech_to_text']
        stt_module.start_continuous_listening(speech_callback)
        
        return jsonify({
            'success': True,
            'message': 'Continuous listening started'
        })
        
    except Exception as e:
        logger.error(f"Error starting continuous listening: {e}")
        speech_active = False
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/speech/stop-continuous', methods=['POST'])
def stop_continuous_listening():
    """Stop continuous speech recognition"""
    global speech_active
    
    try:
        if not speech_active:
            return jsonify({
                'success': False,
                'error': 'Continuous listening not active'
            }), 400
        
        jarvis.stop_speech_recognition()
        speech_active = False
        
        return jsonify({
            'success': True,
            'message': 'Continuous listening stopped'
        })
        
    except Exception as e:
        logger.error(f"Error stopping continuous listening: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/speech/results')
def get_speech_results():
    """Get continuous speech recognition results"""
    global speech_results, speech_active
    
    return jsonify({
        'success': True,
        'data': {
            'results': speech_results,
            'active': speech_active,
            'count': len(speech_results)
        }
    })


@app.route('/api/speech/process-text', methods=['POST'])
def process_text_command():
    """Process a text command"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'Text parameter required'
            }), 400
        
        text = data['text'].strip()
        if not text:
            return jsonify({
                'success': False,
                'error': 'Text cannot be empty'
            }), 400
        
        # Process the command
        response = jarvis.process_text_command(text)
        
        return jsonify({
            'success': True,
            'data': {
                'input': text,
                'response': response,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error processing text command: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/tts/speak', methods=['POST'])
def text_to_speech():
    """Convert text to speech"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'Text parameter required'
            }), 400
        
        text = data['text'].strip()
        if not text:
            return jsonify({
                'success': False,
                'error': 'Text cannot be empty'
            }), 400
        
        if not jarvis.is_module_available('text_to_speech'):
            return jsonify({
                'success': False,
                'error': 'Text to Speech module not available'
            }), 400
        
        blocking = data.get('blocking', False)
        tts_module = jarvis.modules['text_to_speech']
        tts_module.speak(text, blocking=blocking)
        
        return jsonify({
            'success': True,
            'message': 'Text spoken successfully'
        })
        
    except Exception as e:
        logger.error(f"Error in text to speech: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/datetime/current', methods=['GET'])
def get_current_datetime():
    """Get current date and time"""
    try:
        if not jarvis.is_module_available('datetime_module'):
            return jsonify({
                'success': False,
                'error': 'DateTime module not available'
            }), 400
        
        dt_module = jarvis.modules['datetime_module']
        
        return jsonify({
            'success': True,
            'data': {
                'nepal_time': dt_module.get_nepal_time(),
                'nepal_date': dt_module.get_nepal_datetime("%Y-%m-%d"),
                'nepal_datetime': dt_module.get_nepal_datetime(),
                'utc_time': dt_module.get_utc_time(),
                'utc_date': dt_module.get_utc_datetime("%Y-%m-%d"),
                'utc_datetime': dt_module.get_utc_datetime(),
                'current_time': dt_module.get_current_time(),
                'current_date': dt_module.get_current_date(),
                'current_datetime': dt_module.get_current_datetime(),
                'day_of_week': dt_module.get_day_of_week(),
                'month_name': dt_module.get_month_name(),
                'is_weekend': dt_module.is_weekend()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting datetime: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/calendar/events', methods=['GET'])
def get_calendar_events():
    """Get calendar events"""
    try:
        if not jarvis.is_module_available('calendar_module'):
            return jsonify({
                'success': False,
                'error': 'Calendar module not available'
            }), 400
        
        calendar_module = jarvis.modules['calendar_module']
        
        # Check if a specific date is requested
        date_str = request.args.get('date')
        if date_str:
            try:
                target_date = datetime.fromisoformat(date_str).date()
                events = calendar_module.get_events_for_date(target_date)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
        else:
            # Get upcoming events based on days parameter
            days = request.args.get('days', 7, type=int)
            events = calendar_module.get_upcoming_events(days)
        
        events_data = []
        
        for event in events:
            events_data.append({
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'start_time': event.start_time.isoformat(),
                'end_time': event.end_time.isoformat(),
                'location': event.location,
                'is_all_day': event.is_all_day
            })
        
        return jsonify({
            'success': True,
            'data': {
                'events': events_data,
                'count': len(events_data)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting calendar events: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/calendar/events', methods=['POST'])
def create_calendar_event():
    """Create a new calendar event"""
    try:
        if not jarvis.is_module_available('calendar_module'):
            return jsonify({
                'success': False,
                'error': 'Calendar module not available'
            }), 400
        
        data = request.get_json()
        required_fields = ['title', 'start_time', 'end_time']
        
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        calendar_module = jarvis.modules['calendar_module']
        
        # Parse datetime strings
        start_time = datetime.fromisoformat(data['start_time'])
        end_time = datetime.fromisoformat(data['end_time'])
        
        event_id = calendar_module.create_event(
            title=data['title'],
            start_time=start_time,
            end_time=end_time,
            description=data.get('description', ''),
            location=data.get('location', ''),
            attendees=data.get('attendees', []),
            reminder_minutes=data.get('reminder_minutes', 15),
            is_all_day=data.get('is_all_day', False),
            recurrence=data.get('recurrence', 'none')
        )
        
        return jsonify({
            'success': True,
            'data': {
                'event_id': event_id,
                'message': 'Event created successfully'
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating calendar event: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/calendar/summary')
def get_calendar_summary():
    """Get calendar summary"""
    try:
        if not jarvis.is_module_available('calendar_module'):
            return jsonify({
                'success': False,
                'error': 'Calendar module not available'
            }), 400
        
        calendar_module = jarvis.modules['calendar_module']
        days = request.args.get('days', 7, type=int)
        
        summary = calendar_module.get_calendar_summary(days)
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        logger.error(f"Error getting calendar summary: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/calendar/matrix')
def get_calendar_matrix():
    """Get calendar matrix for display"""
    try:
        if not jarvis.is_module_available('calendar_module'):
            return jsonify({
                'success': False,
                'error': 'Calendar module not available'
            }), 400
        
        calendar_module = jarvis.modules['calendar_module']
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        
        matrix_data = calendar_module.get_calendar_matrix(year, month)
        
        # Convert date objects to ISO strings for JSON serialization
        for week in matrix_data['calendar_matrix']:
            for day_data in week:
                day_data['date'] = day_data['date'].isoformat()
                # Convert event objects to dictionaries
                day_data['events'] = [{
                    'id': event.id,
                    'title': event.title,
                    'start_time': event.start_time.isoformat(),
                    'end_time': event.end_time.isoformat()
                } for event in day_data['events']]
        
        return jsonify({
            'success': True,
            'data': matrix_data
        })
        
    except Exception as e:
        logger.error(f"Error getting calendar matrix: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Create templates directory and files
def create_templates():
    """Create HTML templates for the web interface"""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)
    
    # Create base template
    base_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ app_config.name }}{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .module-card {
            transition: transform 0.2s;
            cursor: pointer;
        }
        .module-card:hover {
            transform: translateY(-5px);
        }
        .module-enabled {
            border-left: 4px solid #28a745;
        }
        .module-disabled {
            border-left: 4px solid #dc3545;
        }
        .navbar-brand {
            font-weight: bold;
            font-size: 1.5rem;
        }
        .status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 5px;
        }
        .status-online { background-color: #28a745; }
        .status-offline { background-color: #dc3545; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-robot me-2"></i>{{ app_config.name }}
            </a>
            <div class="navbar-nav ms-auto">
                <span class="navbar-text">
                    <span class="status-indicator status-online"></span>
                    System Online
                </span>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>"""
    
    # Create index template
    index_template = """{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="jumbotron bg-primary text-white p-5 rounded mb-4">
            <h1 class="display-4">Welcome to {{ app_config.name }}</h1>
            <p class="lead">{{ app_config.description }}</p>
            <hr class="my-4">
            <p>Select a module to get started with your AI assistant.</p>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-12 mb-4">
        <h2>Available Modules</h2>
    </div>
</div>

<div class="row">
    {% for module_name, module_config in modules.items() %}
    <div class="col-md-6 col-lg-4 mb-4">
        <div class="card module-card h-100 {{ 'module-enabled' if module_config.enabled else 'module-disabled' }}">
            <div class="card-body">
                <h5 class="card-title">
                    {% if module_name == 'speech_to_text' %}
                        <i class="fas fa-microphone me-2"></i>Speech to Text
                    {% elif module_name == 'text_to_speech' %}
                        <i class="fas fa-volume-up me-2"></i>Text to Speech
                    {% elif module_name == 'nlp_module' %}
                        <i class="fas fa-brain me-2"></i>NLP Module
                    {% elif module_name == 'task_manager' %}
                        <i class="fas fa-tasks me-2"></i>Task Manager
                    {% elif module_name == 'calendar_module' %}
                        <i class="fas fa-calendar me-2"></i>Calendar
                    {% elif module_name == 'email_module' %}
                        <i class="fas fa-envelope me-2"></i>Email
                    {% elif module_name == 'weather_module' %}
                        <i class="fas fa-cloud-sun me-2"></i>Weather
                    {% elif module_name == 'web_search' %}
                        <i class="fas fa-search me-2"></i>Web Search
                    {% elif module_name == 'auth_module' %}
                        <i class="fas fa-lock me-2"></i>Authentication
                    {% elif module_name == 'datetime_module' %}
                        <i class="fas fa-clock me-2"></i>Date Time
                    {% else %}
                        <i class="fas fa-cog me-2"></i>{{ module_name.replace('_', ' ').title() }}
                    {% endif %}
                </h5>
                <p class="card-text">
                    {% if module_config.enabled %}
                        <span class="badge bg-success">Enabled</span>
                    {% else %}
                        <span class="badge bg-secondary">Disabled</span>
                    {% endif %}
                </p>
                {% if module_config.enabled %}
                    {% if module_name == 'speech_to_text' %}
                        <a href="/speech-to-text" class="btn btn-primary">Open Module</a>
                    {% else %}
                        <button class="btn btn-secondary" disabled>Coming Soon</button>
                    {% endif %}
                {% else %}
                    <button class="btn btn-secondary" disabled>Module Disabled</button>
                {% endif %}
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}"""
    
    # Create speech-to-text template
    speech_template = """{% extends "base.html" %}

{% block title %}Speech to Text - {{ super() }}{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="/">Home</a></li>
                <li class="breadcrumb-item active">Speech to Text</li>
            </ol>
        </nav>
    </div>
</div>

<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">
                    <i class="fas fa-microphone me-2"></i>Speech Recognition
                </h5>
            </div>
            <div class="card-body">
                <div class="mb-3">
                    <button id="listenOnceBtn" class="btn btn-primary me-2">
                        <i class="fas fa-microphone"></i> Listen Once
                    </button>
                    <button id="startContinuousBtn" class="btn btn-success me-2">
                        <i class="fas fa-play"></i> Start Continuous
                    </button>
                    <button id="stopContinuousBtn" class="btn btn-danger" disabled>
                        <i class="fas fa-stop"></i> Stop Continuous
                    </button>
                </div>
                
                <div id="statusIndicator" class="alert alert-info">
                    <i class="fas fa-info-circle"></i> Ready to listen
                </div>
                
                <div class="mb-3">
                    <label for="textInput" class="form-label">Or type a command:</label>
                    <div class="input-group">
                        <input type="text" class="form-control" id="textInput" placeholder="Type your command here...">
                        <button class="btn btn-outline-primary" id="processTextBtn">
                            <i class="fas fa-paper-plane"></i> Process
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h6 class="mb-0">System Status</h6>
            </div>
            <div class="card-body">
                <div id="systemStatus">
                    <div class="text-center">
                        <div class="spinner-border spinner-border-sm" role="status"></div>
                        <span class="ms-2">Loading...</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h6 class="mb-0">Recognition Results</h6>
                <button id="clearResultsBtn" class="btn btn-sm btn-outline-secondary">
                    <i class="fas fa-trash"></i> Clear
                </button>
            </div>
            <div class="card-body">
                <div id="resultsContainer" style="max-height: 400px; overflow-y: auto;">
                    <div class="text-center text-muted">
                        <i class="fas fa-microphone-slash"></i>
                        <p>No results yet. Start listening to see recognized speech here.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
let continuousActive = false;
let resultsPollInterval = null;

// DOM elements
const listenOnceBtn = document.getElementById('listenOnceBtn');
const startContinuousBtn = document.getElementById('startContinuousBtn');
const stopContinuousBtn = document.getElementById('stopContinuousBtn');
const statusIndicator = document.getElementById('statusIndicator');
const resultsContainer = document.getElementById('resultsContainer');
const clearResultsBtn = document.getElementById('clearResultsBtn');
const textInput = document.getElementById('textInput');
const processTextBtn = document.getElementById('processTextBtn');
const systemStatus = document.getElementById('systemStatus');

// Status update
function updateStatus(message, type = 'info') {
    statusIndicator.className = `alert alert-${type}`;
    statusIndicator.innerHTML = `<i class="fas fa-${type === 'info' ? 'info-circle' : type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : 'times-circle'}"></i> ${message}`;
}

// System status update
function updateSystemStatus() {
    fetch('/api/modules/status')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const status = data.data;
                let html = '<div class="small">';
                html += `<div><strong>Core:</strong> ${status.core_active ? 'Active' : 'Inactive'}</div>`;
                if (status.modules.speech_to_text) {
                    const stt = status.modules.speech_to_text;
                    html += `<div><strong>STT:</strong> ${stt.is_listening ? 'Listening' : 'Ready'}</div>`;
                    html += `<div><strong>Microphone:</strong> ${stt.microphone_available ? 'Available' : 'Not Available'}</div>`;
                }
                html += '</div>';
                systemStatus.innerHTML = html;
            } else {
                systemStatus.innerHTML = '<div class="text-danger small">Error loading status</div>';
            }
        })
        .catch(error => {
            systemStatus.innerHTML = '<div class="text-danger small">Connection error</div>';
        });
}

// Listen once
listenOnceBtn.addEventListener('click', function() {
    updateStatus('Listening... Please speak now', 'warning');
    listenOnceBtn.disabled = true;
    
    fetch('/api/speech/listen-once', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({timeout: 10})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.data.text) {
            updateStatus(`Recognized: "${data.data.text}"`, 'success');
            addResult(data.data.text, data.data.timestamp, 'single');
        } else {
            updateStatus('No speech detected or recognition failed', 'warning');
        }
    })
    .catch(error => {
        updateStatus('Error during recognition', 'danger');
    })
    .finally(() => {
        listenOnceBtn.disabled = false;
    });
});

// Start continuous listening
startContinuousBtn.addEventListener('click', function() {
    fetch('/api/speech/start-continuous', {method: 'POST'})
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            continuousActive = true;
            updateStatus('Continuous listening active...', 'success');
            startContinuousBtn.disabled = true;
            stopContinuousBtn.disabled = false;
            
            // Start polling for results
            resultsPollInterval = setInterval(pollResults, 1000);
        } else {
            updateStatus('Failed to start continuous listening', 'danger');
        }
    })
    .catch(error => {
        updateStatus('Error starting continuous listening', 'danger');
    });
});

// Stop continuous listening
stopContinuousBtn.addEventListener('click', function() {
    fetch('/api/speech/stop-continuous', {method: 'POST'})
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            continuousActive = false;
            updateStatus('Continuous listening stopped', 'info');
            startContinuousBtn.disabled = false;
            stopContinuousBtn.disabled = true;
            
            // Stop polling
            if (resultsPollInterval) {
                clearInterval(resultsPollInterval);
                resultsPollInterval = null;
            }
        } else {
            updateStatus('Failed to stop continuous listening', 'danger');
        }
    })
    .catch(error => {
        updateStatus('Error stopping continuous listening', 'danger');
    });
});

// Process text command
processTextBtn.addEventListener('click', function() {
    const text = textInput.value.trim();
    if (!text) return;
    
    fetch('/api/speech/process-text', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text: text})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateStatus(`Processed: "${data.data.input}"`, 'success');
            addResult(data.data.input, data.data.timestamp, 'text', data.data.response);
            textInput.value = '';
        } else {
            updateStatus('Failed to process text command', 'danger');
        }
    })
    .catch(error => {
        updateStatus('Error processing text command', 'danger');
    });
});

// Poll for continuous results
function pollResults() {
    fetch('/api/speech/results')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const results = data.data.results;
            if (results.length > 0) {
                // Update results display
                displayResults(results);
            }
        }
    })
    .catch(error => {
        console.error('Error polling results:', error);
    });
}

// Display results
function displayResults(results) {
    if (results.length === 0) return;
    
    resultsContainer.innerHTML = '';
    results.slice(-10).reverse().forEach(result => {
        addResultElement(result.text, result.timestamp, 'continuous');
    });
}

// Add single result
function addResult(text, timestamp, type, response = null) {
    if (resultsContainer.innerHTML.includes('No results yet')) {
        resultsContainer.innerHTML = '';
    }
    addResultElement(text, timestamp, type, response);
}

// Add result element
function addResultElement(text, timestamp, type, response = null) {
    const resultDiv = document.createElement('div');
    resultDiv.className = 'border-bottom pb-2 mb-2';
    
    const typeColor = type === 'single' ? 'primary' : type === 'continuous' ? 'success' : 'info';
    const typeIcon = type === 'single' ? 'microphone' : type === 'continuous' ? 'volume-up' : 'keyboard';
    
    let html = `
        <div class="d-flex justify-content-between align-items-start">
            <div>
                <span class="badge bg-${typeColor} me-2">
                    <i class="fas fa-${typeIcon}"></i> ${type}
                </span>
                <strong>${text}</strong>
            </div>
            <small class="text-muted">${new Date(timestamp).toLocaleTimeString()}</small>
        </div>
    `;
    
    if (response) {
        html += `<div class="mt-1 text-muted small"><strong>Response:</strong> ${response}</div>`;
    }
    
    resultDiv.innerHTML = html;
    resultsContainer.insertBefore(resultDiv, resultsContainer.firstChild);
    
    // Keep only last 20 results
    while (resultsContainer.children.length > 20) {
        resultsContainer.removeChild(resultsContainer.lastChild);
    }
}

// Clear results
clearResultsBtn.addEventListener('click', function() {
    resultsContainer.innerHTML = `
        <div class="text-center text-muted">
            <i class="fas fa-microphone-slash"></i>
            <p>No results yet. Start listening to see recognized speech here.</p>
        </div>
    `;
});

// Enter key for text input
textInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        processTextBtn.click();
    }
});

// Initialize
updateSystemStatus();
setInterval(updateSystemStatus, 5000); // Update every 5 seconds
</script>
{% endblock %}"""
    
    # Write templates
    with open(os.path.join(templates_dir, 'base.html'), 'w', encoding='utf-8') as f:
        f.write(base_template)
    
    with open(os.path.join(templates_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_template)
    
    with open(os.path.join(templates_dir, 'speech_to_text.html'), 'w', encoding='utf-8') as f:
        f.write(speech_template)


def main():
    """Main function to run the JARVIS application"""
    # Create templates
    create_templates()
    
    # Activate JARVIS
    jarvis.activate()
    
    # Start Flask app
    logger.info(f"Starting JARVIS web application on {SERVER_CONFIG['host']}:{SERVER_CONFIG['port']}")
    
    try:
        app.run(
            host=SERVER_CONFIG['host'],
            port=SERVER_CONFIG['port'],
            debug=SERVER_CONFIG['debug']
        )
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    finally:
        jarvis.shutdown()
        logger.info("JARVIS application shutdown complete")


if __name__ == '__main__':
    main()
