from PySide6.QtWidgets import QFrame, QLabel, QSpinBox, QHBoxLayout, QDoubleSpinBox, QPushButton, QGridLayout, QCheckBox, QGroupBox
from PySide6.QtGui import QRegularExpressionValidator
from backend import Backend

class OtherInputsWidget(QFrame):
    '''
    Widget to input the remaining things necessary to optimize synergy
    '''
    def __init__(self, backend:Backend):
        super().__init__()
        self.setLineWidth(2)
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)

        self.backend = backend

        self.create_widgets()
        self.connect_signals()

        self.update_syn_power_display(self.backend.synergy_power)
        self.update_syn_progress_display(self.backend.synergy_progress)
        self.update_syn_energy_display(self.backend.synergy_energy)

    def create_widgets(self):
        layout = QHBoxLayout(self)

        #does the power/progress inputs first
        self.power_progress_groupbox = QGroupBox("Power, Progress, and Energy Inputs")
        power_progress_layout = QGridLayout(self.power_progress_groupbox)

        self.pot_checkbox = QCheckBox("Synergy pot used?")
        self.pot_checkbox.setChecked(self.backend.syn_pot_active)

        self.newb_progress_checkbox = QCheckBox("Newb Progress Trophy")
        self.newb_progress_checkbox.setChecked(self.backend.newb_progress_trophy)
        
        self.pro_progress_checkbox = QCheckBox("Pro Progress Trophy")
        self.pro_progress_checkbox.setChecked(self.backend.pro_progress_trophy)
        
        self.newb_power_checkbox = QCheckBox("Newb Power Trophy")
        self.newb_power_checkbox.setChecked(self.backend.newb_power_trophy)
        
        self.pro_power_checkbox = QCheckBox("Pro Power Trophy")
        self.pro_power_checkbox.setChecked(self.backend.pro_power_trophy)

        self.soul_power_checkbox = QCheckBox("Soul Synergy Power Purchase")
        self.soul_power_checkbox.setChecked(self.backend.syn_power_soul_purchase)
        
        self.newb_energy_checkbox = QCheckBox("Newb Energy Trophy")
        self.newb_energy_checkbox.setChecked(self.backend.newb_energy_trophy)
        
        self.pro_energy_checkbox = QCheckBox("Pro Energy Trophy")
        self.pro_energy_checkbox.setChecked(self.backend.pro_energy_trophy)

        self.adv_item_label = QLabel("Synergy Power from Adventure Items %")
        self.adv_item_entry = QDoubleSpinBox()
        self.adv_item_entry.setRange(0,10000000)
        self.adv_item_entry.setDecimals(2)
        self.adv_item_entry.setSuffix(" %")
        self.adv_item_entry.setMinimumWidth(75)
        self.adv_item_entry.setValue(self.backend.syn_power_adventure)

        self.adv_energy_item_label = QLabel("Synergy Energy from Adventure Items %")
        self.adv_energy_item_entry = QDoubleSpinBox()
        self.adv_energy_item_entry.setRange(0,10000000)
        self.adv_energy_item_entry.setDecimals(2)
        self.adv_energy_item_entry.setSuffix(" %")
        self.adv_energy_item_entry.setMinimumWidth(75)
        self.adv_energy_item_entry.setValue(self.backend.syn_energy_adventure)

        self.max_stage_label = QLabel("Max Adventure Stage")
        self.max_stage_entry = QSpinBox()
        self.max_stage_entry.setRange(0,100000)
        self.max_stage_entry.setMinimumWidth(75)
        self.max_stage_entry.setValue(self.backend.max_stage)
        
        self.syn_perks_label = QLabel("Page 3 Synergy Power Perks Level")
        self.syn_perks_entry = QSpinBox()
        self.syn_perks_entry.setRange(0,100000)
        self.syn_perks_entry.setMinimumWidth(75)
        self.syn_perks_entry.setValue(self.backend.syn_power_perk_level)
        
        self.pomos_level_label = QLabel("Pomos Synergy Power Levels")
        self.pomos_level_entry = QSpinBox()
        self.pomos_level_entry.setRange(0,100000)
        self.pomos_level_entry.setMinimumWidth(75)
        self.pomos_level_entry.setValue(self.backend.pomos_power_levels)

        power_progress_layout.addWidget(self.pot_checkbox,0,0)
        power_progress_layout.addWidget(self.soul_power_checkbox,1,0)
        power_progress_layout.addWidget(self.newb_energy_checkbox,2,0)
        power_progress_layout.addWidget(self.pro_energy_checkbox,3,0)
        power_progress_layout.addWidget(self.newb_progress_checkbox,0,1)
        power_progress_layout.addWidget(self.pro_progress_checkbox,1,1)
        power_progress_layout.addWidget(self.newb_power_checkbox,2,1)
        power_progress_layout.addWidget(self.pro_power_checkbox,3,1)
        power_progress_layout.addWidget(self.adv_item_label,0,2)
        power_progress_layout.addWidget(self.adv_item_entry,0,3)
        power_progress_layout.addWidget(self.adv_energy_item_label,1,2)
        power_progress_layout.addWidget(self.adv_energy_item_entry,1,3)
        power_progress_layout.addWidget(self.max_stage_label,2,2)
        power_progress_layout.addWidget(self.max_stage_entry,2,3)
        power_progress_layout.addWidget(self.syn_perks_label,3,2)
        power_progress_layout.addWidget(self.syn_perks_entry,3,3)
        power_progress_layout.addWidget(self.pomos_level_label,4,2)
        power_progress_layout.addWidget(self.pomos_level_entry,4,3)

        #does remaining script information and displays
        self.script_info_groupbox = QGroupBox("Other Script Information")
        script_info_layout = QGridLayout(self.script_info_groupbox)

        self.bd_label = QLabel("Baby Demons for Synergy")
        self.bd_entry = QSpinBox()
        self.bd_entry.setRange(0,1000000)
        self.bd_entry.setMinimumWidth(75)
        self.bd_entry.setValue(self.backend.total_bd)

        self.power_label = QLabel("Total Synergy Power")
        self.power_display = QLabel("")
        self.power_display.setStyleSheet("border: 1px solid black;")
        self.power_display.setMinimumWidth(75)

        self.progress_label = QLabel("Total Synergy Progress")
        self.progress_display = QLabel("")
        self.progress_display.setStyleSheet("border: 1px solid black;")
        self.progress_display.setMinimumWidth(75)

        self.energy_label = QLabel("Total Synergy Energy")
        self.energy_display = QLabel("")
        self.energy_display.setStyleSheet("border: 1px solid black;")
        self.energy_display.setMinimumWidth(75)

        self.save_settings_button = QPushButton("Save Input Settings")
        self.load_settings_button = QPushButton("Load Input Settings")

        script_info_layout.addWidget(self.bd_label, 0,0)
        script_info_layout.addWidget(self.bd_entry, 0,1)
        script_info_layout.addWidget(self.power_label, 1,0)
        script_info_layout.addWidget(self.power_display, 1,1)
        script_info_layout.addWidget(self.progress_label, 2,0)
        script_info_layout.addWidget(self.progress_display, 2,1)
        script_info_layout.addWidget(self.energy_label, 3,0)
        script_info_layout.addWidget(self.energy_display, 3,1)
        script_info_layout.addWidget(self.save_settings_button,4,0,1,2)
        script_info_layout.addWidget(self.load_settings_button,5,0,1,2)
        script_info_layout.setRowStretch(5,10)

        layout.addStretch()
        layout.addWidget(self.power_progress_groupbox)
        layout.addWidget(self.script_info_groupbox)
        layout.addStretch()
    
    def connect_signals(self):
       #inputs from user
       self.pot_checkbox.stateChanged.connect(lambda : self.backend.set_syn_pot_active(self.pot_checkbox.isChecked()))
       self.newb_progress_checkbox.stateChanged.connect(lambda : self.backend.set_newb_progress_trophy(self.newb_progress_checkbox.isChecked()))
       self.pro_progress_checkbox.stateChanged.connect(lambda : self.backend.set_pro_progress_trophy(self.pro_progress_checkbox.isChecked()))
       self.newb_power_checkbox.stateChanged.connect(lambda : self.backend.set_newb_power_trophy(self.newb_power_checkbox.isChecked()))
       self.pro_power_checkbox.stateChanged.connect(lambda : self.backend.set_pro_power_trophy(self.pro_power_checkbox.isChecked()))
       self.newb_energy_checkbox.stateChanged.connect(lambda : self.backend.set_newb_energy_trophy(self.newb_energy_checkbox.isChecked()))
       self.pro_energy_checkbox.stateChanged.connect(lambda : self.backend.set_pro_energy_trophy(self.pro_energy_checkbox.isChecked()))
       self.soul_power_checkbox.stateChanged.connect(lambda : self.backend.set_syn_power_soul_purchase(self.soul_power_checkbox.isChecked()))
       self.adv_item_entry.editingFinished.connect(lambda: self.backend.set_syn_power_adventure(self.adv_item_entry.value()))
       self.adv_energy_item_entry.editingFinished.connect(lambda: self.backend.set_syn_energy_adventure(self.adv_energy_item_entry.value()))
       self.max_stage_entry.editingFinished.connect(lambda: self.backend.set_max_stage(self.max_stage_entry.value()))
       self.syn_perks_entry.editingFinished.connect(lambda: self.backend.set_syn_power_perk_level(self.syn_perks_entry.value()))
       self.pomos_level_entry.editingFinished.connect(lambda: self.backend.set_pomos_power_levels(self.pomos_level_entry.value()))
       self.bd_entry.editingFinished.connect(lambda: self.backend.set_total_bd(self.bd_entry.value()))
       #updates overall multipliers
       self.backend.synergy_progress_changed.connect(self.update_syn_progress_display)
       self.backend.synergy_power_changed.connect(self.update_syn_power_display)
       self.backend.synergy_energy_changed.connect(self.update_syn_energy_display)
       #button clicks
       self.save_settings_button.clicked.connect(self.backend.save_json_file)
       self.load_settings_button.clicked.connect(self.backend.load_from_json_file)

    def update_syn_power_display(self, value:float):
        if value >1e6:
            self.power_display.setText(f"{value:.2e}")
        else:
            self.power_display.setText(f"{value:.2f}")

    def update_syn_progress_display(self, value:float):
        self.progress_display.setText(f"{value:.2f}")

    def update_syn_energy_display(self, value:float):
        self.energy_display.setText(f"{value:.2f}")