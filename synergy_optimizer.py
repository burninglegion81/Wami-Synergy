from backend import Backend
from frontend.main_screen import MainScreen
import sys

from PySide6.QtWidgets import QApplication


synergy_input  = Backend.load_json_file()
if synergy_input is not None:
    level_1 = synergy_input["page 1 levels"] 
    level_2 = synergy_input["page 2 levels"] 
    level_3 = synergy_input["page 3 levels"]  
    point_1 = synergy_input["page 1 points"]  
    point_2 = synergy_input["page 2 points"] 
    point_3 = synergy_input["page 3 points"]
    bd = synergy_input["total bd"] 
    inputs = synergy_input["inputs dict"] 
    backend = Backend(level_1, level_2, level_3, point_1, point_2, point_3, bd, inputs)
else:
    inputs_dict = {
        
            "Active Syn Pot":False,
            "Newb Progress Trophy":False,
            "Pro Progress Trophy":False,
            "Newb Power Trophy":False,
            "Pro Power Trophy":False,
            "Soul Power Purchase":False,
            "Adventure Power %":0,
            "Syn Power Perks Level":0,
            "Max Stage":400,
            "Pomos Power Levels":0
    }
    backend = Backend([1]*7, [1]*7, [1]*7, [0]*7, [0]*7, [0]*7, 40, inputs_dict)

app = QApplication(sys.argv)
QApplication.setApplicationName("Synergy Optimizer")
QApplication.setApplicationDisplayName("Synergy Optimizer")

main = MainScreen(backend)
main.show()
app.exec()