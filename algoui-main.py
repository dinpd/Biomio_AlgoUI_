from guidata import qapplication
from biowindow import BioWindow

import logging

if __name__ == '__main__':

    logging.basicConfig(
        format='%(levelname)-8s [%(asctime)s] %(message)s',
        level=logging.DEBUG
    )

    app = qapplication()
    window = BioWindow()
    window.show()
    app.exec_()