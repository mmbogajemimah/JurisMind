# logger_config.py
import logging
import logging.config
import os
from datetime import datetime

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Define logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(module)s %(process)d %(thread)d %(message)s'
        }
    },
    
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'app.log'),
            'formatter': 'verbose'
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'errors.log'),
            'formatter': 'verbose'
        },
        'celery_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'celery.log'),
            'formatter': 'verbose'
        }
    },
    
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': True,
        },
        'django': {
            'handlers': ['console', 'file'],
            'propagate': True,
            'level': 'INFO',
        },
        'celery': {
            'handlers': ['celery_file'],
            'level': 'INFO',
        },
        'knowledge_base': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        }
    }
}

# Apply the configuration
logging.config.dictConfig(LOGGING_CONFIG)

# Create a logger instance
logger = logging.getLogger(__name__)

# Optional: Add custom logging levels
def add_custom_levels():
    logging.addLevelName(25, 'STARTUP')
    logging.addLevelName(15, 'AUDIT')
    
    def startup(self, msg, *args, **kwargs):
        self.log(25, msg, *args, **kwargs)
        
    def audit(self, msg, *args, **kwargs):
        self.log(15, msg, *args, **kwargs)
        
    logging.Logger.startup = startup
    logging.Logger.audit = audit

# Add custom levels
add_custom_levels()