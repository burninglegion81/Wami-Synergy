from PySide6.QtCore import Signal, Slot, Property as QProperty, QObject
import numpy as np
import math
from backend import SynergyPage, SynergyRow
from typing import Dict, List
import time
import json
import os
from typing import Optional

if os.name == "nt":
    JSON_SAVE_LOCATION = os.path.join(os.getenv('APPDATA'), "WAMI Optimizer", "synergy_settings.json")
elif os.name == "posix":
    JSON_SAVE_LOCATION = os.path.join(os.getenv("HOME"), ".wami_optimizer", "synergy_settings.json")

class Backend(QObject):
    '''
    Backend class to hold the state of different variables, such as synergy levels, current synergy power, etc.
    This will also perform the optimization using these given inputs.
    The optimization options are:
        Single row:
            maximizes the gains on a single row
        Flat distribution:
            tries to make all of the synergy gains/hour the same, up to the inputted row
        Synergy Energy:
            tries to maximize synergy energy gains on a single page
                this basically just min ticks everything, starting from the first row and moving upwards

    Params:
        ----
        current_levels_page_X: np.ndarray of the current levels for each page of synergy, from row 1 to row 7
        current_points_page_X: np.ndarray of the current points for each page of synergy, from row 1 to row 7
        total_bd: int of how many BD the user current has
        synergy_input_dict: dictionary of various inputs that impact synergy progress or speed
    '''

    def __init__(self, current_levels_page_1: np.ndarray, current_levels_page_2: np.ndarray, current_levels_page_3:np.ndarray,
                 current_points_page_1:np.ndarray, current_points_page_2:np.ndarray, current_points_page_3:np.ndarray,
                 total_bd:int, synergy_inputs_dict:dict):
        super().__init__()
         #dictionary for the base progress of each row of synergy
        #sets up the current levels
        self.synergy_pages:Dict[int, SynergyPage] = {}
        self.synergy_pages[1] = SynergyPage(1, current_levels_page_1, current_points_page_1)
        self.synergy_pages[2] = SynergyPage(2, current_levels_page_2, current_points_page_2)
        self.synergy_pages[3] = SynergyPage(3, current_levels_page_3, current_points_page_3)
    
        self.total_bd = total_bd
        #processes the inputs dict
        self.syn_pot_active:bool = synergy_inputs_dict["Active Syn Pot"]
        self.newb_progress_trophy:bool = synergy_inputs_dict["Newb Progress Trophy"]
        self.pro_progress_trophy:bool = synergy_inputs_dict["Pro Progress Trophy"]
        self.newb_power_trophy:bool = synergy_inputs_dict["Newb Power Trophy"]
        self.pro_power_trophy:bool = synergy_inputs_dict["Pro Power Trophy"]
        self.syn_power_soul_purchase:bool = synergy_inputs_dict["Soul Power Purchase"]
        self.syn_power_adventure:float = synergy_inputs_dict["Adventure Power %"]
        self.syn_power_perk_level:int = synergy_inputs_dict["Syn Power Perks Level"]
        self.max_stage:int = synergy_inputs_dict["Max Stage"]
        self.pomos_power_levels:int = synergy_inputs_dict["Pomos Power Levels"]

        self._synergy_progress:float = 0
        self._synergy_power:float = 0
        self.update_potion_bonus()
        self.calculate_synergy_progress()
        self.calculate_synergy_power()

    def calculate_synergy_progress(self):
        '''
        Function to calculate the current total amount of synergy progress multiplier
        '''
        progress = 1
        #trophies calculation
        #newb is .05, pro is .1
        progress = progress* (1 + self.newb_progress_trophy*.05 + self.pro_progress_trophy*.1)
        #potion calculation
        progress = progress * ( 1 + self.syn_pot_active * (self.potion_bonus-1))

        self.set_synergy_progress(progress)

    @Slot()
    def calculate_synergy_power(self):
        '''
        Function to calculate the current total amount of synergy power multiplier
        '''
        power = 1
        #potion calculation, base effectiveness of 50%
        power = power * (1 + self.syn_pot_active *(self.potion_bonus-1))
        #trophies
        power = power* (1 + self.newb_power_trophy*.05 + self.pro_power_trophy*.1)
        #soul purchase, .25001 due to rounding things
        power = power * (1 + self.syn_power_soul_purchase * .25001)
        #adventure items, need to convert from %
        power = power  * (1 + self.syn_power_adventure/100)
        #perks
        #starts off giving 1%, and grows linearly
        power = power * (1 + (self.syn_power_perk_level) * (self.syn_power_perk_level + 1)/2/100)
        #syn v2
        power = power * math.pow(1.005, self.pomos_power_levels)
        self.set_syngery_power(power)

    def update_potion_bonus(self):
        '''
        Gets the increase to potion effectiveness based off of max stage.
        For every 100 stages exactly above 400, potion effectiveness exponentially increases by 20% each time
        '''
        self.potion_bonus =  .5 * math.pow(1.2, math.floor((self.max_stage-400)/100)) + 1

    synergy_progress_changed = Signal(float)
    def get_synergy_progress(self)->float:
        return self._synergy_progress
    def set_synergy_progress(self, value:float):
        if value != self.synergy_progress:
            self._synergy_progress = value
            self.synergy_progress_changed.emit(self.synergy_progress)
    synergy_progress = QProperty(float, get_synergy_progress, set_synergy_progress, notify=synergy_progress_changed)

    synergy_power_changed = Signal(float)
    def get_synergy_power(self)->float:
        return self._synergy_power
    def set_syngery_power(self, value:float):
        if value != self.synergy_power:
            self._synergy_power = value
            self.synergy_power_changed.emit(self.synergy_power)
    synergy_power = QProperty(float, get_synergy_power, set_syngery_power, notify=synergy_power_changed)

    def update_single_level(self, page:int, row:int, new_level:int):
        #pass through function to update a single rows level
        self.synergy_pages[page].synergy_rows[row].set_level(new_level)
    def update_single_point(self, page:int, row:int, new_points:float):
        #pass through function to update a single rows points
        self.synergy_pages[page].synergy_rows[row].set_current_points(new_points)

    #setters for other synergy inputs
    def set_total_bd(self, value:int):
        self.total_bd = value
    def set_syn_pot_active(self, value:bool):
        self.syn_pot_active = value
        self.calculate_synergy_power()
        self.calculate_synergy_progress()
    def set_newb_progress_trophy(self, value:bool):
        self.newb_progress_trophy = value
        self.calculate_synergy_progress()
    def set_pro_progress_trophy(self, value:bool):
        if value != self.pro_progress_trophy:
            self.pro_progress_trophy = value
            self.calculate_synergy_progress()
    def set_newb_power_trophy(self, value:bool):
        if value != self.newb_power_trophy:
            self.newb_power_trophy = value
            self.calculate_synergy_power()
    def set_pro_power_trophy(self, value:bool):
        if value != self.pro_power_trophy:
            self.pro_power_trophy = value
            self.calculate_synergy_power()
    def set_syn_power_soul_purchase(self, value:bool):
        if value != self.syn_power_soul_purchase:
            self.syn_power_soul_purchase = value
            self.calculate_synergy_power()
    def set_syn_power_adventure(self, value:float):
        if value != self.syn_power_adventure:
            self.syn_power_adventure = value
            self.calculate_synergy_power()
    def set_syn_power_perk_level(self, value:int):
        if value != self.syn_power_perk_level:
            self.syn_power_perk_level = value
            self.calculate_synergy_power()
    def set_max_stage(self, value:int):
        if value != self.max_stage:
            self.max_stage = value
            self.calculate_synergy_power()
            self.calculate_synergy_progress()
    def set_pomos_power_levels(self, value:int):
        if value != self.pomos_power_levels:
            self.pomos_power_levels = value
            self.calculate_synergy_power()
            

    def save_json_file(self):
        '''
        Saves the settings to a json file in appdata/roaming
        '''
        dump = {}
        dump["page 1 levels"] = self.synergy_pages[1].get_all_levels() 
        dump["page 2 levels"] = self.synergy_pages[2].get_all_levels() 
        dump["page 3 levels"] = self.synergy_pages[3].get_all_levels() 
        dump["page 1 points"] = self.synergy_pages[1].get_all_points() 
        dump["page 2 points"] = self.synergy_pages[2].get_all_points() 
        dump["page 3 points"] = self.synergy_pages[3].get_all_points() 
        dump["total bd"] = self.total_bd
        inputs_dict = {}
        inputs_dict["Active Syn Pot"] = self.syn_pot_active
        inputs_dict["Newb Progress Trophy"] = self.newb_progress_trophy
        inputs_dict["Pro Progress Trophy"] = self.pro_progress_trophy
        inputs_dict["Newb Power Trophy"] = self.newb_power_trophy
        inputs_dict["Pro Power Trophy"] = self.pro_power_trophy
        inputs_dict["Soul Power Purchase"] = self.syn_power_soul_purchase
        inputs_dict["Adventure Power %"] = self.syn_power_adventure
        inputs_dict["Syn Power Perks Level"] = self.syn_power_perk_level
        inputs_dict["Max Stage"] = self.max_stage
        inputs_dict["Pomos Power Levels"] = self.pomos_power_levels
        dump["inputs dict"] = inputs_dict
        if not os.path.exists(os.path.split(JSON_SAVE_LOCATION)[0]):
            os.makedirs(os.path.split(JSON_SAVE_LOCATION)[0])

        with open(JSON_SAVE_LOCATION, "w", encoding='utf-8') as f:
            json.dump(dump, f, indent=1)

    @staticmethod
    def load_json_file():
        '''
        class method to load in the json file, so the parameers can be passed in at init
        '''
        if os.path.exists(JSON_SAVE_LOCATION):
            with open(JSON_SAVE_LOCATION) as f:
                j = json.load(f)
            return j
        else:
            return None
        
    def load_from_json_file(self):
        '''
        Reloads the previously saved settings
        '''
        synergy_input = Backend.load_json_file()
        if synergy_input is None:
            return
        level_1 = synergy_input["page 1 levels"] 
        level_2 = synergy_input["page 2 levels"] 
        level_3 = synergy_input["page 3 levels"]  
        point_1 = synergy_input["page 1 points"]  
        point_2 = synergy_input["page 2 points"] 
        point_3 = synergy_input["page 3 points"]
        bd = synergy_input["total bd"] 
        inputs = synergy_input["inputs dict"] 

        self.synergy_pages[1].update_all_levels(level_1)
        self.synergy_pages[2].update_all_levels(level_2)
        self.synergy_pages[3].update_all_levels(level_3)
        self.synergy_pages[1].update_all_points(point_1)
        self.synergy_pages[2].update_all_points(point_2)
        self.synergy_pages[3].update_all_points(point_3)
        self.set_total_bd(bd)

        
        self.set_syn_pot_active(inputs["Active Syn Pot"])
        self.set_newb_progress_trophy(inputs["Newb Progress Trophy"])
        self.set_pro_progress_trophy(inputs["Pro Progress Trophy"])
        self.set_newb_power_trophy( inputs["Newb Power Trophy"])
        self.set_pro_power_trophy(inputs["Pro Power Trophy"])
        self.set_syn_power_soul_purchase(inputs["Soul Power Purchase"])
        self.set_syn_power_adventure( inputs["Adventure Power %"])
        self.set_syn_power_perk_level( inputs["Syn Power Perks Level"])
        self.set_max_stage( inputs["Max Stage"])
        self.set_pomos_power_levels( inputs["Pomos Power Levels"])



    ### Optimization Functions

    def maximize_one_row(self, page:int, row:int):
        '''
        Greedy algorithm to maximize the gains on one row.
        General algo is:
            start by assigning all BD to the desired row.
            Then, iteratively move BD to the minimum row. It will always move BD from the row after the minimum row to 
                the minimum row. This way, we should always keep as many BD as possible in the maximization row, since it will
                only pull what is necessary.
            If any row is speed capped (other than row 1), we can move that many BD down instead of 1
        
        Caps this iteration at max 5x the number of BD
        Returns:
            bd_array: bd distribution to maximize the desired row
            gains_array: the final gains/tick of the distribution
            syn_energy_per_tick: the sum of synergy energy gained per tick
        '''
        start_time = time.time()
        bd_array = np.zeros(row, dtype=int)
        bd_array[row-1] = self.total_bd
        gains_array, speed_capped_array, overcapped_array = self.synergy_pages[page].get_all_gains_per_tick(bd_array, self.synergy_progress, self.synergy_power)
        max_iter = 100*self.total_bd
        iter = 0
        
        while np.any(gains_array < 0) and iter < max_iter:
            iter += 1
            min_row = np.argmin(gains_array)
            max_row = min_row+1
                    
            if speed_capped_array[max_row]:
                bd_array[max_row] -= overcapped_array[max_row]
                bd_array[min_row] += overcapped_array[max_row]
            else:
                bd_array[max_row] -= 1
                bd_array[min_row] += 1
            gains_array, speed_capped_array, overcapped_array = self.synergy_pages[page].get_all_gains_per_tick(bd_array, self.synergy_progress, self.synergy_power)
        
        print(f"Maximization finished after {iter+1} iterations, and took {time.time() - start_time} s")
        syn_energy, _, _ = self.synergy_pages[page].get_all_syn_energy_per_tick(bd_array, self.synergy_progress)
        return bd_array, gains_array, syn_energy
    
    
    def flat_up_to_row(self, page:int, row:int, bd:Optional[int] = None):
        '''
        Greedy algorithm to try to keep gains "flat" up to a certain row.
        This tries to get all of the gains/hour roughly equal
        General algo is:
            put all BD into the final row we want to be flat
            find the row with the smallest gains/hour
            take 1 (or overcapped) bd from the following row, and move it into that row
            repeat until the final row we care about is the smallest gains/hour
        
        Caps this iteration at max 10x the number of BD
        Params:
            page: page of synergy to run, 1 indexed
            row: row of synergy to run, 1 indexed
            bd: the number of bd to optimize with, defaults to total bd
        Returns:
            bd_array: bd distribution to maximize the desired row
            gains_array: the final gains/tick of the distribution
        '''
        start_time = time.time()
        bd_array = np.zeros(row, dtype=int)
        bd_array[row-1] = self.total_bd if bd is None else bd
        gains_array, speed_capped_array, overcapped_array = self.synergy_pages[page].get_all_gains_per_tick(bd_array, self.synergy_progress, self.synergy_power)
        max_iter = 10*self.total_bd
        iter = 0
        

        while iter < max_iter:
            iter += 1
            min_row = np.argmin(gains_array)
            if min_row ==  row-1:
                #if the min row is ever the first one, stop there
                break
            take_row = min_row-1 #takes BD from the previous row
            previous_bd = bd_array
            if speed_capped_array[take_row]:
                bd_array[take_row] -= overcapped_array[take_row]
                bd_array[min_row] += overcapped_array[take_row]
            else:
                bd_array[take_row] -= 1
                bd_array[min_row] += 1

            gains_array, speed_capped_array, overcapped_array = self.synergy_pages[page].get_all_gains_per_tick(bd_array, self.synergy_progress, self.synergy_power)


        bd_array = previous_bd
        print(f"Maximization finished after {iter+1} iterations, and took {time.time() - start_time} s")
        gains_array, speed_capped_array, overcapped_array = self.synergy_pages[page].get_all_gains_per_tick(bd_array, self.synergy_progress, self.synergy_power)
        
        syn_energy, _, _ = self.synergy_pages[page].get_all_syn_energy_per_tick(bd_array, self.synergy_progress)
        return bd_array, gains_array, syn_energy
    
    def see_maximization_one_page(self, page:int):
        '''
        Optimization to show the user what gains are possible on a single page if synergy, if they were
        to maximize any single row.
        Returns:
            bd_array: array of 0 legth 7
            gains_array: the final gains/tick for each row
            syn_energy_per_tick: 0
        '''
        start_time = time.time()
        gains_array = np.zeros(7)
        for i in range(7):
            _, gains_row, _ = self.maximize_one_row(page, i+1)
            gains_array[i] = gains_row[i]
        print(f"Page {page} optimization took {time.time() - start_time} s")
        
        return np.zeros(7, dtype=int), gains_array, 0