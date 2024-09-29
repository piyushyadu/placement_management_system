import logging


class Logger:
    def __init__(self, log_file, log_class):
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(log_class)

    def log(self, component, message, level='info'):
        log_pool = dict(
            info=self.logger.info,
            warning=self.logger.warning,
            error=self.logger.error,
            critical=self.logger.critical
        )
        component = f'[{component}]: '
        log_pool[level](component + message)
