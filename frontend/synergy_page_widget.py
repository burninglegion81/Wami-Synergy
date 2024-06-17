from PySide6.QtWidgets import QWidget, QLabel, QSpinBox, QGridLayout, QGroupBox
from PySide6.QtCore import Qt
from backend import Backend
from typing import List
from frontend.synergy_row_widget import SynergyRowWidget

class SynergyPageWidget(QGroupBox):
    '''
    Widget to show a single page of synergy
    '''

    names_dict = {
        1 : ["Off/def", "Meditation", "DE", "Perks", "Demon Bonus", "Essence", "Conjuring"], 
        2 : ["Gold", "Mana Power", "Mana Refill", "Reincarnation Bonus", "Slime Attack", "Dungeon Bonus", "Generator Bonus"],
        3 : ["EXP", "Dungeon Damage", "Mana Cap Rate", "Class EXP", "Slime EXP", "Slime Bonus", "Alchemy Bonus"]
    }
    def __init__(self, backend:Backend, page:int):
        super().__init__(f"Synergy Page {page}", alignment = Qt.AlignCenter)
        self.backend = backend
        self.page = page

        self.create_widgets()

    def create_widgets(self):
        layout = QGridLayout(self)

        self.row_widgets:List[SynergyRowWidget] = []
        self.name_widgets:List[QLabel] = []
        for i in range(7):
            name_widget = QLabel(self.names_dict[self.page][i])
            name_widget.setStyleSheet("font-weight: bold;")
            row_widget = SynergyRowWidget(self.backend, self.page, i +1)
            self.name_widgets.append(name_widget)
            self.row_widgets.append(row_widget)
            layout.addWidget(name_widget,i,0,alignment=Qt.AlignLeft)
            layout.addWidget(row_widget, i,1,alignment=Qt.AlignRight)
