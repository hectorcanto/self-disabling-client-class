"""
This module works as a template for configuration values.
Use it to create a local_config.py with the real values, but do not add them to the repository.
At the end of the module local_config.py is imported.

If using this class in a Django project, use local_config to import the needed variables from the django app settings.

Be careful with the disabled settings because might do it silently, depending on the logging level. No exceptions
will be raised.
 """
import os
import logging


logger = logging.getLogger("config")


LOG_LEVEL = logging.DEBUG

AWS_REGION = NotImplemented
AWS_ACCESS_KEY_ID = NotImplemented
AWS_SECRET_ACCESS_KEY = NotImplemented

# Enable Services
AWS_S3_ENABLED = False

# S3 - Storage
# TODO change into a django storage backend
AWS_STORAGE_BUCKET_NAME = NotImplemented


if os.path.exists(os.path.join(os.path.dirname(__file__), 'local_config.py')):
    from local_config import *
else:
    logger.warning("Local AWS config file not found")
