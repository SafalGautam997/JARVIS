"""
Speech to Text Module for             with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
        except Exception as e:
            self.logger.error(f"Error calibrating microphone: {e}")
Uses SpeechRecognition library for converting speech to text
"""

import speech_recognition as sr
import pyaudio
import threading
import time
from typing import Optional, Callable


class SpeechToTextModule:
    """
    A class to handle speech-to-text conversion functionality
    """
    
    def __init__(self):
        """Initialize the Speech to Text module"""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.callback = None
        self.listening_thread = None
        
        # Adjust for ambient noise during initialization
        self._calibrate_microphone()
    
    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        try:
            print("Calibrating microphone for ambient noise...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print("Microphone calibrated successfully!")
        except Exception as e:
            print(f"Error calibrating microphone: {e}")
    
    def listen_once(self, timeout: int = 5, language: str = "en-US") -> Optional[str]:
        """
        Listen for speech once and return the recognized text
        
        Args:
            timeout: Maximum time to wait for speech (seconds)
            language: Language code for recognition (default: en-US)
            
        Returns:
            Recognized text as string, or None if recognition failed
        """
        try:            
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
            
            text = self.recognizer.recognize_google(audio, language=language)
            self.logger.info(f"Recognized: {text}")
            return text
            
        except sr.WaitTimeoutError:
            self.logger.warning("No speech detected within timeout period")
            return None
        except sr.UnknownValueError:
            self.logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            self.logger.error(f"Speech recognition service error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return None
    
    def start_continuous_listening(self, callback: Callable[[str], None], language: str = "en-US"):
        """
        Start continuous listening in a separate thread
        
        Args:
            callback: Function to call when speech is recognized
            language: Language code for recognition (default: en-US)
        """
        if self.is_listening:
            self.logger.warning("Already listening...")
            return
        
        self.callback = callback
        self.is_listening = True
        self.listening_thread = threading.Thread(
            target=self._continuous_listen_worker,
            args=(language,),
            daemon=True
        )
        self.listening_thread.start()
        self.logger.info("Started continuous listening...")
    
    def stop_continuous_listening(self):
        """Stop continuous listening"""
        if not self.is_listening:
            self.logger.warning("Not currently listening...")
            return
        
        self.is_listening = False
        if self.listening_thread:
            self.listening_thread.join(timeout=2)
        self.logger.info("Stopped continuous listening...")
    
    def _continuous_listen_worker(self, language: str):
        """Worker method for continuous listening"""
        while self.is_listening:
            try:
                with self.microphone as source:
                    # Listen for audio with shorter timeout for continuous mode
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                # Process in background to avoid blocking
                text = self.recognizer.recognize_google(audio, language=language)
                if text and self.callback:
                    self.callback(text)
                    
            except sr.WaitTimeoutError:
                # Normal timeout, continue listening
                continue
            except sr.UnknownValueError:
                # Could not understand audio, continue listening
                continue
            except sr.RequestError as e:
                self.logger.error(f"Speech recognition service error: {e}")
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Unexpected error in continuous listening: {e}")
                time.sleep(1)
    
    def is_microphone_available(self) -> bool:
        """
        Check if microphone is available
        
        Returns:
            True if microphone is available, False otherwise
        """
        try:
            with self.microphone as source:
                pass
            return True
        except Exception as e:
            self.logger.error(f"Microphone not available: {e}")
            return False
    
    def get_microphone_list(self) -> list:
        """
        Get list of available microphones
        
        Returns:
            List of microphone names
        """
        try:
            mic_list = sr.Microphone.list_microphone_names()
            return mic_list
        except Exception as e:
            self.logger.error(f"Error getting microphone list: {e}")
            return []
    
    def set_microphone(self, device_index: int):
        """
        Set specific microphone device
        
        Args:
            device_index: Index of the microphone device
        """
        try:
            self.microphone = sr.Microphone(device_index=device_index)
            self._calibrate_microphone()
            self.logger.info(f"Microphone set to device index: {device_index}")
        except Exception as e:
            self.logger.error(f"Error setting microphone: {e}")
    
    def get_status(self) -> dict:
        """
        Get current status of the speech recognition module
        
        Returns:
            Dictionary containing status information
        """
        return {
            "is_listening": self.is_listening,
            "microphone_available": self.is_microphone_available(),
            "microphone_count": len(self.get_microphone_list())
        }



