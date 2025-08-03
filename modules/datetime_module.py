"""
DateTime Module for JARVIS
Handles date, time, and scheduling operations
"""

from datetime import datetime, timedelta, date
from typing import Optional, Dict, Any
import calendar
import pytz
from config.logging_config import get_logger


class DateTimeModule:
    """
    A class to handle date and time operations
    """
    
    def __init__(self, timezone: str = "Asia/Kathmandu"):
        """Initialize the DateTime module"""
        self.logger = get_logger('DateTimeModule')
        self.timezone = pytz.timezone(timezone)
        self.utc_timezone = pytz.UTC
        self.logger.info("DateTime module initialized")
    
    def get_current_time(self, format_str: str = "%H:%M:%S") -> str:
        """
        Get current time in specified format
        
        Args:
            format_str: Time format string (default: %H:%M:%S)
            
        Returns:
            Formatted time string
        """
        now = datetime.now(self.timezone)
        return now.strftime(format_str)
    
    def get_current_date(self, format_str: str = "%Y-%m-%d") -> str:
        """
        Get current date in specified format
        
        Args:
            format_str: Date format string (default: %Y-%m-%d)
            
        Returns:
            Formatted date string
        """
        now = datetime.now(self.timezone)
        return now.strftime(format_str)
    
    def get_current_datetime(self, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Get current datetime in specified format
        
        Args:
            format_str: DateTime format string (default: %Y-%m-%d %H:%M:%S)
            
        Returns:
            Formatted datetime string
        """
        now = datetime.now(self.timezone)
        return now.strftime(format_str)
    
    def get_nepal_time(self, format_str: str = "%H:%M:%S") -> str:
        """
        Get current Nepal time
        
        Args:
            format_str: Time format string (default: %H:%M:%S)
            
        Returns:
            Formatted Nepal time string
        """
        nepal_tz = pytz.timezone("Asia/Kathmandu")
        now = datetime.now(nepal_tz)
        return now.strftime(format_str)
    
    def get_utc_time(self, format_str: str = "%H:%M:%S") -> str:
        """
        Get current UTC time
        
        Args:
            format_str: Time format string (default: %H:%M:%S)
            
        Returns:
            Formatted UTC time string
        """
        now = datetime.now(self.utc_timezone)
        return now.strftime(format_str)
    
    def get_nepal_datetime(self, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Get current Nepal datetime
        
        Args:
            format_str: DateTime format string (default: %Y-%m-%d %H:%M:%S)
            
        Returns:
            Formatted Nepal datetime string
        """
        nepal_tz = pytz.timezone("Asia/Kathmandu")
        now = datetime.now(nepal_tz)
        return now.strftime(format_str)
    
    def get_utc_datetime(self, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Get current UTC datetime
        
        Args:
            format_str: DateTime format string (default: %Y-%m-%d %H:%M:%S)
            
        Returns:
            Formatted UTC datetime string
        """
        now = datetime.now(self.utc_timezone)
        return now.strftime(format_str)
        """
        Get current date and time
        
        Args:
            format_str: DateTime format string
            
        Returns:
            Formatted datetime string
        """
        now = datetime.now(self.timezone)
        return now.strftime(format_str)
    
    def get_day_of_week(self, date_obj: Optional[datetime] = None) -> str:
        """
        Get day of the week
        
        Args:
            date_obj: Date object (uses current date if None)
            
        Returns:
            Day name (e.g., 'Monday')
        """
        if date_obj is None:
            date_obj = datetime.now(self.timezone)
        return date_obj.strftime("%A")
    
    def get_month_name(self, date_obj: Optional[datetime] = None) -> str:
        """
        Get month name
        
        Args:
            date_obj: Date object (uses current date if None)
            
        Returns:
            Month name (e.g., 'January')
        """
        if date_obj is None:
            date_obj = datetime.now(self.timezone)
        return date_obj.strftime("%B")
    
    def add_time(self, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0) -> datetime:
        """
        Add time to current datetime
        
        Args:
            days: Days to add
            hours: Hours to add
            minutes: Minutes to add
            seconds: Seconds to add
            
        Returns:
            New datetime object
        """
        now = datetime.now(self.timezone)
        delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        return now + delta
    
    def time_until(self, target_time: str, date_format: str = "%H:%M") -> Dict[str, int]:
        """
        Calculate time until target time today
        
        Args:
            target_time: Target time string (e.g., "14:30")
            date_format: Format of target_time
            
        Returns:
            Dictionary with hours, minutes, seconds until target
        """
        now = datetime.now(self.timezone)
        target_datetime = datetime.strptime(target_time, date_format)
        target_datetime = target_datetime.replace(
            year=now.year, month=now.month, day=now.day,
            tzinfo=self.timezone
        )
        
        # If target time has passed today, calculate for tomorrow
        if target_datetime < now:
            target_datetime += timedelta(days=1)
        
        delta = target_datetime - now
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return {
            'days': delta.days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds
        }
    
    def is_weekend(self, date_obj: Optional[datetime] = None) -> bool:
        """
        Check if date is weekend
        
        Args:
            date_obj: Date object (uses current date if None)
            
        Returns:
            True if weekend, False otherwise
        """
        if date_obj is None:
            date_obj = datetime.now(self.timezone)
        return date_obj.weekday() >= 5  # Saturday = 5, Sunday = 6
    
    def get_calendar_month(self, year: Optional[int] = None, month: Optional[int] = None) -> str:
        """
        Get calendar for specified month
        
        Args:
            year: Year (uses current year if None)
            month: Month (uses current month if None)
            
        Returns:
            Calendar string representation
        """
        now = datetime.now(self.timezone)
        if year is None:
            year = now.year
        if month is None:
            month = now.month
        
        return calendar.month(year, month)
    
    def parse_natural_time(self, time_str: str) -> Optional[datetime]:
        """
        Parse natural language time expressions
        
        Args:
            time_str: Natural time string (e.g., "tomorrow at 3pm", "next monday")
            
        Returns:
            Parsed datetime or None if unable to parse
        """
        now = datetime.now(self.timezone)
        time_str = time_str.lower().strip()
        
        # Handle "now"
        if time_str == "now":
            return now
        
        # Handle "today"
        if "today" in time_str:
            if "at" in time_str:
                time_part = time_str.split("at")[1].strip()
                try:
                    time_obj = datetime.strptime(time_part, "%I%p").time()
                    return datetime.combine(now.date(), time_obj, tzinfo=self.timezone)
                except ValueError:
                    try:
                        time_obj = datetime.strptime(time_part, "%H:%M").time()
                        return datetime.combine(now.date(), time_obj, tzinfo=self.timezone)
                    except ValueError:
                        pass
            return now.replace(hour=12, minute=0, second=0, microsecond=0)
        
        # Handle "tomorrow"
        if "tomorrow" in time_str:
            tomorrow = now + timedelta(days=1)
            if "at" in time_str:
                time_part = time_str.split("at")[1].strip()
                try:
                    time_obj = datetime.strptime(time_part, "%I%p").time()
                    return datetime.combine(tomorrow.date(), time_obj, tzinfo=self.timezone)
                except ValueError:
                    try:
                        time_obj = datetime.strptime(time_part, "%H:%M").time()
                        return datetime.combine(tomorrow.date(), time_obj, tzinfo=self.timezone)
                    except ValueError:
                        pass
            return tomorrow.replace(hour=12, minute=0, second=0, microsecond=0)
        
        # Handle "next week"
        if "next week" in time_str:
            next_week = now + timedelta(weeks=1)
            return next_week.replace(hour=12, minute=0, second=0, microsecond=0)
        
        return None
    
    def format_duration(self, seconds: int) -> str:
        """
        Format duration in seconds to human readable format
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            if remaining_seconds == 0:
                return f"{minutes} minutes"
            return f"{minutes} minutes and {remaining_seconds} seconds"
        elif seconds < 86400:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            if remaining_minutes == 0:
                return f"{hours} hours"
            return f"{hours} hours and {remaining_minutes} minutes"
        else:
            days = seconds // 86400
            remaining_hours = (seconds % 86400) // 3600
            if remaining_hours == 0:
                return f"{days} days"
            return f"{days} days and {remaining_hours} hours"
    
    def set_timezone(self, timezone_str: str):
        """
        Set timezone for the module
        
        Args:
            timezone_str: Timezone string (e.g., 'US/Eastern', 'Europe/London')
        """
        try:
            self.timezone = pytz.timezone(timezone_str)
            self.logger.info(f"Timezone set to {timezone_str}")
        except pytz.exceptions.UnknownTimeZoneError:
            self.logger.error(f"Unknown timezone: {timezone_str}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the datetime module
        
        Returns:
            Dictionary containing status information
        """
        now = datetime.now(self.timezone)
        return {
            "current_time": self.get_current_time(),
            "current_date": self.get_current_date(),
            "timezone": str(self.timezone),
            "day_of_week": self.get_day_of_week(),
            "is_weekend": self.is_weekend(),
            "month_name": self.get_month_name()
        }


# Example usage and testing
if __name__ == "__main__":
    # Create instance
    dt = DateTimeModule()
    
    # Test basic functions
    print(f"Current time: {dt.get_current_time()}")
    print(f"Current date: {dt.get_current_date()}")
    print(f"Day of week: {dt.get_day_of_week()}")
    print(f"Is weekend: {dt.is_weekend()}")
    print(f"Month: {dt.get_month_name()}")
    
    # Test natural language parsing
    print(f"Tomorrow at 3pm: {dt.parse_natural_time('tomorrow at 3pm')}")
    print(f"Today at 14:30: {dt.parse_natural_time('today at 14:30')}")
    
    # Test calendar
    print(f"This month's calendar:\n{dt.get_calendar_month()}")
