import sys
import os

# Add git-cola to path if not installed (for development)
# Assuming we are in the root of the workspace
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'git-cola')))

from qtpy import QtWidgets
from cola import qtutils
from cola import themes
from cola import icons
from cola import i18n
from hellorestsoft import app

def main():
    argv = sys.argv
    context = app.application_init(argv)
    
    # Create main window
    from hellorestsoft.widgets.main import MainWindow
    view = MainWindow(context)
    
    # Start app
    return app.application_run(context, view)

if __name__ == '__main__':
    sys.exit(main())
