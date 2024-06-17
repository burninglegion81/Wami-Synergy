from PySide6.QtWidgets import QWidget, QLabel, QSpinBox, QHBoxLayout
from backend import Backend
from typing import List
from frontend.synergy_page_widget import SynergyPageWidget

class AllPageDisplay(QWidget):
    '''
    Widget to show all 3 pages of synergy
    '''

    def __init__(self, backend:Backend):
        super().__init__()
        self.backend = backend

        self.create_widgets()

    def create_widgets(self):
        layout = QHBoxLayout(self)
        layout.addStretch()


        self.page_widgets:List[SynergyPageWidget] = []
        for i in range(3):
            page_widget = SynergyPageWidget(self.backend, i+1)
            self.page_widgets.append(page_widget)
            layout.addWidget(page_widget)
        layout.addStretch()
