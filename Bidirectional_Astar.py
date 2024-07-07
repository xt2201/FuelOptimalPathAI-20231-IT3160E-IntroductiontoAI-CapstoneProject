import heapq
import AIProjectData as Data
import inflect
from time import time

import os
# os.chdir(r'C:\Users\Hello\OneDrive\Desktop\test AI')

start_time = time()
p = inflect.engine()

AllData = Data.data
NumberLevel = Data.NumberLevel

Intervals = [(0,2)]
for _ in range (len(NumberLevel)):
    interval = (Intervals[-1][1], Intervals[-1][1] + NumberLevel[_])
    Intervals.append(interval)
Intervals.pop(0)
Intervals = Intervals[: -1] + [(0,1)] + [Intervals[-1]]



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

    return graph

def MakeGraphStart_1(df):
    graph = {}
    lst = []
    for i in range (Intervals[0][0], Intervals[0][1]):
        lst.append(Data.haversine(((df["Latitude"].iloc[0], df["Longitude"].iloc[0]) ,
                                   (df["Latitude"].iloc[i], df["Longitude"].iloc[i]))))
    graph[f"Start"] = lst
    return graph
graphS1 = MakeGraphStart_1(AllData)

transformed_graphS1 = {}
for key, values in graphS1.items():
    transformed_values = [(f'firstLevel{i}', value) for i, value in enumerate(values, start=1)]
    transformed_graphS1[key] = transformed_values


level_graph_list = []
for i in range(1, len(NumberLevel)-1):
    level_graph = MakeFramePoint_Point(i)
    level_graph_list.append(level_graph)


def transform_nested_dicts(nested_dicts):
    transformed_graph_list = []
    p = inflect.engine()
    for i in range(len(nested_dicts)):
        transform_graph = {}
        for key, values in nested_dicts[i].items():
            x = p.number_to_words(p.ordinal(i + 2))
            transformed_values = [(f'{x}Level{i}', value) for i, value in enumerate(values, start=1)]
            transform_graph[key] = transformed_values
        transformed_graph_list.append(transform_graph)
    return transformed_graph_list
sub_level_graph = transform_nested_dicts(level_graph_list)
def combine_dictionaries(dictionaries):
    combined_dict = {}
    for dictionary in dictionaries:
        combined_dict.update(dictionary)
    return combined_dict
sub_level_graph2 = combine_dictionaries(sub_level_graph)

def combine_graphs(graph1, graph2):
    combined_graph = graph1.copy()
    for node, edges in graph2.items():
        if node in combined_graph:
            combined_graph[node].extend(edges)
        else:
            combined_graph[node] = edges
    return combined_graph
sub_level_graph3 = combine_graphs(transformed_graphS1, sub_level_graph2)


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

transformed_graphLF = {key: [('Finish', value[0])] for key, value in graphLF.items()}

combined_graphLevel = combine_graphs(sub_level_graph3, transformed_graphLF)

reversed_graphlevel = {}
for key, value in combined_graphLevel.items():
    for pair in value:
        dest_key, dest_value = pair
        if dest_key not in reversed_graphlevel:
            reversed_graphlevel[dest_key] = []
        reversed_graphlevel[dest_key].append((key, dest_value))


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
    return graph
station_graph_list = []
for i in range(1, len(NumberLevel)):
    station_graph = MakeFramePoint_Station(i)
    station_graph_list.append(station_graph)
def transform_nested_dicts1(nested_dicts):
    transformed_graph_list = []
    for i in range(len(nested_dicts)):
        transform_graph = {}
        for key, values in nested_dicts[i].items():
            transformed_values = [(f'Station{i}', value) for i, value in enumerate(values, start=1)]
            transform_graph[key] = transformed_values
        transformed_graph_list.append(transform_graph)
    return transformed_graph_list
