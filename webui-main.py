# from algointerface import AlgorithmsInterface
#
#
# def main():
#     interface = AlgorithmsInterface()
#     print interface.get_databases_list()
#     print interface.get_database_settings(interface.get_databases_list()[0]['pk'])
#     print interface.get_algorithms_list()
#     print interface.get_settings_template(interface.get_databases_list()[0]['pk'])
#     settings = interface.get_settings_template(interface.get_databases_list()[0]['pk'])
#     settings['database'] = interface.get_databases_list()[0]['pk']
#     settings['max_neigh'] = 50
#     settings['data'] = "D:/Projects/Biomio/Test1/db/yaleB11/yaleB11_P00A+000E+00.pgm"
#     print "Settings", settings
#     print interface.apply_algorithm(interface.get_databases_list()[0]['pk'], settings)
#

from webAlgoUI.webAlgoUI import app

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')