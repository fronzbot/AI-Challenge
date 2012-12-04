#!/usr/bin/env python
from random import shuffle
from ants import *
import io
import operator
import copy
import os

'''
MyBot
Revision C
12/04/2011
'''
   
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
        self.turn = 0
        self.antNum = 0
        self.antsEscaping = {}
        self.pathToNode = []
        self.noPath = True
        self.T_Junctions = []
        self.enemyLocations = []
        self.guardAnts = {}          # guardAnt:[[hunterAnt][pathGuardShouldTake]]
        self.hunterAnts = {}        # hunterAnt:[[hunterAntGuards][pathToEnemy]]

         
    def do_setup(self, ants):
        for hillLoc in ants.my_hills():
            weightMap.append([hillLoc, 500])
        try:
            os.remove('path.txt')
            os.remove('currentTask.txt')
        except WindowsError:
            pass
          
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
        turn = self.turn
        antNum = self.antNum
        pathToNode = self.pathToNode
        antsEscaping = self.antsEscaping
        T_Junctions = self.T_Junctions
        enemyLocations = self.enemyLocations
        guardAnts = self.guardAnts
        hunterAnts = self.hunterAnts

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


        # A* Search.  Could use optimization
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
                        rowDist = goal[0]-next_node[0]
                        colDist = goal[1]-next_node[1]
                        newCost = sqrt(rowDist*rowDist + colDist*colDist)
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
            

        # Breadth-first search.  Could use optimization.
        def BFS(start, goal, todo, maxDist, maxIterations):
            "BFS to find path from start to goal as long as goal is"
            "located at a distance less than maxDist and will return"
            "no path if algorithm performs more iterations than that"
            "given in maxIterations"
            distance = ants.distance(start[0],start[1],goal[0],goal[1])
            i = 0
            if distance < maxDist:
                while 0 < len(todo):
                    if i > maxIterations:
                        return []
                    (node, path) = todo.pop(0)
                    graph = [ants.destination(node[0], node[1], 'n'),
                             ants.destination(node[0], node[1], 'e'),
                             ants.destination(node[0], node[1], 'w'),
                             ants.destination(node[0], node[1], 's')]
                    for next_node in graph:
                        if ants.passable(next_node[0], next_node[1]):
                            if next_node in path:
                                continue
                            elif next_node == goal:
                                return path + [next_node]
                            else:
                                todo.append([next_node, path + [next_node]])
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
                    try:
                        index = antsLookingForFood.index((antRow, antCol))
                        antsLookingForFood[index] = ((destRow, destCol))
                    except ValueError:
                        pass
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
        self.turn = self.turn+1
        fl = open('currentTask.txt','a')
        fl.write('\n\n=== TURN '+str(self.turn)+' ===')
        
        #########################################
        ######      FOR EVERY ANT           #####
        #########################################
            
            
        for antRow, antCol in allAnts:
            
            fl.write('\nANT: '+'('+str(antRow)+','+str(antCol)+') --> ')

            hitWater = {'n':False, 'e':False,
                        'w':False, 's':False}
            antNum = antNum + 1
            foodClose = True
            resetAntsLookingForFood = False
            gatheringFood = False
            foodInSight = True
            followingNearbyAnt = False
            antHunting = False
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

                        
        #########################################
        ######          JUNCTIONS           #####
        #########################################
            waterTiles = []
            nextDirBlocked = []
            for i in range(1,3):
                surroundingTiles = {'n':(-i,0),
                                    'e':(0,i),
                                    'w':(0,-i),
                                    's':(i,0)}
                for direction in allDirections:
                    if not hitWater[direction]:
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
                            hitWater[direction] = True
                        if not ants.passable(row, col) and i == 1:
                            nextDirBlocked.append(direction)
                            hitWater[direction] = True
                            
                        

            possibleDirections = ['n','e','w','s']
            blockedDirections = []
            # Check for junctions
            for direction in allDirections:
                if hitWater[direction]:
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
                    if len(blockedDirections) == 1:
                        T_Junctions.append((antRow, antCol))

                        

        #########################################
        ######         ESCAPE HILL          #####
        #########################################
            notEscaping = True
            if pathToNode or antsEscaping:
                self.noPath = False
                fl.write("THERE IS A PATH TO GOAL, ")
                if (antRow, antCol) in antsEscaping:
                    if antsEscaping[(antRow, antCol)] != []:
                        fl.write("IN ESCAPING DICT, ")
                        path = antsEscaping[(antRow, antCol)]
                        if path[0] not in destinations and ants.unoccupied(path[0][0], path[0][1]):
                            fl.write("NEXT MOVE IS NOT BLOCKED, ")
                            # If ant has not reached destination
                            fl.write("ESCAPING HILL, ")
                            destRow, destCol = path.pop(0)
                            direction = ants.direction(antRow, antCol, destRow, destCol)[0]
                            antsEscaping[(destRow, destCol)] = path
                            possibilities = []
                            possibilities.append([antRow, antCol, direction])
                            issueOrder(antRow, antCol, possibilities)
                            notEscaping = False
                        else:
                            destinations.append((antRow, antCol))
                            notEscaping = False
                    # Else we have reached our goal, remove from dictionary
                    else:
                        fl.write("REACHED GOAL, ")
                        del antsEscaping[(antRow, antCol)]
                        notEscaping = True
                    
                # If the ant is not escaping but steps in the path to the node
                elif (antRow, antCol) in pathToNode:
                    fl.write("STEPPING ON ESCAPE ROUTE, ")
                    posInList = [i for i,x in enumerate(pathToNode) if x == (antRow,antCol)][0]
                    path = copy.copy(pathToNode)
                    del path[:posInList]
                    path.pop(0)
                    fl.write("PATH[0] = "+str(path[0]))
                    if path[0] not in destinations and ants.unoccupied(path[0][0], path[0][1]):
                        fl.write("NEXT MOVE IS NOT BLOCKED AFTER STEP ONTO ESCAPE, ")
                        destRow, destCol = path.pop(0)
                        direction = ants.direction(antRow, antCol, destRow, destCol)[0]
                        antsEscaping[(antRow, antCol)] = path
                        possibilities = []
                        possibilities.append([antRow, antCol, direction])
                        issueOrder(antRow, antCol, possibilities)
                        notEscaping = False
                    
                else:
                    path = copy.copy(pathToNode)
                    for hillLoc in ants.my_hills():
                        if (antRow, antCol) == hillLoc and path: #or ants.distance(antRow, antCol, hillLoc[0], hillLoc[1]) <= 6:
                            fl.write("JUST SPAWNED, ")
                            if path[0] not in destinations and ants.unoccupied(path[0][0],path[0][1]):
                                fl.write("SPAWNED -> NOW ESCAPING, ")
                                destRow, destCol = path.pop(0)
                                antsEscaping[(antRow, antCol)] = path
                                direction = ants.direction(antRow, antCol, destRow, destCol)[0]
                                possibilities = []
                                possibilities.append([antRow, antCol, direction])
                                issueOrder(antRow, antCol, possibilities)
                                notEscaping = False
                            else:
                                fl.write("PATH BLOCKED, ")
                                destinations.append((antRow, antCol))
                                notEscaping = True
            elif self.noPath:
                notEscaping = True
                # No escape path found, should only be called once
                for hillLoc in ants.my_hills():
                    if ants.distance(antRow, antCol, hillLoc[0], hillLoc[1]) >= 24 and (antRow, antCol) not in deadEnds:
                        fl.write("SETTING GOAL NODE FOR ESCAPE, ")
                        pathToNode = Astar(hillLoc, (antRow, antCol), 48, 8192)
                        pathToNode.pop(0)
                        f = open('path.txt','a')
                        f.write('----------\n')
                        for p in pathToNode:
                            f.write(str(p)+'\n')
                        f.write('\n')
                        f.close()
                        
                        
        #########################################
        ######           HUNTERS            #####
        #########################################
            if notEscaping:  
                distToEnemy = []
                localEnemyAnts = []
                # get distance to each enemy from current ant
                for enemyRow, enemyCol in ants.enemy_ants_plain():
                    enemyLocations.append((enemyRow, enemyCol))
                    dist = ants.distance(antRow, antCol, enemyRow, enemyCol)
                    distToEnemy.append([dist, (enemyRow, enemyCol)])
                    if dist <= 10:
                        localEnemyAnts.append((enemyRow, enemyCol))
                        
                # Use closest enemy ant as goal
                distToEnemy.sort()
                if len(distToEnemy) > 0:
                    enemyLoc = distToEnemy[0][1]
                    enemyNearby = True
                else:
                    enemyNearby = False

                # Sets up hunters and bodyguards
                if enemyNearby and (antRow, antCol) in hunterAnts:
                    # Ant already Hunting
                    # check locations around hunterAnts[(antRow, antCol)][1][-1]
                    # If enemyLoc == hunterAnts[(antRow, antCol)][1][-2]:
                    #   remove last location in path remove old enemyloc, append New, else:
                    # append to path
                    # If not in surrounding locations, 
                    #   find path from last location to current enemyLoc
                    #   append result to path
                    #   remove old enemyloc, append New
                    # If hunterAnts[(antRow, antCol)][1] is empty,
                    #   remove hunterAnts from dictionary
                    fl.write("SETTING UP HUNTERS AND GUARDS, ")
                    surroundingEnemy = {}
                    pathToEnemy = hunterAnts[(antRow, antCol)][1]
                    lastKnownEnemy = pathToEnemy[-1]
                    for d in ['n','e','w','s']:
                        surroundingEnemy[tuple(map(operator.add, (lastKnownEnemy[0], lastKnownEnemy[1], AIM[d])))] = d
                    if enemyLoc == hunterAnts[(antRow, antCol)][1][-2]:
                        pathToEnemy.pop(-1)
                    elif enemyLoc in surroundingEnemy:
                        newEnemyRow, newEnemyCol = ants.destination(lastKnownEnemy[0], lastKnownEnemy[1], surroundingEnemy[enemyLoc])
                        pathToEnemy.append((newEnemyRow, newEnemyCol))
                    else:
                        pathToNewEnemy = Astar(lastKnownEnemy, enemyLoc, 4, 1024)
                        for p in pathToNewEnemy:
                            if p != lastKnownEnemy:
                                pathToEnemy.append(p)
                    if not hunterAnts[(antRow, antCol)][1]:
                        currentGuards = hunterAnts[(antRow, antCol)[0]]
                        for g in currentGuards:
                            if g in guardAnts:
                                del guardAnts[g]
                        del hunterAnts[(antRow, antCol)]
                            
                        
                        
                elif enemyNearby and (antRow, antCol) in guardAnts:
                    # Ant is bodygaurd for hunter
                    # if len(guardPath) < len(hunterPath):
                    #   get directions from hunter guardAnts[(antRow, antCol)][0]
                    #   while guardPath length < hunterPath length:
                    #       check destination(hunterPathNext, direction)
                    #       if passable, append to guardPath
                    #       else, not passable, try other directions
                    #       if ran out of directions, break from loop
                    # else if length of guardPath > hunterPath:
                    #   delete end of guard Path up to length of hunterPath
                    # else path is OK
                    fl.write("BODYGUARD FOR " + str(guardAnts[(antRow,antCol)][0])+", ")
                    guardPath = guardAnts[(antRow, antCol)][1]
                    hunterPath = hunterAnts[guardAnts[(antRow, antCol)][0]][1]
                    if len(guardPath) < len(hunterPath):
                        hunter = guardAnts[(antRow, antCol)][0]
                        directionFromHunter = ants.direction(hunter[0],hunter[1], antRow, antCol)
                        index = len(hunterPath) - len(guardPath)
                        while len(guardPath) < len(hunterPath):
                            for d in directionFromHunter:
                                nextRow, nextCol = ants.destination(hunterPath[index][0], hunterPath[index][1], d)
                                if ants.passable(nextRow, nextCol):
                                    guardPath.append((nextRow, nextCol))
                                    appendSuccessful = True
                                    break
                                else:
                                    appendSuccessful = False
                            if not appendSuccessful:
                                break
                    elif len(guardPath) > len(hunterPath):
                        while len(guardPath) > len(hunterPath):
                            guardPath.pop(-1)
                            
                    
                elif enemyNearby and enemyLoc not in enemyLocations:
                    # No ant chasing enemy, set as hunter
                    # append enemyLoc to enemyLocations
                    # find path from current ant to enemy
                    # add current ant plus path to dictionary, empty guardList
                    fl.write("HUNTING ANT " + str(enemyLoc)+", ")
                    enemyLocations.append(enemyLoc)
                    newPath = Astar((antRow, antCol), enemyLoc, 12, 8192)
                    newPath.pop(0)
                    hunterAnts[(antRow, antCol)] = [[],newPath]

                    
                elif (antRow, antCol) not in hunterAnts and (antRow, antCol) not in guardAnts:
                    # If hunter nearby, set as guard
                    aroundAnt = ants.surrounding_area(antRow, antCol)
                    # If other ant in location aroundAnt and other ant is a hunter:
                    #   set current ant to guard hunter, get direction and set list properly
                    for loc in aroundAnt:
                        if loc in hunterAnts:
                            g,p = hunterAnts[loc]
                            g.append((antRow, antCol))
                            dirFromHunter = ants.direction(loc[0],loc[1],antRow,antCol)
                            currRow = antRow
                            currCol = antCol
                            gPath = []
                            for dests in p:
                                nextRow, nextCol = ants.destination(currRow,currCol,dirFromHunter)
                                gPath.append((nextRow,nextCol))
                                currRow = nextRow
                                currCol = nextCol
                            guardAnts[(antRow, antCol)] = [loc, gPath]
                            fl.write("GUARDING ANT " + str(loc)+", ")
                            break

                # performs hunting actions
                if (antRow, antCol) in hunterAnts:
                    antHunting = True
                    # If len(localEnemyAnts) < len(hunterAnts[(antRow, antCol)][0]):
                    #   Move to next spot in path
                    #   safeToMove = True
                    # else:
                    #   stay put
                    #   safeToMove = False
                    #
                    # issue Order
                    if len(localEnemyAnts) < len(hunterAnts[(antRow, antCol)][0]):
                        destRow, destCol = hunterAnts[(antRow,antCol)][1][0]
                        safeToMove = True
                        possibilities = []
                        if ants.passable(destRow, destCol) and ants.unoccupied(destRow, destCol):
                            fl.write("HUNTING MOVE TO " + str(destRow)+','+str(destCol)+", ")
                            hunterAnts[(antRow,antCol)][1].pop(0)
                            direction = ants.direction(antRow, antCol, destRow, destCol)[0]
                            possibilities.append([antRow, antCol, direction])
                            for g in hunterAnts[(antRow, antCol)][0]:
                                if g in guardAnts:
                                    guardAnts[g][0] = (destRow, destCol)
                    else:
                        safeToMove = False

                    issueOrder(antRow, antCol, possibilities)
                        
                            
                elif (antRow, antCol) in guardAnts and safeToMove:
                    # If next move not blocked:
                    #   Move to next spot in path
                    # else:
                    #   look for better position
                    #   what is my new direction relative to hunter?
                    #   set direction list
                    # Issue order
                    antHunting = True
                    nextMove = guardAnts[(antRow, antCol)][1][0]
                    possibilites = []
                    if ants.passable(nextMove[0], nextMove[1]) and ants.unoccupied(nextMove[0],nextMove[1]):
                        fl.write("GUARD MOVE TO " + str(nextMove[0])+','+str(nextMove[1])+", ")
                        guardAnts[(antRow, antCol)][1].pop(0)
                        direction = ants.direction(antRow, antCol, nextMove[0], nextMove[1])[0]
                        possibilities.append([antRow, antCol, direction])
                        myHunter = guardAnts[(antRow, antCol)][0]
                        guards = hunterAnts[myHunter][0]
                        for g in guards:
                            if g == (antRow, antCol):
                                guards.remove((antRow, antCol))
                                guards.append(nextMove)
                        hunter, path = guardAnts[(antRow, antCol)]
                        del guardAnts[(antRow, antCol)]
                        guardAnts[nextMove] = [hunter, path]
                    else:
                        for d in allDirections:
                            nextRow, nextCol = ants.destination(antRow, antCol, d)
                            if ants.passable(nextRow, nextCol) and ants.unoccupied(nextRow, nextCol):
                                fl.write("GUARD MOVE TO " + str(nextRow)+','+str(nextCol)+", ")
                                guardAnts[(antRow, antCol)][1].pop(0)
                                possibilities.append([antRow, antCol, d])
                                myHunter = guardAnts[(antRow, antCol)][0]
                                guards = hunterAnts[myHunter][0]
                                for g in guards:
                                    if g == (antRow, antCol):
                                        guards.remove((antRow, antCol))
                                        guards.append((nextRow, nextCol))
                                hunter, path = guardAnts[(antRow, antCol)]
                                del guardAnts[(antRow, antCol)]
                                guardAnts[(nextRow, nextCol)] = [hunter, path]
                                break
                    issueOrder(antRow, antCol, possibilities)
                    
                else:
                    antHunting = False





        #########################################
        ######          GATHERERS           #####
        #########################################
            if notEscaping and not antHunting:
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
                        elif len(antsLookingForFood) < gathererAnts:
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
                            todoList = [[(antRow, antCol), [(antRow, antCol)]]]
                            pathToFood[indexOfTodoList] = BFS((antRow, antCol), foodLoc, todoList, 10, 768)
                            
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
                            # If the next tile is unoccupied and not in queue, send order
                            if ants.unoccupied(currentPath[0], currentPath[1]) and (currentPath[0], currentPath[1]) not in destinations:
                                possibilities = []
                                possibilities.append([antRow, antCol, direction])
                                fl.write("GATHERING FOOD, ")
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
                        fl.write("AT A JUNCTION, ")
                    elif (antRow, antCol) in deadEnds:
                        fl.write("AT A DEAD END, ")
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
                    fl.write("EXPLORING MAP, ")
                    issueOrder(antRow, antCol, possibilities)
                    fl.write('\n------\n')
    
       
             
       
                              
                      
                  
       
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
