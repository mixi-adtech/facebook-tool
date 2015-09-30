from flask import Blueprint, render_template, request
from app.common.config import Config
from app.model.bulk_adgroup.create_carousel import CarouselAdCreativeModel

import os
import hashlib
import time

app = Blueprint(__name__, 'add_carousel')
this_dir = os.path.dirname(__file__)
config = Config().get_config()


@app.route('/add_carousel')
def index():
    return render_template('add_carousel.html')


@app.route('/add_carousel/add', methods=['POST'])
def add():
    attachments = []
    for count in range(1, 6):
        filename = 'filename' + str(count)
        title = 'title' + str(count)
        if filename in request.files and title in request.form:
            file = request.files[filename]
            name, ext = os.path.splitext(file.filename)
            hashed_filename = hashlib.md5(str(time.time())).hexdigest()
            file.save(os.path.join(this_dir, '../../upload/' + hashed_filename + ext))
            attachment = {
                'title': request.form[title],
                'filename': hashed_filename + ext,
            }
            attachments.append(attachment)
            time.sleep(1)

    model = CarouselAdCreativeModel(request.form, attachments)
    adcreative = model.create_carousel_ad_creative()
    return render_template('result.html', ads=adcreative)