sub_station_graph1 = transform_nested_dicts1(station_graph_list)
sub_station_graph2 = combine_dictionaries(sub_station_graph1)
def MakeGraphStation_Finish(df):
    graph = {}
    lst = []
    for j in range(Intervals[-1][0], Intervals[-1][1]):
        lst.append(Data.haversine(((df["Latitude"].iloc[1],df["Longitude"].iloc[1]), 
                                   (df["Latitude"].iloc[j],df["Longitude"].iloc[j]))))
    graph["Finish"] = lst
    lst = []

    return graph

def MakeGraphStation_Start(df):
    graph = {}
    lst = []
    for j in range(Intervals[-1][0], Intervals[-1][1]):
        lst.append(Data.haversine(((df["Latitude"].iloc[0],df["Longitude"].iloc[0]), 
                                   (df["Latitude"].iloc[j],df["Longitude"].iloc[j]))))
    graph["Start"] = lst
    lst = []

    return graph

def MakeGraphStation_Station(df):
    graph = {}
    lst = []
    for i in range(Intervals[-1][0], Intervals[-1][1]):
        for j in range(Intervals[-1][0], Intervals[-1][1]):
            lst.append(Data.haversine(((df["Latitude"].iloc[i],df["Longitude"].iloc[i]), 
                                        (df["Latitude"].iloc[j],df["Longitude"].iloc[j]))))
        graph[f"Station{i - Intervals[-1][0] + 1}"] = lst
        lst = []

    return graph

graphStF = MakeGraphStation_Finish(AllData)
graphStS = MakeGraphStation_Start(AllData)
graphStSt = MakeGraphStation_Station(AllData)
transformed_graphStS = {}
transformed_graphStF = {}
for key, values in graphStS.items():
    transformed_values = [(f'Station{i}', value) for i, value in enumerate(values, start=1)]
    transformed_graphStS[key] = transformed_values
for key, values in graphStF.items():
    transformed_values = [(f'Station{i}', value) for i, value in enumerate(values, start=1)]
    transformed_graphStF[key] = transformed_values

sub_station_graph3 = combine_graphs(transformed_graphStS,sub_station_graph2)
combined_graphStation = combine_graphs(sub_station_graph3, transformed_graphStF)

def transform_nested_dict3(nested_dict):
    transformed_dict = {}
    for level, stations in nested_dict.items():
        for station, value in stations:
            if station not in transformed_dict:
                transformed_dict[station] = []
            transformed_dict[station].append((level, value))
    return transformed_dict
transformed_combined_graphStation = transform_nested_dict3(combined_graphStation)

finish_distance = Data.distances_to_finish
name = Data.inside
forward_heuristics = dict(zip(name, finish_distance))

coordinates = Data.info
def create_new_list(old_list):
    new_list = [(t[0], t[1]) for t in old_list]
    return new_list

new_coordinates = create_new_list(coordinates)
start_coordinates = new_coordinates[0]
distance_to_start_point = []
for i in new_coordinates:
    x, y = i
    distance_to_start_point.append(Data.haversine(((x, y),
                                       start_coordinates)))

backward_heuristics = dict(zip(name, distance_to_start_point))

