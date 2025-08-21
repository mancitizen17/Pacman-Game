import pygame
import sys
from pygame.locals import *
import random
import heapq

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
PACMAN_SPEED = 10
GHOST_SPEED = 30
INITIAL_GHOST_DELAY = 5000  # 5 sec
ADDITIONAL_GHOST_DELAY = 7000  # 7 sec after each ghost activation
MAX_GHOSTS = 4
NEW_GHOST_DELAY = 15000  # Time new ghost is added

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
STOP = (0, 0)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (144, 238, 144)  # Pellet color

# Initialize game objects and settings
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pac-Man")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Load images
pacman_image = pygame.image.load(r'C:\Users\mansi\OneDrive\Documents\Mansi\sem 5\DAA\assignment\pacman.jpg').convert_alpha()
ghost_images = [
    pygame.image.load(r'C:\Users\mansi\OneDrive\Documents\Mansi\sem 5\DAA\assignment\redmonster.jpg').convert_alpha(),
    pygame.image.load(r'C:\Users\mansi\OneDrive\Documents\Mansi\sem 5\DAA\assignment\pinkmonster.jpg').convert_alpha(),
    pygame.image.load(r'C:\Users\mansi\OneDrive\Documents\Mansi\sem 5\DAA\assignment\bluemonster.jpg').convert_alpha(),
    pygame.image.load(r'C:\Users\mansi\OneDrive\Documents\Mansi\sem 5\DAA\assignment\orangemonster.jpg').convert_alpha()
]

# Scale images to fit grid
pacman_image = pygame.transform.scale(pacman_image, (GRID_SIZE, GRID_SIZE))
ghost_images = [pygame.transform.scale(img, (GRID_SIZE, GRID_SIZE)) for img in ghost_images]

# Game object classes
class GameObject:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Pacman(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.direction = STOP
        self.speed_counter = 0
        self.score = 0

    def move(self, walls, pellets):
        if self.speed_counter >= PACMAN_SPEED:
            self.speed_counter = 0
            new_x = (self.x + self.direction[0]) % GRID_WIDTH
            new_y = (self.y + self.direction[1]) % GRID_HEIGHT
            if (new_x, new_y) not in walls:
                if (new_x, new_y) in pellets:
                    pellets.remove((new_x, new_y))
                    self.score += 10  # Increment score for each pellet eaten
                self.x, self.y = new_x, new_y
        else:
            self.speed_counter += 1

class Ghost(GameObject):
    def __init__(self, x, y, image):
        super().__init__(x, y)
        self.image = image
        self.speed_counter = 0
        self.active = False  # Ghosts start inactive

    def move(self, pacman, walls):
        if self.active and self.speed_counter >= GHOST_SPEED:
            self.speed_counter = 0
            path = self.find_path(pacman, walls)
            if path:
                self.x, self.y = path[1]  # Move to the next position in the path
        else:
            self.speed_counter += 1

    def find_path(self, pacman, walls):
        # A* algorithm to find the path to Pac-Man
        open_list = [(0, (self.x, self.y))]  # Priority queue for open list
        came_from = {}
        g_score = {(self.x, self.y): 0}

        while open_list:
            _, current = heapq.heappop(open_list)

            if current == (pacman.x, pacman.y):
                # Reconstruct the path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path

            for neighbor in [(current[0] + 1, current[1]), (current[0] - 1, current[1]),
                             (current[0], current[1] + 1), (current[0], current[1] - 1)]:
                if neighbor not in walls and 0 <= neighbor[0] < GRID_WIDTH and 0 <= neighbor[1] < GRID_HEIGHT:
                    tentative_g_score = g_score[current] + 1  # Assuming a uniform cost of movement
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score = tentative_g_score + self.manhattan_distance(neighbor, (pacman.x, pacman.y))
                        heapq.heappush(open_list, (f_score, neighbor))

        # No path found
        return []

    def manhattan_distance(self, point1, point2):
        return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])

