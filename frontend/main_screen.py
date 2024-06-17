from PySide6.QtWidgets import QWidget, QLabel, QSpinBox, QGridLayout, QGroupBox, QTabWidget, QVBoxLayout
from PySide6.QtCore import Qt
from backend import Backend
from typing import List
from frontend.all_page_display import AllPageDisplay
from frontend.other_inputs_widget import OtherInputsWidget
from frontend.optimizer_widget import OptimizerWidget

class MainScreen(QWidget):
    '''
    Widget to  hold all of the other widgets
    '''

    def __init__(self, backend:Backend):
        super().__init__()
        self.backend = backend
        self.setWindowTitle("Synergy Optimizer")

        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()

        self.inputs_tab_widget = QWidget()
        input_tab_layout = QVBoxLayout(self.inputs_tab_widget)
        self.synergy_pages_widget = AllPageDisplay(self.backend)
        self.other_inputs_widget = OtherInputsWidget(self.backend)
        input_tab_layout.addWidget(self.synergy_pages_widget)
        input_tab_layout.addWidget(self.other_inputs_widget)

        self.tab_widget.addTab(self.inputs_tab_widget, "Synergy Inputs")

        self.optimize_widget = OptimizerWidget(self.backend)
        self.tab_widget.addTab(self.optimize_widget, "Optimize")


        layout.addWidget(self.tab_widget)