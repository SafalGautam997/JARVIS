"""
Test file for JARVIS modules
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.speech_to_text import SpeechToTextModule
from modules.assistant_core import JarvisAssistantCore
from config.settings import MODULES_CONFIG


class TestSpeechToText(unittest.TestCase):
    """Test cases for Speech to Text module"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.stt = SpeechToTextModule()
    
    def test_initialization(self):
        """Test if module initializes correctly"""
        self.assertIsNotNone(self.stt.recognizer)
        self.assertIsNotNone(self.stt.microphone)
        self.assertFalse(self.stt.is_listening)
    
    def test_microphone_list(self):
        """Test microphone listing"""
        mic_list = self.stt.get_microphone_list()
        self.assertIsInstance(mic_list, list)
    
    def test_status(self):
        """Test status retrieval"""
        status = self.stt.get_status()
        self.assertIn('is_listening', status)
        self.assertIn('microphone_available', status)
        self.assertIn('microphone_count', status)


class TestAssistantCore(unittest.TestCase):
    """Test cases for Assistant Core"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.assistant = JarvisAssistantCore()
    
    def test_initialization(self):
        """Test if assistant core initializes correctly"""
        self.assertIsNotNone(self.assistant.modules)
        
        # Check if speech to text module is loaded when enabled
        if MODULES_CONFIG['speech_to_text']['enabled']:
            self.assertIn('speech_to_text', self.assistant.modules)
    
    def test_module_availability(self):
        """Test module availability checking"""
        available_modules = self.assistant.get_available_modules()
        self.assertIsInstance(available_modules, list)
    
    def test_status(self):
        """Test status retrieval"""
        status = self.assistant.get_module_status()
        self.assertIn('core_active', status)
        self.assertIn('modules', status)


if __name__ == '__main__':
    unittest.main(verbosity=2)
