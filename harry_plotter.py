import random
import numpy as np
from ..bot_control import Move
from pprint import pprint
import math

X = 0 # Move.LEFT is towarts X 0, Move.RIGHT is towarts max X 
Y = 1 # Move.DOWN is towarts Y 0, Move.UP is towarts max Y 

debug = False
id_moves = [Move.RIGHT, Move.UP, Move.LEFT, Move.LEFT, Move.DOWN, Move.DOWN, Move.RIGHT, Move.RIGHT]

class HarryPlotter:

    def __init__(self):
        self.myid = 0
        self.grid = None
        self.enemies = None
        self.game_info = None

        self.enemies_pos_list = {}
        self.enemies_move_list = {}
        self.friend = []

        self.target = 0
    
    def get_name(self):
        return "Harry Plotter ( " + str(self.target) + " )"

    def get_contributor(self):
        return "Bram Fenijn"
    
    def determine_new_tile_colour(self, bot_colour, floor_colour):
        if floor_colour == 0: return bot_colour # Bot always paints a white floor tile
        return [floor_colour, 0, bot_colour][(bot_colour - floor_colour) % 3]
    
    def can_overwrite(self, id, tile):
        if tile == 0: return True
        return (id - tile) % 3 == 2
    
    def find_high_score_list(self):
        tile_counts = np.zeros((len(self.enemies)+1), dtype=np.int16)
        max_tiles = self.grid.shape[X] * self.grid.shape[Y]
        for x in range(self.grid.shape[X]):
            for y in range(self.grid.shape[Y]):
                id = self.grid[x][y]
                tile_counts[id]+=1
        # pprint(tile_counts)
        score_list = []
        for id, count in enumerate(tile_counts):
            score = count / max_tiles * 100.0
            # print(f"id {id} has {count} tiles, thats {score}%")
            score_list.append({"id": id, "score": score})
        score_list = sorted(score_list[1:], key=lambda d: -d['score']) 
        return score_list

                
    
        
    def detect_friend(self):
        if self.game_info.current_round < 10:
            for enemie in self.enemies:
                if enemie["id"] not in self.enemies_pos_list.keys():
                    self.enemies_pos_list[enemie["id"]] = []
                self.enemies_pos_list[enemie["id"]].append(enemie["position"])
        if self.game_info.current_round == 10:
            for key, poses in self.enemies_pos_list.items():
                # print(key)
                # pprint(poses)
                self.enemies_move_list[key] = []
                for i in range(len(poses)-1):
                    y = poses[i][0] - poses[i+1][0]
                    x = poses[i][1] - poses[i+1][1]
                    # print(f" x:{x} y:{y}")
                    if x == -1:
                        self.enemies_move_list[key].append(Move.UP)
                        continue
                    if x == 1:
                        self.enemies_move_list[key].append(Move.DOWN)
                        continue
                    if y == -1:
                        self.enemies_move_list[key].append(Move.RIGHT)
                        continue
                    if y == 1:
                        self.enemies_move_list[key].append(Move.LEFT)
                        continue
            # pprint(self.enemies_move_list)
            for id, moves in self.enemies_move_list.items():
                if moves == id_moves:
                    # print(f"Friend detected with id: {id}")
                    self.friend.append(id)

    def get_grid_tile(self, pos, x=0, y=0):
        if pos[X] + x < 0 or pos[X] + x > self.grid.shape[1]-1:
            return -1
        if pos[Y] + y < 0 or pos[Y] + y > self.grid.shape[0]-1:
            return -1
        # print(f"pos: x:{pos[1]}, y:{pos[0]}, ofset: x:{x},y:{y}")
        return self.grid[pos[Y] + y][pos[X] + x]      
    
    def get_next_move_grid_tile(self, move):
        if move == Move.UP:
            return self.get_grid_tile(self.position, 0, 1)
        if move == Move.DOWN:
            return self.get_grid_tile(self.position, 0, -1)
        if move == Move.LEFT:
            return self.get_grid_tile(self.position, 0, -1)
        if move == Move.RIGHT:
            return self.get_grid_tile(self.position, 0, 1)
    
    def find_target_tiles_move(self):
        move = Move.STAY
        x_steps = 1
        y_steps = 1
        x_dir = 1
        y_dir = 1
        current_steps = 0
        isXStep = True
        max = 1000
        i = 0
        x = 0
        y = 0
        target_x= 0
        target_y = 0
        while True:
            i+=1
            if isXStep:
                x += x_dir
                current_steps+=1
                if current_steps == x_steps:
                    x_dir *= -1
                    x_steps+=1
                    current_steps = 0
                    isXStep = False
            else:
                y += y_dir
                current_steps+=1
                if current_steps == y_steps:
                    y_dir *= -1
                    y_steps+=1
                    current_steps = 0
                    isXStep = True

            tile = self.get_grid_tile(self.position, x,y)
            
            if tile == self.target:
                
                target_x = self.position[X] + x
                target_y = self.position[Y] + y
                # print(f"found target {self.target} at: {target_x}({x}),{target_y}({y})")
                break
            if i > max:
                # print(f"tile {self.target} not found")
                for enemie in self.enemies:
                    if enemie["id"] == self.target:
                        x = enemie["position"][X] - self.position[X]
                        y = enemie["position"][Y] - self.position[Y]
                        break
                break
            
        
        if abs(x) > abs(y):
            if (x > 0):
                move = Move.RIGHT

            if (x < 0):
                move = Move.LEFT
        else:
            if (y > 0):
                move = Move.UP

            if (y < 0):
                move = Move.DOWN
        # print(f"x:{x}, y:{y} move: {move} current pos: ({self.position[1]},{self.position[0]})")
        return move

    def find_move(self):
        move = Move.STAY

        tile_R = self.get_grid_tile(self.position, 1, 0)
        if tile_R == self.target:
            move = Move.RIGHT

        tile_L = self.get_grid_tile(self.position, -1, 0)
        if tile_L == self.target:
            move = Move.LEFT

        tile_U = self.get_grid_tile(self.position, 0, 1)
        if tile_U == self.target:
            move = Move.UP

        tile_D = self.get_grid_tile(self.position, 0, -1)
        if tile_D == self.target:
            move = Move.DOWN

        # print(f"R: {tile_R}, L: {tile_L}, U: {tile_U}, D: {tile_D}")

        if move == Move.STAY:
            # print("no nearby tiles")
            move = self.find_target_tiles_move()
      
        if move == Move.STAY:
            move = Move.DOWN

        return move

    
    def determine_next_move(self, grid, enemies, game_info):
        # print(f"\nCurrent pos: ({self.position[X]},{self.position[Y]})")

        self.grid = grid
        # pprint(grid[0][1])
        self.enemies = enemies
        self.myid = self.id 
        self.game_info = game_info

        next_move = Move.STAY
        if len(self.friend) == 0:
            self.friend.append(self.id)

        # if len(self.friend) == 1:
        #     self.detect_friend()
        #     return next_move
        
        if self.game_info.current_round % 25 == 0 or self.target == 0:
            highscores = self.find_high_score_list()
            # pprint(highscores)
            for enemy in highscores:
                enemy_id = enemy["id"]
                if enemy_id not in self.friend:
                    if self.determine_new_tile_colour(self.id, enemy_id) == enemy_id:
                        # print(f"Canot override {enemy_id} ")
                        continue
                    self.target = enemy["id"]    
                    # print(f"Target is {self.target}")
                    break
                            
        move = self.find_move()

        # if self.get_next_move_grid_tile(move) in self.friend:
        #     move = Move.STAY

        return move
        
    