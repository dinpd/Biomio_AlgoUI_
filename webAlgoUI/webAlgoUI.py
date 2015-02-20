import os
from flask import Flask
from flask import request
from flask.templating import render_template
from algointerface import AlgorithmsInterface
import re
import unicodedata

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_MEDIA_PATH = os.path.join(APP_ROOT, 'static', 'media_images')

app = Flask(__name__)

algorithms_interface = AlgorithmsInterface()


@app.context_processor
def inject_db_list():
    print algorithms_interface.get_databases_list()
    return dict(db_list=algorithms_interface.get_databases_list())


@app.context_processor
def inject_algo_list():
    print algorithms_interface.get_algorithms_list()
    return dict(algo_list=algorithms_interface.get_algorithms_list())


@app.route('/', methods=['GET'])
def home_page():
    return render_template('main_algo_template.html')


@app.route('/run/<int:algo_id>/<int:db_id>', methods=['POST'])
def run_algorithm(algo_id, db_id):
    """
    Will gather all input values from request POST data and will invoke selected algorithm.
    :return:
    """
    form = request.form
    selected_image = os.path.join(STATIC_MEDIA_PATH, form['person_selector'], form['image_selector'])
    algo_settings = dict(data=selected_image, database=db_id)
    for key in form.keys():
        for value in form.getlist(key):
            if key not in ['image_selector', 'person_selector']:
                algo_settings.update({key: value})
    algo_result = algorithms_interface.apply_algorithm(algo_id, algo_settings)
    algo_result.update({'log': algo_result.get('log').replace('\n', '<br>')})
    return render_template('result_template.html', person=form['person_selector'], image=form['image_selector'],
                           algo_result=algo_result)


@app.route('/', methods=['POST'])
def show_algo_properties():
    """
    Will render the template with selected algorithm parameters.
    :return:
    """
    algo_id = int(request.form['algo_id'])
    db_id = int(request.form['db_id'])
    algo_settings = algorithms_interface.get_settings_template(algo_id)
    print algo_settings
    return render_template('algo_db_settings.html', algo_id=algo_id, db_id=db_id,
                           db_settings=algorithms_interface.get_database_settings(db_id),
                           selects=algo_settings.get('selects', None), inputs=algo_settings.get('inputs', None),
                           checkboxes=algo_settings.get('checkboxes', None),
                           radiobuttons=algo_settings.get('radio_buttons', None),
                           persons=os.listdir(STATIC_MEDIA_PATH),
                           settings_parameters=algo_settings.get('settings_parameters', None))


@app.route('/get-images', methods=['POST'])
def get_person_images():
    return render_template('images_and_preview.html', person=request.form['person'],
                           images=os.listdir(os.path.join(STATIC_MEDIA_PATH, request.form['person'])))


_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    From Django's "django/template/defaultfilters.py".
    """

    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(_slugify_strip_re.sub('', value).strip().lower())
    return _slugify_hyphenate_re.sub('-', value)


@app.template_filter('slugify')
def _slugify(string):
    if not string:
        return ""
    return slugify(string)


if __name__ == '__main__':
    app.debug = True
    app.run()
