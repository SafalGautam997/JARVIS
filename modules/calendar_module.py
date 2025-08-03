"""
Calendar Module for JARVIS
Handles calendar operations, events, and scheduling
"""

import json
import os
import uuid
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from config.logging_config import get_logger


@dataclass
class CalendarEvent:
    """Represents a calendar event"""
    id: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    location: str = ""
    attendees: List[str] = None
    reminder_minutes: int = 15
    is_all_day: bool = False
    recurrence: str = "none"  # "none", "daily", "weekly", "monthly", "yearly"
    created_at: datetime = None
    
    def __post_init__(self):
        if self.attendees is None:
            self.attendees = []
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat()
        data['created_at'] = self.created_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CalendarEvent':
        """Create event from dictionary"""
        # Convert ISO format strings back to datetime objects
        data['start_time'] = datetime.fromisoformat(data['start_time'])
        data['end_time'] = datetime.fromisoformat(data['end_time'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


class CalendarModule:
    """
    A class to handle calendar operations and event management
    """
    
    def __init__(self, data_file: str = "data/calendar_events.json"):
        """Initialize the Calendar module"""
        self.logger = get_logger('CalendarModule')
        self.data_file = data_file
        self.events: List[CalendarEvent] = []
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        
        # Load existing events
        self._load_events()
        
        self.logger.info("Calendar module initialized")
    
    def _load_events(self):
        """Load events from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    events_data = json.load(f)
                    self.events = [CalendarEvent.from_dict(event_data) for event_data in events_data]
                self.logger.info(f"Loaded {len(self.events)} events from {self.data_file}")
            else:
                self.events = []
                self.logger.info("No existing calendar file found, starting with empty calendar")
        except Exception as e:
            self.logger.error(f"Error loading events: {e}")
            self.events = []
    
    def _save_events(self):
        """Save events to JSON file"""
        try:
            events_data = [event.to_dict() for event in self.events]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(events_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved {len(self.events)} events to {self.data_file}")
        except Exception as e:
            self.logger.error(f"Error saving events: {e}")
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        return str(uuid.uuid4())[:8]
    
    def create_event(self, title: str, start_time: datetime, end_time: datetime,
                    description: str = "", location: str = "", attendees: List[str] = None,
                    reminder_minutes: int = 15, is_all_day: bool = False,
                    recurrence: str = "none") -> str:
        """
        Create a new calendar event
        
        Args:
            title: Event title
            start_time: Event start time
            end_time: Event end time
            description: Event description
            location: Event location
            attendees: List of attendee email addresses
            reminder_minutes: Minutes before event to remind
            is_all_day: Whether the event is all day
            recurrence: Recurrence pattern
            
        Returns:
            Event ID
        """
        event_id = self._generate_event_id()
        
        event = CalendarEvent(
            id=event_id,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location=location,
            attendees=attendees or [],
            reminder_minutes=reminder_minutes,
            is_all_day=is_all_day,
            recurrence=recurrence
        )
        
        self.events.append(event)
        self._save_events()
        
        self.logger.info(f"Created event: {title} ({event_id})")
        return event_id
    
    def get_event(self, event_id: str) -> Optional[CalendarEvent]:
        """
        Get event by ID
        
        Args:
            event_id: Event ID
            
        Returns:
            CalendarEvent or None if not found
        """
        for event in self.events:
            if event.id == event_id:
                return event
        return None
    
    def update_event(self, event_id: str, **kwargs) -> bool:
        """
        Update an existing event
        
        Args:
            event_id: Event ID
            **kwargs: Fields to update
            
        Returns:
            True if updated, False if not found
        """
        event = self.get_event(event_id)
        if not event:
            return False
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(event, key):
                setattr(event, key, value)
        
        self._save_events()
        self.logger.info(f"Updated event: {event_id}")
        return True
    
    def delete_event(self, event_id: str) -> bool:
        """
        Delete an event
        
        Args:
            event_id: Event ID
            
        Returns:
            True if deleted, False if not found
        """
        for i, event in enumerate(self.events):
            if event.id == event_id:
                deleted_event = self.events.pop(i)
                self._save_events()
                self.logger.info(f"Deleted event: {deleted_event.title} ({event_id})")
                return True
        return False
    
    def get_events_for_date(self, target_date: date) -> List[CalendarEvent]:
        """
        Get all events for a specific date
        
        Args:
            target_date: Target date
            
        Returns:
            List of events for the date
        """
        events = []
        for event in self.events:
            event_date = event.start_time.date()
            if event_date == target_date:
                events.append(event)
        
        # Sort by start time
        events.sort(key=lambda e: e.start_time)
        return events
    
    def get_events_for_week(self, start_date: Optional[date] = None) -> List[CalendarEvent]:
        """
        Get all events for a week
        
        Args:
            start_date: Week start date (defaults to current week)
            
        Returns:
            List of events for the week
        """
        if start_date is None:
            today = date.today()
            start_date = today - timedelta(days=today.weekday())
        
        end_date = start_date + timedelta(days=6)
        
        events = []
        for event in self.events:
            event_date = event.start_time.date()
            if start_date <= event_date <= end_date:
                events.append(event)
        
        events.sort(key=lambda e: e.start_time)
        return events
    
    def get_events_for_month(self, year: Optional[int] = None, month: Optional[int] = None) -> List[CalendarEvent]:
        """
        Get all events for a specific month
        
        Args:
            year: Year (defaults to current year)
            month: Month (defaults to current month)
            
        Returns:
            List of events for the month
        """
        now = datetime.now()
        if year is None:
            year = now.year
        if month is None:
            month = now.month
        
        events = []
        for event in self.events:
            if event.start_time.year == year and event.start_time.month == month:
                events.append(event)
        
        events.sort(key=lambda e: e.start_time)
        return events
    
    def get_upcoming_events(self, days: int = 7) -> List[CalendarEvent]:
        """
        Get upcoming events within specified days
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of upcoming events
        """
        now = datetime.now()
        future_date = now + timedelta(days=days)
        
        events = []
        for event in self.events:
            if now <= event.start_time <= future_date:
                events.append(event)
        
        events.sort(key=lambda e: e.start_time)
        return events
    
    def get_events_needing_reminders(self) -> List[CalendarEvent]:
        """
        Get events that need reminders now
        
        Returns:
            List of events needing reminders
        """
        now = datetime.now()
        events_needing_reminders = []
        
        for event in self.events:
            reminder_time = event.start_time - timedelta(minutes=event.reminder_minutes)
            # Check if reminder time is within the last minute
            if reminder_time <= now <= reminder_time + timedelta(minutes=1):
                events_needing_reminders.append(event)
        
        return events_needing_reminders
    
    def search_events(self, query: str) -> List[CalendarEvent]:
        """
        Search events by title, description, or location
        
        Args:
            query: Search query
            
        Returns:
            List of matching events
        """
        query = query.lower()
        matching_events = []
        
        for event in self.events:
            if (query in event.title.lower() or 
                query in event.description.lower() or 
                query in event.location.lower()):
                matching_events.append(event)
        
        matching_events.sort(key=lambda e: e.start_time)
        return matching_events
    
    def get_free_time_slots(self, target_date: date, duration_minutes: int = 60) -> List[Dict[str, datetime]]:
        """
        Find free time slots on a given date
        
        Args:
            target_date: Target date
            duration_minutes: Minimum duration for free slots
            
        Returns:
            List of free time slots with start and end times
        """
        # Get events for the date
        events = self.get_events_for_date(target_date)
        
        # Define work hours (9 AM to 6 PM)
        work_start = datetime.combine(target_date, datetime.min.time().replace(hour=9))
        work_end = datetime.combine(target_date, datetime.min.time().replace(hour=18))
        
        # Sort events by start time
        events.sort(key=lambda e: e.start_time)
        
        free_slots = []
        current_time = work_start
        
        for event in events:
            # Check if there's a gap before this event
            if event.start_time > current_time:
                slot_duration = (event.start_time - current_time).seconds // 60
                if slot_duration >= duration_minutes:
                    free_slots.append({
                        'start': current_time,
                        'end': event.start_time
                    })
            
            # Move current time to after this event
            current_time = max(current_time, event.end_time)
        
        # Check for free time after last event
        if current_time < work_end:
            slot_duration = (work_end - current_time).seconds // 60
            if slot_duration >= duration_minutes:
                free_slots.append({
                    'start': current_time,
                    'end': work_end
                })
        
        return free_slots
    
    def get_event_conflicts(self, start_time: datetime, end_time: datetime, exclude_event_id: str = None) -> List[CalendarEvent]:
        """
        Check for event conflicts with a time range
        
        Args:
            start_time: Proposed start time
            end_time: Proposed end time
            exclude_event_id: Event ID to exclude from conflict check
            
        Returns:
            List of conflicting events
        """
        conflicts = []
        
        for event in self.events:
            if exclude_event_id and event.id == exclude_event_id:
                continue
            
            # Check for overlap
            if (start_time < event.end_time and end_time > event.start_time):
                conflicts.append(event)
        
        return conflicts
    
    def get_calendar_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Get calendar summary for the next N days
        
        Args:
            days: Number of days to summarize
            
        Returns:
            Calendar summary dictionary
        """
        upcoming_events = self.get_upcoming_events(days)
        events_by_date = {}
        
        for event in upcoming_events:
            event_date = event.start_time.date().isoformat()
            if event_date not in events_by_date:
                events_by_date[event_date] = []
            events_by_date[event_date].append({
                'title': event.title,
                'start_time': event.start_time.strftime('%H:%M'),
                'end_time': event.end_time.strftime('%H:%M'),
                'location': event.location
            })
        
        return {
            'total_events': len(self.events),
            'upcoming_events': len(upcoming_events),
            'events_by_date': events_by_date,
            'next_event': upcoming_events[0].title if upcoming_events else None
        }
    
    def get_calendar_matrix(self, year: Optional[int] = None, month: Optional[int] = None) -> Dict[str, Any]:
        """
        Get calendar matrix for display (6 weeks x 7 days)
        
        Args:
            year: Year (defaults to current year)
            month: Month (defaults to current month)
            
        Returns:
            Dictionary containing calendar matrix and metadata
        """
        import calendar
        from datetime import timedelta
        
        now = datetime.now()
        if year is None:
            year = now.year
        if month is None:
            month = now.month
        
        # Get first and last day of the month
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
        
        # Calculate start and end dates for the calendar (6 weeks)
        # We want to start from Sunday (US calendar format)
        # first_day.weekday(): Monday=0, Sunday=6
        # We need to convert to: Sunday=0, Monday=1, ..., Saturday=6
        first_day_weekday = (first_day.weekday() + 1) % 7  # Convert to Sunday=0 format
        start_date = first_day - timedelta(days=first_day_weekday)
        
        # Get all events that might appear in the calendar
        all_events = []
        current_events = self.get_events_for_month(year, month)
        all_events.extend(current_events)
        
        # Get events from previous month if needed
        if start_date.month != month or start_date.year != year:
            prev_events = self.get_events_for_month(start_date.year, start_date.month)
            all_events.extend(prev_events)
        
        # Create events dict by date
        events_by_date = {}
        for event in all_events:
            date_key = event.start_time.date()
            if date_key not in events_by_date:
                events_by_date[date_key] = []
            events_by_date[date_key].append(event)
        
        # Build 6 weeks of calendar data
        calendar_data = []
        today = datetime.now().date()
        current_date = start_date
        
        for week_num in range(6):  # 6 weeks
            week_data = []
            for day_num in range(7):  # 7 days
                is_current_month = (current_date.month == month and current_date.year == year)
                
                week_data.append({
                    'day': current_date.day,
                    'date': current_date,
                    'is_current_month': is_current_month,
                    'is_today': current_date == today,
                    'events': events_by_date.get(current_date, []),
                    'has_events': current_date in events_by_date
                })
                
                current_date += timedelta(days=1)
            
            calendar_data.append(week_data)
        
        return {
            'calendar_matrix': calendar_data,
            'year': year,
            'month': month,
            'month_name': calendar.month_name[month],
            'events_count': len(current_events),
            'total_days_with_events': len([d for d in events_by_date.keys() 
                                          if d.year == year and d.month == month])
        }

    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the calendar module
        
        Returns:
            Dictionary containing status information
        """
        now = datetime.now()
        today_events = self.get_events_for_date(now.date())
        upcoming_events = self.get_upcoming_events(7)
        
        return {
            "total_events": len(self.events),
            "today_events": len(today_events),
            "upcoming_events": len(upcoming_events),
            "next_event": upcoming_events[0].title if upcoming_events else None,
            "data_file": self.data_file
        }



