import sys

sys.path.append('/var/www/html/autoport/')

from main import app as application
from main import startAutoport

startAutoport()