#!/usr/bin/env python
import sys
import traceback
import random
import time
from math import sqrt
import operator
  
try:
    from sys import maxint
except ImportError:
    from sys import maxsize as maxint
         
MY_ANT = 0
ANTS = 0
DEAD = -1
LAND = -2
FOOD = -3
WATER = -4
UNSEEN = -5
HILL = -6
  
PLAYER_ANT = 'abcdefghij'
HILL_ANT = string = 'ABCDEFGHIJ'
PLAYER_HILL = string = '0123456789'
MAP_OBJECT = '?%*.!'
MAP_RENDER = PLAYER_ANT + HILL_ANT + PLAYER_HILL + MAP_OBJECT
  
  
AIM = {'n': (-1, 0),
       'e': (0, 1),
       's': (1, 0),
       'w': (0, -1)}
AIMTWICE = {'n': (-2, 0),
            'e': (0, 2),
            's': (2, 0),
            'w': (0, -2)}
RIGHT = {'n': 'e',
         'e': 's',
         's': 'w',
         'w': 'n'}
LEFT = {'n': 'w',
        'e': 'n',
        's': 'e',
        'w': 's'}
BEHIND = {'n': 's',
          's': 'n',
          'e': 'w',
          'w': 'e'}
  
class Ants():
    def __init__(self):
        self.width = None
        self.height = None
        self.map = None
        self.ant_list = {}
        self.food_list = []
        self.dead_list = []
        self.hill_list = {}
        self.turntime = 0
        self.loadtime = 0
        self.turn_start_time = None
        self.current_ants = {} # ants that are currently alive
        
        # cache used by neighbourhood_offsets() to determine nearby squares
        self.offsets_cache = {}
  
    def setup(self, data):
        'parse initial input and setup starting game state'
        for line in data.split('\n'):
            line = line.strip().lower()
            if len(line) > 0:
                tokens = line.split()
                key = tokens[0]
                if key == 'cols':
                    self.width = int(tokens[1])
                elif key == 'rows':
                    self.height = int(tokens[1])
                elif key == 'player_seed':
                    random.seed(int(tokens[1]))
                elif key == 'turntime':
                    self.turntime = int(tokens[1])
                elif key == 'loadtime':
                    self.loadtime = int(tokens[1])
                elif key == 'viewradius2':
                    self.viewradius2 = int(tokens[1])
                elif key == 'attackradius2':
                    self.attackradius2 = int(tokens[1])
                elif key == 'spawnradius2':
                    self.spawnradius2 = int(tokens[1])
        self.map = [[UNSEEN for col in range(self.width)]
                    for row in range(self.height)]
  
    def update(self, data):
        "Parse engine input and update the game state"
        # start timer
        self.turn_start_time = time.clock()
         
        # clear ant and food data
        for (row, col), owner in self.ant_list.items():
            self.map[row][col] = LAND
        self.ant_list = {}
        for row, col in self.food_list:
            self.map[row][col] = LAND
        self.food_list = []
        for row, col in self.dead_list:
            self.map[row][col] = LAND
        self.dead_list = []
        for (row, col), owner in self.hill_list.items():
            self.map[row][col] = LAND
        self.hill_list = {}
  
        # update map and create new ant and food lists
        for line in data.split('\n'):
            line = line.strip().lower()
            if len(line) > 0:
                tokens = line.split()
                if len(tokens) >= 3:
                    row = int(tokens[1])
                    col = int(tokens[2])
                    if tokens[0] == 'a':
                        owner = int(tokens[3])
                        self.map[row][col] = owner
                        self.ant_list[(row, col)] = owner
                    elif tokens[0] == 'f':
                        self.map[row][col] = FOOD
                        self.food_list.append((row, col))
                    elif tokens[0] == 'w':
                        self.map[row][col] = WATER
                    elif tokens[0] == 'l':
                        self.map[row][col] = LAND
                    elif tokens[0] == 'd':
                        # food could spawn on a spot where an ant just died
                        # don't overwrite the space unless it is land
                        if self.map[row][col] == LAND:
                            self.map[row][col] = DEAD
                        # but always add to the dead list
                        self.dead_list.append((row, col))
                    elif tokens[0] == 'h':
                        owner = int(tokens[3])
                        self.hill_list[(row, col)] = owner
  
    def issue_order(self, order):
        sys.stdout.write('o %s %s %s\n' % (order[0], order[1], order[2]))
        sys.stdout.flush()
         
    def finish_turn(self):
        sys.stdout.write('go\n')
        sys.stdout.flush()
  
    def my_ants(self):
        return [loc for loc, owner in self.ant_list.items()
                    if owner == MY_ANT]
  
    def enemy_ants(self):
        return [(loc, owner) for loc, owner in self.ant_list.items()
                    if owner != MY_ANT]
    
    def enemy_ants_plain(self):
        return [loc for loc, owner in self.ant_list.items()
                    if owner != MY_ANT]
     
    def my_hills(self):
        return [loc for loc, owner in self.hill_list.items()
                    if owner == MY_ANT]
  
    def enemy_hills(self):
        return [(loc, owner) for loc, owner in self.hill_list.items()
                    if owner != MY_ANT]
         
    def food(self):
        return self.food_list[:]
  
    def passable(self, row, col):
        return self.map[row][col] != WATER
     
    def unoccupied(self, row, col):
        return self.map[row][col] in (LAND, DEAD, UNSEEN)
  
    def destination(self, row, col, direction):
        d_row, d_col = AIM[direction]
        return ((row + d_row) % self.height, (col + d_col) % self.width)       
  
    def distance(self, row1, col1, row2, col2):
        row1 = row1 % self.height
        row2 = row2 % self.height
        col1 = col1 % self.width
        col2 = col2 % self.width
        d_col = min(abs(col1 - col2), self.width - abs(col1 - col2))
        d_row = min(abs(row1 - row2), self.height - abs(row1 - row2))
        return d_col + d_row
  
    def direction(self, row1, col1, row2, col2):
        d = []
        row1 = row1 % self.height
        row2 = row2 % self.height
        col1 = col1 % self.width
        col2 = col2 % self.width
        if row1 < row2:
            if row2 - row1 >= self.height//2:
                d.append('n')
            if row2 - row1 <= self.height//2:
                d.append('s')
        if row2 < row1:
            if row1 - row2 >= self.height//2:
                d.append('s')
            if row1 - row2 <= self.height//2:
                d.append('n')
        if col1 < col2:
            if col2 - col1 >= self.width//2:
                d.append('w')
            if col2 - col1 <= self.width//2:
                d.append('e')
        if col2 < col1:
            if col1 - col2 >= self.width//2:
                d.append('e')
            if col1 - col2 <= self.width//2:
                d.append('w')
        return d
  
    def closest_food(self,row1,col1,filter=None):
        #find the closest food from this row/col
        min_dist=maxint
        closest_food = None
        for food in self.food_list:
            if filter is None or food not in filter:
                dist = self.distance(row1,col1,food[0],food[1])
                if dist<min_dist:
                    min_dist = dist
                    closest_food = food
        return closest_food   
  
    def closest_enemy_ant(self,row1,col1,filter=None):
        #find the closest enemy ant from this row/col
        min_dist=maxint
        closest_ant = None
        for ant in self.enemy_ants():
            if filter is None or ant not in filter:
                dist = self.distance(row1,col1,ant[0][0],ant[0][1])
                if dist<min_dist:
                    min_dist = dist
                    closest_ant = ant[0]
        return closest_ant   
  
    def closest_enemy_hill(self,row1,col1,filter=None):
        #find the closest enemy hill from this row/col
        min_dist=maxint
        closest_hill = None
        for hill in self.enemy_hills():
            if filter is None or hill[0] not in filter:
                dist = self.distance(row1,col1,hill[0][0],hill[0][1])
                if dist<min_dist:
                    min_dist = dist
                    closest_hill = hill[0]
        return closest_hill  
  
    def closest_unseen(self,row1,col1,filter=None):
        #find the closest unseen from this row/col
        min_dist=maxint
        closest_unseen = None
        for row in range(self.height):
            for col in range(self.width):
                if filter is None or (row, col) not in filter:
                    if self.map[row][col] == UNSEEN:
                        dist = self.distance(row1,col1,row,col)
                        if dist<min_dist:
                            min_dist = dist
                            closest_unseen = (row, col)
        return closest_unseen

    def unseen_tiles(self, filter=None):
        #find all unseen positions
        unseen = []
        for row in range(self.height):
            for col in range(self.width):
                if filter is None or (row, col) not in filter:
                    if self.map[row][col] == UNSEEN:
                        unseen.append((row, col))
        return unseen


    def neighbourhood_offsets(self, max_dist):
        """ Return a list of squares within a given distance of loc

            Loc is not included in the list
            For all squares returned: 0 < distance(loc,square) <= max_dist

            Offsets are calculated so that:
              -height <= row+offset_row < height (and similarly for col)
              negative indicies on self.map wrap thanks to python
        """
        if max_dist not in self.offsets_cache:
            offsets = []
            mx = int(sqrt(max_dist))
            for d_row in range(-mx,mx+1):
                for d_col in range(-mx,mx+1):
                    d = d_row**2 + d_col**2
                    if 0 < d <= max_dist:
                        offsets.append((
                            d_row%self.height-self.height,
                            d_col%self.width-self.width
                        ))
            self.offsets_cache[max_dist] = offsets
        return self.offsets_cache[max_dist]    
  
    def render_text_map(self):
        tmp = ''
        for row in self.map:
            tmp += '# %s\n' % ''.join([MAP_RENDER[col] for col in row])
        return tmp

    def surrounding_area(self, r, c):
        area_locs = [(r+1,c),(r+1,c+1),(r,c+1),(r-1,c+1),
                    (r-1,c),(r-1,c-1),(r,c-1),(r+1,c-1)]
        for i in range(len(area_locs)):
            d_row, d_col = area_locs[i]
            # If we wrap around the map, set proper row, col
            if d_row < 0:
                d_row = self.height - 1
            if d_row > (self.height - 1):
                d_row = 0
            if d_col < 0:
                d_col = self.width - 1
            if d_col > (self.width - 1):
                d_col = 0
            area_locs[i] = (d_row,d_col)

        return area_locs
     
    def time_remaining(self):
        return self.turntime - int(1000 * (time.clock() - self.turn_start_time))

    def between_water(self, row, col, distFromWater):
        index = {'n':0,'e':1,'s':2,'w':3}
        mapping = [[],[],[],[]]
        for i in range(distFromWater):
            waterAIM = {'n':(-i,0),
                        'e':(0,i),
                        'w':(0,-i),
                        's':(i,0)}
            for d in ['n', 'e', 'w', 's']:
                d_row, d_col = tuple(map(operator.add, (row, col), waterAIM[d]))
                # If we wrap around the map, set proper row, col
                if d_row < 0:
                    d_row = self.height - 1
                if d_row > (self.height - 1):
                    d_row = 0
                if d_col < 0:
                    d_col = self.width - 1
                if d_col > (self.width - 1):
                    d_col = 0
                if not self.passable(d_row, d_col):
                    mapping[index[d]].append((d_row, d_col))

        # We want to output the direction to get to the center of the water walls
        # North and South
        if mapping[0] and mapping[2]:
            x_max = mapping[0][0][0]
            x_min = mapping[2][0][0]
            midX = (x_max+x_min)/2
            midY = mapping[0][0][1]
            return [(midX, midY)]
        if mapping[1] and mapping[3]:
            y_max = mapping[1][0][1]
            y_min = mapping[3][0][1]
            midX = mapping[1][0][0]
            midY = (y_max+y_min)/2
            return [(midX, midY)]

        return []
                    
                        
                        
  
    @staticmethod
    def run(bot):
        ants = Ants()
        map_data = ''
        while(True):
            try:
                current_line = sys.stdin.readline().rstrip('\r\n') # strip new line char
                if current_line.lower() == 'ready':
                    ants.setup(map_data)
                    bot.do_setup(ants)
                    ants.finish_turn()
                    map_data = ''
                elif current_line.lower() == 'go':
                    ants.update(map_data)
                    bot.do_turn(ants)
                    ants.finish_turn()
                    map_data = ''
                else:
                    map_data += current_line + '\n'
            except EOFError:
                break
            except Exception as e:
                traceback.print_exc(file=sys.stderr)
                break
