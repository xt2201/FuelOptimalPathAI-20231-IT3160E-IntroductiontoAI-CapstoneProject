import numpy as np
import pandas as pd
import math
import queue
import AIProjectData as Data
import inflect
import sys
from time import time


start_time = time()
p = inflect.engine()

AllData = Data.data
NumberLevel = Data.NumberLevel

Intervals = [(0,2)]
for _ in range (len(NumberLevel)):
    interval = (Intervals[-1][1], Intervals[-1][1] + NumberLevel[_])
    Intervals.append(interval)
Intervals.pop(0)
Intervals = Intervals[: -1] + [(1,2)] + [Intervals[-1]]


def interval_norm(interval):
    norm  = interval[1] - interval[0]
    return norm

def MakeFramePoint_Point(index):  ## index: điểm bắt đầu
    def MakeGraph(df, interval1, interval2,p, index):  ## interval1: khoảng điểm bắt đầu   ,    interval2: khoảng điểm đến
        graph = {}
        lst = []
        for i in range (interval1[0], interval1[1]) :
            for j in range (interval2[0], interval2[1]):
                lst.append(Data.haversine(((df["Latitude"].iloc[i],df["Longitude"].iloc[i]), 
                                        (df["Latitude"].iloc[j],df["Longitude"].iloc[j]))))
            graph[p.number_to_words(p.ordinal(index)) + 'Level' + f"{i - interval1[0] +1 }"] = lst
            lst = []
        return graph

    graph = MakeGraph(AllData, Intervals[index -1], Intervals[index], p, index)
    df = pd.DataFrame(graph, [p.number_to_words(p.ordinal(index + 1))+ "Level" + f"{i}" for i in range (1 , NumberLevel[index] + 1)])
    return df

def MakeGraphStart_1(df):
    graph = {}
    lst = []
    for i in range (Intervals[0][0], Intervals[0][1]):
        lst.append(Data.haversine(((df["Latitude"].iloc[0], df["Longitude"].iloc[0]) ,
                                   (df["Latitude"].iloc[i], df["Longitude"].iloc[i]))))
    graph[f"Start"] = lst
    return graph
graphS1 = MakeGraphStart_1(AllData)
dfS1 = pd.DataFrame(graphS1, index = [f"firstLevel{i}" for i in range (1, NumberLevel[0] +1)])
DataFrame  = [dfS1]

for i in range (1, len(NumberLevel)-1):
    df = MakeFramePoint_Point(i)
    DataFrame.append(df)

def MakeGraphLast_Finish(df, last = len(NumberLevel)-1):
    graph = {}
    lst = []
    for i in range (Intervals[-3][0], Intervals[-3][1]):
        lst.append(Data.haversine(((df["Latitude"].iloc[i],df["Longitude"].iloc[i]), 
                                   (df["Latitude"].iloc[1],df["Longitude"].iloc[1]))))
        graph[p.number_to_words(p.ordinal(last)) + 'Level' + f"{i - Intervals[-3][0] +1 }"] = lst
        lst = []

    return graph
graphLF = MakeGraphLast_Finish(AllData)
dfLF = pd.DataFrame(graphLF, ["Finish"])

DataFrame.append(dfLF)


def MakeFramePoint_Station(index):
    def MakeGraphPoint_Station(df, interval, p, index):
        graph = {}
        lst = []
        for i in range (interval[0], interval[1]):
            for j in range (Intervals[-1][0], Intervals[-1][1]):
                lst.append(Data.haversine(((df["Latitude"].iloc[i],df["Longitude"].iloc[i]), 
                                        (df["Latitude"].iloc[j],df["Longitude"].iloc[j]))))
            graph[p.number_to_words(p.ordinal(index)) + 'Level' + f"{i - interval[0] +1 }"] = lst
            lst = []

        return graph
    graph = MakeGraphPoint_Station(AllData, Intervals[index -1], p, index)
    df = pd.DataFrame(graph, ["Station" + f"{i}" for i in range (1 , NumberLevel[-1] + 1)])
    return df

dfSt = pd.DataFrame()


def MakeGraphStation_Finish(df):
    graph = {}
    lst = []
    for j in range (Intervals[-1][0], Intervals[-1][1]):
        lst.append(Data.haversine(((df["Latitude"].iloc[1],df["Longitude"].iloc[1]), 
                                   (df["Latitude"].iloc[j],df["Longitude"].iloc[j]))))
    graph["Finish"] = lst
    lst = []

    return graph

def MakeGraphStation_Start(df):
    graph = {}
    lst = []
    for j in range (Intervals[-1][0], Intervals[-1][1]):
        lst.append(Data.haversine(((df["Latitude"].iloc[0],df["Longitude"].iloc[0]), 
                                   (df["Latitude"].iloc[j],df["Longitude"].iloc[j]))))
    graph["Start"] = lst
    lst = []

    return graph

