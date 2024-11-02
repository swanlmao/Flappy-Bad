import pygame
import random
import os

pygame.init()

WIDTH, HEIGHT = 400, 600
BIRD_WIDTH, BIRD_HEIGHT = 70, 50
BIRD_X = 100
GRAVITY = 0.4
JUMP = -8.5
PIPE_WIDTH = 100
PIPE_HEIGHT = 500
PIPE_GAP = 250
PIPE_SPACING = 300

# Colors
WHITE = (255, 255, 255)
SKY_BLUE = (135, 206, 235)
GROUND_BROWN = (165, 42, 42)
BUTTON_COLOR = (255, 165, 0)

# Create the window
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Flappy Bad")

# Bird class
class Bird:
    def __init__(self):
        self.x = BIRD_X
        self.y = HEIGHT // 2
        self.velocity = 0
        self.icon = pygame.image.load("flappy_bad.png")  # Use the new bird image
        self.icon = pygame.transform.scale(self.icon, (BIRD_WIDTH, BIRD_HEIGHT))
        self.flap_count = 0  # Counter for wing flap animation
        self.is_alive = True

    def jump(self):
        self.velocity = JUMP
        self.flap_count = 15  # Set the wing flap count to start animation

    def move(self):
        self.velocity += GRAVITY
        self.y += self.velocity

        if self.y <= 0 or self.y + BIRD_HEIGHT >= HEIGHT:
            self.is_alive = False

    def draw(self):
        # Bird wing flap animation
        if self.flap_count > 0:
            self.icon = pygame.image.load("flappy_bad_flap.png")
        else:
            self.icon = pygame.image.load("flappy_bad.png")
        self.flap_count -= 1

        # Resize the bird image while preserving its aspect ratio
        aspect_ratio = self.icon.get_width() / self.icon.get_height()
        bird_width = int(BIRD_HEIGHT * aspect_ratio)
        self.icon = pygame.transform.scale(self.icon, (bird_width, BIRD_HEIGHT))

        window.blit(self.icon, (self.x, self.y))

# Pipe class
class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(100, HEIGHT - PIPE_GAP - 100)
        self.is_passed = False

        self.pipe_top = pygame.image.load("pipe.png")  # Use the new pipe image
        self.pipe_top = pygame.transform.scale(self.pipe_top, (PIPE_WIDTH, PIPE_HEIGHT))
        self.pipe_bottom = pygame.transform.flip(self.pipe_top, False, True)

    def move(self):
        self.x -= 2

    def draw(self):
        window.blit(self.pipe_top, (self.x, self.height - PIPE_HEIGHT))
        window.blit(self.pipe_bottom, (self.x, self.height + PIPE_GAP))

    def collision(self, bird):
        top_pipe_rect = pygame.Rect(self.x, self.height - PIPE_HEIGHT, PIPE_WIDTH, PIPE_HEIGHT)
        bottom_pipe_rect = pygame.Rect(self.x, self.height + PIPE_GAP, PIPE_WIDTH, PIPE_HEIGHT)

        bird_rect = pygame.Rect(bird.x, bird.y, BIRD_WIDTH, BIRD_HEIGHT)

        return bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect)

# Check if the point (x, y) is inside a rectangle
def is_inside_rect(x, y, rect):
    return rect[0] < x < rect[0] + rect[2] and rect[1] < y < rect[1] + rect[3]

# Main function
def main():
    global window, WIDTH, HEIGHT
    bird = Bird()
    pipes = []
    is_start_screen = True
    score = 0

    clock = pygame.time.Clock()

    # Function to draw the map
    def draw_map():
        for pipe in pipes:
            pipe.draw()

    # Function to display the score at the top of the screen
    def display_score():
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        window.blit(score_text, (10, 10))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if is_start_screen:
                        is_start_screen = False
                    elif not bird.is_alive:
                        bird = Bird()
                        pipes = []
                        is_start_screen = True
                        score = 0
                    elif bird.is_alive:
                        bird.jump()
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.size
                window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

        if not is_start_screen and bird.is_alive:
            bird.move()

            if pipes and pipes[-1].x < WIDTH - PIPE_SPACING:
                pipes.append(Pipe(WIDTH))
            elif not pipes:
                pipes.append(Pipe(WIDTH))
                score += 1

            for pipe in pipes:
                pipe.move()

                # Check for collisions
                if pipe.collision(bird) or not (0 <= bird.y <= HEIGHT - BIRD_HEIGHT):
                    bird.is_alive = False

                if not pipe.is_passed and bird.x > pipe.x + PIPE_WIDTH:
                    pipe.is_passed = True
                    score += 1

                if pipe.x + PIPE_WIDTH < 0:
                    pipes.remove(pipe)

        window.fill(SKY_BLUE)

        if not is_start_screen and bird.is_alive:
            bird.draw()
            draw_map()
            display_score()
        else:
            if not bird.is_alive:
                # Display "Game Over" Screen
                font = pygame.font.SysFont(None, 48)
                game_over_text = font.render("Game Over", True, WHITE)
                game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
                window.blit(game_over_text, game_over_rect)

                retry_button_rect = (WIDTH // 2 - 100, HEIGHT // 2, 200, 60)
                pygame.draw.rect(window, BUTTON_COLOR, retry_button_rect)
                font = pygame.font.SysFont(None, 24)
                retry_text = font.render("Press SPACE to retry", True, (0, 0, 0))
                retry_text_rect = retry_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
                window.blit(retry_text, retry_text_rect)

                # Display final score
                score_text = font.render(f"Final Score: {score}", True, WHITE)
                score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
                window.blit(score_text, score_rect)

            if is_start_screen:
                # Display start screen text
                font = pygame.font.SysFont(None, 36)
                title_text = font.render("Flappy Bad", True, WHITE)
                instruction_text = font.render("Press SPACE to jump", True, WHITE)
                start_text = font.render("Press SPACE to start", True, WHITE)

                title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
                instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 1.5))

                window.blit(title_text, title_rect)
                window.blit(instruction_text, instruction_rect)
                window.blit(start_text, start_rect)
                draw_map()

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
