import os
basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE = "images.db"
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, DATABASE)
TITLE = 'IMAGE SPACE'
HOST = '0.0.0.0'
PORT = 8000
DEBUG = True
UPLOAD_DIR = os.path.join(basedir, "../uploaded_images") or os.environ.get("UPLOAD_DIR")
MEMEX_URL = os.environ.get('IMAGE_SPACE_SOLR') or "http://localhost:8081/solr/imagecatdev"
LOGGING_FILE = "image_solr.log"

ALLOWED_EXTENSIONS = set(('tiff', 'tif', 'png', 'jpg', 'jpeg', 'gif'))
