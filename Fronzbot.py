#!/usr/bin/env python
import random
from ants import *
import io
import operator
import copy
import os


class Fronzbot(object):
    def __init__(self):
        pass

    def do_setup(self, ants):
        ''' Setup data structures for ants '''
        self.weight_map      = {}
        self.turn_count      = 0
        self.orders          = []
        self.future_locs     = []
        self.hills           = set(ants.my_hills())
        self.max             = 100
        self.threshold       = self.max - 10

        for hill in self.hills:
            self.hills.add(ants.surrounding_area(hill[0], hill[1]))        
    
    def do_turn(self, ants):
        self.orders = []        # Keep track of orders issued each turn
        self.future_locs = []   # Keep track of future locations (probably not needed any more)
        self.turn_count += 1

        # Decrement weight of each cell by 2 
        for loc, weight in self.weight_map.items():
            if weight > 0:
                self.weight_map[loc] -= 2
            
        for ant in ants.my_ants():
            order_issued = False           

            if self.clear_hills(ants, ant):
                continue
            elif self.collect_food(ants, ant):
                continue
            elif self.hunt_enemy(ants, ant):
                continue
            
            else:
                # Look around, find a possible direction, go to cell with lowest weight
                locs  = []
                possible_directions = self.look_around(ant, ants)  # Check possible directions
                for direction in possible_directions:
                    next_loc = ants.destination(ant, direction)
                    if next_loc in self.weight_map:
                        locs.append((next_loc, self.weight_map[next_loc], direction))
                    else:
                        locs.append((next_loc, 0, direction))

                temp = self.threshold
                self.threshold = self.max - 2
                for next_loc, weight, direction in sorted(locs, key=lambda x: x[1]):
                    if self.send_order(ants, ant, direction):
                        break
                self.threshold = temp
              
            

    def hunt_enemy(self, ants, ant):
        ''' Method to hunt enemy ants '''
        cost = []
        friend_count = 0
        enemy_count  = 0
        guard_count  = 0
        run_away     = False
        enemy = ants.closest_enemy_ant(ant[0],  ant[1])
        hill  = ants.closest_enemy_hill(ant[0], ant[1])
        if not enemy and not hill:
            return False
        for nearby in ants.surrounding_area(ant[0], ant[1]):
            if nearby in ants.my_ants():
                friend_count += 1
        if enemy:
            for nearby in ants.surrounding_area(enemy[0], enemy[1]):
                if nearby in ants.enemy_ants():
                    enemy_count += 1
        if hill:
            for nearby in ants.surrounding_area(hill[0], hill[1]):
                if nearby in ants.enemy_ants():
                    guard_count += 1

        if hill and friend_count >= guard_count:
            target_loc = hill
        elif enemy and friend_count > enemy_count:
            target_loc = enemy
        elif friend_count <= enemy_count:
            target_loc = enemy
            run_away = True
        else:
            return False
        
        for direction in self.look_around(ant, ants):
            next_loc = ants.destination(ant, direction)
            if run_away:
                cost.append((ants.distance(next_loc, target_loc), ants.opposite_direction(direction), target_loc))
            else:
                cost.append((ants.distance(next_loc, target_loc), direction, target_loc))
        cost = sorted(cost)
            
        for element in cost:
            direction = element[1]
            next_loc  = ants.destination(ant, direction)
            if self.send_order(ants, ant, direction):
                return True
        return False
                

    def collect_food(self, ants, ant):
        ''' Method to collect food '''
        ''' Basically uses A* search '''
        cost = []
        food = ants.closest_food(ant[0], ant[1])
        if not food:
            return False
        for direction in ants.direction(ant[0], ant[1], food[0], food[1]):
            next_loc = ants.destination(ant, direction)
            if ants.passable(next_loc):
                try:
                    weight = self.weight_map[next_loc]
                except KeyError:
                    weight = 0
                cost.append((ants.distance(next_loc, food)+weight, direction, food))
            
        if not cost:
            for direction in self.look_around(ant, ants):
                next_loc = ants.destination(ant, direction)
                cost.append((ants.distance(next_loc, food), direction, food))
                
        cost = sorted(cost)
            
        for element in cost:
            direction = element[1]
            next_loc  = ants.destination(ant, direction)
            target    = element[2]
            if self.send_order(ants, ant, direction):
                return True
        return False
    
    def clear_hills(self, ants, ant):
        ''' Move ants from hill '''
        if ant in self.hills:
            if self.send_order(ants, ant, 'n'):
                return True
            if self.send_order(ants, ant, 'e'):
                return True
            if self.send_order(ants, ant, 'w'):
                return True
            if self.send_order(ants, ant, 's'):
                return True
        return False
                    
    def send_order(self, ants, cur_loc, direction):
        ''' Send order for ant (if possible) '''
        next_loc = ants.destination(cur_loc, direction)
        if self.can_issue_order(next_loc, (cur_loc[0], cur_loc[1], direction), ants):
            self.future_locs.append(next_loc)
            self.orders.append((cur_loc[0], cur_loc[1], direction))
            ants.issue_order((cur_loc[0], cur_loc[1], direction))
            if next_loc in self.weight_map:
                self.weight_map[next_loc] += 10
            else:
                self.weight_map[next_loc] = self.max
            return True
        return False
    
    def can_issue_order(self, loc, command, ants):
        ''' Check if OK to send order '''
        try:
            if self.weight_map[loc] >= self.threshold:
                return False
        except KeyError:
            pass
       
        return (ants.passable(loc) and loc not in self.future_locs and command not in self.orders
                and ants.unoccupied(loc[0], loc[1]) and loc not in ants.my_hills())

    def random_direction(self):
        return ['n', 'e', 'w', 's'].pop(random.randint(0, 3))
            
    def look_around(self, ant, ants):                    
        good_directions = []
        if ants.passable(ants.destination(ant, 'n')):
            good_directions.append('n')
        if ants.passable(ants.destination(ant, 's')):
            good_directions.append('s')
        if ants.passable(ants.destination(ant, 'e')):
            good_directions.append('e')
        if ants.passable(ants.destination(ant, 'w')):
            good_directions.append('w')
        return good_directions

            

if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    try:
        Ants.run(Fronzbot())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
