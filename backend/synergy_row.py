import numpy as np
import math
from PySide6.QtCore import Signal, Slot, Property as QProperty, QObject
import time

class SynergyRow(QObject):
    '''
    Class to represent a single row of synergy. This is to simplify getting logic for getting progress, 
    and doing various things
    '''
    
    base_progress_dict = {
        1: np.array([10000, 20000, 35000, 55000, 80000, 110000, 150000]),
        2: np.array([20000, 40000, 70000, 110000, 160000, 220000, 300000]),
        3: np.array([50000, 100000, 175000, 280000, 400000, 550000, 750000])
    } #dict to hold the base progress values for each page/row

    bonus_divisors_dict = {
        1:[1,1,1,1,1,2,2],
        2: [1,1,1,2,2,2,2],
        3: [1,2,2,2,2,4,4]
    } #divisors for each page and row of synergy. All rows of synergy have very similar 
    #formulas to calculate the bonus, with these divisors applied after the fact to let
    #the later pages/rows scale worse

    log_scaling_array = [6, 5.6, 5.2, 4.8, 4.4, 4, 3.5] #log scaling for each row of synergy
    #the higher the log scaling, the more you need to increase your points to double a bonus


    level_changed = Signal(int, int, int) #emits page, row, new level
    points_changed = Signal(int, int, float) #emits page, row, new points
    bonus_changed = Signal(int, int, float) #emits page, row, new bonus
    
    def __init__(self, page:int, row: int, current_level:int, current_points:float):
        super().__init__()
        self.level = current_level
        self.page = page
        self.row = row

        self.base_progress = self.base_progress_dict[page][row-1]
        self.divisor = self.bonus_divisors_dict[page][row-1]
        self.log_scaling = self.log_scaling_array[row-1]
        self.current_progress = 0

        self.synergy_energy_per_fill = np.sum(range(1,row+1))

        self.current_points = current_points
        self.current_bonus = self.calculate_bonus(self.current_points)

        self.update_current_progress()

    def update_current_progress(self):
        '''
        Actually synergy progress requirement has a minimum value of 1/10 of the base progress
        Otherwise, the current progress requirement is reduced by 10 for every level
        '''
        self.current_progress = max(self.base_progress/10, self.base_progress-(self.level-1)*10)
                                    
    def set_level(self, level:int):
        self.level = level
        self.level_changed.emit(self.page, self.row, self.level)
        self.update_current_progress()

    def calculate_gains_per_tick(self, number_bd:int, progress_mult:float, power_mult:float):
        '''
        calculates the results of a certain number of baby demons being applied to this row of synergy.
        As a note, each row of synergy will consume 2x its level every time it finishes from the row before
        Returns:
            ----
            gains_per_tick: how much synergy points will result from a single tick with this number of bds
            consume_per_tick: how much synergy points will be consumed from the previous row with this nuymber of bds
            speed_capped: bool showing if this is speed capped
            speed_capped_removal: if speed capped is true, this is how many BD we are overcapping by
        '''
        points_per_tick = number_bd * progress_mult
        if points_per_tick > self.current_progress / 10:
            #if the points per tick is more than 1/10th of the requirement, we do a min tick calculation
            ticks_to_fill = math.ceil(self.current_progress/points_per_tick) #gets how maany ticks it's currently taking to fill the bar
            #calculates the actual gains we're getting
            gains_per_tick = self.level * power_mult /ticks_to_fill
            consume_per_tick = self.level * 2 / ticks_to_fill

            #calculate the required BD to get the actual number of ticks we want as 
            #the "effective" progress requirement (current progress divided by progress multi), divided 
            #by the number of ticks we're taking. This is ceiling'd
            required_bd = math.ceil((self.current_progress/progress_mult)/ticks_to_fill)
            overcapped_bd = number_bd - required_bd
            return gains_per_tick, consume_per_tick, True, overcapped_bd
        else:
            #otherwise, we dont care about the speed capping impacts
            gains_per_tick = points_per_tick * self.level * power_mult / self.current_progress
            consume_per_tick = points_per_tick * self.level * 2 / self.current_progress
            return gains_per_tick, consume_per_tick, False, 0
        
        
    def calculate_bonus(self, points:float):
        '''
        Calculates the bonus that would give applied from this row of synergy based off of 
        an input number of points.
        Below 1000, this scales linearly with points. I.e., if there is a divisor of 1,
        then a points of 100 would give 100/1000 or .1 (10%) bonus, 500 would give 50%, etc.
        Above 1000 points, the scaling is determined mostly by the log scaling.
        Earlier rows scale more "harshly", i.e. with a log scaling of 6.5, a row needs 6.5x points
        to double its bonus.
        A log scaling of 5 requires 5x the points to 2x the bonus, etc

        This returns the multiplicative bonus, i.e. if the game would display 50%, this returns 1.5.
        If the game would display 100%, this displays 2, etc
        '''
        if points <=1000:
                return points/1000/self.divisor + 1
        else:
            return (2**(math.log(points/1000, self.log_scaling)))/self.divisor + 1
        
    def set_current_points(self, points:float):
        self.current_points = points
        self.current_bonus = self.calculate_bonus(self.current_points)
        self.points_changed.emit(self.page, self.row, self.current_points)
        self.bonus_changed.emit(self.page, self.row, self.current_bonus)

    def calculate_syn_energy_per_tick(self, number_bd:int, progress_mult:float):
        '''
        calculates the results of a certain number of baby demons being applied to this row of synergy,
        returning the synergy energy gained per tick.
        Returns:
            ----
            gains_per_tick: how much synergy energy will result from a single tick with this number of bds
            speed_capped: bool showing if this is speed capped
            speed_capped_removal: if speed capped is true, this is how many BD we are overcapping by
        '''
        points_per_tick = number_bd * progress_mult
        ticks_to_fill = math.ceil(self.current_progress/points_per_tick) #gets how maany ticks it's currently taking to fill the bar
        if points_per_tick > self.current_progress / 10:
            #if the points per tick is more than 1/10th of the requirement, we do a min tick calculation
            ticks_to_fill = math.ceil(self.current_progress/points_per_tick) #gets how maany ticks it's currently taking to fill the bar
            #calculates the actual gains we're getting
            gains_per_tick = self.synergy_energy_per_fill/ticks_to_fill

            #calculate the required BD to get the actual number of ticks we want as 
            #the "effective" progress requirement (current progress divided by progress multi), divided 
            #by the number of ticks we're taking. This is ceiling'd
            required_bd = math.ceil((self.current_progress/progress_mult)/ticks_to_fill)
            overcapped_bd = number_bd - required_bd
            return gains_per_tick, True, overcapped_bd
        else:
            #otherwise, we dont care about the speed capping impacts
            gains_per_tick = points_per_tick * self.synergy_energy_per_fill / self.current_progress
            return gains_per_tick, False, 0