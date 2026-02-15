import pygame
import numpy as np
import random


# Setup up screen
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)
YELLOW = (255, 255, 0, 100) # The fourth value is for transparency (requires special handling in Pygame)


class Waste:
    def __init__(self):
        # Generate waste at a random position on the screen
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.radius = 6
        self.collected = False

    def draw(self, screen):
        if not self.collected:
            pygame.draw.circle(screen, (0, 150, 0), (int(self.x), int(self.y)), self.radius)


class USVRobot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.theta = 0.0  # Initial orientation (0 is right)
        self.radius = 15  # Visual size of the robot

        # Vision parameters
        self.fov_angle = np.radians(70)
        self.vision_range = 150 # Pixels in the simulation

    def draw(self, screen):
        # 1. Draw the vision cone (FOV)
        # Create a transparent surface for the FOV
        fov_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        points = [(self.x, self.y)]
        num_steps = 20
        start_angle = self.theta - self.fov_angle / 2
        end_angle = self.theta + self.fov_angle / 2

        for i in range(num_steps + 1):
            angle = start_angle + (end_angle - start_angle) * (i / num_steps)
            px = self.x + self.vision_range * np.cos(angle)
            py = self.y + self.vision_range * np.sin(angle)
            points.append((px, py))

        pygame.draw.polygon(fov_surface, (255, 255, 0, 60), points)
        screen.blit(fov_surface, (0,0))

        # 2. Draw the robot body
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)

        # 3. Direction line
        end_x = self.x + self.radius * 1.5 * np.cos(self.theta)
        end_y = self.y + self.radius * 1.5 * np.sin(self.theta)
        pygame.draw.line(screen, (0,0,0), (self.x, self.y), (end_x, end_y), 3)


    def detect_waste(self, wastes):
        detected_list = []
        for w in wastes:
            if w.collected: continue

            # 1. Calculate distance (Euclidean)
            dx = w.x - self.x
            dy = w.y - self.y
            distance = np.sqrt(dx**2 + dy**2)

            # 2. Check range
            if distance <= self.vision_range:
                # 3. Calculate relative angle
                # atan2 returns angle from world X-axis
                target_angle = np.arctan2(dy, dx)

                # 4. Difference between robot orientation and target
                angle_diff = target_angle - self.theta

                # Normalize angle to be between -pi and pi
                angle_diff = (angle_diff + np.pi) % (2 * np.pi) - np.pi

                # 5. Check if within FOV half-angle
                if abs(angle_diff) <= self.fov_angle / 2:
                    detected_list.append(w)

        return detected_list

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(" USV Birmingham simulation - Phase 1")
    clock = pygame.time.Clock()

    robot = USVRobot(WIDTH//2, HEIGHT//2)

    # Create 10 pieces of waste
    wastes = [Waste() for _ in range(10)]

    running = True
    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # For now, let's make the robot rotate slowly to test the FOV
        robot.theta += 0.01

        detected = robot.detect_waste(wastes)

        # DRAWING SECTION
        for w in wastes:
            w.draw(screen)

        # Visual feedback for detection
        for d in detected:
            # Draw a line to detected waste to confirm the logic works
            pygame.draw.line(screen, (0, 255, 0), (robot.x, robot.y), (d.x, d.y), 2)
            # Draw a bigger indicator on top of the robot
            pygame.draw.circle(screen, (0, 255, 0), (int(robot.x), int(robot.y)), 10)

        robot.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()