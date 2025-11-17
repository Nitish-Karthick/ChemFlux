import sys
import os
import requests
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QFileDialog,
    QTableWidget, QTableWidgetItem, QGroupBox, QFrame, QDialog,
    QDialogButtonBox, QHeaderView, QSizePolicy, QStackedWidget
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

API_BASE = os.environ.get('CHEMFLUX_API', 'http://127.0.0.1:8000/api')


class ChartCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(5, 3), tight_layout=True)
        super().__init__(self.fig)
        # Dark theme styling for charts
        self.fig.patch.set_facecolor('#111827')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#0b1020')
        self.ax.tick_params(colors='#94a3b8')

    def plot_bar(self, data):
        self.ax.clear()
        if data:
            labels = list(data.keys())
            values = list(data.values())
            self.ax.bar(labels, values, color='#3b82f6')
            self.ax.set_title('Averages', color='#ffffff', fontsize=12, fontweight='bold')
            self.ax.tick_params(axis='x', labelrotation=45)
            # cleaner look
            self.ax.grid(False)
            for spine in self.ax.spines.values():
                spine.set_color('#17334b')
            self.fig.subplots_adjust(left=0.12, right=0.96, top=0.88, bottom=0.22)
        self.draw()

    def plot_pie(self, data):
        self.ax.clear()
        if data:
            labels = list(data.keys())
            values = list(data.values())
            self.ax.pie(values, labels=None, autopct='%1.1f%%', textprops={'color':'#e5e7eb'})
            # Legend at bottom for readability (white text)
            leg = self.ax.legend(labels, loc='lower center', bbox_to_anchor=(0.5, -0.18), ncol=3, frameon=False, fontsize=8)
            for t in leg.get_texts():
                t.set_color('#ffffff')
            self.ax.set_title('Type Distribution', color='#ffffff', fontsize=12, fontweight='bold')
            self.ax.axis('equal')
            self.fig.subplots_adjust(left=0.06, right=0.94, top=0.86, bottom=0.30)
        self.draw()


class ChemFluxApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ChemFlux Desktop')
        self.resize(1200, 720)

        self.username = ''
        self.password = ''
        self.current_dataset = None

        root = QWidget()
        self.setCentralWidget(root)
        shell = QHBoxLayout(root)
        shell.setSpacing(0)
        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName('Sidebar')
        self.sidebar.setFixedWidth(220)
        side = QVBoxLayout(self.sidebar)
        logo = QLabel('CF')
        logo.setObjectName('Logo')
        logo.setAlignment(QtCore.Qt.AlignCenter)
        logo.setFixedSize(36, 36)
        side.addWidget(logo)
        self.navDash = QPushButton('Dashboard')
        self.navDash.setObjectName('Nav')
        self.navReport = QPushButton('Download Report')
        self.navReport.setObjectName('Nav')
        self.navReport.clicked.connect(self.download_pdf)
        side.addWidget(self.navDash)
        side.addWidget(self.navReport)
        side.addStretch(1)
        shell.addWidget(self.sidebar)

        # Main content area
        content = QWidget()
        main = QVBoxLayout(content)
        main.setContentsMargins(12, 0, 12, 12)
        main.setSpacing(12)
        shell.addWidget(content, 1)

        # Top bar
        topbar = QFrame()
        topbar.setObjectName('Topbar')
        tLay = QHBoxLayout(topbar)
        tLay.setContentsMargins(12, 8, 12, 8)
        tTitle = QLabel('Equipment Parameter Dashboard')
        tTitle.setObjectName('TopTitle')
        font = tTitle.font(); font.setPointSize(16); font.setBold(True)
        tTitle.setFont(font)
        tTitle.setStyleSheet('color: #ffffff; font-size: 20px; font-weight: 800; letter-spacing: 0.5px;')
        tTitle.setMinimumHeight(32)
        tTitle.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        tTitle.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        tLay.addWidget(tTitle)
        tLay.addStretch(1)
        avatar = QLabel('U')
        avatar.setObjectName('Avatar')
        avatar.setAlignment(QtCore.Qt.AlignCenter)
        avatar.setFixedSize(32, 32)
        self.avatar = avatar
        tLay.addWidget(self.avatar)
        main.addWidget(topbar)
        topbar.setFixedHeight(96)
        self.pages = QStackedWidget()
        main.addWidget(self.pages, 1)

        # Auth
        authBox = QGroupBox('Authentication (DRF Basic Auth)')
        authLayout = QHBoxLayout()
        authBox.setLayout(authLayout)
        authLayout.addWidget(QLabel('Username'))
        self.userEdit = QLineEdit()
        self.userEdit.setText('')
        self.passEdit = QLineEdit()
        self.passEdit.setEchoMode(QLineEdit.Password)
        authLayout.addWidget(self.userEdit)
        authLayout.addWidget(QLabel('Password'))
        authLayout.addWidget(self.passEdit)
        self.loginBtn = QPushButton('Login/Test')
        self.loginBtn.clicked.connect(self.login)
        authLayout.addWidget(self.loginBtn)
        self.statusLbl = QLabel('Not authenticated')
        authLayout.addWidget(self.statusLbl)
        self.authBox = authBox
        # Hidden in favor of modal login at startup
        self.authBox.setVisible(False)
        main.addWidget(self.authBox)

        # Hero upload panel
        self.heroBox = QGroupBox('Upload your data to get started')
        self.heroBox.setObjectName('Hero')
        hLay = QHBoxLayout()
        self.heroBox.setLayout(hLay)
        self.heroBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.heroBox.setMinimumHeight(100)
        self.heroBox.setMaximumHeight(120)
        subLbl = QLabel('Drag & drop or use Select CSV, then click Upload')
        subLbl.setObjectName('HeroSub')
        self.selectBtn = QPushButton('Select CSV')
        self.selectBtn.clicked.connect(self.select_csv)
        self.uploadBtn = QPushButton('Upload')
        self.uploadBtn.setObjectName('Primary')
        self.uploadBtn.clicked.connect(self.upload_csv)
        self.refreshBtn = QPushButton('Refresh History')
        self.refreshBtn.clicked.connect(self.load_history)
        self.pdfBtn = QPushButton('Download PDF')
        self.pdfBtn.clicked.connect(self.download_pdf)
        hLay.addWidget(subLbl)
        hLay.addStretch(1)
        hLay.addWidget(self.selectBtn)
        hLay.addWidget(self.uploadBtn)
        hLay.addWidget(self.refreshBtn)
        hLay.addWidget(self.pdfBtn)
        

        # Stats cards
        self.statsBox = QGroupBox('Summary Statistics')
        self.statsBox.setStyleSheet('QGroupBox::title{color:#ffffff; font-size:16px; font-weight:800;}')
        sCards = QHBoxLayout()
        self.statsBox.setLayout(sCards)
        def make_card(title):
            card = QFrame()
            card.setProperty('card', True)
            v = QVBoxLayout(card)
            lbl = QLabel(title)
            lbl.setStyleSheet('color:#e2e8f0; font-size:14px; font-weight:600;')
            val = QLabel('—')
            val.setObjectName('StatValue')
            val.setMinimumHeight(42)
            val.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            v.addWidget(lbl)
            v.addWidget(val)
            v.addStretch(1)
            return card, val
        c1, self.statTotal = make_card('Total Equipment Units')
        c2, self.statPressure = make_card('Average Pressure (PSI)')
        c3, self.statTemp = make_card('Mean Temperature (°C)')
        c4, self.statFlow = make_card('Average Flow Rate')
        for c in (c1, c2, c3, c4):
            sCards.addWidget(c)
        
        # Keep stats compact so content below remains visible
        self.statsBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.statsBox.setMaximumHeight(180)

        # Data area (hidden until data loaded)
        self.dataArea = QWidget()
        self.dataArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right = QVBoxLayout(self.dataArea)
        
        # collapse when hidden to avoid empty space
        self.dataArea.setVisible(False)
        self.dataArea.setMaximumHeight(0)

        # Summary
        self.summaryBox = QGroupBox('Summary')
        sLay = QVBoxLayout()
        self.summaryBox.setLayout(sLay)
        self.totalLbl = QLabel('Total Count: -')
        sLay.addWidget(self.totalLbl)

        self.avgTable = QTableWidget(0, 2)
        self.avgTable.setHorizontalHeaderLabels(['Parameter', 'Average'])
        self.avgTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.avgTable.verticalHeader().setDefaultSectionSize(26)
        self.avgTable.setMinimumHeight(200)
        self.avgTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.avgTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.avgTable.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.avgTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.typeTable = QTableWidget(0, 2)
        self.typeTable.setHorizontalHeaderLabels(['Type', 'Count'])
        self.typeTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.typeTable.verticalHeader().setDefaultSectionSize(26)
        self.typeTable.setMinimumHeight(200)
        self.typeTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.typeTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.typeTable.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.typeTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        topRow = QHBoxLayout()
        topRow.addWidget(self.avgTable, 1)
        topRow.addWidget(self.typeTable, 1)
        sLay.addLayout(topRow)

        self.previewTable = QTableWidget(0, 0)
        self.previewTable.verticalHeader().setDefaultSectionSize(24)
        self.previewTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.previewTable.setMinimumHeight(240)
        self.previewTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.previewTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.previewTable.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.previewTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        sLay.addWidget(self.previewTable)
        sLay.setStretch(0, 0)
        sLay.setStretch(1, 2)
        sLay.setStretch(2, 3)
        self.summaryBox.setMinimumHeight(280)
        right.addWidget(self.summaryBox, 1)

        # Charts
        self.chartsBox = QGroupBox('Charts')
        cLay = QHBoxLayout()
        self.chartsBox.setLayout(cLay)
        self.barCanvas = ChartCanvas()
        self.barCanvas.setMinimumHeight(320)
        self.pieCanvas = ChartCanvas()
        self.pieCanvas.setMinimumHeight(360)
        cLay.addWidget(self.barCanvas)
        cLay.addWidget(self.pieCanvas)
        right.addWidget(self.chartsBox, 1)
        right.setStretch(0, 3)
        right.setStretch(1, 2)

        # History at bottom
        histBox = QGroupBox('History (Last 5)')
        histLayout = QVBoxLayout()
        histBox.setLayout(histLayout)
        self.historyList = QListWidget()
        self.historyList.itemSelectionChanged.connect(self.history_selected)
        histLayout.addWidget(self.historyList)
        histBox.setFixedHeight(220)
        
        # Build stacked pages
        prePage = QWidget(); preLay = QVBoxLayout(prePage)
        preLay.addWidget(self.heroBox)
        histBoxPre = QGroupBox('History (Last 5)')
        histLayoutPre = QVBoxLayout(); histBoxPre.setLayout(histLayoutPre)
        self.historyListPre = QListWidget()
        self.historyListPre.itemSelectionChanged.connect(self.history_selected)
        histLayoutPre.addWidget(self.historyListPre)
        histBoxPre.setFixedHeight(140)
        preLay.addWidget(histBoxPre)
        preLay.addStretch(1)

        self.dashPage = QWidget(); dashLay = QVBoxLayout(self.dashPage)
        dashLay.addWidget(self.statsBox)
        dashLay.addWidget(self.dataArea, 1)
        dashLay.addWidget(histBox)

        self.prePage = prePage
        self.pages.addWidget(self.prePage)
        self.pages.addWidget(self.dashPage)
        self.pages.setCurrentWidget(self.prePage)

        self.selected_csv = None
        # Hide until a dataset is selected
        self.statsBox.setVisible(True)
        self.summaryBox.setVisible(False)
        self.chartsBox.setVisible(False)

    # Helpers
    def auth(self):
        return (self.username, self.password) if self.username and self.password else None

    def set_status(self, text):
        self.statusLbl.setText(text)

    # Actions
    def login(self):
        self.username = self.userEdit.text().strip()
        self.password = self.passEdit.text().strip()
        try:
            r = requests.get(f"{API_BASE}/datasets/", auth=self.auth(), timeout=10)
            if r.status_code == 200:
                self.set_status('Authenticated')
                self.load_history()
            else:
                self.set_status(f'Auth failed: {r.status_code}')
        except Exception as e:
            self.set_status(f'Error: {e}')

    def select_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Select CSV', '', 'CSV Files (*.csv)')
        if path:
            self.selected_csv = path
            self.set_status(f'Selected {os.path.basename(path)}')

    def upload_csv(self):
        if not self.selected_csv:
            self.set_status('No CSV selected')
            return
        try:
            with open(self.selected_csv, 'rb') as f:
                files = {'file': (os.path.basename(self.selected_csv), f, 'text/csv')}
                r = requests.post(f"{API_BASE}/upload/", files=files, auth=self.auth(), timeout=30)
            if r.status_code in (200, 201):
                data = r.json()
                self.current_dataset = data
                self.update_summary()
                self.set_status('Upload success')
                self.load_history()
            else:
                self.set_status(f'Upload failed: {r.status_code}')
        except Exception as e:
            self.set_status(f'Error: {e}')

    def load_history(self):
        try:
            r = requests.get(f"{API_BASE}/datasets/", auth=self.auth(), timeout=10)
            r.raise_for_status()
            data = r.json()
            items = data.get('results', [])
            self.historyList.clear()
            if hasattr(self, 'historyListPre'):
                self.historyListPre.clear()
            for it in items:
                text = f"{it['id']}: {it['name']} | {it['uploaded_at']}"
                self.historyList.addItem(text)
                if hasattr(self, 'historyListPre'):
                    self.historyListPre.addItem(text)
            # Do not auto-select; wait for user action
        except Exception as e:
            self.set_status(f'Error: {e}')

    def history_selected(self):
        src = self.sender()
        lst = src if isinstance(src, QListWidget) else self.historyList
        current = lst.currentItem()
        if not current:
            return
        text = current.text()
        ds_id = int(text.split(':', 1)[0])
        self.fetch_detail(ds_id)
        if hasattr(self, 'pages') and hasattr(self, 'dashPage'):
            self.pages.setCurrentWidget(self.dashPage)

    def fetch_detail(self, ds_id):
        try:
            r = requests.get(f"{API_BASE}/datasets/{ds_id}/", auth=self.auth(), timeout=10)
            r.raise_for_status()
            self.current_dataset = r.json()
            self.update_summary()
            self.set_status(f'Loaded dataset {ds_id}')
        except Exception as e:
            self.set_status(f'Error: {e}')

    def update_summary(self):
        ds = self.current_dataset or {}
        s = ds.get('summary', {})
        # total
        self.totalLbl.setText(f"Total Count: {s.get('total_count', 0)}")
        self.statsBox.setVisible(True)
        self.summaryBox.setVisible(True)
        self.chartsBox.setVisible(True)
        # Reveal the data area once data is available
        if hasattr(self, 'dataArea'):
            self.dataArea.setMaximumHeight(16777215)
            self.dataArea.setVisible(True)
        if hasattr(self, 'pages') and hasattr(self, 'dashPage'):
            self.pages.setCurrentWidget(self.dashPage)
        # Hide hero after data loads to free space
        if hasattr(self, 'heroBox'):
            self.heroBox.setVisible(False)
        # stats cards
        total = s.get('total_count', 0)
        av = s.get('averages', {})
        def find_avg(keys):
            for k, v in av.items():
                lk = k.lower()
                if any(x in lk for x in keys):
                    return v
            return '—'
        self.statTotal.setText(str(total))
        self.statPressure.setText(str(find_avg(['pressure','psi'])))
        self.statTemp.setText(str(find_avg(['temperature','temp'])))
        self.statFlow.setText(str(find_avg(['flowrate','flow rate','flow'])))
        # averages table
        av = s.get('averages', {})
        self.avgTable.setRowCount(len(av))
        self.avgTable.setColumnCount(2)
        self.avgTable.setHorizontalHeaderLabels(['Parameter', 'Average'])
        for i, (k, v) in enumerate(av.items()):
            self.avgTable.setItem(i, 0, QTableWidgetItem(str(k)))
            self.avgTable.setItem(i, 1, QTableWidgetItem(str(v)))
        # type distribution
        td = s.get('type_distribution', {})
        self.typeTable.setRowCount(len(td))
        self.typeTable.setColumnCount(2)
        self.typeTable.setHorizontalHeaderLabels(['Type', 'Count'])
        for i, (k, v) in enumerate(td.items()):
            self.typeTable.setItem(i, 0, QTableWidgetItem(str(k)))
            self.typeTable.setItem(i, 1, QTableWidgetItem(str(v)))
        # preview
        cols = s.get('columns', [])
        prev = s.get('preview', [])
        self.previewTable.setColumnCount(len(cols))
        self.previewTable.setHorizontalHeaderLabels([str(c) for c in cols])
        self.previewTable.setRowCount(len(prev))
        for i, row in enumerate(prev):
            for j, c in enumerate(cols):
                self.previewTable.setItem(i, j, QTableWidgetItem(str(row.get(c, ''))))
        # charts
        self.barCanvas.plot_bar(av)
        self.pieCanvas.plot_pie(td)

    def download_pdf(self):
        if not self.current_dataset:
            self.set_status('No dataset selected')
            return
        ds_id = self.current_dataset['id']
        try:
            r = requests.get(f"{API_BASE}/datasets/{ds_id}/report/", auth=self.auth(), timeout=30)
            r.raise_for_status()
            data = r.content
            path, _ = QFileDialog.getSaveFileName(self, 'Save Report', f'chemflux_report_{ds_id}.pdf', 'PDF (*.pdf)')
            if path:
                with open(path, 'wb') as f:
                    f.write(data)
                self.set_status(f'Saved {os.path.basename(path)}')
        except Exception as e:
            self.set_status(f'Error: {e}')

    def set_credentials(self, username: str, password: str):
        self.username = username
        self.password = password
        # Update avatar initial
        if username:
            self.avatar.setText(username[0].upper())


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Sign in to ChemFlux')
        self.resize(420, 180)
        lay = QVBoxLayout(self)
        row1 = QHBoxLayout(); row2 = QHBoxLayout()
        lay.addLayout(row1); lay.addLayout(row2)
        row1.addWidget(QLabel('Username'))
        self.userEdit = QLineEdit()
        row1.addWidget(self.userEdit)
        row2.addWidget(QLabel('Password'))
        self.passEdit = QLineEdit(); self.passEdit.setEchoMode(QLineEdit.Password)
        row2.addWidget(self.passEdit)
        self.errorLbl = QLabel('')
        self.errorLbl.setStyleSheet('color:#ef4444;')
        lay.addWidget(self.errorLbl)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        lay.addWidget(btns)
        btns.accepted.connect(self.try_login)
        btns.rejected.connect(self.reject)

    def try_login(self):
        u = self.userEdit.text().strip()
        p = self.passEdit.text().strip()
        try:
            r = requests.get(f"{API_BASE}/datasets/", auth=(u, p), timeout=10)
            if r.status_code == 200:
                self.username = u
                self.password = p
                self.accept()
            else:
                self.errorLbl.setText('Invalid credentials')
        except Exception as e:
            self.errorLbl.setText(str(e))



def main():
    app = QApplication(sys.argv)
    # Load QSS theme
    try:
        qss_path = os.path.join(os.path.dirname(__file__), 'style.qss')
        if os.path.exists(qss_path):
            with open(qss_path, 'r', encoding='utf-8') as f:
                app.setStyleSheet(f.read())
    except Exception:
        pass
    win = ChemFluxApp()
    # Modal login before using the app
    dlg = LoginDialog(win)
    if dlg.exec_() == QDialog.Accepted:
        win.set_credentials(dlg.username, dlg.password)
        win.set_status('Authenticated')
        try:
            win.load_history()
        except Exception:
            pass
    else:
        win.set_status('Not authenticated')
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
