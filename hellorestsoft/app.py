import sys
import time
from qtpy import QtWidgets, QtCore
from cola import qtutils
from cola import themes
from cola import icons
from cola import i18n
from cola import qtcompat

class ApplicationContext:
    def __init__(self):
        self.app = None
        self.view = None
        self.cfg = None # TODO: Implement config
        self.model = None # TODO: Implement model
        self.runtask = None # Initialized in set_view or manually

    def set_view(self, view):
        self.view = view
        self.runtask = qtutils.RunTask(parent=view)

class HelloRestApplication(QtWidgets.QApplication):
    def __init__(self, context, argv):
        super().__init__(argv)
        self.context = context
        # Setup themes, icons etc similar to cola
        qtcompat.install()
        # icons.install(['light']) # Default to light for now

def application_init(argv):
    context = ApplicationContext()
    context.app = HelloRestApplication(context, argv)
    return context

def application_run(context, view):
    context.set_view(view)
    view.show()
    return context.app.exec_()
