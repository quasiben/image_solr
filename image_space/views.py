import os
import exifread
import requests

from flask import redirect, flash, render_template, request, url_for, send_from_directory, jsonify
from werkzeug import secure_filename

from image_space import app
from image_space.db_api import get_all_images,\
                               filter_all, \
                               clear_uploaded_images, \
                               get_uploaded_image_names, \
                               get_info, \
                               reset_db, \
                               get_info_serial
import utils

@app.route('/')
@app.route('/overview')
def overview():
    return render_template('overview.html')

@app.route('/image_table')
def image_table():
    images = get_all_images()
    return render_template('image_table.html', images=images)

def lost_camera_retreive(serial_num):
    camera_dir = app.config['LOST_CAMERA_DIR']
    path = os.path.join(camera_dir, serial_num)
    static_dir_path = os.path.join(os.path.dirname(__file__), "static")

    list_of_pics = []
    if os.path.exists(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, static_dir_path)
                if 'stolen' in relative_path:
                    list_of_pics.append((relative_path, file, 'stolencamera'))
                else:
                    list_of_pics.append((relative_path, file, 'cameratrace'))

    return list_of_pics

def image_retrieve(filename, size=None):
        return send_from_directory(app.config['UPLOAD_DIR'], filename)

def image_crawled(image, size=None):
        dirname = os.path.join("/", os.path.dirname(image))
        basename = os.path.basename(image)
        return send_from_directory(dirname, basename)

@app.route('/crawled/<path:image>')
def crawled(image):
    return image_crawled(image)

@app.route('/uploaded/<image>')
def uploaded(image):
    return image_retrieve(image)

def serve_upload_page():
    """Returns response to upload an image and lists other uploaded images"""
    image_names = get_uploaded_image_names()
    image_pages = [ {"name":filename, "url":url_for('compare', image=filename) } \
                    for filename in image_names]
    return render_template('upload.html', image_pages=image_pages)

@app.route('/clear')
def clear_uploads():
    clear_uploaded_images()
    return redirect(url_for('compare'))

@app.route('/reset')
def reset():
    reset_db()
    clear_uploaded_images()
    flash('Reset Demo successfully', 'success')
    return redirect(url_for('overview'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
    elif request.method == 'POST':
        uploaded_file = request.files['file']

        if uploaded_file and utils.allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            full_path = os.path.join(app.config['UPLOAD_DIR'], filename)
            uploaded_file.save(full_path)

            with open(full_path, 'rb') as f:
                exif_data = exifread.process_file(f)
                utils.process_exif(exif_data, filename)

                return jsonify(dict(
                    album_path=url_for('compare', image=filename)
                    ))

        else:
            allowed = ', '.join(app.config['ALLOWED_EXTENSIONS'])
            response = jsonify(dict(
                error="File does not match allowed extensions: %s" % allowed))
            response.status_code = 500
            return response

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/compare')
@app.route('/compare/<image>')
def compare(image=None):
    if image is None:
        return serve_upload_page()

    image_obj = get_info(image)[0]

    exif_info = dict(zip(('EXIF_BodySerialNumber', 'EXIF_LensSerialNumber',
              'Image_BodySerialNumber', 'MakerNote_InternalSerialNumber',
              'MakerNote_SerialNumber', 'MakerNote_SerialNumberFormat'),

             (image_obj.EXIF_BodySerialNumber, image_obj.EXIF_LensSerialNumber,
              image_obj.Image_BodySerialNumber, image_obj.MakerNote_InternalSerialNumber,
              image_obj.MakerNote_SerialNumber, image_obj.MakerNote_SerialNumberFormat)))

    # serial_num = exif_info['EXIF_BodySerialNumber']

    headers = {'content-type': 'image/jpeg', 'Accept': 'application/json'}

    full_path = os.path.join(app.config['UPLOAD_DIR'], image)
    url = "http://localhost:8899/meta"
    r = requests.put(url, data=open(full_path), headers=headers)
    json_dict = r.json()
    serial_num = json_dict.get("Serial Number") or json_dict.get("Camera Serial Number")


    url_serial_number = os.path.join(app.config['MEMEX_URL'],
                             "select?q=serial_number:{}&wt=json&indent=true".format(serial_num))

    url_camera_serial_number = os.path.join(app.config['MEMEX_URL'],
                             "select?q=camera_serial_number:{}&wt=json&indent=true".format(serial_num))
    urls = [url_serial_number, url_camera_serial_number]

    solr_docs = []
    for url in urls:
        try:
            r = requests.get(url)
            solr_docs.extend(r.json()['response']['docs'])
        except ValueError:
            pass

    for d in solr_docs:
        d['dirname'] = os.path.dirname(d['id'])
        d['basename'] = os.path.basename(d['id'])
        d['id'] = d['id'].strip('/')

    # serial_matches = get_info_serial(image_obj.EXIF_BodySerialNumber)
    return render_template('compare.html', num_images=10, image=image, exif_info=exif_info,
                           solr_docs=solr_docs)

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/map')
def map():
    return render_template('map.html')
