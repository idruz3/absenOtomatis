import sys
import logging
from datetime import datetime
from pathlib import Path

class Logger:
    """Class for handling logging operations"""
    
    def __init__(self):
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Configure logging to both file and console"""
        try:
            # Get the executable's directory
            base_path = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent.parent
                
            # Create logs directory
            logs_dir = base_path / 'logs'
            logs_dir.mkdir(exist_ok=True)
            
            # Create log file with date
            log_file = logs_dir / f'automation_{datetime.now().strftime("%Y%m%d")}.log'
            
            # Configure logging
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(str(log_file), encoding='utf-8', mode='a'),
                    logging.StreamHandler()
                ]
            )
            return logging.getLogger("LMSAutomation")
            
        except Exception as e:
            # Fallback to basic console logging if file logging fails
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
            logger = logging.getLogger("LMSAutomation")
            logger.error(f'Failed to initialize file logging: {e}')
            return logger
    
    def info(self, message: str) -> None:
        """Log info level message"""
        self.logger.info(message)
    
    def error(self, message: str) -> None:
        """Log error level message"""
        self.logger.error(message)
    
    def warning(self, message: str) -> None:
        """Log warning level message"""
        self.logger.warning(message)