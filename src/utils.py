"""Logging and progress tracking utilities."""

import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

# Import with fallback for missing packages
try:
    from tqdm import tqdm as tqdm_class
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    
try:
    from colorama import Fore, Style
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

# Fallback implementations
if not TQDM_AVAILABLE:
    class tqdm_class:
        def __init__(self, *args, **kwargs):
            self.desc = kwargs.get('desc', '')
            self.total = kwargs.get('total', None)
            self.current = 0
            
        def update(self, n=1):
            self.current += n
            if self.total:
                print(f"\r{self.desc}: {self.current}/{self.total}", end='', flush=True)
            else:
                print(f"\r{self.desc}: {self.current}", end='', flush=True)
        
        def close(self):
            print()
        
        def __enter__(self):
            return self
        
        def __exit__(self, *args):
            self.close()

if not COLORAMA_AVAILABLE:
    class Fore:
        RED = GREEN = YELLOW = CYAN = BLUE = MAGENTA = WHITE = ''
    
    class Style:
        RESET_ALL = ''


class ProgressTracker:
    """Enhanced progress tracking with logging."""
    
    def __init__(self, total: int, description: str = "Processing", 
                 log_interval: int = 10, file_path: Optional[str] = None):
        """Initialize progress tracker."""
        self.total = total
        self.description = description
        self.log_interval = log_interval
        self.current = 0
        self.successful = 0
        self.failed = 0
        self.start_time = datetime.now()
        self.file_path = file_path
        
        # Setup progress bar
        self.pbar = tqdm_class(total=total, desc=description, unit="item")
        
        # Setup logger
        self.logger = logging.getLogger(f"progress.{description.lower().replace(' ', '_')}")
        
        # Initialize log file if specified
        if file_path:
            self._init_log_file()
    
    def _init_log_file(self):
        """Initialize progress log file."""
        if not self.file_path:
            return
            
        log_data = {
            'session_start': self.start_time.isoformat(),
            'description': self.description,
            'total': self.total,
            'progress_log': []
        }
        
        try:
            with open(self.file_path, 'w') as f:
                json.dump(log_data, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Could not initialize log file: {e}")
    
    def update(self, success: bool = True, message: Optional[str] = None, data: Any = None):
        """Update progress with success/failure info."""
        self.current += 1
        
        if success:
            self.successful += 1
        else:
            self.failed += 1
        
        # Update progress bar
        self.pbar.update(1)
        
        # Log at intervals
        if self.current % self.log_interval == 0 or not success:
            self._log_progress(success, message, data)
        
        # Update log file
        if self.file_path:
            self._update_log_file(success, message, data)
    
    def _log_progress(self, success: bool, message: Optional[str] = None, data: Any = None):
        """Log progress information."""
        status = "SUCCESS" if success else "FAILED"
        elapsed = datetime.now() - self.start_time
        rate = self.current / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
        
        log_msg = f"Progress: {self.current}/{self.total} ({self.current/self.total*100:.1f}%) | "
        log_msg += f"Success: {self.successful} | Failed: {self.failed} | "
        log_msg += f"Rate: {rate:.1f} items/sec"
        
        if message:
            log_msg += f" | {message}"
        
        if success:
            self.logger.info(log_msg)
        else:
            self.logger.warning(f"{status}: {log_msg}")
    
    def _update_log_file(self, success: bool, message: Optional[str] = None, data: Any = None):
        """Update progress log file."""
        if not self.file_path:
            return
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'item_number': self.current,
            'success': success,
            'message': message,
            'data': data
        }
        
        try:
            # Read existing log
            with open(self.file_path, 'r') as f:
                log_data = json.load(f)
            
            # Append new entry
            log_data['progress_log'].append(entry)
            log_data['current_progress'] = {
                'current': self.current,
                'successful': self.successful,
                'failed': self.failed,
                'completion_percentage': (self.current / self.total * 100) if self.total > 0 else 0
            }
            
            # Write back
            with open(self.file_path, 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            self.logger.warning(f"Could not update log file: {e}")
    
    def finish(self, summary_message: Optional[str] = None):
        """Finish progress tracking and log summary."""
        self.pbar.close()
        
        elapsed = datetime.now() - self.start_time
        
        summary = {
            'total_processed': self.current,
            'successful': self.successful,
            'failed': self.failed,
            'success_rate': (self.successful / self.current * 100) if self.current > 0 else 0,
            'elapsed_time': str(elapsed),
            'average_rate': self.current / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
        }
        
        self.logger.info(f"Progress completed: {summary}")
        
        if summary_message:
            self.logger.info(summary_message)
        
        # Final log file update
        if self.file_path:
            self._finalize_log_file(summary)
        
        return summary
    
    def _finalize_log_file(self, summary: dict):
        """Finalize progress log file."""
        if not self.file_path:
            return
            
        try:
            with open(self.file_path, 'r') as f:
                log_data = json.load(f)
            
            log_data['session_end'] = datetime.now().isoformat()
            log_data['summary'] = summary
            
            with open(self.file_path, 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            self.logger.warning(f"Could not finalize log file: {e}")
    
    def get_summary(self) -> dict:
        """Get current progress summary."""
        elapsed = datetime.now() - self.start_time
        
        return {
            'current': self.current,
            'total': self.total,
            'successful': self.successful,
            'failed': self.failed,
            'completion_percentage': (self.current / self.total * 100) if self.total > 0 else 0,
            'success_rate': (self.successful / self.current * 100) if self.current > 0 else 0,
            'elapsed_time': str(elapsed),
            'estimated_remaining': self._estimate_remaining_time(),
            'average_rate': self.current / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
        }
    
    def _estimate_remaining_time(self) -> str:
        """Estimate remaining time based on current progress."""
        if self.current == 0:
            return "Unknown"
        
        elapsed = datetime.now() - self.start_time
        rate = self.current / elapsed.total_seconds()
        
        if rate > 0:
            remaining_items = self.total - self.current
            remaining_seconds = remaining_items / rate
            remaining_time = str(timedelta(seconds=int(remaining_seconds)))
            return remaining_time
        
        return "Unknown"


class ContactImportLogger:
    """Specialized logger for contact import operations."""
    
    def __init__(self, log_file: Optional[str] = None):
        """Initialize contact import logger."""
        self.log_file = log_file or f"contact_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.logger = logging.getLogger('contact_import')
        
        # Setup file handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Setup console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.DEBUG)
    
    def log_session_start(self, total_contacts: int, file_path: str):
        """Log session start information."""
        self.logger.info(f"=== Contact Import Session Started ===")
        self.logger.info(f"File: {file_path}")
        self.logger.info(f"Total contacts to process: {total_contacts}")
        self.logger.info(f"Session started at: {datetime.now()}")
    
    def log_contact_result(self, phone_number: str, success: bool, error: Optional[str] = None):
        """Log individual contact import result."""
        if success:
            self.logger.info(f"SUCCESS: {phone_number} added to contacts")
        else:
            self.logger.error(f"FAILED: {phone_number} - {error or 'Unknown error'}")
    
    def log_batch_result(self, batch_num: int, total_batches: int, 
                        successful: int, failed: int, errors: Optional[list] = None):
        """Log batch processing result."""
        self.logger.info(f"Batch {batch_num}/{total_batches} completed: "
                        f"{successful} successful, {failed} failed")
        
        if errors:
            for error in errors:
                self.logger.warning(f"Batch error: {error}")
    
    def log_session_end(self, summary: dict):
        """Log session end information."""
        self.logger.info(f"=== Contact Import Session Completed ===")
        self.logger.info(f"Total processed: {summary.get('total_processed', 0)}")
        self.logger.info(f"Successful: {summary.get('successful', 0)}")
        self.logger.info(f"Failed: {summary.get('failed', 0)}")
        self.logger.info(f"Success rate: {summary.get('success_rate', 0):.1f}%")
        self.logger.info(f"Session duration: {summary.get('elapsed_time', 'Unknown')}")
    
    def get_log_file_path(self) -> str:
        """Get the log file path."""
        return self.log_file


def setup_logging(level: str = "INFO", log_file: Optional[str] = None, console: bool = True):
    """Setup application logging."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[]
    )
    
    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)
    
    # Add console handler if enabled
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)