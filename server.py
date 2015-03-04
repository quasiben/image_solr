import os
from image_space import app

app.config.from_pyfile('config.py')

app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])
