import random
import pygame
import time
from datetime import timedelta

class Config:
    DISPLAY = False
    FULLSCREEN = False
    SUPERPROGRESS = False
    PROGRESS = SUPERPROGRESS or False
    PATH_TRACKING = False
    COMPLETED_TRACKING = False
    TAKE_IMAGE_PROGRESS = True
    CURRENT_CELL = False
    BACKTRACK_CELL = False

    WIDTH, HEIGHT = (1000, 1000)
    OFFSET = 5
    THICKNESS = 2
    MAZESIZE = 200
    FPS = 200
    SEED = None
    
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Node:
    
    def __init__(self, position) -> None:
        self.position = position
        self.walls = [1,1,1,1] #left, right, top, bottom
        self.neighbours = [
            (self.position[0] - 1, self.position[1]),
            (self.position[0] + 1, self.position[1]),
            (self.position[0], self.position[1] - 1),
            (self.position[0], self.position[1] + 1),
        ]
        self.completed = False
        self.connected_to = []
        self.id = 0
        self.colour = None
        
    def addConnection(self, neighbour, colour):
        self.completed = True
        self.connected_to.append(neighbour.position)
        index = self.neighbours.index(neighbour.position)
        self.walls[index] = 0
        self.colour = colour
        if index % 2 == 0:
            neighbour.walls[index + 1] = 0
            
        else:
            neighbour.walls[index - 1] = 0     
    
    def validNeighbours(self, maze):
        neighbours = []
        for neighbour in self.neighbours:
            if maze.getNode(neighbour) == False: continue
            elif not maze.getNode(neighbour).completed: neighbours.append(neighbour)
            
        return neighbours
    
    def hasPath(self, maze):
        return True if len(self.validNeighbours(maze)) != 0 else False
    
    def __str__(self) -> str:
        return str(self.position)
    
    def __repr__(self) -> str:
        return str(self.position)
    
class Maze:
    
    NUM_COMPLETED = -1
    
    def __init__(self, sizeX, sizeY) -> None:
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.nodes = {}
        self.previous_cells = []
        self.completed = False
        self.currentCell = None
        self.generateEmpty()
        
    def generateEmpty(self):
        for i in range(self.sizeX):
            for j in range(self.sizeY):
                self.nodes[(i, j)] = Node((i, j))
        
    def getNode(self, position):
        if position[0] >= self.sizeX or position[0] < 0: return False
        if position[1] >= self.sizeY or position[1] < 0: return False
        return self.nodes[position]
        
    def generatePath(self, position):
        colour = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        self.currentCell = self.getNode(position)
        while self.currentCell.hasPath(self):
            
            validNeighbours = self.currentCell.validNeighbours(self)
            if not self.currentCell.hasPath(self): break
            
            random_neighbour = random.choice(validNeighbours)
            
            self.currentCell.id = Maze.NUM_COMPLETED + 1
            Maze.NUM_COMPLETED += 1
            Stats.TotalCells += 1
            self.currentCell.addConnection(self.getNode(random_neighbour), colour)
            self.previous_cells.append(self.currentCell)
            self.currentCell = self.getNode(random_neighbour)
            
            if Config.SUPERPROGRESS: 
                Screen.updateScreen()
                Screen.clock.tick(Config.FPS)
            
        self.currentCell.id = Maze.NUM_COMPLETED + 1
        if len(self.previous_cells) != 0:
            self.currentCell.addConnection(self.previous_cells[-1], colour)
        Stats.PathsCreated += 1
        
    def backtrace(self):
        Stats.BacktracksPerformed += 1
        while not self.previous_cells[-1].hasPath(self):
            Stats.CellsBacktracked += 1
            self.previous_cells = self.previous_cells[:-1]
            if len(self.previous_cells) == 0: 
                self.completed = True
                break
        
            if Config.SUPERPROGRESS:
                Screen.updateScreen()
                Screen.clock.tick(Config.FPS)
            
    def __str__(self) -> str:
        toString = ""
        for i in range(self.sizeX):
            for j in range(self.sizeY):
                toString += "1\t" if self.getNode((i, j)).completed else "0\t"
                
            toString += "\n"
            
        return toString + "\n\n"
        
    def generateMaze(self):
        random.seed(Config.SEED)
        x = random.randint(0, self.sizeX-1)
        y = random.randint(0, self.sizeY-1)
        currentCellPosition = (x, y)
        while not self.completed:
            self.generatePath(currentCellPosition)
            self.backtrace()
            if len(self.previous_cells) == 0:
                break
            currentCellPosition = self.previous_cells[-1].position
            
