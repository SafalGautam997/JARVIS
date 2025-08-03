"""
Text to Speech Module for JARVIS
Converts text to speech using pyttsx3 library
"""

import pyttsx3
import time
import threading
from typing import Optional, List, Dict, Any
from config.logging_config import get_logger


class TextToSpeechModule:
    """
    A class to handle text-to-speech conversion functionality
    """
    
    def __init__(self):
        """Initialize the Text to Speech module"""
        self.logger = get_logger('TextToSpeechModule')
        self.engine = None
        self.is_speaking = False
        self._engine_lock = threading.Lock()
        
        # Initialize TTS engine
        self._initialize_engine()
        
        self.logger.info("Text to Speech module initialized")
    
    def _initialize_engine(self):
        """Initialize the TTS engine"""
        try:
            # If engine already exists, clean it up first
            if hasattr(self, 'engine') and self.engine:
                try:
                    self.engine.stop()
                except:
                    pass
                try:
                    self.engine = None
                except:
                    pass
                
            # Create new engine instance
            self.engine = pyttsx3.init()
            
            # Set default properties
            self._set_default_properties()
            self.logger.info("TTS engine initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS engine: {e}")
            self.engine = None
    
    def _set_default_properties(self):
        """Set default TTS properties"""
        if not hasattr(self, 'engine') or not self.engine:
            return
        
        try:
            # Set speech rate (words per minute)
            self.engine.setProperty('rate', 200)
            
            # Set volume (0.0 to 1.0)
            self.engine.setProperty('volume', 0.9)
            
            # Try to set a more natural voice
            voices = self.engine.getProperty('voices')
            if voices:
                # Try to find a female voice first, then any available voice
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
                else:
                    # Use the first available voice
                    self.engine.setProperty('voice', voices[0].id)
                    
        except Exception as e:
            self.logger.error(f"Error setting TTS properties: {e}")
    
    def speak(self, text: str, blocking: bool = False):
        """
        Convert text to speech
        
        Args:
            text: Text to speak
            blocking: Whether to wait for speech to complete (ignored for simplicity)
        """
        if not text or not text.strip():
            return
        
        with self._engine_lock:
            if not hasattr(self, 'engine') or not self.engine:
                self.logger.error("TTS engine not available")
                return
            
            try:
                self.is_speaking = True
                text = text.strip()
                self.logger.info(f"Speaking: {text[:50]}{'...' if len(text) > 50 else ''}")
                
                # Stop any ongoing speech
                try:
                    self.engine.stop()
                except:
                    pass
                
                # For Windows SAPI, try to reset the engine state
                try:
                    # Clear any pending utterances
                    while self.engine._inLoop:
                        self.engine.endLoop()
                        time.sleep(0.01)
                except:
                    pass
                    
                # Reinitialize engine for reliable operation
                self._initialize_engine()
                
                if self.engine:
                    self.engine.say(text)
                    self.engine.runAndWait()
                    
                    # Give the engine time to complete and reset
                    time.sleep(0.3)
                    
            except Exception as e:
                self.logger.error(f"Error during speech: {e}")
                # Force reinitialize the engine if there's an error
                self._initialize_engine()
            finally:
                self.is_speaking = False
    
    def stop_speech(self):
        """Stop current speech"""
        if hasattr(self, 'engine') and self.engine and self.is_speaking:
            try:
                self.engine.stop()
                self.is_speaking = False
                self.logger.info("Speech stopped")
                # Reinitialize engine after stopping for next use
                self._initialize_engine()
            except Exception as e:
                self.logger.error(f"Error stopping speech: {e}")
                # Force reinitialize if stop fails
                self._initialize_engine()
    
    def set_rate(self, rate: int):
        """
        Set speech rate
        
        Args:
            rate: Speech rate in words per minute (50-300)
        """
        if not hasattr(self, 'engine') or not self.engine:
            return
        
        # Clamp rate to reasonable bounds
        rate = max(50, min(300, rate))
        
        try:
            self.engine.setProperty('rate', rate)
            self.logger.info(f"Speech rate set to {rate} WPM")
        except Exception as e:
            self.logger.error(f"Error setting speech rate: {e}")
    
    def set_volume(self, volume: float):
        """
        Set speech volume
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        if not hasattr(self, 'engine') or not self.engine:
            return
        
        # Clamp volume to valid range
        volume = max(0.0, min(1.0, volume))
        
        try:
            self.engine.setProperty('volume', volume)
            self.logger.info(f"Speech volume set to {volume}")
        except Exception as e:
            self.logger.error(f"Error setting speech volume: {e}")
    
    def set_voice(self, voice_index: int):
        """
        Set voice by index
        
        Args:
            voice_index: Index of voice to use
        """
        if not hasattr(self, 'engine') or not self.engine:
            return
        
        try:
            voices = self.engine.getProperty('voices')
            if voices and 0 <= voice_index < len(voices):
                self.engine.setProperty('voice', voices[voice_index].id)
                self.logger.info(f"Voice set to: {voices[voice_index].name}")
            else:
                self.logger.error(f"Invalid voice index: {voice_index}")
        except Exception as e:
            self.logger.error(f"Error setting voice: {e}")
    
    def get_voices(self) -> List[Dict[str, str]]:
        """
        Get list of available voices
        
        Returns:
            List of voice information dictionaries
        """
        if not hasattr(self, 'engine') or not self.engine:
            return []
        
        try:
            voices = self.engine.getProperty('voices')
            voice_list = []
            
            for i, voice in enumerate(voices):
                voice_info = {
                    'index': i,
                    'id': voice.id,
                    'name': voice.name,
                    'languages': getattr(voice, 'languages', []),
                    'gender': getattr(voice, 'gender', 'unknown')
                }
                voice_list.append(voice_info)
            
            return voice_list
        except Exception as e:
            self.logger.error(f"Error getting voices: {e}")
            return []
    
    def save_to_file(self, text: str, filename: str):
        """
        Save speech to audio file
        
        Args:
            text: Text to convert to speech
            filename: Output filename (should end with .wav)
        """
        if not hasattr(self, 'engine') or not self.engine:
            self.logger.error("TTS engine not available")
            return False
        
        try:
            self.engine.save_to_file(text, filename)
            self.engine.runAndWait()
            self.logger.info(f"Speech saved to file: {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving speech to file: {e}")
            return False
    
    def is_engine_available(self) -> bool:
        """
        Check if TTS engine is available
        
        Returns:
            True if engine is available, False otherwise
        """
        return hasattr(self, 'engine') and self.engine is not None
    
    def get_properties(self) -> Dict[str, Any]:
        """
        Get current TTS properties
        
        Returns:
            Dictionary of current properties
        """
        if not hasattr(self, 'engine') or not self.engine:
            return {}
        
        try:
            return {
                'rate': self.engine.getProperty('rate'),
                'volume': self.engine.getProperty('volume'),
                'voice': self.engine.getProperty('voice')
            }
        except Exception as e:
            self.logger.error(f"Error getting properties: {e}")
            return {}
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the TTS module
        
        Returns:
            Dictionary containing status information
        """
        return {
            "engine_available": self.is_engine_available(),
            "is_speaking": self.is_speaking,
            "queue_size": 0,  # No queue in simplified version
            "voices_available": len(self.get_voices()),
            "properties": self.get_properties()
        }
    
    def shutdown(self):
        """Shutdown the TTS module and clean up resources"""
        self.logger.info("Shutting down TTS module")
        
        # Stop any ongoing speech
        self.stop_speech()
        
        # Clean up engine
        if hasattr(self, 'engine') and self.engine:
            try:
                self.engine.stop()
            except:
                pass
            self.engine = None



