import random
import numpy as np
from ..bot_control import Move
import pygame
import time
class LeonardoDaVidi:

    def __init__(self):
        pygame.init()
        self.gridmap = None

        self.enemie_kernel =  np.array([[1, 2, 1],
                              [2, 3, 2],
                              [1, 2, 1]])
        
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.screen = None
        self.myid = 0
        

    def get_name(self):
        return "LeonardoDaVidi"

    def get_contributor(self):
        return "Bram Fenijn"
    
    def can_overwrite(self, id, tile):
        if tile == 0: return True
        return (id - tile) % 3 == 2
    
    # def create_debug_window(self, screen_size):
    #     self.screen = pygame.display.set_mode(screen_size)
    #     pygame.display.set_caption("LeonardoDaVidi debug display", "2")

    # def draw_debug_window(self):
    #     cell_size = 10
    #     for i in range(self.gridmap.shape[0]):
    #         for j in range(self.gridmap.shape[1]):
    #             # Determine the color based on the value in the grid map
    #             color = (self.gridmap[i,j], self.gridmap[i,j], self.gridmap[i,j])
                
    #             # Draw the cell
    #             pygame.draw.rect(self.screen, color, (j*cell_size, i*cell_size, cell_size, cell_size))
    #             pygame.draw.rect(self.screen, self.BLACK, (j*cell_size, i*cell_size, cell_size, cell_size), 1)


    #     pygame.display.flip()


    
    def put_kernel(self, pos, multiplier):
        # print(pos)
        sub_arr = self.gridmap[pos[0]-1:pos[0]+2, pos[1]-1:pos[1]+2]
        # print(sub_arr)
        result = self.enemie_kernel * multiplier   # or kernel * -1
        # print(result)
        sub_arr += result
        self.gridmap[pos[0]-1:pos[0]+2, pos[1]-1:pos[1]+2] = sub_arr

        # for i in range(self.enemie_kernel.shape[0]):
        #     for j in range(self.enemie_kernel.shape[1]):
        #         x = i + pos[0]-self.enemie_kernel.shape[0] / 2
        #         y = j + pos[1]-self.enemie_kernel.shape[1] / 2
        #         if x > 0 and x <  self.gridmap.shape[0] - 1 and y > 0 and y < self.gridmap.shape[1] - 1:
        #             self.gridmap[x][y] += self.enemie_kernel[i][j] * multiplier


    def gridmap_update(self, grid, enemies):
        for enemie in enemies:
            if enemie["id"] == self.myid:
                continue
            if enemie["position"][0] > 0 and enemie["position"][0] <  self.gridmap.shape[0] - 1 and enemie["position"][1] > 0 and enemie["position"][1] < self.gridmap.shape[1] - 1:
                self.put_kernel(enemie["position"], -1)
        
        

    def determine_next_move(self, grid, enemies, game_info):
        pos_x = self.position[0]
        pos_y = self.position[1]
        grid_size = grid.shape[0]

        self.myid = self.id

        # if game_info.current_round == 0:
        #     self.create_debug_window((grid_size, grid_size))

        self.gridmap = np.zeros((grid_size, grid_size), dtype=np.float64)
        
        self.gridmap_update(grid, enemies)

        # self.draw_debug_window()

        return Move.STAY