# Generate symmetric walls
def generate_symmetric_walls():
    walls = set()
    wall_density = 0.15  # Adjust this to change the density of walls (lower means more open)
   
    # Create walls for half of the grid and mirror them to make the maze symmetric
    for y in range(GRID_HEIGHT // 2):
        for x in range(GRID_WIDTH):
            if random.random() < wall_density and (x, y) != (1, 1):  # Leave Pac-Man's starting point open
                walls.add((x, y))
                walls.add((GRID_WIDTH - x - 1, GRID_HEIGHT - y - 1))  # Mirror walls to create symmetry

    # Add boundary walls around the grid
    for x in range(GRID_WIDTH):
        walls.add((x, 0))
        walls.add((x, GRID_HEIGHT - 1))
    for y in range(GRID_HEIGHT):
        walls.add((0, y))
        walls.add((GRID_WIDTH - 1, y))
   
    return walls

# Initialize pellets and ghosts
def initialize_pellets(walls):
    return {(x, y) for y in range(GRID_HEIGHT) for x in range(GRID_WIDTH) if (x, y) not in walls}

def initialize_game():
    global pacman, ghosts, pellets, walls
    walls = generate_symmetric_walls()  # Generate random symmetric walls
    pellets = initialize_pellets(walls)  # Generate pellets where there are no walls
    pacman = Pacman(1, 1)
    ghost_spawn_positions = [(GRID_WIDTH - 2, y) for y in range(1, 5)]
    ghosts = [Ghost(x, y, ghost_images[i]) for i, (x, y) in enumerate(ghost_spawn_positions[:MAX_GHOSTS])]

# Game Over screen with retry button
def game_over_screen(score):
    game_over = True
    retry_button = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 50, 100, 50)
    while game_over:
        screen.fill(BLACK)
        game_over_text = font.render("Game Over!", True, WHITE)
        score_text = font.render(f"Final Score: {score}", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 100))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
       
        draw_button("Retry", retry_button, BLUE)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left-click event
                if retry_button.collidepoint(event.pos):
                    game_over = False
                    initialize_game()  # Reinitialize the game state
                    main()  # Restart the main loop



def draw_button(text, rect, color, text_color=WHITE):
    pygame.draw.rect(screen, color, rect)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)  # Center text on the button
    screen.blit(text_surface, text_rect)


# Main game loop
def main():
    running = True
    game_start_time = pygame.time.get_ticks()
    last_ghost_time = game_start_time  # Time when the last ghost was added

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                handle_user_input()

        current_time = pygame.time.get_ticks()

        pacman.move(walls, pellets)

        # Activate and move ghosts
        for i, ghost in enumerate(ghosts):
            if not ghost.active and current_time - game_start_time > INITIAL_GHOST_DELAY + i * ADDITIONAL_GHOST_DELAY:
                ghost.active = True
            if ghost.active:
                ghost.move(pacman, walls)

        if check_ghost_collision():
            game_over_screen(pacman.score)
            break

        draw_game()
        clock.tick(60)

    pygame.quit()
    sys.exit()

# Helper functions
def handle_user_input():
    keys = pygame.key.get_pressed()
    if keys[K_LEFT]:
        pacman.direction = LEFT
    elif keys[K_RIGHT]:
        pacman.direction = RIGHT
    elif keys[K_UP]:
        pacman.direction = UP
    elif keys[K_DOWN]:
        pacman.direction = DOWN

def draw_game():
    screen.fill(BLACK)
    for wall in walls:
        pygame.draw.rect(screen, BLUE, (wall[0] * GRID_SIZE, wall[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
    for pellet in pellets:
        pygame.draw.circle(screen, ORANGE, (pellet[0] * GRID_SIZE + GRID_SIZE // 2, pellet[1] * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE // 5.5)
    
    # Draw Pac-Man with the image
    screen.blit(pacman_image, (pacman.x * GRID_SIZE, pacman.y * GRID_SIZE))
    
    # Draw each ghost with respective image
    for ghost in ghosts:
        screen.blit(ghost.image, (ghost.x * GRID_SIZE, ghost.y * GRID_SIZE))
    
    score_text = font.render(f"Score: {pacman.score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    pygame.display.update()

def check_ghost_collision():
    return any(ghost.x == pacman.x and ghost.y == pacman.y for ghost in ghosts)

if __name__ == "__main__":
    initialize_game()
    main()
