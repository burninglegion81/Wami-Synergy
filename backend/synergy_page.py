from typing import Dict, List, Tuple
import numpy as np
from PySide6.QtCore import  QObject

from  backend.synergy_row import SynergyRow


class SynergyPage(QObject):
    '''
    Class to hold a single page of synergy.
    This has a dictionary holding each of the underlying synergy rows, and has some extra functions related to 
    helping out optimizations
    '''
    

    def __init__(self, page:int, initial_levels:list, initial_points:list):
        super().__init__()
        self.page = page
        self.synergy_rows:Dict[int, SynergyRow] = {}

        for i in range(7):
            self.synergy_rows[i+1] = SynergyRow(self.page, i+1, initial_levels[i], initial_points[i])

    def update_level(self, row:int, new_level:int):
        '''
        pass through function to update the level for a single row
        '''
        self.synergy_rows[row].set_level(new_level)

    def update_all_levels(self, all_levels:list):
        for i in range(7):
            self.synergy_rows[i+1].set_level(all_levels[i])
    def update_all_points(self, all_points:list):
        for i in range(7):
            self.synergy_rows[i+1].set_current_points(all_points[i])

    def get_all_gains_per_tick(self, baby_demon_array:List[int], progress_mult:float, power_mult:float):
        '''
        Function to get all gains for a single page of synergy.
        As a note for future reference, there are 10 ticks/second, so 36000 ticks in an hour
        Params:
            -----
            baby_demon_array: list of baby demons to apply to each row of synergy
            progress_mult: progress mutliplier
            power_mult: power multiplier
        '''
        number_rows = len(baby_demon_array)
        gains_array = np.zeros(number_rows)
        speed_capped_array = [False] * number_rows
        overcapped_array = np.zeros(number_rows)
        for i in range(len(baby_demon_array)):
            gains, consume, speed_capped, overcapped = self.synergy_rows[i+1].calculate_gains_per_tick(baby_demon_array[i], progress_mult, power_mult)
            gains_array[i] = gains 
            if i != 0:
                gains_array[i-1] = gains_array[i-1] - consume
            speed_capped_array[i] = speed_capped
            overcapped_array[i] = overcapped
        return gains_array, speed_capped_array, overcapped_array
    
    def get_all_syn_energy_per_tick(self, baby_demon_array:List[int], progress_mult:float):
        '''
        Function to get all syn energy for a single page of synergy.
        As a note for future reference, there are 10 ticks/second, so 36000 ticks in an hour
        Params:
            -----
            baby_demon_array: list of baby demons to apply to each row of synergy
            progress_mult: progress mutliplier
        '''
        number_rows = len(baby_demon_array)
        speed_capped_array = [False] * number_rows
        overcapped_array = np.zeros(number_rows)
        syn_energy_total = 0
        for i in range(len(baby_demon_array)):
            syn_energy_row, speed_capped, overcapped = self.synergy_rows[i+1].calculate_syn_energy_per_tick(baby_demon_array[i], progress_mult)
            syn_energy_total += syn_energy_row
            speed_capped_array[i] = speed_capped
            overcapped_array[i] = overcapped
        return syn_energy_total, speed_capped_array, overcapped_array
    
    def get_min_tick(self, row:int, baby_demon_available:int, progress_mult:int, power_mult:int) -> Tuple[int, float, float]:
        '''
        Given a row and number of BD to use, returns the number of BD needed to not overcap that row, as well as the
        gains/tick resulting from this distribution
        '''
        required_bd = self.synergy_rows[row].calculate_bd_for_min_tick(baby_demon_available, progress_mult)
        gains_tick,_, _, _ = self.synergy_rows[row].calculate_gains_per_tick(required_bd, progress_mult, power_mult)
        return required_bd, gains_tick


    def get_all_levels(self):
        return [x.level for _, x in self.synergy_rows.items()]
    def get_all_points(self):
        return [x.current_points for _, x in self.synergy_rows.items()]