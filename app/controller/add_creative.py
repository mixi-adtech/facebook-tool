from flask import Blueprint, render_template, jsonify, request, abort
from app.common.config import Config
from app.model.bulk_adgroup.select import AdSetModel
from app.model.bulk_adgroup.create import AdCreativeModel
from facebookads.objects import AdGroup

import os, hashlib, re, time

app = Blueprint(__name__, 'add_creative')
this_dir = os.path.dirname(__file__)
config = Config().get_config()

@app.route('/add_creative')
def index():
    return render_template('add_creative.html')

@app.route('/add_creative/api/adset/<account>/<target_os>')
def get_ad_set(account, target_os):

    if not _is_get_ad_set_valid(account, target_os):
        abort()

    act_id = config['act_id'][account]
    link_url = config['link_url'][account][target_os]

    model = AdSetModel(act_id, link_url)
    adset = model.get_ad_set()
    return jsonify(result=adset)

@app.route('/add_creative/add', methods=['POST'])
def add():
    if request.method == 'POST' and _is_add_request_valid():
        f = request.files['filename']
        filename = f.filename
        name, ext = os.path.splitext(filename)
        hashed_filename = hashlib.md5(str(time.time())).hexdigest()

        f.save(os.path.join(this_dir, '../../upload/'+ hashed_filename + ext))

        model = AdCreativeModel(request.form, hashed_filename + ext)
        adcreative = model.create_ad_creative()
        return render_template('result.html', ads=adcreative)
    return render_template('add_creative.html', error=1)

def _is_get_ad_set_valid(account, target_os):
    if not (account in config['act_id']):
        return False
    if not (account in config['link_url']):
        return False
    if not (target_os in config['link_url'][account]):
        return False
    return True

def _is_add_request_valid():
    if not 'creative_name' in request.form or len(request.form['creative_name']) == 0:
        return False
    if not 'account' in request.form or len(request.form['account']) == 0:
        return False
    account = request.form['account']
    if not (account in config['act_id']) or not (account in config['link_url']):
        return False
    if not 'os' in request.form or len(request.form['os']) == 0:
        return False
    target_os = request.form['os']
    if not (target_os in config['link_url'][account]):
        return False
    if not 'title' in request.form or len(request.form['title']) == 0:
        return False
    if not 'message' in request.form or len(request.form['message']) == 0:
        return False
    if not 'status' in request.form or len(request.form['status']) == 0:
        return False
    status = request.form['status']
    if status != AdGroup.Status.active and status != AdGroup.Status.paused:
        return False
    if not 'filename' in request.files:
        return False
    f = request.files['filename']
    filename = f.filename
    name, ext = os.path.splitext(filename)
    ext_re = re.compile(ext, re.IGNORECASE)
    if ext_re.match('.jpg') == None and ext_re.match('.jpeg') == None and ext_re.match('.png') == None and ext_re.match('.gif') == None:
        return False
    if not 'adset_ids' in request.form:
        return False
    return True
