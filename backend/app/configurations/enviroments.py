from os import environ
from dotenv import load_dotenv

"""
==========================================================================
 ➠ Enviroments Configuration File
 ➠ Section By: Fabricio Abreu
 ➠ Related system: Enviroments
==========================================================================
"""

load_dotenv()

SECRET_KEY = environ.get('JWT_SECRET_KEY')
ENCRYPTION_ALGORITHM = environ.get('JWT_ENCRYPTION_ALGORITHM')
ACCESS_TOKEN_EXPIRES = int(environ.get('JWT_ACCESS_TOKEN_EXPIRES'))
REFRESH_TOKEN_EXPIRES = int(environ.get('JWT_REFRESH_TOKEN_EXPIRES'))