class Screen:

    screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT)) if not Config.FULLSCREEN else pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    maze = Maze(Config.MAZESIZE, Config.MAZESIZE)
    gridX = ((Config.WIDTH / maze.sizeX) - (Config.OFFSET / maze.sizeX * 2))
    gridY = ((Config.HEIGHT / maze.sizeY) - (Config.OFFSET / maze.sizeY * 2))
    running = False
    clock = pygame.time.Clock()
    
    @classmethod
    def regen(cls):
        cls.screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT)) if not Config.FULLSCREEN else pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        cls.maze = Maze(Config.MAZESIZE, Config.MAZESIZE)
        cls.gridX = ((Config.WIDTH / cls.maze.sizeX) - (Config.OFFSET / cls.maze.sizeX * 2))
        cls.gridY = ((Config.HEIGHT / cls.maze.sizeY) - (Config.OFFSET / cls.maze.sizeY * 2))
        cls.running = False
        cls.clock = pygame.time.Clock()
    
    @classmethod
    def generateImage(cls):
        Stats.StartGenTime = time.perf_counter()
        if not Config.DISPLAY: pygame.display.iconify()
        cls.maze.generateMaze()
        Stats.EndGenTime = time.perf_counter()
        Stats.StartDrawTime = time.perf_counter()
        
        cls.drawScreen()
        
        pygame.image.save(cls.screen, f"maze{cls.maze.sizeX}x{cls.maze.sizeY}.png")
        Stats.EndDrawTime = time.perf_counter()
        
    @classmethod
    def viewProgress(cls):
        Stats.StartGenTime, Stats.StartDrawTime = time.perf_counter(), time.perf_counter()
        cls.running = True
        x = random.randint(0, cls.maze.sizeX-1)
        y = random.randint(0, cls.maze.sizeY-1)
        cls.currentCellPosition = (x, y)
        cls.last_maze = time.perf_counter()
        random.seed(Config.SEED)
        while cls.running:
            if not cls.maze.completed: cls.updateMaze()
            if not Config.SUPERPROGRESS: cls.updateScreen()
            if not cls.running or cls.maze.completed: break
            cls.clock.tick(Config.FPS)

        if Config.TAKE_IMAGE_PROGRESS: pygame.image.save(cls.screen, f"maze{cls.maze.sizeX}x{cls.maze.sizeY}.png")
        Stats.EndGenTime, Stats.EndDrawTime = time.perf_counter(), time.perf_counter()
        pygame.quit()
    
    @classmethod
    def updateMaze(cls):
        Stats.MazeUpdates += 1
        cls.maze.generatePath(cls.currentCellPosition)
        if len(cls.maze.previous_cells) != 0:
            cls.maze.backtrace()
            
        if len(cls.maze.previous_cells) != 0:
            cls.currentCellPosition = cls.maze.previous_cells[-1].position
        cls.last_maze = time.time()
        
    @classmethod
    def drawScreen(cls):
        cls.screen.fill(WHITE)
        colour = 205/(Maze.NUM_COMPLETED+1)
        for pos, node in cls.maze.nodes.items():
            x = pos[0] * cls.gridX + Config.OFFSET
            y = pos[1] * cls.gridY + Config.OFFSET
                
            if node.completed and Config.COMPLETED_TRACKING:
                pygame.draw.rect(cls.screen, (50, 50, colour * node.id + 50), (x, y, cls.gridX+1, cls.gridY+1))
                Stats.DrawCalls += 1
            
            if node.colour and Config.PATH_TRACKING:
                pygame.draw.rect(cls.screen, node.colour, (x, y, cls.gridX+1, cls.gridY+1))
                Stats.DrawCalls += 1
                
            if pos == cls.maze.currentCell.position and Config.CURRENT_CELL:
                pygame.draw.rect(cls.screen, (0, 200, 0), (x, y, cls.gridX+1, cls.gridY+1))
                Stats.DrawCalls += 1
            
            if len(cls.maze.previous_cells) != 0:
                if pos == cls.maze.previous_cells[-1].position and Config.BACKTRACK_CELL:
                    pygame.draw.rect(cls.screen, (200, 0, 0), (x, y, cls.gridX+1, cls.gridY+1))
                    Stats.DrawCalls += 1
                
            if node.walls[0] == 1:
                pygame.draw.line(cls.screen, BLACK, (x, y), (x, y + cls.gridY))
                Stats.DrawCalls += 1
                
            if node.walls[2] == 1:
                pygame.draw.line(cls.screen, BLACK, (x, y), (x + cls.gridX, y))
                Stats.DrawCalls += 1

        width = (cls.maze.sizeX) * cls.gridX
        height = (cls.maze.sizeY) * cls.gridY
        pygame.draw.line(cls.screen, BLACK, (Config.OFFSET, height + Config.OFFSET), (width + Config.OFFSET, height + Config.OFFSET))
        pygame.draw.line(cls.screen, BLACK, (width + Config.OFFSET, Config.OFFSET), (width + Config.OFFSET, height + Config.OFFSET))
        Stats.DrawCalls += 1
            
    @classmethod
    def updateScreen(cls):
        Stats.ScreenUpdates += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cls.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: 
                    cls.running = False
                    
        cls.drawScreen()
                
        pygame.display.flip()
        
