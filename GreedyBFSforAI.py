import pandas as pd
import numpy as np
import copy
import os
from assistedFunctions import *

import AIProjectData
data = AIProjectData.data
hier_index = AIProjectData.hier_index
NumberOfLevels = AIProjectData.NumberOfLevelsandStations - 1
levelPoints = []
for i in data.index.get_level_values(0).unique():
    levelPoints.append([j[1] for j in hier_index if j[0] == i])



data = data.reset_index().drop('level_0', axis = 1).set_index("level_1")



# Maximum distance allowed:
out_dist = AIProjectData.fuel_capacity

# ASSISTED FUNCTIONS
def queue_sort(path):
        # The heuristic is the number of levels unvisited
    count = np.array([0 for i in range(NumberOfLevels)])
    for i in path:
        for j in range(2, len(levelPoints) - 1):
            if i in levelPoints[j]:
                count[j-2] += 1
    return list(count > 0).count(False) 

def coordinate(node):
    ''' Return the coordinate of a node by accessing its name '''
    lat = data.loc[node, 'Latitude']
    long = data.loc[node, 'Longitude']
    return (lat, long)

def path_cost(path: list):
    ''' Return the distance when travelling through a path '''
    s = 0
    for i in range(len(path)-1):
        s += haversine((coordinate(path[i]), coordinate(path[i+1])))
    return s

def fuel_constraint(path):
    ''' Check if a path violates the fuel constraint or not '''
    # Find the index of the first station (not when the path[0] is a station) found in the path.
    for node in path:
        if node in levelPoints[-1]: 
            idx = path.index(node)
            if idx == 0:
                continue
            break
        else:
            idx = -1
    # The base cases when the path contains only one station, that station is the first element of the path OR when the path doesn't contain any stations.
    if idx == -1:
        dsta = path_cost(path)
        if path[-1] == 'Finish':
            if dsta > out_dist: return False
            else: return True
        else:
            if dsta >= out_dist: return False
            else: return True
    # The base cases when the path contains only one station, which is at the end of it OR the case when the path contains 2 stations, which are the endpoints of that path.
    if idx == len(path) - 1:
        d2sta = path_cost(path)
        if path[-1] in levelPoints[-1]:
            # Account for the case when the moment the vehicle gets to the next station, it is out of petrol.
            if d2sta > out_dist: return False
            else: return True
        else:
            if d2sta >= out_dist: return False
            else: return True
    else:
        lst1 = path[:(idx+1)]
        lst2 = path[idx:]
        if not fuel_constraint(lst1): return False
        else: 
            return fuel_constraint(lst2)
        
def check_levels(path):
    ''' Return the position of the next level to be visited 
    in a list of ['firstLevel', 'secondLevel', 'thirdLevel', ...., 'finalLevel']'''
    count = np.array([0 for i in range(NumberOfLevels)])
    for i in path:
        for j in range(2, len(levelPoints) - 1):
            if i in levelPoints[j]:
                count[j-2] += 1
                
    bool_count = list(count > 0)
    if False in bool_count:
        return list(count > 0).index(False) 
    else: return -1

def neighbours(path):
    ''' Return the list of neighbours to be expanded '''
    node = path[-1] # Here, node is the last element in the path list.
    dupLevelPoints = copy.deepcopy(levelPoints)
    
    for i in path: # Remove all visited nodes
        for j in range(2, len(dupLevelPoints)):
            if i in dupLevelPoints[j]:
                dupLevelPoints[j].remove(i)   
            
    if node == 'Start':
        neighbours = dupLevelPoints[2] + dupLevelPoints[-1]
        
    for j in range(2, len(dupLevelPoints)):
        if node in levelPoints[j]:
            if j == len(dupLevelPoints) - 1: # The last point in the path is a station.
                if check_levels(path) == -1: # All levels have been visited.
                    neighbours = ['Finish']
                else: 
                    neighbours = dupLevelPoints[check_levels(path) + 2]
                    # neighbours = dupLevelPoints[check_levels(path) + 2] + dupLevelPoints[-1]
            
            elif j == len(dupLevelPoints) - 2: # The last point in the path is in the final level
                neighbours = ['Finish'] + dupLevelPoints[-1]
            
            else: # The last point can be in any levels except the final one.
                neighbours = dupLevelPoints[j+1] + dupLevelPoints[-1]
    return neighbours

def printAnswer(path: list):
    if path == None:
        return 
    else:
        print('The path found is:')
        for i in path:
            if i != 'Finish':
                print(i, '->', end = ' ')
            else:
                print(i + '.')
    
        print('Distance travelled:', path_cost(path), 'km.')
        return
            

# THE ALGORITHM
def GreedyBestFirstSearch(start, goal):
    queue = [[start]]
    node_expanded = 0
    while queue:
        path = queue.pop(0)
        node = path[-1]
        node_expanded += 1
        if node == goal:
            # print('Number of nodes expanded:', nodes_expanded)
            return path,node_expanded
        
        if node in levelPoints[-2]: # If the final node in the path is of the final level.
            path.append('Finish')
            if fuel_constraint(path):
                # print('Number of nodes expanded:', nodes_expanded)
                return (path, node_expanded)
            else: path.remove('Finish')
        
        for neighbour in neighbours(path):
            new_path = list(path)
            new_path.append(neighbour)
            if fuel_constraint(new_path):
                queue.append(new_path)
        queue.sort(key = queue_sort)
    print('The algorithm has failed!!!')
    return 
 
path, node_expanded = GreedyBestFirstSearch('Start', 'Finish')
distance = path_cost(path)
