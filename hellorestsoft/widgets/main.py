from qtpy import QtWidgets, QtCore
from cola import qtutils

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.context = context
        self.setWindowTitle("HelloRestSoft")
        self.resize(1000, 700)
        
        self.main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.main_widget)
        
        self.layout = QtWidgets.QHBoxLayout(self.main_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Sidebar
        self.sidebar_widget = QtWidgets.QWidget()
        self.sidebar_layout = QtWidgets.QVBoxLayout(self.sidebar_widget)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.sidebar_widget)
        
        self.sidebar_header = QtWidgets.QLabel("Collections")
        self.sidebar_header.setStyleSheet("font-weight: bold; padding: 5px;")
        self.sidebar_layout.addWidget(self.sidebar_header)

        self.sidebar = QtWidgets.QTreeWidget()
        self.sidebar.setHeaderHidden(True)
        self.sidebar.setFixedWidth(250)
        self.sidebar.itemDoubleClicked.connect(self.load_request_from_item)
        self.sidebar_layout.addWidget(self.sidebar)
        
        # Collection Manager
        import os
        from hellorestsoft.models.collection import CollectionManager
        self.collection_manager = CollectionManager(os.path.expanduser("~/.hellorestsoft/collections"))
        self.refresh_sidebar()

        # Main Content Area (Tabs)
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.layout.addWidget(self.tabs)
        
        # Add a default new request tab
        self.add_new_request_tab()
        
        # Status Bar
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def refresh_sidebar(self):
        self.sidebar.clear()
        requests = self.collection_manager.get_requests()
        for req in requests:
            item = QtWidgets.QTreeWidgetItem([req['name']])
            item.setData(0, QtCore.Qt.UserRole, req['path'])
            self.sidebar.addTopLevelItem(item)

    def load_request_from_item(self, item, column):
        path = item.data(0, QtCore.Qt.UserRole)
        if path:
            data = self.collection_manager.load_request(path)
            self.add_new_request_tab(data, name=item.text(0))

    def add_new_request_tab(self, data=None, name="New Request"):
        from hellorestsoft.widgets.request_view import RequestView
        view = RequestView(self.context)
        view.save_requested.connect(self.save_request)
        if data:
            view.set_data(data)
        index = self.tabs.addTab(view, name)
        self.tabs.setCurrentIndex(index)

    def save_request(self, data):
        from cola import qtutils
        name, ok = qtutils.prompt("Enter request name:", "Save Request")
        if ok and name:
            self.collection_manager.save_request(name, data)
            self.refresh_sidebar()
            # Update tab title
            self.tabs.setTabText(self.tabs.currentIndex(), name)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
