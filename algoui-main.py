from guidata import qapplication
from biowindow import BioWindow

if __name__ == '__main__':
    from guidata import qapplication
    app = qapplication()
    window = BioWindow()
    window.show()
    app.exec_()