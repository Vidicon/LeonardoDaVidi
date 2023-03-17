import random
import numpy as np
from ..bot_control import Move
from pprint import pprint

# import matplotlib
# matplotlib.use('TkAgg')
# import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import time

class LeonardoDaVidi:

    def __init__(self):
        self.gridmap = None

        self.enemie_kernel =  np.array([[1, 2, 1],
                              [2, 3, 2],
                              [1, 2, 1]])
        
        self.enemie_kernel = self.gaussian_kernel((5,5), )
        
        self.myid = 0

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
    
    def create_debug_window(self, screen_size):
        print("create_debug_window")

        # Create a figure and axis object
        self.fig, self.ax = plt.subplots()

        # Set the x and y limits
        self.ax.set_xlim(0, screen_size[0])
        self.ax.set_ylim(0, screen_size[1])

        # Display the gridmap as a heatmap
        self.heatmap = self.ax.imshow(self.gridmap, cmap='summer')


    def draw_debug_window(self):
        # self.heatmap.set_data(self.gridmap)
        # plt.draw()
        plt.show(block=False)


    # def put_kernel(self, pos, multiplier):
    #     i_min = max(pos[0]-1, 0)
    #     i_max = min(pos[0]+2, self.gridmap.shape[0])
    #     j_min = max(pos[1]-1, 0)
    #     j_max = min(pos[1]+2, self.gridmap.shape[1])
        
    #     sub_arr = self.gridmap[i_min:i_max, j_min:j_max]
    #     result = self.enemie_kernel * multiplier
    #     sub_arr += result
    #     self.gridmap[i_min:i_max, j_min:j_max] = sub_arr
    def add_kernel_to_gridmap(self, position):
        # Calculate padding needed to center kernel at specified position
        pad_width = ((self.enemie_kernel.shape[0]-1)//2, self.gridmap.shape[0]-self.enemie_kernel.shape[0]//2-1), \
                    ((self.enemie_kernel.shape[1]-1)//2, self.gridmap.shape[1]-self.enemie_kernel.shape[1]//2-1)
        
        # Pad the gridmap with zeros
        padded_gridmap = np.pad(self.gridmap, pad_width, mode='constant')
        
        # Add the enemie_kernel to the padded gridmap at the specified position
        pos_x, pos_y = position
        padded_gridmap[pos_x:pos_x+self.enemie_kernel.shape[0], pos_y:pos_y+self.enemie_kernel.shape[1]] += self.enemie_kernel
        
        # Extract the desired portion of the padded gridmap
        self.gridmap = padded_gridmap[1:self.gridmap.shape[0]+1, 1:self.gridmap.shape[1]+1]

    def put_kernel(self, pos, multiplier):
        i, j = pos
        i_min = max(i-1, 0)
        i_max = min(i+2, self.gridmap.shape[0])
        j_min = max(j-1, 0)
        j_max = min(j+2, self.gridmap.shape[1])

        sub_arr = self.gridmap[i_min:i_max, j_min:j_max]
        print("sub_arr shape:", sub_arr.shape)
        result = self.enemie_kernel * multiplier
        
        print("result shape:", result.shape)

        if i_min == 0:
            result = result[1:,:]
        if i_max == self.gridmap.shape[0]:
            result = result[:-1,:]
        if j_min == 0:
            result = result[:,1:]
        if j_max == self.gridmap.shape[1]:
            result = result[:,:-1]

        sub_arr += result
        self.gridmap[i_min:i_max, j_min:j_max] = sub_arr

    # def put_kernel(self, pos, multiplier):
    #     # print(pos)
    #     sub_arr = self.gridmap[pos[0]-1:pos[0]+2, pos[1]-1:pos[1]+2]
    #     # print(sub_arr)
    #     result = self.enemie_kernel * multiplier   # or kernel * -1
    #     # print(result)
    #     sub_arr += result
    #     self.gridmap[pos[0]-1:pos[0]+2, pos[1]-1:pos[1]+2] = sub_arr

        # for i in range(self.enemie_kernel.shape[0]):
        #     for j in range(self.enemie_kernel.shape[1]):
        #         x = i + pos[0]-self.enemie_kernel.shape[0] / 2
        #         y = j + pos[1]-self.enemie_kernel.shape[1] / 2
        #         if x > 0 and x <  self.gridmap.shape[0] - 1 and y > 0 and y < self.gridmap.shape[1] - 1:
        #             self.gridmap[x][y] += self.enemie_kernel[i][j] * multiplier


    def gridmap_update(self, grid, enemies):
        for enemie in enemies:
            print((enemie["position"][1],enemie["position"][0]))
        print("")
        for enemie in enemies:
            if enemie["id"] == self.myid:
                continue
            pass
            self.add_kernel_to_gridmap((enemie["position"][1],enemie["position"][0]))
            # self.put_kernel(enemie["position"], -1)
        for i in range(self.gridmap.shape[0]):
            for j in range(self.gridmap.shape[1]):
                self.gridmap[i][j] += self.can_overwrite(self.myid, grid[i][j])

    # def can_overwrite(self, id, tile):

    def gaussian_kernel(self, size, sigma=1):

        if size % 2 == 0:
            raise ValueError("Kernel size must be odd.")
        
        x, y = np.meshgrid(np.linspace(-1, 1, size), np.linspace(-1, 1, size))
        d = np.sqrt(x * x + y * y)
        g = np.exp(-(d ** 2 / (2.0 * sigma ** 2)))
        return g / np.sum(g)

    def display_gridmap(self):
        self.ax.clear()
        plt.ion()
        self.ax.imshow(self.gridmap, cmap='gray', origin='lower')
        plt.grid(True)
        # plt.xticks(range(27))
        # self.ax.colorbar()
        # print("gridmap: {}".format(self.gridmap.shape[0]))
        plt.show()
        plt.pause(0.0001)
        # pprint(self.gridmap)
        

    def determine_next_move(self, grid, enemies, game_info):
        pos_x = self.position[0]
        pos_y = self.position[1]
        grid_size = grid.shape[0]
        # print("Girdsize: {}".format(grid_size))

        self.myid = self.id

        # if self.gridmap is not None:
        #     self.ax.clear()
        #     self.ax.imshow(self.gridmap)
        #     plt.pause(0.001)
        # else:
        #     self.fig, self.ax = plt.subplots()
        #     self.ax.imshow(self.gridmap)
        #     plt.show()
        # if self.gridmap is None:
        self.gridmap = np.zeros((grid_size, grid_size), dtype=np.float64)
        
        self.gridmap_update(grid, enemies)

        # if self.heatmap is None:
            # self.create_debug_window((grid_size, grid_size))
            
     
            # self.draw_debug_window()
        # self.heatmap.set_data(self.gridmap)
        # self.fig.canvas.draw()
        # self.draw_debug_window()
        self.display_gridmap()



        return Move.STAY