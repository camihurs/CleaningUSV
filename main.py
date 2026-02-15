import pygame
import numpy as np
import random


# Setup up screen
WIDTH, HEIGHT = 1200, 800
FPS = 60

# Canal Borders (Y coordinates)
CANAL_TOP = 150
CANAL_BOTTOM = 650

# Colors
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)
YELLOW = (255, 255, 0, 100) # The fourth value is for transparency (requires special handling in Pygame)


class Waste:
    def __init__(self):
        # Generate waste at a random position on the screen
        # Ensure waste only appears inside the canal boundaries
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(CANAL_TOP + 20, CANAL_BOTTOM - 20)
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

    def update(self, width, height):
        """
        Update robot position and handle canal boundary logic.
        """
        # Constant speed (0.5 units per frame for now)
        # In a real scenario, this would be adjusted by delta time (dt)
        linear_speed = 1.5

        # Calculate new potential position
        new_x = self.x + linear_speed * np.cos(self.theta)
        new_y = self.y + linear_speed * np.sin(self.theta)

        # Boundary logic for the canal
        # Margin for X (left/right screen edges) and CANAL limits for Y
        margin_x = 30
        if new_x < margin_x or new_x > WIDTH - margin_x or \
           new_y < CANAL_TOP + 10 or new_y > CANAL_BOTTOM - 10:
            # Rotate when hitting the canal walls or ends
            self.theta += 0.05
        else:
            self.x = new_x
            self.y = new_y

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(" USV Birmingham simulation - Phase 1")
    clock = pygame.time.Clock()

    robot = USVRobot(100, 400)

    # Create 10 pieces of waste
    wastes = [Waste() for _ in range(10)]

    running = True
    while running:
        screen.fill(WHITE)
        # Draw water background (Light Blue)
        pygame.draw.rect(screen, (230, 245, 255), (0, CANAL_TOP, WIDTH, CANAL_BOTTOM - CANAL_TOP))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # For now, let's make the robot rotate slowly to test the FOV
        # robot.theta += 0.01

        # Draw Canal Walls (Visual boundaries)
        # Line from (0, CANAL_TOP) to (WIDTH, CANAL_TOP)
        pygame.draw.line(screen, (50, 50, 50), (0, CANAL_TOP), (WIDTH, CANAL_TOP), 5)
        # Line from (0, CANAL_BOTTOM) to (WIDTH, CANAL_BOTTOM)
        pygame.draw.line(screen, (50, 50, 50), (0, CANAL_BOTTOM), (WIDTH, CANAL_BOTTOM), 5)


        # 1. Update robot physics/movement
        robot.update(WIDTH, HEIGHT)

        # 2. DRAWING waste SECTION
        for w in wastes:
            w.draw(screen)

        # 3. Sensor logic (Vision)
        detected = robot.detect_waste(wastes)

        # 4. Visual feedback for detection (green lines)
        for d in detected:
            # Draw a line to detected waste to confirm the logic works
            pygame.draw.line(screen, (0, 255, 0), (robot.x, robot.y), (d.x, d.y), 2)
            # Draw a bigger indicator on top of the robot
            pygame.draw.circle(screen, (0, 255, 0), (int(robot.x), int(robot.y)), 10)

        # 5. Draw robot on top
        robot.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()