__author__ = 'vitalius.parubochyi'

from algointerface import AlgorithmsInterface


def main():
    interface = AlgorithmsInterface()
    print interface.get_databases_list()
    print interface.get_database_settings(interface.get_databases_list()[0]['pk'])
    print interface.get_algorithms_list()


if __name__ == '__main__':
    main()