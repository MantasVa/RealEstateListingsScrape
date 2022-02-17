import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler


def getLogger(name: str = 'Logger1', aiKey: str = None) -> logging.Logger:
    logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if aiKey is not None:
        logger.addHandler(AzureLogHandler(
            connection_string=f'InstrumentationKey={aiKey}'))
        
    return logger