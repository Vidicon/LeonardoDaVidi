import random
import numpy as np
from ..bot_control import Move
from pprint import pprint
import math

debug = False
if debug:
    import matplotlib.pyplot as plt
import time

class LeonardoDaVidi:

    def __init__(self):
        self.gridmap = np.zeros((1, 1), dtype=np.float64)
        self.myid = 0

        if debug:
            self.fig = None
            self.ax = None
            self.fig, self.ax = plt.subplots()
        
        

    def get_name(self):
        return "LeonardoDaVidi"

    def get_contributor(self):
        return "Bram Fenijn"
    
    def can_overwrite(self, id, tile):
        if tile == 0: return True
        return (id - tile) % 3 == 2

    def find_highest_average_area(self):
        max_average = 0
        max_average_pos = (0,0)

        # return max_average_pos
    
        for i in range(4,self.gridmap.shape[0] - 7):
            for j in range(4,self.gridmap.shape[1] - 7):
                # Get 8x8 subarray
                subarray = self.gridmap[i:i+8, j:j+8]
                # Compute average of subarray
                subarray_average = np.average(subarray)
                # Check if subarray average is higher than current max average
                
                if subarray_average > max_average:
                    print('more')
                    max_average = subarray_average
                    max_average_pos = (j,i)
                print(f'pos: [{i},{j}],  subarray_average:{subarray_average}, max_average:{max_average}')

        return max_average_pos
    
    def convolve2d(self, image, kernel, mode='same', boundary='fill'):
        # Define padding depending on boundary conditions
        if boundary == 'fill':
            padding = [(kernel.shape[0]-1)//2, (kernel.shape[1]-1)//2]
            padded_image = np.pad(image, padding, mode='constant', constant_values=0)
        elif boundary == 'symm':
            padding = [(kernel.shape[0]-1)//2, (kernel.shape[1]-1)//2]
            padded_image = np.pad(image, padding, mode='symmetric')
        elif boundary == 'wrap':
            padded_image = np.pad(image, kernel.shape[0]-1, mode='wrap')
        else:
            raise ValueError('Invalid boundary condition')
        
        # Compute output size depending on mode
        if mode == 'same':
            output_size = image.shape
        elif mode == 'valid':
            output_size = (image.shape[0] - kernel.shape[0] + 1, image.shape[1] - kernel.shape[1] + 1)
        else:
            raise ValueError('Invalid mode')
        
        # Compute convolution
        output = np.zeros(output_size, dtype=image.dtype)
        for i in range(output_size[0]):
            for j in range(output_size[1]):
                output[i,j] = np.sum(padded_image[i:i+kernel.shape[0], j:j+kernel.shape[1]] * kernel)
        
        return output

    def find_n_smooth_peaks(self, n, window_size=11):
        smoothed_map = self.gridmap.copy()
        # apply a moving average filter to smooth the map
        kernel = np.ones((window_size, window_size)) / (window_size * window_size)
        smoothed_map = self.convolve2d(smoothed_map, kernel, mode="same", boundary="symm")
        # initialize peak coordinates list
        peaks = []
        for i in range(1, self.gridmap.shape[0] - 1):
            for j in range(1, self.gridmap.shape[1] - 1):
                # check if the current element is a peak
                if (smoothed_map[i,j] > smoothed_map[i-1,j] and 
                    smoothed_map[i,j] > smoothed_map[i+1,j] and 
                    smoothed_map[i,j] > smoothed_map[i,j-1] and 
                    smoothed_map[i,j] > smoothed_map[i,j+1]):
                    # add the current peak to the list of peaks
                    peaks.append((i,j))
        # sort the peaks by their values in descending order
        sorted_peaks = sorted(peaks, key=lambda x: self.gridmap[x[0],x[1]], reverse=True)
        # return the n highest peaks
        return sorted_peaks[:n]

                

    def display_gridmap(self,target_pos, enemies, peak_list):
        self.ax.clear()
        
        
        plt.ion()
        
        self.ax.imshow(self.gridmap, cmap='PRGn', origin='lower', vmin= -1, vmax= 1) #
        for enemie in enemies:
            circle = plt.Circle(enemie["position"], 0.5, color='r', fill=False)
            if self.can_overwrite(self.myid, enemie["id"]):
                circle = plt.Circle(enemie["position"], 0.5, color='g', fill=False)
            if enemie["id"] == self.myid:
                circle = plt.Circle(enemie["position"], 0.5, color='b', fill=True)
            
            self.ax.add_patch(circle)
        
        # if target_pos is not None:
        #     rec = plt.Rectangle ((target_pos[0]-2, target_pos[1]-2), 4,4, color='w', fill=False)
        #     self.ax.add_patch(rec)

        for peak in peak_list:
            rec = plt.Rectangle ((peak[1]-2, peak[0]-2), 4,4, color='w', fill=False)
            self.ax.add_patch(rec)

        plt.grid(True)
        plt.show()
        plt.pause(0.001)
    
    def get_enemie_score(self, pos, enemies): # high score is good
        score = 0.0

        for enemie in enemies:
            if enemie["id"] == self.myid:
                continue

            distance = math.dist(enemie["position"], pos)
            max_dis = 10
            distance = min(max_dis, distance)


            if self.can_overwrite(self.myid, enemie["id"]):
                distance_score = (max_dis - distance) / max_dis
                if distance == 0:
                    distance_score = -0.5

                # print(f'enemie: {enemie["id"]}, can override, dis:{distance}, score:{distance_score}')
                score += distance_score * 1.0
            else:
                distance_score = (max_dis - distance) / max_dis
                # print(f'enemie: {enemie["id"]}, cant override, dis:{distance}, score:{distance_score}')
                score -= distance_score * 1.0

        score = min(max(score, -1), 1)
              

        return score
    
    def calculate_tile_score(self, pos, grid, enemies, use_tile_score = True, use_enemies_score = True):
        score = 0
        if use_tile_score:
            tile_value = grid[pos[0]][pos[1]]
            if tile_value == 0:
                score = 0.5 # is white, can override
            elif self.can_overwrite(self.myid, tile_value):
                score = 0.8 # is other player, can override, (if we overrite this we remove % from other)
            elif tile_value == self.myid:
                score = -0.8 # my id will do nothing
            else:
                score = -0.5 # cant overrite wil only remove from other player 

        if use_enemies_score:
            score += self.get_enemie_score((pos[1],pos[0]), enemies) * 1.0
        return min(max(score, -1), 1)

    def gridmap_update(self, grid, enemies):
        for i in range(self.gridmap.shape[0]):
            for j in range(self.gridmap.shape[1]):
                self.gridmap[i][j] = self.calculate_tile_score((i,j), grid, enemies)
                

    def path_plan(self):
        path = []
        return path

    def get_grid_tile(self, pos, x=0, y=0):
        if pos[1] + x < 0 or pos[1] + x > self.gridmap.shape[0]-1:
            return -1.0
        if pos[0] + y < 0 or pos[0] + y > self.gridmap.shape[1]-1:
            return -1
        
        return self.gridmap[pos[1] + x][pos[0]+y]
    
    def determine_move(self, target):
        move = Move.STAY
        
        max = -1.0
        if debug:
            print(f'pos: [{self.position[1]},{self.position[0]}]')

        tile = self.get_grid_tile(self.position, 0, 1)
        if debug:
            print(f'right: {tile}')
        if tile > max:
            max = tile
            move = Move.RIGHT

        tile = self.get_grid_tile(self.position, 0, -1)
        if debug:
            print(f'left: {tile}')
        if tile > max:
            max = tile
            move = Move.LEFT

        tile = self.get_grid_tile(self.position, 1, 0)
        if debug:
            print(f'up: {tile}')
        if tile > max:
            max = tile
            move = Move.UP

        tile = self.get_grid_tile(self.position, -1, 0)
        if debug:
            print(f'down: {tile}')
        if tile > max:
            max = tile
            move = Move.DOWN


        if debug:
            print(f'max: {max} move: {move}')
      
        if move == Move.STAY:
            move = Move.DOWN

        return move
    
    def determine_next_move(self, grid, enemies, game_info):
        pos_x = self.position[0]
        pos_y = self.position[1]
        grid_size = grid.shape[0]

        self.myid = self.id
        if self.gridmap.shape[0] == 1 or True:
            self.gridmap = np.zeros((grid_size, grid_size), dtype=np.float64)
        
        self.gridmap_update(grid, enemies)

        # peak_list = self.find_n_smooth_peaks(3)
        # target_pos = self.find_highest_average_area()
        target_pos = (0,0)
        peak_list = []
        # print(target_pos)

        next_move = self.determine_move(target_pos)

        if debug:
            self.display_gridmap(target_pos, enemies, peak_list)

        return next_move
    

# Tournament finished in 4335 seconds
# Ran tournament of 200 games of 2000 rounds each.
# ============================================================
# The Final Scores
# ============================================================
# Rank Name                          Contributor         Avg [us]       Score    
# 1    Hein Won't Let Me Cheat       Lewie               930.355        8.676   %
# 2    Atilla the Attacker           Jorik de Vries      874.738        8.205   %
# 3    Kadabra                       Rayman              603.089        7.639   %
# 4    Picasso                       Daniel              587.833        6.936   %
# 5    Abra                          Rayman              126.965        6.442   %
# 6    LeonardoDaVidi                Bram Fenijn         80653.641      6.233   %
# 7    The Clueless African          JP Potgieter        49.336         5.855   %
# 8    Short Sighted Steve           Nobleo              84.727         5.409   %
# 9    Greedy Gerard                 Rayman              71.357         4.756   %
# 10   LeaRoundo Da Vinci            Hein                820.601        4.32    %
# 11   Big Ass Bot                   Mahmoud             82.598         4.129   %
# 12   Vector                        Ishu                20.281         4.127   %
# 13   ShortSpanDog                  Felipe              20.826         4.122   %
# 14   Rambo The Rando               Nobleo              20.199         4.068   %
# 15   Aslan                         Hakan               21.092         4.054   %
# 16   RapidRothko                   Jorik de Vries      11.06          3.663   %
# 17   RickbrandtVanRijn             Rick Voogt          2.108          0.079   %



# ============================================================
# Best Efficiency
# ============================================================
# Rank Name                          Contributor         Avg [us]       Score [%]   Efficiency [%/us]
# 1    RapidRothko                   Jorik de Vries      11.06          3.663       0.331
# 2    Vector                        Ishu                20.281         4.127       0.203
# 3    Rambo The Rando               Nobleo              20.199         4.068       0.201
# 4    ShortSpanDog                  Felipe              20.826         4.122       0.198
# 5    Aslan                         Hakan               21.092         4.054       0.192
# 6    The Clueless African          JP Potgieter        49.336         5.855       0.119
# 7    Greedy Gerard                 Rayman              71.357         4.756       0.067
# 8    Short Sighted Steve           Nobleo              84.727         5.409       0.064
# 9    Abra                          Rayman              126.965        6.442       0.051
# 10   Big Ass Bot                   Mahmoud             82.598         4.129       0.05
# 11   RickbrandtVanRijn             Rick Voogt          2.108          0.079       0.037
# 12   Kadabra                       Rayman              603.089        7.639       0.013
# 13   Picasso                       Daniel              587.833        6.936       0.012
# 14   Atilla the Attacker           Jorik de Vries      874.738        8.205       0.009
# 15   Hein Won't Let Me Cheat       Lewie               930.355        8.676       0.009
# 16   LeaRoundo Da Vinci            Hein                820.601        4.32        0.005
# 17   LeonardoDaVidi                Bram Fenijn         80653.641      6.233       0.0