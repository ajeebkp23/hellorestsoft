from qtpy import QtWidgets, QtCore
from cola import qtutils
import httpx
import asyncio
import json

class RequestView(QtWidgets.QWidget):
    save_requested = QtCore.Signal(dict)

    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.context = context
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Top Bar: Method, URL, Send
        self.top_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.top_layout)
        
        self.method_combo = QtWidgets.QComboBox()
        self.method_combo.addItems(["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
        self.top_layout.addWidget(self.method_combo)
        
        self.url_input = QtWidgets.QLineEdit()
        self.url_input.setPlaceholderText("Enter URL")
        self.top_layout.addWidget(self.url_input)
        
        self.send_button = QtWidgets.QPushButton("Send")
        self.send_button.clicked.connect(self.send_request)
        self.top_layout.addWidget(self.send_button)

        self.save_button = QtWidgets.QPushButton("Save")
        self.save_button.clicked.connect(self.request_save)
        self.top_layout.addWidget(self.save_button)
        
        # Main Content Splitter
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.layout.addWidget(self.splitter)
        
        # Request Area
        self.request_tabs = QtWidgets.QTabWidget()
        self.splitter.addWidget(self.request_tabs)
        
        self.req_body_edit = QtWidgets.QPlainTextEdit()
        self.request_tabs.addTab(self.req_body_edit, "Body")
        
        self.req_headers_edit = QtWidgets.QPlainTextEdit()
        self.req_headers_edit.setPlaceholderText("Key: Value")
        self.request_tabs.addTab(self.req_headers_edit, "Headers")
        
        # Response Area
        self.response_tabs = QtWidgets.QTabWidget()
        self.splitter.addWidget(self.response_tabs)
        
        self.resp_body_edit = QtWidgets.QPlainTextEdit()
        self.resp_body_edit.setReadOnly(True)
        self.response_tabs.addTab(self.resp_body_edit, "Response Body")
        
        self.resp_headers_edit = QtWidgets.QPlainTextEdit()
        self.resp_headers_edit.setReadOnly(True)
        self.response_tabs.addTab(self.resp_headers_edit, "Response Headers")
        
        # Status Bar for this view
        self.status_label = QtWidgets.QLabel("Ready")
        self.layout.addWidget(self.status_label)

    def send_request(self):
        method = self.method_combo.currentText()
        url = self.url_input.text()
        if not url:
            return
            
        body = self.req_body_edit.toPlainText()
        headers_text = self.req_headers_edit.toPlainText()
        headers = {}
        for line in headers_text.splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                headers[k.strip()] = v.strip()
        
        self.status_label.setText("Sending...")
        self.send_button.setEnabled(False)
        
        # Use git-cola's RunTask to run in background
        # We wrap the async call in a sync function for SimpleTask
        task = qtutils.SimpleTask(self._run_async_request, method, url, headers, body)
        self.context.runtask.start(task, result=self.handle_response, finish=self.request_finished)

    def _run_async_request(self, method, url, headers, body):
        return asyncio.run(self._make_request(method, url, headers, body))

    async def _make_request(self, method, url, headers, body):
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, headers=headers, content=body)
            return {
                'status_code': response.status_code,
                'text': response.text,
                'headers': dict(response.headers),
                'elapsed': response.elapsed.total_seconds()
            }

    def handle_response(self, result):
        if isinstance(result, Exception):
            self.resp_body_edit.setPlainText(f"Error: {str(result)}")
            self.status_label.setText("Error")
            return

        self.status_label.setText(f"Status: {result['status_code']} | Time: {result['elapsed']:.3f}s")
        
        # Try to format JSON
        try:
            json_obj = json.loads(result['text'])
            formatted = json.dumps(json_obj, indent=2)
            self.resp_body_edit.setPlainText(formatted)
        except:
            self.resp_body_edit.setPlainText(result['text'])
            
        headers_text = "\n".join([f"{k}: {v}" for k, v in result['headers'].items()])
        self.resp_headers_edit.setPlainText(headers_text)

    def request_finished(self, task):
        self.send_button.setEnabled(True)

    def set_data(self, data):
        if 'method' in data:
            self.method_combo.setCurrentText(data['method'])
        if 'url' in data:
            self.url_input.setText(data['url'])
        if 'headers' in data:
            self.req_headers_edit.setPlainText(data['headers'])
        if 'body' in data:
            self.req_body_edit.setPlainText(data['body'])

    def get_data(self):
        return {
            'method': self.method_combo.currentText(),
            'url': self.url_input.text(),
            'headers': self.req_headers_edit.toPlainText(),
            'body': self.req_body_edit.toPlainText()
        }

    def request_save(self):
        self.save_requested.emit(self.get_data())
