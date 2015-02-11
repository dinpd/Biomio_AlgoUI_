from flask import Flask
from flask.templating import render_template
from algointerface import AlgorithmsInterface as agi

app = Flask(__name__)


@app.route('/')
def home_page():
    return render_template('main_algo_template.html')


@app.route('/run', methods=['POST'])
def run_algorithm():
    """
    Will gather all input values from request POST data and will invoke selected algorithm.
    :return:
    """
    return 'OK'


@app.route('/', methods=['POST'])
def show_algo_properties():
    """
    Will render the template with selected algorithm parameters.
    :param algo_name: Name of the algorithm
    :return:
    """
    return 'OK'


@app.context_processor
def inject_db_list():
    return dict(db_list=agi.getDatabasesList())


@app.context_processor
def inject_algo_list():
    return dict(algo_list=agi.getAlgorithmsList())

if __name__ == '__main__':
    app.run()
