import os
from flask import Flask
from flask import request
from flask.templating import render_template
from algointerface import AlgorithmsInterface
from fake_data import FAKE_ALGO_LIST, FAKE_DB_LIST, FAKE_ALGO_DB_SETTINGS
import re

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_MEDIA_PATH = os.path.join(APP_ROOT, 'static', 'media_images')

app = Flask(__name__)

algorithms_interface = AlgorithmsInterface()


@app.context_processor
def inject_db_list():
    return dict(db_list=FAKE_DB_LIST)


@app.context_processor
def inject_algo_list():
    return dict(algo_list=FAKE_ALGO_LIST)


@app.route('/', methods=['GET'])
def home_page():
    return render_template('main_algo_template.html')


@app.route('/run/<int:algo_id>/', methods=['POST'])
def run_algorithm(algo_id):
    """
    Will gather all input values from request POST data and will invoke selected algorithm.
    :return:
    """

    print algo_id
    return 'OK'


@app.route('/', methods=['POST'])
def show_algo_properties():
    """
    Will render the template with selected algorithm parameters.
    :return:
    """
    algo_id = request.form['algo_id']
    db_id = request.form['db_id']
    algo_db_settings = FAKE_ALGO_DB_SETTINGS.get('algo__db')
    return render_template('algo_db_settings.html', algo_id=algo_id, db_id=db_id,
                           selects=algo_db_settings.get('selects', None), inputs=algo_db_settings.get('inputs', None),
                           checkboxes=algo_db_settings.get('checkboxes', None),
                           radiobuttons=algo_db_settings.get('radio_buttons', None),
                           images=os.listdir(STATIC_MEDIA_PATH))


_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    From Django's "django/template/defaultfilters.py".
    """
    import unicodedata

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
    app.run()
