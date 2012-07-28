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
        self.weight_map      = {}
        self.turn_count      = 0
        self.orders          = []
        self.future_locs     = []
        self.hills           = set(ants.my_hills())
        self.threshold       = 0
        self.max             = 100
        for hill in self.hills:
            self.hills.add(ants.surrounding_area(hill[0], hill[1]))        
    
    def do_turn(self, ants):
        self.orders = []
        self.future_locs = []
        self.current_targets = []
        self.turn_count += 1
        for loc, weight in self.weight_map.items():
            if weight > 0:
                self.weight_map[loc] -= 2
                
        if len(ants.my_ants()) % 10:
            self.threshold += 1
            
        for ant in ants.my_ants():
            order_issued = False
            possible_directions = self.look_around(ant, ants)

            if self.clear_hills(ants, ant):
                continue
            elif self.collect_food(ants, ant):
                continue
            elif self.hunt_enemy(ants, ant):
                continue
            
            else:
                locs  = []
                north = (ants.destination(ant, 'n'), 'n')
                south = (ants.destination(ant, 's'), 's')
                east  = (ants.destination(ant, 'e'), 'e')
                west  = (ants.destination(ant, 'w'), 'w')
                for next_loc, direction in (north, south, east, west):
                    if next_loc in self.weight_map:
                        locs.append((next_loc, self.weight_map[next_loc], direction))
                
                prev_thresh    = self.threshold
                self.threshold = self.max - 1
                for next_loc, weight, direction in sorted(locs, key=lambda x: x[1]):
                    if self.send_order(ants, ant, direction):
                        self.threshold = prev_thresh
                        break
                self.threshold = prev_thresh
            

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
                #if ant not in self.hills:
                #    self.last_locations[ant] = next_loc
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
            else:
                self.weight_map[next_loc] = 200
        if not cost:
            for direction in self.look_around(ant, ants):
                next_loc = ants.destination(ant, direction)
                cost.append((ants.distance(next_loc, food), direction, food))
                
        cost = sorted(cost)
            
        for element in cost:
            direction = element[1]
            next_loc  = ants.destination(ant, direction)
            try:
                if self.weight_map[next_loc] >= 85:
                    continue
            except KeyError:
                pass
            target    = element[2]
            if self.send_order(ants, ant, direction):
                #if ant not in self.hills:
                #    self.last_locations[ant] = next_loc
                return True
        return False
    
    def clear_hills(self, ants, ant):
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
        next_loc = ants.destination(cur_loc, direction)
        if self.can_issue_order(next_loc, (cur_loc[0], cur_loc[1], direction), ants):
            self.future_locs.append(next_loc)
            self.orders.append((cur_loc[0], cur_loc[1], direction))
            ants.issue_order((cur_loc[0], cur_loc[1], direction))
            self.weight_map[next_loc] = self.max
            return True
        return False
    
    def can_issue_order(self, loc, command, ants):
        return (ants.passable(loc) and loc not in self.future_locs and command not in self.orders
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
