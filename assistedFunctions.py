import math
import heapq

def haversine(pair: tuple): 
    ''' The distance (km) of any 2 points using their (latitude, longitude) coordinates'''
    x, y = pair
    latx, lonx = x
    laty, lony = y
    
    Earth_radius = 6731
    phi_x = math.radians(latx)
    phi_y = math.radians(laty)
    
    delta_phi = math.radians(laty - latx)
    delta_lambda = math.radians(lony - lonx)
    
    a = math.sin(delta_phi/2)**2 + math.cos(phi_x) * math.cos(phi_y) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    km = Earth_radius * c
    return km

def haversine_transformation(lst: list):
    return list(map(haversine, lst))

class PriorityQueue:  ## priority queue with 2 priority key
    def __init__(self):
        self.heap = []

    def put(self, item, priority1, priority2):
        heapq.heappush(self.heap, (priority1, priority2, item))

    def get(self):
        key1, key2, item = heapq.heappop(self.heap)
        return item, key1, key2
    
    def empty(self):
        if len(self.heap) == 0:
            return True
        



        
        return False
