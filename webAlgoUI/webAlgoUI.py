from flask import Flask
from flask.templating import render_template

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


@app.route('/<algo_name>')
def show_algo_properties(algo_name):
    """
    Will render the template with selected algorithm parameters.
    :param algo_name: Name of the algorithm
    :return:
    """
    return algo_name


if __name__ == '__main__':
    app.run()
