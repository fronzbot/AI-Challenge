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
        self.last_locations  = []
        self.turn_count      = 0
        self.orders          = []
        self.future_locs     = []
        
    
    def do_turn(self, ants):
        self.orders = []
        self.future_locs = []
        self.current_targets = []
        self.turn_count += 1
        for ant in ants.my_ants():
            order_issued = False
            possible_directions = self.look_around(ant, ants)

            if self.clear_hills(ants, ant):
                next
            elif self.collect_food(ants, ant):
                next
            elif self.hunt_enemy(ants, ant):
                next
            
            else:
                for i in range(0, 6):
                    direction = self.random_direction()
                    next_loc = ants.destination(ant, direction)
                    if self.send_order(ants, ant, direction):
                        break
            
        if self.last_locations and self.turn_count % 5 == 0:
            self.last_locations.pop(0)
        

        
    def hunt_enemy(self, ants, ant):
        cost = []
        friend_count = 0
        enemy_count  = 0
        enemy = ants.closest_enemy_ant(ant[0], ant[1])
        if not enemy:
            return False
        for nearby in ants.surrounding_area(ant[0], ant[1]):
            if nearby in ants.my_ants():
                friend_count += 1
        for nearby in ants.surrounding_area(enemy[0], enemy[1]):
            if nearby in ants.enemy_ants():
                enemy_count += 1
                
        if friend_count < enemy_count:
            return False
        
        for direction in self.look_around(ant, ants):
            next_loc = ants.destination(ant, direction)
            cost.append((ants.distance(next_loc, enemy), direction, enemy))
        cost = sorted(cost)
            
        for element in cost:
            direction = element[1]
            next_loc  = ants.destination(ant, direction)
            if self.send_order(ants, ant, direction):
                self.last_locations.append(ant)
                return True
        return False
                

    def collect_food(self, ants, ant):
        cost = []
        food = ants.closest_food(ant[0], ant[1])
        if not food:
            return False
        for direction in ants.direction(ant[0], ant[1], food[0], food[1]):
            next_loc = ants.destination(ant, direction)
            if ants.passable(next_loc):
                cost.append((ants.distance(next_loc, food), direction, food))
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
                self.last_locations.append(ant)
                return True
        return False
    
    def clear_hills(self, ants, ant):
        for hill in ants.my_hills():
            for loc in ants.surrounding_area(hill[0], hill[1]):
                if loc in self.last_locations:
                    self.last_locations.pop(self.last_locations.index(loc))
        if ant in ants.my_hills():
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
        next_loc = ants.destination(cur_loc, direction)
        if self.can_issue_order(next_loc, (cur_loc[0], cur_loc[1], direction), ants):
            self.future_locs.append(next_loc)
            self.orders.append((cur_loc[0], cur_loc[1], direction))
            ants.issue_order((cur_loc[0], cur_loc[1], direction))
            return True
        return False
    
    def can_issue_order(self, loc, command, ants):
        return (ants.passable(loc) and loc not in self.last_locations
                and loc not in self.future_locs and command not in self.orders
                and ants.unoccupied(loc[0], loc[1]) and loc not in ants.my_hills())

    def random_direction(self):
        return ['n', 'e', 'w', 's'].pop(random.randint(0, 3))
            
    def look_around(self, ant, ants):                    
        good_directions = []
        if ants.passable(ants.destination(ant, 'n')):
            good_directions.append('n')
        elif ants.passable(ants.destination(ant, 's')):
            good_directions.append('s')
        elif ants.passable(ants.destination(ant, 'e')):
            good_directions.append('e')
        elif ants.passable(ants.destination(ant, 'w')):
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
