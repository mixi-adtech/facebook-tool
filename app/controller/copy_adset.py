from flask import Blueprint, render_template, jsonify, request, abort
from app.common.config import Config
from app.model.copy_ad_set.select import AdSetModel, SelectTarget
from app.model.copy_ad_set.copy_ad_set_below import CopyAdSet

app = Blueprint(__name__, 'copy_adset')
config = Config().get_config()


@app.route('/copy_adset')
def index():
    return render_template('copy_adset.html')


@app.route('/copy_adset/api/adset/<account>')
def get_ad_set(account):

    if not (account in config['act_id']):
        abort()

    act_id = config['act_id'][account]
    model = AdSetModel(act_id)
    adset = model.get_ad_set()
    return jsonify(result=adset)


@app.route('/copy_adset/select_target', methods=['POST'])
def select_target():
    if request.method == 'POST':
        model = SelectTarget(request.form)
        target = model.select_target()

        return render_template('select_target.html', params=target)
    return render_template('copy_adset.html', error=1)


@app.route('/copy_adset/add', methods=['POST'])
def copy():
    if request.method == 'POST':
        model = CopyAdSet(request.form)
        result = model.copy()

        return render_template('copy_adset_result.html', params=result)
    return render_template('copy_adset.html', error=1)
