import random
import numpy as np
from ..bot_control import Move
from pprint import pprint
import math

debug_start = 300
debug = False
use_full_map = False

if debug:
    import matplotlib.pyplot as plt
import time

id_moves = [Move.RIGHT, Move.UP, Move.LEFT, Move.LEFT, Move.DOWN, Move.DOWN, Move.RIGHT, Move.RIGHT]

class LeonardoDaVidi:

    def __init__(self):
        self.myid = 0
        self.grid = None
        self.enemies = None
        self.game_info = None         

        if use_full_map:
            self.gridmap = np.zeros((1, 1), dtype=np.float64)
            self.enemymap = np.zeros((1, 1), dtype=np.float64)

        if debug:
            self.fig = None
            self.ax = None
            self.fig, self.ax = plt.subplots()
            self.tiles_moved = 0
            self.tiles_writen = 0

        self.moveType = 1
    
    def get_name(self):
        return "LeonardoDaVidi"

    def get_contributor(self):
        return "Bram Fenijn"
    
    def determine_new_tile_colour(self, bot_colour, floor_colour):
        if floor_colour == 0: return bot_colour # Bot always paints a white floor tile
        return [floor_colour, 0, bot_colour][(bot_colour - floor_colour) % 3]
    
    def can_overwrite(self, id, tile):
        if tile == 0: return True
        return (id - tile) % 3 == 2
                

    def display_gridmap(self):
        self.ax.clear()
        plt.ion()
        
        self.ax.imshow(self.gridmap, cmap='PRGn', origin='lower') #, vmin= -1, vmax= 1
        for enemie in self.enemies:
            circle = plt.Circle(enemie["position"], 0.5, color='r', fill=False)
            new_tile = self.determine_new_tile_colour(self.myid, enemie["id"])
            if new_tile == self.myid:
                circle = plt.Circle(enemie["position"], 0.5, color='g', fill=False)
            if new_tile == 0:
                circle = plt.Circle(enemie["position"], 0.5, color='y', fill=False)
            if enemie["id"] == self.myid:
                circle = plt.Circle(enemie["position"], 0.5, color='b', fill=True)
            
            self.ax.add_patch(circle)
        
        # if target_pos is not None:
        #     rec = plt.Rectangle ((target_pos[0]-2, target_pos[1]-2), 4,4, color='w', fill=False)
        #     self.ax.add_patch(rec)

        # for peak in peak_list:
        #     rec = plt.Rectangle ((peak[1]-2, peak[0]-2), 4,4, color='w', fill=False)
        #     self.ax.add_patch(rec)

        plt.grid(True)
        plt.show()
        plt.pause(0.001)
    
    def get_enemie_score(self, pos): # high score is good
        score = 0.0

        for enemie in self.enemies:
            if enemie["id"] == self.myid:
                continue

            distance = math.dist(enemie["position"], pos)
            max_dis = 10
            if distance > max_dis:
                continue
            # distance = min(max_dis, distance)

            new_tile = self.determine_new_tile_colour(self.myid, enemie["id"])
            if new_tile == enemie["id"]: # cant clear
                distance_score = (max_dis - distance) / max_dis
                # if distance == 0:
                #     distance_score = -1.0
                score -= distance_score * 0.5

            elif new_tile == 0: # can clear
                distance_score = (max_dis - distance) / max_dis
                if distance == 0:
                    distance_score = -0.8
                score -= distance_score * 0.3

            else:# new_tile == self.myid: can overrite
                distance_score = (max_dis - distance) / max_dis
                if distance == 0:
                    distance_score = -2.0
                if distance == 1:
                    distance_score *= 0.5
                score += distance_score * 0.5

        score = min(max(score, -1), 1)
              

        return score
    
    def calculate_tile_score(self, pos, use_tile_score = True, use_enemies_score = True):
        score = 0
        # print(self.grid)
        if use_enemies_score:
            score = self.get_enemie_score((pos[1], pos[0])) * 1.0
            # print(score)
            # score = self.enemymap[pos[0]][pos[1]]

        if use_tile_score:
            
            tile_value = self.grid[pos[0]][pos[1]]
            # print(tile_value)
            new_tile = self.determine_new_tile_colour(self.myid, tile_value)

            if tile_value == 0: # is white, can override
                score += 0.6

            elif tile_value != self.myid and new_tile == self.myid: # is other player, can override, (if we overrite this we remove % from other)
                score += 0.8 

            elif new_tile == 0: # is other player, can clear, (if we clear this we remove % from other)
                score = -0.4 

            elif new_tile != 0: # is other player, cant clear.
                score = -0.8

            elif tile_value == self.myid:
                score = -1.0 # my id will do nothing

        return score#min(max(score, -1), 1)

    def gridmap_update(self):
        for i in range(self.gridmap.shape[0]):
            for j in range(self.gridmap.shape[1]):
                self.gridmap[i][j] = self.calculate_tile_score((i,j))

    def enemymap_update(self):
        for i in range(self.enemymap.shape[0]):
            for j in range(self.enemymap.shape[1]):
                self.enemymap[i][j] = self.get_enemie_score((j,i)) * 1.0
    

    def get_grid_tile(self, pos, x=0, y=0):
        if pos[1] + x < 0 or pos[1] + x > self.grid.shape[0]-1:
            return -1.0
        if pos[0] + y < 0 or pos[0] + y > self.grid.shape[1]-1:
            return -1
        
        if use_full_map and self.game_info.current_round > debug_start:
            return self.gridmap[pos[1] + x][pos[0]+y]
        else:
            return self.calculate_tile_score((pos[1]+ x,pos[0]+y))
    
    def find_better_move(self):
        for i in range(20):
            if self.get_grid_tile(self.position, 0, i) > 0:
                return Move.RIGHT
            if self.get_grid_tile(self.position, 0, -i) > 0:
                return Move.LEFT
            if self.get_grid_tile(self.position, i, 0) > 0:
                return Move.UP
            if self.get_grid_tile(self.position, -i, 0) > 0:
                return Move.DOWN
        print("Did not find high spot")
        return Move.UP
    
    def find_better_move2(self):
        score_right = 0.0
        score_left = 0.0
        score_up = 0.0
        score_down = 0.0
        scan_range = 10
        for i in range(scan_range):
            multiplier = (scan_range - i) / (scan_range/2)
            score_right += self.get_grid_tile(self.position, 0, i) * multiplier
            score_left += self.get_grid_tile(self.position, 0, -i) * multiplier
            score_up += self.get_grid_tile(self.position, i, 0) * multiplier
            score_down += self.get_grid_tile(self.position, -i, 0) * multiplier

        highest = -10.0
        next_move = Move.UP
        if score_right > highest:
            highest = score_right
            next_move = Move.RIGHT

        if score_left > highest:
            highest = score_left
            next_move = Move.LEFT

        if score_up > highest:
            highest = score_up
            next_move = Move.UP

        if score_down > highest:
            highest = score_down
            next_move = Move.DOWN
        # print(f"best move was: {next_move} r:{score_right}, l:{score_left}, u:{score_up}, d:{score_down}")
        return next_move
    
    def simple_move(self):
        move = Move.STAY
        max = -10.0

        tile = self.get_grid_tile(self.position, 0, 1)
        if tile > max:
            max = tile
            move = Move.RIGHT

        tile = self.get_grid_tile(self.position, 0, -1)
        if tile > max:
            max = tile
            move = Move.LEFT

        tile = self.get_grid_tile(self.position, 1, 0)
        if tile > max:
            max = tile
            move = Move.UP

        tile = self.get_grid_tile(self.position, -1, 0)
        if tile > max:
            max = tile
            move = Move.DOWN

        if max < 0:
            # print("Change move type")
            # self.moveType = 2
            move = self.find_better_move()
      
        if move == Move.STAY:
            move = Move.DOWN

        return move
    
    def determine_move(self):
        
        if self.moveType == 1:
            return self.simple_move()
        elif self.moveType == 2:
            return self.find_better_move2()
        
    
    def determine_next_move(self, grid, enemies, game_info):
        pos_x = self.position[0]
        pos_y = self.position[1]
        grid_size = grid.shape[0]

        self.grid = grid
        self.enemies = enemies
        self.myid = self.id 
        self.game_info = game_info

        if (game_info.current_round - 1) < len(id_moves):
            return id_moves[game_info.current_round-1]

        if use_full_map and game_info.current_round > debug_start:
            if self.gridmap.shape[0] == 1:
                self.gridmap = np.zeros((grid_size, grid_size), dtype=np.float64)
                self.enemymap = np.zeros((grid_size, grid_size), dtype=np.float64)
            self.enemymap_update()
            self.gridmap_update()

        next_move = self.determine_move()

        if debug and game_info.current_round > debug_start:
            self.display_gridmap()

        # if debug:
        #     self.tiles_moved+=1
        #     i = 0
        #     j = 0
        #     if next_move == Move.DOWN:
        #         j = -1
        #     if next_move == Move.UP:
        #         j = 1
        #     if next_move == Move.LEFT:
        #         i = -1
        #     if next_move == Move.RIGHT:
        #         i = 1

        #     tile_value = grid[self.position[0]+i][self.position[1]+j]
        #     if self.can_overwrite(self.myid, tile_value):
        #         self.tiles_writen+=1
        #     print(f'writen tiles: {self.tiles_writen} {(self.tiles_writen / self.tiles_moved) * 100}%')

        return next_move
    