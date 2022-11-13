from math import sqrt
from datetime import timedelta
import pygame
from time import perf_counter
from random import choice, randint

DISPLAY = True
RESETABLE = True
FULLSCREEN = False

WIDTH, HEIGHT = (3000, 3000)
OFFSET = 5
THICKNESS = 2
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
MAZESIZE = 50

class Maze:

    def __init__(self, width, height, start = None) -> None:
        self.grid = {}
        self.pathCells = []
        self.nonePathCells = []
        self.width = width
        self.height = height
        self.genBlank()
        self.genMaze(start)

    def addToPath(self, pos):
        if pos not in self.pathCells:
            self.pathCells.append(pos)
            self.nonePathCells.remove(pos)

    def genBlank(self):
        for x in range(self.width):
            for y in range(self.height):
                pos = (x, y)
                self.grid[pos] = [1, 1, 1, 1]
                self.nonePathCells.append(pos)

    def getNeighbours(self, currentPos, allowingPath = False):
        neighbours = []
        neighbours.append((currentPos[0] - 1, currentPos[1]))
        neighbours.append((currentPos[0] + 1, currentPos[1]))
        neighbours.append((currentPos[0], currentPos[1] - 1))
        neighbours.append((currentPos[0], currentPos[1] + 1))

        toReturn = []
        for pos in neighbours:
            if pos in self.grid:
                if pos not in self.pathCells or allowingPath:
                    toReturn.append(pos)

        return toReturn
    
    def genPath(self, startPos):

        if startPos == None:
            startPos = (self.width // 2, self.height // 2)

        currentPos = startPos
        for _ in range(self.width * self.height):
            neighbours = self.getNeighbours(currentPos)
            if len(neighbours) > 0:
                toGoTo = choice(neighbours)
                self.breakWalls(currentPos, toGoTo)
                self.addToPath(currentPos)
                currentPos = toGoTo

            else:
                self.addToPath(currentPos)
                break

    def checkNonePaths(self):
        for key in self.nonePathCells:
            self.genPath(key)

    def addFinish(self):
        finishes = []
        for key in reversed(self.pathCells):
            if key[1] == self.height - 1:
                finishes.append(key)

        maxDist = 0
        finish = None
        for key in finishes:
            x = key[0] - 0
            y = key[1] - 0

            dist = sqrt((x ** 2) + (y ** 2))
            if dist > maxDist:
                finish = key
                maxDist = dist
        
        if finish != None:
            self.grid[finish][1] = 0

    def addStart(self):
        starts = []
        for key in self.pathCells:
            if key[1] == 0:
                starts.append(key)

        minDist = self.width
        start = None
        for key in starts:
            x = key[0] - 0
            y = key[1] - 0

            dist = sqrt((x ** 2) + (y ** 2))
            if dist < minDist:
                start = key
                minDist = dist

        if start != None:
            self.grid[start][0] = 0      

    def checkSingleCells(self):
        for key in self.grid:
            cell = self.grid[key]
            if cell == [1, 1, 1, 1]:
                neighbours = self.getNeighbours(key, True)
                self.breakWalls(key, choice(neighbours))

    def genMaze(self, start = None):

        print(f"\033[92m \033[04m --- CREATING {self.width}x{self.height} MAZE --- \033[00m")

        startTime = perf_counter()
        if start == None:
            start = (self.width // 2, self.height // 2)

        for _ in range(self.width * self.height):
            if len(self.pathCells) == 0:
                self.genPath(start)

            else:
                pos = choice(self.pathCells)
                self.genPath(pos)

        mazeGenTime = perf_counter()
        time = timedelta(seconds = mazeGenTime - startTime)
        print(f"\033[96m --- GENERATED MAIN PATHS : {time} --- \033[00m")

        self.addStart()
        startGenTime = perf_counter()
        time = timedelta(seconds = startGenTime - mazeGenTime)
        print(f"\033[96m --- START FOUND : {time} --- \033[00m")

        self.addFinish()
        finishGenTime = perf_counter()
        time = timedelta(seconds = finishGenTime - startGenTime)
        print(f"\033[96m --- FINISH FOUND : {time} --- \033[00m")
        
        self.checkNonePaths()
        filledPathTime = perf_counter()
        time = timedelta(seconds = filledPathTime - finishGenTime)
        print(f"\033[96m --- FILLED PATHS : {time} --- \033[00m")

        self.checkSingleCells()
        filledSingleCellTime = perf_counter()
        time = timedelta(seconds = filledSingleCellTime - filledPathTime)
        print(f"\033[96m --- FILLED SINGLE CELLS : {time} --- \033[00m")

        time = timedelta(seconds = filledSingleCellTime - startTime)
        print(f"\033[91m \033[04m --- FULL MAZE GEN : {time} --- \033[00m \n")


    def breakWalls(self, start, end):
        if start[1] > end[1]:
            self.grid[start][0] = 0
            self.grid[end][1] = 0

        elif start[1] < end[1]:
            self.grid[start][1] = 0
            self.grid[end][0] = 0

        else:
            if start[0] > end[0]:
                self.grid[start][2] = 0
                self.grid[end][3] = 0

            elif start[0] < end[0]:
                self.grid[start][3] = 0
                self.grid[end][2] = 0

    def getWalls(self):
        gridX = ((WIDTH) / self.width) - (OFFSET / self.width * 2)
        gridY = ((HEIGHT) / self.height) - (OFFSET / self.height * 2)
        walls = []
        for pos, wall in self.grid.items():
            x = (pos[0] * (gridX)) + OFFSET
            y = (pos[1] * (gridY)) + OFFSET
            if wall[0] == 1:
                walls.append([(x, y), (x + gridX, y)])

            if wall[1] == 1: 
                walls.append([(x, y + gridY), (x + gridX, y + gridY)])

            if wall[2] == 1:
                walls.append([(x, y), (x, y + gridY)])

            if wall[3] == 1:
                walls.append([(x + gridX, y), (x + gridX, y + gridY)])

        return walls

    def getName(self):
        return f"{self.width}x{self.height}"


if __name__ == "__main__":

    #MAZED GEN
    maze = Maze(MAZESIZE, MAZESIZE)
    wallsToDraw = maze.getWalls()

    #SCREEN SETTINGS
    if FULLSCREEN:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(maze.getName())

    #DISPLAY MAZE AND SCREEN CAPTURE
    screen.fill(WHITE)
    for wall in wallsToDraw:
            pygame.draw.line(screen, BLACK, wall[0], wall[1], THICKNESS)
        
    pygame.display.flip()
    capture = screen.subsurface((0, 0, WIDTH, HEIGHT))
    pygame.image.save(capture, f"{maze.getName()}.jpg")

    if DISPLAY:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: 
                        running = False

                    elif event.key == pygame.K_RETURN:
                        if RESETABLE:
                            #RESET MAZE
                            maze = Maze(MAZESIZE, MAZESIZE)
                            wallsToDraw = maze.getWalls()
                            capture = screen.subsurface((0, 0, WIDTH, HEIGHT))
                            pygame.image.save(capture, f"{maze.getName()}.jpg")

            screen.fill(WHITE)

            for wall in wallsToDraw:
                pygame.draw.line(screen, BLACK, wall[0], wall[1], THICKNESS)
            
            pygame.display.flip()