class Stats:
    
    PathsCreated = 0
    BacktracksPerformed = 0
    MazeUpdates = 0 
    ScreenUpdates = 0
    StartGenTime = 0
    EndGenTime = 0
    StartDrawTime = 0
    EndDrawTime = 0
    DrawCalls = 0
    CellsBacktracked = 0
    TotalCells = 0
    
    @classmethod
    def getStats(cls):
        return {
            "PathsCreated": cls.PathsCreated,
            "BacktracksPerformed": cls.BacktracksPerformed,
            "CellsBacktracked": cls.CellsBacktracked,
            "MazeUpdates": cls.MazeUpdates,
            "ScreenUpdates": cls.ScreenUpdates,
            "GenDuration": cls.EndGenTime - cls.StartGenTime,
            "DrawDuration": cls.EndDrawTime - cls.StartDrawTime,
            "DrawCalls": cls.DrawCalls,
            "AveragePathLength": cls.TotalCells / cls.PathsCreated,
            "TotalCells": cls.TotalCells
        }
        
    @classmethod
    def displayStats(cls):
        print(f"Paths Created:\t\t\t {cls.PathsCreated}")
        print(f"Total Cells Pathed:\t\t {cls.TotalCells}")
        print(f"Average Path Length:\t\t {cls.TotalCells / cls.PathsCreated}")
        print(f"Backtracks Performed:\t\t {cls.BacktracksPerformed}")
        print(f"Number of Cells Backtracked:\t {cls.CellsBacktracked}")
        print(f"Maze Updates Performed:\t\t {cls.MazeUpdates}")
        print(f"Screen Updates Performed:\t {cls.ScreenUpdates}")
        print(f"Number of Draw Calls:\t\t {cls.DrawCalls}")
        print(f"Maze Generation Time:\t\t {timedelta(seconds = cls.EndGenTime - cls.StartGenTime)}")
        print(f"Maze Draw Time:\t\t\t {timedelta(seconds = cls.EndDrawTime - cls.StartDrawTime)}")
        
if __name__ == "__main__":
    if Config.DISPLAY: Screen.viewProgress()
    else: Screen.generateImage()
    
    Stats.displayStats()