def MakeGraphStation_Station(df):
    graph = {}
    lst = []
    for i in range (Intervals[-1][0], Intervals[-1][1]):
        for j in range (Intervals[-1][0], Intervals[-1][1]):
            lst.append(Data.haversine(((df["Latitude"].iloc[i],df["Longitude"].iloc[i]), 
                                        (df["Latitude"].iloc[j],df["Longitude"].iloc[j]))))
        graph[f"Station{i - Intervals[-1][0] + 1}"] = lst
        lst = []

    return graph

graphStF = MakeGraphStation_Finish(AllData)
graphStS = MakeGraphStation_Start(AllData)
graphStSt = MakeGraphStation_Station(AllData)
dfSt = pd.concat([dfSt, pd.DataFrame(graphStS, [f"Station{i}" for  i in range (1, NumberLevel[-1]+ 1)])], axis=1)
dfSt = pd.concat([dfSt, pd.DataFrame(graphStF, [f"Station{i}" for  i in range (1, NumberLevel[-1]+ 1)])], axis=1)
for i in range (1,len(NumberLevel)):
    df = MakeFramePoint_Station(i)
    dfSt = pd.concat([dfSt, df], axis=1)
dfSt = pd.concat([dfSt, pd.DataFrame(graphStSt,[f"Station{i}" for  i in range (1, NumberLevel[-1]+ 1)])], axis=1)
dfSt = dfSt.T


def DropStationDataFrame(df, interval):
    for _ in range(interval_norm(interval)):
        df = df.drop(df.index[0], axis = 0)
    return df

count = 0
store_distance = []
steppriorityQueue = Data.PriorityQueue()
priorityQueue = Data.PriorityQueue()

def PointPath(node, path, interval, df, AllData, fuel, distance, level):  
    global count 
    global dfSt
    steppriorityQueue = Data.PriorityQueue()
    # priorityQueue = queue.PriorityQueue() # ( heuristic value, [name, distance] ) 
    curr_level = level 
    priorityQueue_Station = queue.PriorityQueue()
    for i in range (interval_norm(interval[level-1])):
        successor = df[level-1][node].index[i]
        if successor == "Finish":
            priorityQueue.put([df[level-1][node].index[i], df[level-1][node].iloc[i]],
                              -level,
                              AllData["Distances to finish point"].iloc[i+interval[level-1][0]] + df[level-1][node].iloc[i] + distance)
        else:
            for j in range (interval_norm(interval[level])):
                steppriorityQueue.put([df[level-1][node].index[i], df[level-1][node].iloc[i]],
                                   -level,
                                    AllData["Distances to finish point"].iloc[j+interval[level][0]] + df[level-1][node].iloc[i] + df[level][successor].iloc[j] + distance)
            min, key1, key2 = steppriorityQueue.get()
            steppriorityQueue = Data.PriorityQueue()
            priorityQueue.put(min, key1, key2)
                
        # priorityQueue.put([df[level-1][node].index[i], df[level-1][node].iloc[i]],                                                      ## Tên
        #                   -level,                                                                                                       ## Key 1
        #                   AllData["Distances to finish point"].iloc[i+interval[level-1][0]] + df[level-1][node].iloc[i] + distance)     ## Key 2
    while priorityQueue.empty() == False:
        current = priorityQueue.get()
        count += 1
        traverse_level = -current[1]
        if traverse_level >= curr_level:
            pass
        else:
            distance -= store_distance[-1]
            fuel += store_distance[-1]
            path.pop(-1)
            curr_level = traverse_level
        if current[0][1] > fuel: ## Fuel constraint is violated

            ## Visit Station
            for i in range (1, interval_norm(Intervals[-1]) + 1):
                if dfSt[f"Station{i}"].loc[node] > fuel:
                    continue
                else:
                    priorityQueue_Station.put((dfSt.loc["Finish"].iloc[i-1] + dfSt.loc[node].iloc[i-1] + distance , 
                                            [dfSt.loc[node].index[i-1] ,dfSt.loc[node].iloc[i-1]]))
                    
            ## If there is no station satisfy, then backtrack to visit other point
            if priorityQueue_Station.empty() == True:
                # current = priorityQueue.get()[1] #Backtracking
                # path.append(current[0])
                # distance += current[1]
                # fuel -= current[1]
                continue

            ## If there exist a station satisfy
            else:
                current = priorityQueue_Station.get()[1]
                count += 1
                distance += current[1]
                store_distance.append(current[1])
                fuel = fuel_capacity
                path.append(current[0])
                # if level != 1:
                #     dfSt = DropStationDataFrame(dfSt, Intervals[level - 1 - 1])
                priorityQueue_Station = queue.PriorityQueue()
                ## Execute StationPath when current position is a station
                current, path, distance, fuel = StationPath(current[0], path, Intervals, dfSt, DataFrame ,AllData, fuel_capacity, distance, traverse_level)

            
        else:  ## Fuel constraint is satisfied
            distance += current[0][1]
            store_distance.append(current[0][-1])
            fuel -= current[0][1]
            path.append(current[0][0])
            # if level != 1:
            #     dfSt = DropStationDataFrame(dfSt, Intervals[level - 1 - 1])
    ## Back to previous level if there is no point satisfied
        if curr_level >= level:
            return current, path, distance, fuel
        else:
            for i in range (level - curr_level -1,-1,-1):
                current, path, distance, fuel = PointPath(path[-1], path, Intervals, DataFrame, AllData, fuel, distance, level-i)
            return current, path, distance, fuel
    

