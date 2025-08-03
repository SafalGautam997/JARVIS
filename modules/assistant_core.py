"""
Assistant Core Module for JARVIS
Main coordinator for all JARVIS modules
"""

from config.logging_config import get_logger
from config.settings import MODULES_CONFIG, SPEECH_CONFIG
from modules.speech_to_text import SpeechToTextModule
from modules.text_to_speech import TextToSpeechModule
from modules.datetime_module import DateTimeModule
from modules.calendar_module import CalendarModule
from typing import Optional, Dict, Any


class JarvisAssistantCore:
    """
    Main assistant core that manages all JARVIS modules
    """
    
    def __init__(self):
        """Initialize the JARVIS Assistant Core"""
        self.logger = get_logger('AssistantCore')
        self.modules = {}
        self.is_active = False
        
        # Initialize modules based on configuration
        self._initialize_modules()
        
        self.logger.info("JARVIS Assistant Core initialized")
    
    def _initialize_modules(self):
        """Initialize all enabled modules"""
        # Initialize Speech to Text module
        if MODULES_CONFIG['speech_to_text']['enabled']:
            try:
                self.modules['speech_to_text'] = SpeechToTextModule()
                self.logger.info("Speech to Text module initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Speech to Text: {e}")
        
        # Initialize Text to Speech module
        if MODULES_CONFIG['text_to_speech']['enabled']:
            try:
                self.modules['text_to_speech'] = TextToSpeechModule()
                self.logger.info("Text to Speech module initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Text to Speech: {e}")
        
        # Initialize DateTime module
        if MODULES_CONFIG['datetime_module']['enabled']:
            try:
                timezone = MODULES_CONFIG['datetime_module'].get('timezone', 'UTC')
                self.modules['datetime_module'] = DateTimeModule(timezone=timezone)
                self.logger.info("DateTime module initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize DateTime module: {e}")
        
        # Initialize Calendar module
        if MODULES_CONFIG['calendar_module']['enabled']:
            try:
                self.modules['calendar_module'] = CalendarModule()
                self.logger.info("Calendar module initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Calendar module: {e}")
        
        # TODO: Initialize other modules when they are implemented
        # if MODULES_CONFIG['nlp_module']['enabled']:
        #     self.modules['nlp'] = NLPModule()
        
        # ... and so on for other modules
    
    def start_speech_recognition(self, continuous: bool = False) -> Optional[str]:
        """
        Start speech recognition
        
        Args:
            continuous: Whether to use continuous listening mode
            
        Returns:
            Recognized text (for single mode) or None (for continuous mode)
        """
        if 'speech_to_text' not in self.modules:
            self.logger.error("Speech to Text module not available")
            return None
        
        stt_module = self.modules['speech_to_text']
        
        if continuous:
            # Start continuous listening
            stt_module.start_continuous_listening(
                callback=self._handle_speech_input,
                language=SPEECH_CONFIG['language']
            )
            self.logger.info("Started continuous speech recognition")
            return None
        else:
            # Single recognition
            text = stt_module.listen_once(
                timeout=SPEECH_CONFIG['timeout'],
                language=SPEECH_CONFIG['language']
            )
            if text:
                self._handle_speech_input(text)
            return text
    
    def stop_speech_recognition(self):
        """Stop continuous speech recognition"""
        if 'speech_to_text' not in self.modules:
            return
        
        stt_module = self.modules['speech_to_text']
        stt_module.stop_continuous_listening()
        self.logger.info("Stopped speech recognition")
    
    def _handle_speech_input(self, text: str):
        """
        Handle recognized speech input
        
        Args:
            text: The recognized speech text
        """
        self.logger.info(f"Processing speech input: {text}")
        
        # Convert to lowercase for command matching
        text_lower = text.lower().strip()
        response = None
        
        # Greeting commands
        if any(phrase in text_lower for phrase in ["hello jarvis", "hi jarvis", "hey jarvis"]):
            response = "Hello! How can I help you today?"
        
        # Stop commands
        elif any(phrase in text_lower for phrase in ["stop listening", "stop jarvis", "goodbye jarvis"]):
            response = "Goodbye! Stopping speech recognition."
            self.stop_speech_recognition()
        
        # Time and date commands
        elif any(phrase in text_lower for phrase in ["what time is it", "current time", "tell me the time"]):
            if 'datetime_module' in self.modules:
                dt_module = self.modules['datetime_module']
                current_time = dt_module.get_current_time("%I:%M %p")
                response = f"The current time is {current_time}"
            else:
                from datetime import datetime
                current_time = datetime.now().strftime("%I:%M %p")
                response = f"The current time is {current_time}"
        
        elif any(phrase in text_lower for phrase in ["what date is it", "current date", "today's date"]):
            if 'datetime_module' in self.modules:
                dt_module = self.modules['datetime_module']
                current_date = dt_module.get_current_date("%A, %B %d, %Y")
                response = f"Today is {current_date}"
            else:
                from datetime import datetime
                current_date = datetime.now().strftime("%A, %B %d, %Y")
                response = f"Today is {current_date}"
        
        elif "what day is it" in text_lower:
            if 'datetime_module' in self.modules:
                dt_module = self.modules['datetime_module']
                day_name = dt_module.get_day_of_week()
                response = f"Today is {day_name}"
            else:
                from datetime import datetime
                day_name = datetime.now().strftime("%A")
                response = f"Today is {day_name}"
        
        # Calendar commands
        elif any(phrase in text_lower for phrase in ["my calendar", "today's events", "what's on my calendar"]):
            if 'calendar_module' in self.modules:
                calendar_module = self.modules['calendar_module']
                from datetime import date
                today_events = calendar_module.get_events_for_date(date.today())
                if today_events:
                    response = f"You have {len(today_events)} events today: "
                    for event in today_events[:3]:  # Show first 3 events
                        response += f"{event.title} at {event.start_time.strftime('%I:%M %p')}, "
                    response = response.rstrip(', ')
                else:
                    response = "You have no events scheduled for today"
            else:
                response = "Calendar module is not available"
        
        elif "upcoming events" in text_lower:
            if 'calendar_module' in self.modules:
                calendar_module = self.modules['calendar_module']
                upcoming = calendar_module.get_upcoming_events(7)
                if upcoming:
                    response = f"You have {len(upcoming)} upcoming events in the next week. "
                    next_event = upcoming[0]
                    response += f"Your next event is {next_event.title} on {next_event.start_time.strftime('%A at %I:%M %p')}"
                else:
                    response = "You have no upcoming events in the next week"
            else:
                response = "Calendar module is not available"
        
        # Schedule commands (basic parsing)
        elif "schedule" in text_lower and ("meeting" in text_lower or "appointment" in text_lower):
            if 'calendar_module' in self.modules:
                # This is a simplified example - you'd want more sophisticated NLP parsing
                response = "I'd be happy to help you schedule an event. Please use the web interface for detailed scheduling."
            else:
                response = "Calendar module is not available"
        
        # Default response
        else:
            response = f"I heard: {text}. I'm still learning new commands!"
        
        # Log the response
        self.logger.info(f"Response: {response}")
        
        # Speak the response if TTS is available
        if 'text_to_speech' in self.modules and response:
            tts_module = self.modules['text_to_speech']
            tts_module.speak(response, blocking=False)
        else:
            # Just print if TTS not available
            print(f"JARVIS: {response}")
        
        return response
    
    def get_module_status(self) -> Dict[str, Any]:
        """
        Get status of all modules
        
        Returns:
            Dictionary containing module status information
        """
        status = {
            'core_active': self.is_active,
            'modules': {}
        }
        
        for module_name, module in self.modules.items():
            if hasattr(module, 'get_status'):
                status['modules'][module_name] = module.get_status()
            else:
                status['modules'][module_name] = {'available': True}
        
        return status
    
    def get_available_modules(self) -> list:
        """
        Get list of available modules
        
        Returns:
            List of available module names
        """
        return list(self.modules.keys())
    
    def is_module_available(self, module_name: str) -> bool:
        """
        Check if a specific module is available
        
        Args:
            module_name: Name of the module to check
            
        Returns:
            True if module is available, False otherwise
        """
        return module_name in self.modules
    
    def process_text_command(self, command: str) -> str:
        """
        Process a text command directly (for web interface)
        
        Args:
            command: The text command to process
            
        Returns:
            Response text
        """
        self.logger.info(f"Processing text command: {command}")
        self._handle_speech_input(command)
        return f"Processed command: {command}"
    
    def activate(self):
        """Activate the assistant"""
        self.is_active = True
        self.logger.info("JARVIS Assistant activated")
    
    def deactivate(self):
        """Deactivate the assistant"""
        self.is_active = False
        self.stop_speech_recognition()
        self.logger.info("JARVIS Assistant deactivated")
    
    def shutdown(self):
        """Shutdown the assistant and clean up resources"""
        self.deactivate()
        
        # Clean up modules
        if 'text_to_speech' in self.modules:
            self.modules['text_to_speech'].shutdown()
        
        # Other modules don't require special cleanup yet
        
        self.logger.info("JARVIS Assistant shutdown complete")


# Example usage
if __name__ == "__main__":
    # Create assistant instance
    assistant = JarvisAssistantCore()
    
    # Activate assistant
    assistant.activate()
    
    # Test single speech recognition
    print("Testing single speech recognition...")
    result = assistant.start_speech_recognition(continuous=False)
    
    # Test continuous speech recognition
    print("Testing continuous speech recognition (say 'stop jarvis' to end)...")
    assistant.start_speech_recognition(continuous=True)
    
    # Keep running until interrupted
    try:
        import time
        while assistant.modules['speech_to_text'].is_listening:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        assistant.shutdown()
