from PySide6.QtWidgets import QFrame, QLabel, QSpinBox, QHBoxLayout, QDoubleSpinBox, QLineEdit
from PySide6.QtGui import QRegularExpressionValidator
from backend import Backend

class SynergyRowWidget(QFrame):
    '''
    Widget to show a single row of synergy
    '''

    def __init__(self, backend:Backend, page:int, row:int):
        super().__init__()
        self.setLineWidth(2)
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.backend = backend
        self.page = page
        self.row = row

        self.create_widgets()
        self.connect_signals()
        self.update_bonus()

    def create_widgets(self):
        layout = QHBoxLayout(self)


        self.level_label = QLabel("Level:")
        self.level_entry = QSpinBox()
        self.level_entry.setRange(0,1000000)
        self.level_entry.setMinimumWidth(75)
        self.level_entry.setValue(self.backend.synergy_pages[self.page].synergy_rows[self.row].level)
        
        self.point_label = QLabel("Points:")
        self.point_entry = QLineEdit()
        self.point_entry.setValidator(QRegularExpressionValidator(r"^-?\d+(?:\.\d+)?(?:[eE][+\-]?\d+)?$"))
        self.point_entry.setMinimumWidth(50)
        self.point_entry.setText(str(self.backend.synergy_pages[self.page].synergy_rows[self.row].current_points))

        self.bonus_label= QLabel("Bonus:")
        self.bonus_display = QLabel("")
        self.bonus_display.setMinimumWidth(75)

        layout.addWidget(self.level_label)
        layout.addWidget(self.level_entry)
        layout.addWidget(self.point_label)
        layout.addWidget(self.point_entry)
        layout.addWidget(self.bonus_label)
        layout.addWidget(self.bonus_display)


    def connect_signals(self):
        self.backend.synergy_pages[self.page].synergy_rows[self.row].bonus_changed.connect(self.update_bonus)
        self.backend.synergy_pages[self.page].synergy_rows[self.row].level_changed.connect(lambda p, r, l: self.level_entry.setValue(l))
        self.backend.synergy_pages[self.page].synergy_rows[self.row].points_changed.connect(lambda p, r, l: self.point_entry.setText(str(l)))
        self.level_entry.editingFinished.connect(lambda:self.backend.update_single_level(self.page, self.row, self.level_entry.value()))
        self.point_entry.editingFinished.connect(lambda:self.backend.update_single_point(self.page, self.row, float(self.point_entry.text())))
    
    def update_bonus(self):
        bonus = self.backend.synergy_pages[self.page].synergy_rows[self.row].current_bonus
        if bonus > 10000:
            self.bonus_display.setText(f"x{bonus:.1e}")
        elif bonus > 100:
            self.bonus_display.setText(f"x{bonus:.1f}")
        else:
            self.bonus_display.setText(f"x{bonus:.3f}")