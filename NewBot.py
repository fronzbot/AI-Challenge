#!/usr/bin/env python
from random import shuffle
from ants import *
import io
import operator
from math import sqrt
   
class MyBot():
    def __init__(self):
        self.weightMap = []
        self.prevLoc = []
        self.orthDir = {'n':['e','w'], 's':['e','w'],
                        'e':['n','s'], 'w':['n','s']}
        self.recurDepth = 0
        self.todoList = []

        self.antsLookingForFood = []
        self.foodDests = []
        self.pathToFood = []
        self.explorerAnts = []
        self.gathererAnts = 100

        self.deadEnds = {}
        self.junctions = {}
        self.prevLocations = [] # Format: [[(prevLoc2), (prevLoc1), (antLoc)]]
        self.locIndex = False
        self.noPrevMove = {}

         
    def do_setup(self, ants):
        for hillLoc in ants.my_hills():
            weightMap.append([hillLoc, 500])  
        
          
    def do_turn(self, ants):
        destinations = []
        unseen = ants.unseen_tiles()
        weightMap = self.weightMap
        orthDir = self.orthDir
        
        numberAntsGettingFood = 0
        recurDepth = self.recurDepth
        recurDepth = 0
        todoList = self.todoList
        antsLookingForFood = self.antsLookingForFood
        foodDests = self.foodDests
        pathToFood = self.pathToFood
        gathererAnts = self.gathererAnts
        junctions = self.junctions
        deadEnds = self.deadEnds
        prevLocations = self.prevLocations
        locIndex = self.locIndex
        noPrevMove = self.noPrevMove

        # Append hill locations to destinations
        for hillLoc in ants.my_hills():
            destinations.append(hillLoc)
            for direction in ['n','e','s','w']:
                hrow, hcol = tuple(map(operator.add, hillLoc, AIM[direction]))
                hrow_s, hcol_s = tuple(map(operator.add, hillLoc, AIMTWICE[direction]))
                weightMap.append([(hrow, hcol), 250])
                weightMap.append([(hrow_s, hcol_s), 250])

        # Get all ants
        allAnts = ants.my_ants()
        
        # Get key from dictionary based on value
        def get_dict_key(dictionary, value):
            "retrieve key from dictionary corresponding to value"
            return [k for k, v in dictionary.items() if v == value][0]


        # Breadth-first search.  Could use optimization.
        def Astar(start, goal, maxDist, maxIterations):
            "Astar to find path from start to goal as long as goal is"
            "located at a distance less than maxDist and will return"
            "no path if algorithm performs more iterations than that"
            "given in maxIterations"
            distance = ants.distance(start[0],start[1],goal[0],goal[1])
            i = 0
            todo = [[distance, start, [start]]]
            if distance < maxDist:
                while 0 < len(todo):
                    todo.sort()
                    if i > maxIterations:
                        return []
                    (cost, node, path) = todo.pop(0)
                    graph = [ants.destination(node[0], node[1], 'n'),
                             ants.destination(node[0], node[1], 'e'),
                             ants.destination(node[0], node[1], 'w'),
                             ants.destination(node[0], node[1], 's')]
                    for next_node in graph:
                        #newCost = ants.distance(next_node[0], next_node[1], goal[0], goal[1])
                        rowDist = abs(goal[0]-next_node[0])
                        colDist = abs(goal[1]-next_node[1])
                        newCost = int(sqrt(rowDist*rowDist + colDist*colDist))
                        if ants.passable(next_node[0], next_node[1]):
                            if next_node in path:
                                continue
                            elif next_node == goal:
                                return path + [next_node]
                            else:
                                todo.append([newCost, next_node, path + [next_node]])
                    i = i+1
            else:
                return []


        # Function to issue orders to ants and update weight maps
        def issueOrder(antRow, antCol, possibilities):
            # We have all possible moves
            if possibilities:
                # Choose to go to one at random
                # Add the order to the destination so another ant doesn't go there
                shuffle(possibilities)
                order = possibilities[0]
                destRow, destCol = ants.destination(possibilities[0][0], possibilities[0][1], possibilities[0][2])
                noPrevMove[(destRow, destCol)] = False
    
                # Append destination to destinations list
                destinations.append((destRow,destCol))
                # If we moved looking for food, update list with new ant location
                if resetAntsLookingForFood:
                    index = antsLookingForFood.index((antRow, antCol))
                    antsLookingForFood[index] = ((destRow, destCol))
                # ISSUE OUR ORDER
                ants.issue_order(order)
                newRow, newCol = ants.destination(order[0], order[1], order[2])
                prevWeight = searchList(weightMap, (newRow, newCol), 1)
                # Previous Location Handling
                if type(locIndex) is int:
                    if len(prevLocations[locIndex]) < 2:
                        prevLocations[locIndex].append((newRow, newCol))
                    else:
                        prevLocations[locIndex].pop(0)
                        prevLocations[locIndex].append((newRow, newCol))
                # Weight map handling
                if prevWeight == 0:
                    weightMap.append([(newRow, newCol), 10])
                else:
                    indexOfWeight = [y[0] for y in weightMap].index((newRow, newCol))
                    weightMap[indexOfWeight][1] = min(prevWeight+5, 250)
            # If possibilities empty (hopefully it never is!)
            else:
                noPrevMove[(antRow, antCol)] = True
                destinations.append((antRow, antCol))
                prevWeight = searchList(weightMap, (antRow, antCol), 1)
                if prevWeight == 0:
                    weightMap.append([(antRow, antCol), 10])
                else:
                    indexOfWeight = [y[0] for y in weightMap].index((antRow, antCol))
                    weightMap[indexOfWeight][1] = min(prevWeight+5, 250)

        # Function to search a list for a given element at a certain location 
        def searchList(list_name, element, elementLoc):
            "returns element of list located at sublist[elementLoc]"
            try:
                return next(sublist for sublist in list_name if element in sublist)[elementLoc]
            except StopIteration:
                return(0)
 
        for hillLoc in ants.my_hills():
            destinations.append(hillLoc)



        #########################################
        ######      FOR EVERY ANT           #####
        #########################################
            
            
        for antRow, antCol in allAnts:
            foodClose = True
            resetAntsLookingForFood = False
            gatheringFood = False
            foodInSight = True
            followingNearbyAnt = False
            allDirections = ['n', 'e', 'w', 's']
            # Mark water tiles as "don't go here"
            for direction in allDirections:
                nextRow, nextCol = ants.destination(antRow, antCol, direction)
                if not ants.passable(nextRow, nextCol):
                    weightMap.append([(nextRow, nextCol), 500])
                    # Mark surrounding passable tiles as "don't go here"
                    row, col = tuple(map(operator.add, (nextRow, nextCol), AIM[direction]))
                    # If we map around the map, set proper row, col
                    if row < 0:
                        row = ants.height - 1
                    if row > (ants.height - 1):
                        row = 0
                    if col < 0:
                        col = ants.width - 1
                    if col > (ants.width - 1):
                        col = 0
                    if ants.passable(row, col):
                        weightMap.append([(row, col), 500])
            # If in sight of hill, mark with high weight

                        
            # Set up junctions and directions when junction is encountered
            waterTiles = []
            for i in range(1,4):
                surroundingTiles = {'n':(-i,0),
                                    'e':(0,i),
                                    'w':(0,-i),
                                    's':(i,0)}
                for direction in allDirections:
                    row, col = tuple(map(operator.add, (antRow, antCol), surroundingTiles[direction]))
                    # If we wrap, set new coordinates
                    if row < 0:
                        row = ants.height - 1
                    if row > (ants.height - 1):
                        row = 0
                    if col < 0:
                        col = ants.width - 1
                    if col > (ants.width - 1):
                        col = 0
                    # Store directions and coordinates
                    if not ants.passable(row, col):
                        waterTiles.append([(row, col), direction])

            possibleDirections = ['n','e','w','s']
            blockedDirections = []
            # Check for junctions
            for (w_row, w_col), direction in waterTiles:
                if direction not in blockedDirections:
                    possibleDirections.remove(direction)
                    blockedDirections.append(direction)

            if (antRow, antCol) in junctions:
                if len(possibleDirections) < len(junctions[(antRow, antCol)]):
                    junctions[(antRow, antCol)] = possibleDirections
            else:

                # Dead end
                if len(blockedDirections) == 3:
                    if (antRow, antCol) not in deadEnds:
                        deadEnds[(antRow, antCol)] = possibleDirections
                        weightMap.append([(antRow, antCol), 500])

                # Junction
                if len(blockedDirections) > 0 and len(blockedDirections) < 3:
                    if (antRow, antCol) not in junctions:
                        junctions[(antRow, antCol)] = possibleDirections

                    

        #########################################
        ######          GATHERERS           #####
        #########################################
                    
            # Dedicate ants to food searching
            if len(antsLookingForFood) <= gathererAnts:
                distToFood = []
                # Get distances to each food location from ant
                for foodRow, foodCol in ants.food():
                    if (foodRow, foodCol) not in foodDests:
                        dist = ants.distance(antRow, antCol, foodRow, foodCol)
                        distToFood.append([dist, (foodRow, foodCol)])
                # Use closest food location as goal
                distToFood.sort()
                if distToFood:
                    foodLoc = distToFood[0][1]
                else:
                    foodInSight = False
                    
                if foodInSight:
                    if (antRow, antCol) in antsLookingForFood:
                        indexOfTodoList = antsLookingForFood.index((antRow, antCol))
                    elif len(antsLookingForFood) != gathererAnts:
                        antsLookingForFood.append((antRow, antCol))
                        pathToFood.append([])
                        indexOfTodoList = antsLookingForFood.index((antRow, antCol))
                    else:
                        # Check paths, if empty, delete location from antsLooking, insertNew
                        for i in range(len(pathToFood)):
                            if not pathToFood[i]:
                                antsLookingForFood[i] = (antRow, antCol)
                                indexOfTodoList = i
                                
                    # If the Path is empty
                    if not pathToFood[indexOfTodoList]:
                        #todoList = [[(antRow, antCol), [(antRow, antCol)]]]
                        pathToFood[indexOfTodoList] = Astar((antRow, antCol), foodLoc, 18, 1024)
                        
                        if pathToFood[indexOfTodoList] == []:
                            foodClose = False
                            resetAntsLookingForFood = True
                            gatheringFood = False
    
                    if foodClose:
                        # Pop next node off of path and store in currentPath
                        currentPath = pathToFood[indexOfTodoList].pop(0)
                    
                        if currentPath == (antRow, antCol) and len(pathToFood[indexOfTodoList]) > 1:
                            currentPath = pathToFood[indexOfTodoList].pop(0)
                        
                        directions = ants.direction(antRow, antCol, currentPath[0], currentPath[1])
                        if directions:
                            direction = directions[0]
                        else:
                            shuffle(allDirections)
                            direction = allDirections[0]
                        destRow, destCol = ants.destination(antRow, antCol, direction)
                        possibilities = [[antRow, antCol, direction]]
                        # If the next tile is unoccupied and not in queue, send order
                        if ants.unoccupied(currentPath[0], currentPath[1]) and (currentPath[0], currentPath[1]) not in destinations:
                            antsLookingForFood[indexOfTodoList] = (destRow, destCol)
                            for i in range(len(pathToFood[indexOfTodoList])):
                                destinations.append(pathToFood[indexOfTodoList][i])
                            issueOrder(antRow, antCol, possibilities)
                            gatheringFood = True
                        else:
                            resetAntsLookingForFood = True


        #########################################
        ######          EXPLORERS           #####
        #########################################
                    
            if not gatheringFood:
                # Choose lowest location around us
                # Randomly choose one if equal
                minimum = 250
                possibilities = []

                # Check for dead end or junction
                if (antRow, antCol) in junctions:
                    allDirections = junctions[(antRow, antCol)]
                elif (antRow, antCol) in deadEnds:
                    allDirections = deadEnds[(antRow, antCol)]
                
                shuffle(allDirections)
                secondIndex = 0
                if prevLocations:
                    for i in range(len(prevLocations)):
                        secondIndex = len(prevLocations[i]) - 1
                        if prevLocations[i][secondIndex] == (antRow, antCol):
                            locIndex = i
                            break
                        else:
                            locIndex = False
                try:
                    didNotMoveLastTurn = noPrevMove[(antRow, antCol)]
                except KeyError:
                    didNotMoveLastTurn = False

                if didNotMoveLastTurn:
                    allDirections = ['n', 'e', 'w', 's']
 
                for direction in allDirections:
                    goodDirection = True 
                    destRow, destCol = ants.destination(antRow, antCol, direction)
                    
                    # Previous location handling
                    if type(locIndex) is int:
                        if (destRow, destCol) in prevLocations[locIndex]:
                            goodDirection = False
                    else:
                        prevLocations.append([(antRow, antCol)])
                        locIndex = len(prevLocations) - 1
                                
                    # If the tile has nothing there and another any is not there
                    # Order to move there for next turn
                    if ants.unoccupied(destRow, destCol) and (destRow, destCol) not in destinations and goodDirection:
                        weight = searchList(weightMap, (destRow, destCol), 1)
                        if weight < minimum:
                            possibilites = []
                            minimum = weight
                            possibilities.append([antRow, antCol, direction])
                        elif weight == minimum:
                            possibilities.append([antRow, antCol, direction])
                issueOrder(antRow, antCol, possibilities)

   
         
   
                          
                  
              
   
if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    try:
        Ants.run(MyBot())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
