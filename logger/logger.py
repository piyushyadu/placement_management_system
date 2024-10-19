import logging
import uuid


class Logger:
    def __init__(self, log_file: str, log_name: str):
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format=' %(levelname)s - %(asctime)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(log_name)
        self.log_id = str(uuid.uuid4())

    def log(self, message, level='info'):
        log_pool = dict(
            info=self.logger.info,
            warning=self.logger.warning,
            error=self.logger.error,
            critical=self.logger.critical
        )
        log_pool[level](f'{self.log_id} - {message}')
