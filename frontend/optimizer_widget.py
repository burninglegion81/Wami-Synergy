from PySide6.QtWidgets import QWidget, QLabel, QSpinBox, QHBoxLayout, QDoubleSpinBox, QPushButton, QGridLayout, QCheckBox, QGroupBox, QRadioButton, QButtonGroup,\
        QComboBox
from PySide6.QtGui import QRegularExpressionValidator
from backend import Backend
from frontend.synergy_page_widget import SynergyPageWidget
from typing import List

class OptimizerWidget(QWidget):
    '''
    Widget to input the remaining things necessary to optimize synergy
    '''
    def __init__(self, backend:Backend):
        super().__init__()

        self.backend = backend

        self.create_widgets()
        self.connect_signals()

        self.page_dropdown.setCurrentText("1")
        self.row_dropdown.setCurrentIndex(0)
    
    def create_widgets(self):
        layout = QGridLayout(self)
        
        #optimizer setup information gets done first
        self.setup_groupbox = QGroupBox("Optimization Settings")
        setup_layout = QGridLayout(self.setup_groupbox)

        self.page_label = QLabel("Page to Optimize")
        self.page_dropdown = QComboBox()
        self.page_dropdown.addItems(["1", "2", "3"])
        self.page_dropdown.setCurrentText("2")

        self.row_label = QLabel("Row To Optimize")
        self.row_dropdown = QComboBox()
        self.row_dropdown.addItems([str(x+1) for x in range(7)])

        self.hours_label = QLabel("Hours to Run Synergy for")
        self.hours_entry = QSpinBox()
        self.hours_entry.setRange(0,1000)
        self.hours_entry.setMinimumWidth(75)
        self.hours_entry.setValue(24)

        self.run_button = QPushButton("Run Optimization")

        self.method_group = QButtonGroup()
        self.method_group.setExclusive(True)
        self.method_label = QLabel("Choose Optimization Method Below")
        
        self.max_button = QRadioButton("Maximize gains on one row")
        self.flat_button = QRadioButton("Make gains equal up to row")
        self.max_page_button = QRadioButton("Show potential gains on one page")
        #button to do min tick on one row, flat below it
        self.min_page_button = QRadioButton("See BD required to min tick each row on one page")
        #button to maximuze synergy energy gains/hour
        self.method_group.addButton(self.max_button)
        self.method_group.addButton(self.flat_button)
        self.method_group.addButton(self.max_page_button)

        self.method_group.addButton(self.min_page_button)

        self.max_button.setChecked(True)
        
        setup_layout.addWidget(self.page_label,0,0)
        setup_layout.addWidget(self.page_dropdown,0,1)
        setup_layout.addWidget(self.row_label,1,0)
        setup_layout.addWidget(self.row_dropdown,1,1)
        setup_layout.addWidget(self.hours_label,2,0)
        setup_layout.addWidget(self.hours_entry,2,1)
        setup_layout.addWidget(self.run_button,3,0,1,2)
        setup_layout.addWidget(self.method_label,4,0,1,2)
        setup_layout.addWidget(self.max_button,5,0,1,2)
        setup_layout.addWidget(self.flat_button,6,0,1,2)
        setup_layout.addWidget(self.max_page_button,7,0,1,2)
        setup_layout.addWidget(self.min_page_button, 9,0,1,2)

        #now we display the results of the script optimization
        self.results_groupbox = QGroupBox("Optimization Results")
        results_layout = QGridLayout(self.results_groupbox)

        #sets up the row names
        self.name_label = QLabel("Row Name")
        results_layout.addWidget(self.name_label,0,0)
        self.name_widgets:List[QLabel] = []
        for i in range(7):
            label = QLabel("test")
            label.setStyleSheet("border: 1px solid black;")
            label.setMinimumWidth(75)
            self.name_widgets.append(label)
            results_layout.addWidget(label, i+1,0)

        #sets up the BD displays
        self.bd_label = QLabel("Optimized BD")
        results_layout.addWidget(self.bd_label,0,1)
        self.bd_widgets:List[QLabel] = []
        for i in range(7):
            label = QLabel("")
            label.setStyleSheet("border: 1px solid black;")
            label.setMinimumWidth(75)
            self.bd_widgets.append(label)
            results_layout.addWidget(label, i+1,1)
            
        #sets up the gains/hour displays
        self.gains_hour_label = QLabel("Point Gains/Hour")
        results_layout.addWidget(self.gains_hour_label,0,2)
        self.gains_hour_widgets:List[QLabel] = []
        for i in range(7):
            label = QLabel("")
            label.setStyleSheet("border: 1px solid black;")
            label.setMinimumWidth(75)
            self.gains_hour_widgets.append(label)
            results_layout.addWidget(label, i+1,2)
            
        #sets up the final points displays
        self.final_points_label = QLabel("Final Points")
        results_layout.addWidget(self.final_points_label,0,3)
        self.final_points_widgets:List[QLabel] = []
        for i in range(7):
            label = QLabel("")
            label.setStyleSheet("border: 1px solid black;")
            label.setMinimumWidth(75)
            self.final_points_widgets.append(label)
            results_layout.addWidget(label, i+1,3)
            
        #sets up the final bonus displays
        self.final_bonus_label = QLabel("Final Bonus")
        results_layout.addWidget(self.final_bonus_label,0,4)
        self.final_bonus_widgets:List[QLabel] = []
        for i in range(7):
            label = QLabel("")
            label.setStyleSheet("border: 1px solid black;")
            label.setMinimumWidth(75)
            self.final_bonus_widgets.append(label)
            results_layout.addWidget(label, i+1,4)

        #sets up the multiplicative gain displays
        self.rel_gains_label = QLabel("Relative Bonus Gains")
        results_layout.addWidget(self.rel_gains_label,0,5)
        self.rel_gains_widgets:List[QLabel] = []
        for i in range(7):
            label = QLabel("")
            label.setStyleSheet("border: 1px solid black;")
            label.setMinimumWidth(75)
            self.rel_gains_widgets.append(label)
            results_layout.addWidget(label, i+1,5)

        results_layout.setRowStretch(10,10)

        #sets up synergy energy gains
        self.syn_energy_label = QLabel("Synergy Energy Gains")
        self.syn_energy_display = QLabel("")
        self.syn_energy_display.setStyleSheet("border: 1px solid black;")
        self.syn_energy_display.setMinimumWidth(75)

        results_layout.addWidget(self.syn_energy_label,9,0)
        results_layout.addWidget(self.syn_energy_display,9,1)

        layout.addWidget(self.setup_groupbox,0,0)
        layout.addWidget(self.results_groupbox,0,1)
        layout.setRowStretch(0,0)
        layout.setRowStretch(1,1000)
    
    def connect_signals(self):
        self.page_dropdown.currentTextChanged.connect(self.update_row_displays)
        self.run_button.clicked.connect(self.run_optimization)
    
    def update_row_displays(self, new_page:str):
        '''
        Function to update the displays of the row names whenever the page number changes
        '''
        new_page = int(new_page)
        names = SynergyPageWidget.names_dict[new_page]
        for count, label in enumerate(self.name_widgets):
            label.setText(names[count])

    def run_optimization(self):
        '''
        Actually runs the optimization
        '''
        selected_button = self.method_group.checkedButton()
        page = int(self.page_dropdown.currentText())
        row = int(self.row_dropdown.currentText())
        if selected_button == self.max_button:
            bd, gains_tick, syn_energy = self.backend.maximize_one_row(page, row)
        elif selected_button == self.flat_button:
            bd, gains_tick, syn_energy = self.backend.flat_up_to_row(page, row)
        elif selected_button == self.max_page_button:
            bd, gains_tick, syn_energy = self.backend.see_maximization_one_page(page)
        elif selected_button == self.min_page_button:
            bd, gains_tick, syn_energy = self.backend.see_min_tick_one_page(page)

        self.update_results(bd, gains_tick, syn_energy)
    
    def text_helper(self, value:float) -> str:
        '''
        Helper function to display values in a repeatable way
        '''
        if value > 1e6:
            return f"{value:.2e}"
        elif value > 100:
            return f"{value:.1f}"
        else:
            return f"{value:.3f}"

    def update_results(self, bd:List[int], gains_tick:List[float], syn_energy:float):
        '''
        standaridzed function to upadte the displays after an optimization runs
        '''
        optimized_rows = len(bd)
        selected_page=  int(self.page_dropdown.currentText())
        for i in range(7):
            if i < optimized_rows:
                self.bd_widgets[i].setText(f"{bd[i]:d}")
                gain_hour = gains_tick[i]*36000
                self.gains_hour_widgets[i].setText(self.text_helper(gain_hour))
                final_points = gain_hour * self.hours_entry.value() + self.backend.synergy_pages[selected_page].synergy_rows[i+1].current_points
                self.final_points_widgets[i].setText(self.text_helper(final_points))
                final_bonus = self.backend.synergy_pages[selected_page].synergy_rows[i+1].calculate_bonus(final_points)
                self.final_bonus_widgets[i].setText(self.text_helper(final_bonus))
                current_bonus = self.backend.synergy_pages[selected_page].synergy_rows[i+1].current_bonus
                relative_gains = final_bonus/current_bonus
                self.rel_gains_widgets[i].setText(f"x{relative_gains:.2f}")
            else:
                self.bd_widgets[i].setText("")
                self.gains_hour_widgets[i].setText("")
                self.final_points_widgets[i].setText("")
                self.final_bonus_widgets[i].setText("")
                self.rel_gains_widgets[i].setText("")
        #sets synergy energy
        ticks_total = 36000*self.hours_entry.value()
        self.syn_energy_display.setText(f"{syn_energy*ticks_total:.1f}")

        return
