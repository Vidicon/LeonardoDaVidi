import random
import numpy as np
from ..bot_control import Move
from pprint import pprint
import math

debug = True
if debug:
    import matplotlib.pyplot as plt
import time

class LeonardoDaVidi:

    def __init__(self):
        self.gridmap = np.zeros((1, 1), dtype=np.float64)

        # self.enemie_kernel =  np.array([[1, 2, 1],
        #                                 [2, 3, 2],
        #                                 [1, 2, 1]])
        
        # self.enemie_kernel =  np.array([[0, 0, 0],
        #                                 [0, 1, 0],
        #                                 [0, 0, 0]])
        
        # self.enemie_kernel =  np.array([[5, 0, 0, 0, 2],
        #                                 [0, 0, 0, 0, 0],
        #                                 [0, 0, 10, 0, 0],
        #                                 [0, 0, 0, 0, 0],
        #                                 [0, 0, 0, 0, 0],])

        # self.enemie_kernel =  np.array([[1, 2, 3, 2, 1],
        #                                 [2, 3, 4, 3, 2],
        #                                 [3, 4, 5, 4, 3],
        #                                 [2, 3, 4, 3, 2],
        #                                 [1, 2, 3, 2, 1],])
        
        
        # self.enemie_kernel = self.gaussian_kernel(size=9, sigma=1)
        # self.taken_kernel = self.gaussian_kernel(size=1, sigma=1)
        # print(self.enemie_kernel )
        
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
    
    

    # def add_kernel_to_gridmap2(self, kernel, position, multiplier=1):
    #     # Calculate the top-left corner of the kernel based on the specified position
    #     kernel_x = position[0] - (kernel.shape[0] - 1) // 2
    #     kernel_y = position[1] - (kernel.shape[1] - 1) // 2

    #     # Calculate the bottom-right corner of the kernel based on the top-left corner
    #     kernel_bottom_x = kernel_x + kernel.shape[0]
    #     kernel_bottom_y = kernel_y + kernel.shape[1]

    #     # Pad the gridmap with zeros to accommodate the kernel
    #     pad_width_x = (max(0, -kernel_x), max(0, kernel_bottom_x - self.gridmap.shape[0]))
    #     pad_width_y = (max(0, -kernel_y), max(0, kernel_bottom_y - self.gridmap.shape[1]))
    #     padded_gridmap = np.pad(self.gridmap, (pad_width_x, pad_width_y), mode='constant')

    #     # Multiply the kernel by the multiplier
    #     new_kernel = kernel * multiplier

    #     # Add the kernel to the padded gridmap at the specified position
    #     kernel_slice_x = slice(kernel_x + pad_width_x[0], kernel_bottom_x + pad_width_x[0])
    #     kernel_slice_y = slice(kernel_y + pad_width_y[0], kernel_bottom_y + pad_width_y[0])
    #     padded_gridmap[kernel_slice_x, kernel_slice_y] += new_kernel

    #     # Extract the desired portion of the padded gridmap
    #     gridmap_slice_x = slice(pad_width_x[0], pad_width_x[0] + self.gridmap.shape[0])
    #     gridmap_slice_y = slice(pad_width_y[0], pad_width_y[0] + self.gridmap.shape[1])
    #     self.gridmap = padded_gridmap[gridmap_slice_x, gridmap_slice_y]




    # def gaussian_kernel(self, size, sigma=1):
    #     if size % 2 == 0:
    #         raise ValueError("Kernel size must be odd.")
    #     x, y = np.meshgrid(np.linspace(-1, 1, size), np.linspace(-1, 1, size))
    #     d = np.sqrt(x * x + y * y)
    #     g = np.exp(-(d ** 2 / (2.0 * sigma ** 2)))
    #     return g / np.sum(g)
    

    def find_highest_average_area(self):
        max_average = 0
        max_average_pos= None

        for i in range(self.gridmap.shape[0] - 7):
            for j in range(self.gridmap.shape[1] - 7):
                # Get 8x8 subarray
                subarray = self.gridmap[i:i+8, j:j+8]
                # Compute average of subarray
                subarray_average = np.mean(subarray)
                # Check if subarray average is higher than current max average
                if subarray_average > max_average:
                    max_average = subarray_average
                    max_average_pos = (i,j)

        return max_average_pos
                

    def display_gridmap(self,target_pos, enemies):
        self.ax.clear()
        
        
        plt.ion()
        
        self.ax.imshow(self.gridmap, cmap='PRGn', origin='lower', vmin= -1, vmax= 1) #
        for enemie in enemies:
            color = 'r'
            if self.can_overwrite(self.myid, enemie["id"]):
                color = 'g'
            if enemie["id"] == self.myid:
                color = 'b'
            circle = plt.Circle(enemie["position"], 0.5, color=color, fill=False)
            self.ax.add_patch(circle)
        if target_pos is not None:
            rec = plt.Rectangle ((target_pos[0]-2, target_pos[1]-2), 4,4, color='w', fill=False)
            self.ax.add_patch(rec)
        plt.grid(True)

        plt.show()
        plt.pause(0.00001)
    
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
        return score

    def gridmap_update(self, grid, enemies):
        for i in range(self.gridmap.shape[0]):
            for j in range(self.gridmap.shape[1]):
                self.gridmap[i][j] = self.calculate_tile_score((i,j), grid, enemies)
                

    def path_plan(self):
        path = []
        return path

    def determine_move(self, target):


        move = Move.STAY
        return move
    
    def determine_next_move(self, grid, enemies, game_info):
        pos_x = self.position[0]
        pos_y = self.position[1]
        grid_size = grid.shape[0]

        self.myid = self.id
        if self.gridmap.shape[0] == 1 or True:
            self.gridmap = np.zeros((grid_size, grid_size), dtype=np.float64)
        
        self.gridmap_update(grid, enemies)

        target_pos = self.find_highest_average_area()
        # print(target_pos)

        next_move = self.determine_move(target_pos)

        if debug:
            self.display_gridmap(target_pos, enemies)

        return next_move
    