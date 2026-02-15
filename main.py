import pygame
import numpy as np

# Configuración de pantalla
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colores
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)
YELLOW = (255, 255, 0, 100) # El cuarto valor es para transparencia (requiere manejo especial en Pygame)

class USVRobot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.theta = 0.0  # Orientación inicial (0 es derecha)
        self.radius = 15  # Tamaño visual del robot

        # Parámetros de visión
        self.fov_angle = np.radians(70)
        self.vision_range = 150 # Píxeles en la simulación

    def draw(self, screen):
        # 1. Dibujar el cono de visión (FOV)
        # Creamos una superficie transparente para el FOV
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

        # 2. Dibujar el cuerpo del robot
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)

        # 3. Línea de dirección
        end_x = self.x + self.radius * 1.5 * np.cos(self.theta)
        end_y = self.y + self.radius * 1.5 * np.sin(self.theta)
        pygame.draw.line(screen, (0,0,0), (self.x, self.y), (end_x, end_y), 3)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simulación USV Birmingham - Fase 1")
    clock = pygame.time.Clock()

    robot = USVRobot(WIDTH//2, HEIGHT//2)

    running = True
    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Por ahora, hagamos que el robot gire lentamente para probar el FOV
        robot.theta += 0.02

        robot.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()