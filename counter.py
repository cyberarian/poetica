import json
import os
from datetime import datetime
import threading
import logging
from pathlib import Path
from functools import wraps
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TimedCache:
    def __init__(self, ttl=60):
        self.ttl = ttl
        self.cache = {}
        self.timestamps = {}

    def __call__(self, func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            key = str((args, kwargs))
            now = time.time()
            
            # Check if cached and not expired
            if key in self.cache:
                if now - self.timestamps[key] < self.ttl:
                    return self.cache[key]
                else:
                    # Expired, remove from cache
                    del self.cache[key]
                    del self.timestamps[key]
            
            # Get fresh value
            result = func(*args, **kwargs)
            self.cache[key] = result
            self.timestamps[key] = now
            return result
        return wrapped

class RequestCounter:
    def __init__(self, counter_dir="counters"):
        self.counter_dir = Path(counter_dir)
        self.counter_file = self.counter_dir / "request_counter.json"
        self.lock = threading.Lock()
        self._ensure_counter_file()
    
    def _ensure_counter_file(self):
        """Ensure counter directory and file exist"""
        self.counter_dir.mkdir(exist_ok=True)
        if not self.counter_file.exists():
            self._save_counter({
                "total_requests": 0,
                "daily_counts": {},
                "monthly_counts": {},
                "last_updated": datetime.now().isoformat()
            })

    def _save_counter(self, data):
        """Safely save counter data to file"""
        temp_file = self.counter_file.with_suffix('.tmp')
        try:
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            temp_file.replace(self.counter_file)
        except Exception as e:
            logger.error(f"Error saving counter: {e}")
            if temp_file.exists():
                temp_file.unlink()
            raise

    def _load_counter(self):
        """Load counter data from file"""
        try:
            with open(self.counter_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading counter: {e}")
            return None

    @TimedCache(ttl=60)  # Cache for 60 seconds
    def get_counts(self):
        """Get current counter values"""
        data = self._load_counter()
        if data is None:
            return {
                "total_requests": 0,
                "today": 0,
                "this_month": 0
            }
        
        today = datetime.now().strftime("%Y-%m-%d")
        month = datetime.now().strftime("%Y-%m")
        
        return {
            "total_requests": data["total_requests"],
            "today": data["daily_counts"].get(today, 0),
            "this_month": data["monthly_counts"].get(month, 0)
        }

    def increment(self):
        """Increment counter with thread safety"""
        with self.lock:
            data = self._load_counter()
            if data is None:
                return False

            # Update counts
            data["total_requests"] += 1
            
            # Update daily count
            today = datetime.now().strftime("%Y-%m-%d")
            data["daily_counts"][today] = data["daily_counts"].get(today, 0) + 1
            
            # Update monthly count
            month = datetime.now().strftime("%Y-%m")
            data["monthly_counts"][month] = data["monthly_counts"].get(month, 0) + 1
            
            # Cleanup old entries (keep last 30 days and 12 months)
            self._cleanup_old_entries(data)
            
            # Save updated data
            self._save_counter(data)
            
            # Clear cache manually since we're not using lru_cache
            self.get_counts.__wrapped__(self)  # Call original function to clear cache
            
            return data["total_requests"]

    def _cleanup_old_entries(self, data):
        """Remove entries older than 30 days for daily counts and 12 months for monthly counts"""
        today = datetime.now()
        
        # Cleanup daily counts
        daily_counts = data["daily_counts"]
        data["daily_counts"] = {
            date: count 
            for date, count in daily_counts.items()
            if (today - datetime.strptime(date, "%Y-%m-%d")).days <= 30
        }
        
        # Cleanup monthly counts
        monthly_counts = data["monthly_counts"]
        current_month = int(today.strftime("%Y%m"))
        data["monthly_counts"] = {
            month: count 
            for month, count in monthly_counts.items()
            if current_month - int(month.replace("-", "")) <= 12
        }