def StationPath(node, path, interval, df, dfp , AllData, fuel, distance, level):  ## Hàng dọc là điểm bắt đầu, Hàng ngang là điểm cần đến
    global count
    stepQueue = queue.PriorityQueue()
    pQueue = queue.PriorityQueue()
    priorityQueue_Station = queue.PriorityQueue()
    # for i in range (interval_norm(interval[level-1])):
    #     pQueue.put((AllData["Distances to finish point"].iloc[i+interval[level-1][0]] + df[node].iloc[i + interval[level-1][0] ] + distance,
    #                       [df[node].index[i+ interval[level-1][0] ], df[node].iloc[i+ interval[level-1][0] ]]))
    for i in range (interval_norm(interval[level-1])):
        successor = df[node].index[i + interval[level-1][0]]
        if successor == "Finish":
            pQueue.put(( AllData["Distances to finish point"].iloc[i+interval[level-1][0]] + df[node].iloc[i+ interval[level-1][0]] + distance,
                        [df[node].index[i + interval[level-1][0]], df[node].iloc[i + interval[level-1][0]]]))
        else:
            try:
                for j in range (interval_norm(interval[level])):
                    stepQueue.put((AllData["Distances to finish point"].iloc[j+interval[level][0]] + df[node].iloc[i + interval[level-1][0]] + dfp[level][successor].iloc[j] + distance,
                                [df[node].index[i + interval[level-1][0]], df[node].iloc[i + interval[level-1][0]]]))
                min = stepQueue.get()
                pQueue.put(min)

            except:
                print(successor)
    while pQueue.empty() == False:
        current = pQueue.get()[1]
        count += 1
        if current[1] > fuel:
            for i in range (1, interval_norm(Intervals[-1]) + 1):
                if dfSt[f"Station{i}"].loc[node] > fuel:
                    continue
                else:
                    priorityQueue_Station.put((dfSt.loc["Finish"].iloc[i-1] + dfSt[node].iloc[i-1] + distance , 
                                             [dfSt.loc[node].index[i-1] ,dfSt.loc[node].iloc[i-1]]))
                
            ## 
            if priorityQueue_Station.empty() == True:  ## There is no station satisfied --> Choose another point
                # current = priorityQueue.get()[1] #Backtracking
                # path.append(current[0])
                # distance += current[1]
                # fuel -= current[1]
                continue
            else:  ## When there is a station satisfied
                while priorityQueue.empty() != True:
                    current = priorityQueue_Station.get()[1]
                    count += 1
                    if current[0] != path[-1]:
                        distance += current[1]
                        store_distance.append(current[-1])
                        fuel = fuel_capacity
                        path.append(current[0])
                        priorityQueue_Station = queue.PriorityQueue()
                        current, path, distance, fuel = StationPath(current[0], path, interval, dfSt, DataFrame , AllData, fuel_capacity, distance, level)
                        return current, path, distance, fuel
                    else:
                        continue
        else:
            distance += current[1]
            store_distance.append(current[-1])
            fuel -= current[1]
            path.append(current[0])
            return current, path, distance, fuel
        

def Astar():
    global current, path, distance, fuel, AllData
    for k in range (len(Intervals)-1):
        # try:
        #     current, path, distance, fuel = PointPath(path[-1], path, Intervals[k], DataFrame[k], AllData, fuel, distance)
        # except:
        #     print("bước cuối")
        #     break
        current, path, distance, fuel = PointPath(path[-1], path, Intervals, DataFrame, AllData, fuel, distance, k+1)
        # print("Đường đi hiện tại:", path, "     Khoảng cách:", distance) 

    return path, distance

lst = []
for i in range (len(Intervals)-1):
    a = dfSt[Intervals[i][0]: Intervals[i][1]].min().min()  ## --> ra được station có thể đi được, kết nối => cần tìm khoảng cách nhỏ nhất để đến được node đó
    lst.append(a)



current = ["Start", 0]
distance = 0
path = ["Start"]
fuel_capacity = Data.fuel_capacity
fuel = fuel_capacity


path, distance = Astar()
node_expanded = count