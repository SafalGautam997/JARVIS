"""
Settings Configuration for JARVIS
"""

# Server Configuration
SERVER_CONFIG = {
    'host': '127.0.0.1',
    'port': 5000,
    'debug': True
}

# Speech Recognition Settings
SPEECH_CONFIG = {
    'language': 'en-US',
    'timeout': 10,
    'phrase_time_limit': 5,
    'energy_threshold': 4000,
    'dynamic_energy_threshold': True
}

# Module Settings
MODULES_CONFIG = {
    'speech_to_text': {
        'enabled': True,
        'continuous_mode': False
    },
    'text_to_speech': {
        'enabled': True,
        'voice_rate': 200,
        'voice_volume': 0.9
    },
    'nlp_module': {
        'enabled': False
    },
    'task_manager': {
        'enabled': False
    },
    'calendar_module': {
        'enabled': True
    },
    'email_module': {
        'enabled': False
    },
    'weather_module': {
        'enabled': False
    },
    'web_search': {
        'enabled': False
    },
    'auth_module': {
        'enabled': False
    },
    'datetime_module': {
        'enabled': True,
        'timezone': 'UTC'
    }
}

# Application Settings
APP_CONFIG = {
    'name': 'JARVIS',
    'version': '1.0.0',
    'description': 'Just A Rather Very Intelligent System'
}
