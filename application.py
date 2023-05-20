import os
from datetime import datetime
from logging.config import dictConfig

from app import create_app
from app.utils import log_err

filename = os.path.join(
    os.environ.get('ERROR_LOG_FOLDER'),
    'error_%s.log' % (datetime.now().strftime("%Y%m%d"))
)
filename_process = os.path.join(
    os.environ.get('ERROR_LOG_FOLDER'),
    'process_%s.log' % (datetime.now().strftime("%Y%m%d"))
)

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s %(filename)s line %(lineno)d: %(message)s',
        'datefmt': '%Y-%m-%d %H:%M:%S'
    }},
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'DEBUG'
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': filename,
            'level': 'ERROR'
        },
        'process_file': {
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': filename_process,
            'level': 'DEBUG'
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'file']
    },
    'loggers': {
        'process_log': {
            'level': 'DEBUG',
            'propagate': False,
            'handlers': ['process_file']
        }
    }
})

application = create_app()

if __name__ == "__main__":
    try:
        application.run(host='0.0.0.0', port=443, ssl_context='adhoc')
    except Exception as e:
        import traceback
        log_err(traceback.format_exc())
        raise e