def bidirectional_astar(graph, start, goal, forward_heuristics, backward_heuristics, new_graph):
    def get_path(forward_parents, backward_parents, meeting_node):
        path = []
        node = meeting_node
        while node is not None:
            path.insert(0, node)
            node = forward_parents[node]
        node = backward_parents[meeting_node]
        while node is not None:
            path.append(node)
            node = backward_parents[node]
        return path
    def get_forward_path(forward_parents, node):
        path = []
        first_node = node
        while node is not None:
            path.insert(0, node)
            first_node = forward_parents[first_node]
        new_path = path[::-1]
        return new_path
    def get_backward_path(backward_parents, node):
        path = []
        first_node = node
        while node is not None:
            path.insert(0, node)
            first_node = backward_parents[first_node]

        return path
    forward_queue = [(0, start)]
    backward_queue = [(0, goal)]
    forward_visited = set()
    backward_visited = set()
    forward_distances = {start: 0}
    backward_distances = {goal: 0}
    forward_parents = {start: None}
    backward_parents = {goal: None}
    best_path = None
    best_cost = float('inf')
    node_explored = 0
    while forward_queue and backward_queue:
        forward_cost, forward_node = heapq.heappop(forward_queue)
        forward_visited.add(forward_node)
        node_explored += 1
        if forward_node in backward_visited:
            # Found a meeting point
            cost = forward_distances[forward_node] + backward_distances[forward_node]
            if cost < best_cost:
                best_cost = cost
                best_path = get_path(forward_parents, backward_parents, forward_node)

        for neighbor, distance in graph[forward_node]:
            new_cost = forward_distances[forward_node] + distance
            if neighbor == goal:
                if new_cost < best_cost:
                    best_cost = new_cost
                    best_path = get_forward_path(forward_parents, neighbor)
                    break
            elif neighbor not in forward_distances:
                forward_distances[neighbor] = new_cost
                forward_parents[neighbor] = forward_node
                heapq.heappush(forward_queue, (new_cost + forward_heuristics[neighbor], neighbor))


        backward_cost, backward_node = heapq.heappop(backward_queue)
        backward_visited.add(backward_node)
        node_explored += 1
        if backward_node in forward_visited:
            # Found a meeting point
            cost = backward_distances[backward_node] + forward_distances[backward_node]
            if cost < best_cost:
                best_cost = cost
                best_path = get_path(forward_parents, backward_parents, backward_node)

        for neighbor, distance in new_graph[backward_node]:
            new_cost = backward_distances[backward_node] + distance
            if neighbor == start:
                if new_cost < best_cost:
                    best_cost = new_cost
                    best_path = get_backward_path(backward_parents, neighbor)
                    break
            elif neighbor not in backward_distances:
                backward_distances[neighbor] = new_cost
                backward_parents[neighbor] = backward_node
                heapq.heappush(backward_queue, (new_cost + backward_heuristics[neighbor], neighbor))
    return best_path, best_cost, node_explored

start = "Start"
goal = "Finish"

def add_station(tmp_route, max_distance, graph1, graph2, graph3, tmp_best_cost):
    distance = []
    cost = tmp_best_cost
    for i in range(len(tmp_route) - 1):
        level_list = graph1[tmp_route[i]]
        for level_tuple in level_list:
            if level_tuple[0] == tmp_route[i + 1]:
                value = level_tuple[1]
                distance.append(value)
    new_distance = []
    sum = 0
    for i in distance:
        sum += i
        new_distance.append(sum)
    new_distance.insert(0, 0)
    remaining_tmp_distance = []
    for i in new_distance:
        remaining_tmp_distance.append(max_distance - i)
    distance.insert(0, 0)
    while any(num < 0 for num in remaining_tmp_distance):
        for i in range(1, len(remaining_tmp_distance)):
            if remaining_tmp_distance[i] < 0:
                total = 0
                station_list = graph2[tmp_route[i - 1]]
                sorted_station_list = sorted(station_list, key= lambda x: x[1])
                # tmp_route.insert(i, sorted_station_list[0][0])
                cost += sorted_station_list[0][1]
                for list_level in graph3[sorted_station_list[0][0]]:
                    if list_level[0] == tmp_route[i]:
                        cost += list_level[1]
                        total += list_level[1]
                tmp_route.insert(i, sorted_station_list[0][0])
                remaining_tmp_distance[i] = max_distance
                for j in range(i + 1, len(remaining_tmp_distance)):
                    total += distance[j]
                    remaining_tmp_distance[j] = max_distance - total
    return tmp_route, cost


max_distance = Data.fuel_capacity
best_path, best_cost, node_expanded = bidirectional_astar(combined_graphLevel, start, goal, forward_heuristics, backward_heuristics, reversed_graphlevel)
path, distance = (add_station(best_path, max_distance, combined_graphLevel, combined_graphStation, transformed_combined_graphStation, best_cost))



