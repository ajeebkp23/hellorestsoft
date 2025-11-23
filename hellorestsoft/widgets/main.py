import os
from qtpy import QtWidgets, QtCore, QtGui
from cola import qtutils

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.context = context
        self.setWindowTitle("HelloRestSoft")
        self.resize(1000, 700)
        
        # Set Icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'logo.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))
        
        self.main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.main_widget)
        
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.layout = QtWidgets.QVBoxLayout(self.main_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.splitter)
        
        # Sidebar
        self.sidebar_widget = QtWidgets.QWidget()
        self.sidebar_layout = QtWidgets.QVBoxLayout(self.sidebar_widget)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.splitter.addWidget(self.sidebar_widget)
        
        # Sidebar Header
        self.sidebar_header_widget = QtWidgets.QWidget()
        self.sidebar_header_layout = QtWidgets.QHBoxLayout(self.sidebar_header_widget)
        self.sidebar_header_layout.setContentsMargins(5, 5, 5, 5)
        self.sidebar_layout.addWidget(self.sidebar_header_widget)

        self.sidebar_label = QtWidgets.QLabel("Collections")
        self.sidebar_label.setStyleSheet("font-weight: bold;")
        self.sidebar_header_layout.addWidget(self.sidebar_label)
        
        self.sidebar_header_layout.addStretch()

        self.new_collection_btn = QtWidgets.QToolButton()
        self.new_collection_btn.setText("+")
        self.new_collection_btn.setToolTip("New Collection")
        self.new_collection_btn.clicked.connect(self.create_collection)
        self.sidebar_header_layout.addWidget(self.new_collection_btn)

        self.sidebar = QtWidgets.QTreeWidget()
        self.sidebar.setHeaderHidden(True)
        # self.sidebar.setFixedWidth(250) # Removed fixed width
        self.sidebar.itemDoubleClicked.connect(self.load_request_from_item)
        self.sidebar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sidebar.customContextMenuRequested.connect(self.show_sidebar_context_menu)
        self.sidebar_layout.addWidget(self.sidebar)
        
        # Collection Manager
        from hellorestsoft.models.collection import CollectionManager
        self.collection_manager = CollectionManager(os.path.expanduser("~/.hellorestsoft/collections"))
        self.refresh_sidebar()

        # Main Content Area (Tabs)
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        
        # New Request Button in Tab Bar
        self.new_tab_btn = QtWidgets.QToolButton()
        self.new_tab_btn.setText("+")
        self.new_tab_btn.setToolTip("New Request (Ctrl+T)")
        self.new_tab_btn.clicked.connect(lambda: self.add_new_request_tab())
        self.tabs.setCornerWidget(self.new_tab_btn, QtCore.Qt.TopRightCorner)
        
        self.splitter.addWidget(self.tabs)
        
        # Set initial splitter sizes (e.g., 250px for sidebar, rest for tabs)
        self.splitter.setSizes([250, 750])
        
        # Add a default new request tab
        self.add_new_request_tab()
        
        # Status Bar
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Shortcuts
        QtWidgets.QShortcut(QtGui.QKeySequence.New, self, self.add_new_request_tab)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+T"), self, self.add_new_request_tab)

    def refresh_sidebar(self):
        self.sidebar.clear()
        tree = self.collection_manager.get_tree()
        self._populate_tree(self.sidebar, tree, self.collection_manager.root_path)
        self.sidebar.expandAll()

    def _populate_tree(self, parent_widget, tree_data, current_path):
        # Add directories
        for name, subtree in tree_data.get('dirs', {}).items():
            item = QtWidgets.QTreeWidgetItem([name])
            item.setIcon(0, self.style().standardIcon(QtWidgets.QStyle.SP_DirIcon))
            full_path = os.path.join(current_path, name)
            item.setData(0, QtCore.Qt.UserRole, {'type': 'dir', 'path': full_path})
            
            if isinstance(parent_widget, QtWidgets.QTreeWidget):
                parent_widget.addTopLevelItem(item)
            else:
                parent_widget.addChild(item)
                
            self._populate_tree(item, subtree, full_path)
            
        # Add files
        for file_info in tree_data.get('files', []):
            item = QtWidgets.QTreeWidgetItem([file_info['name']])
            item.setIcon(0, self.style().standardIcon(QtWidgets.QStyle.SP_FileIcon))
            item.setData(0, QtCore.Qt.UserRole, {'type': 'file', 'path': file_info['path']})
            
            if isinstance(parent_widget, QtWidgets.QTreeWidget):
                parent_widget.addTopLevelItem(item)
            else:
                parent_widget.addChild(item)

    def show_sidebar_context_menu(self, position):
        menu = QtWidgets.QMenu()
        
        # Determine context
        item = self.sidebar.itemAt(position)
        item_data = item.data(0, QtCore.Qt.UserRole) if item else None
        
        create_collection_action = menu.addAction("New Collection")
        create_collection_action.triggered.connect(self.create_collection)
        
        # Only allow deleting if an item is selected
        if item:
             # TODO: Add delete functionality
             pass

        menu.exec_(self.sidebar.viewport().mapToGlobal(position))

    def create_collection(self):
        # Get selected item for parent
        selected_items = self.sidebar.selectedItems()
        parent_path = self.collection_manager.root_path
        if selected_items:
            item = selected_items[0]
            item_data = item.data(0, QtCore.Qt.UserRole)
            if item_data['type'] == 'dir':
                parent_path = item_data['path']
            elif item_data['type'] == 'file':
                parent_path = os.path.dirname(item_data['path'])

        name, ok = qtutils.prompt("Enter collection name:", "New Collection")
        if ok and name:
            try:
                self.collection_manager.create_collection(name, parent_path)
                self.refresh_sidebar()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def load_request_from_item(self, item, column):
        data = item.data(0, QtCore.Qt.UserRole)
        if data and data['type'] == 'file':
            req_data = self.collection_manager.load_request(data['path'])
            self.add_new_request_tab(req_data, name=item.text(0))

    def add_new_request_tab(self, data=None, name="New Request"):
        from hellorestsoft.widgets.request_view import RequestView
        view = RequestView(self.context)
        view.save_requested.connect(self.save_request)
        if data:
            view.set_data(data)
        index = self.tabs.addTab(view, name)
        self.tabs.setCurrentIndex(index)

    def save_request(self, data):
        # Get selected item in sidebar to determine save location
        selected_items = self.sidebar.selectedItems()
        parent_path = self.collection_manager.root_path
        
        if selected_items:
            item = selected_items[0]
            item_data = item.data(0, QtCore.Qt.UserRole)
            if item_data['type'] == 'dir':
                parent_path = item_data['path']
            elif item_data['type'] == 'file':
                parent_path = os.path.dirname(item_data['path'])
        
        name, ok = qtutils.prompt("Enter request name:", "Save Request")
        if ok and name:
            try:
                self.collection_manager.save_request(name, data, parent_path)
                self.refresh_sidebar()
                # Update tab title
                self.tabs.setTabText(self.tabs.currentIndex(), name)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
