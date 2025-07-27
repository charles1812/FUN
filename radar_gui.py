import pygame
import math
import random

pygame.init()
WIDTH, HEIGHT = 800, 800
CENTER = WIDTH // 2, HEIGHT // 2
RADIUS = 350

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Radar Display V2")
font = pygame.font.SysFont("monospace", 14)
clock = pygame.time.Clock()
angle = 0

# Target class
class Target:
    def __init__(self, angle, distance, v_angle, v_dist, label):
        self.angle = angle
        self.distance = distance
        self.v_angle = v_angle
        self.v_dist = v_dist
        self.label = label
        self.color = (0, 255, 0)
        self.history = []

    def update(self):
        self.angle = (self.angle + self.v_angle) % 360
        self.distance += self.v_dist
        
        # Behavior by type:
        if "✈️" in self.label:  # planes
            # Reverse when inside radar radius to simulate flying out
            if self.distance < RADIUS * 0.6 and self.v_dist < 0:
                self.v_dist = -self.v_dist
            # Remove if fully outside (far away)
            if self.distance > RADIUS * 1.5:
                return False  # signal to remove target

        else:  # missiles or drones
            # Remove if they reach the center (simulate hit)
            if self.distance < 10:
                return False  # remove target

        # Keep history as before
        self.history.append((self.angle, self.distance))
        if len(self.history) > 20:
            self.history.pop(0)

        return True


    def get_pos(self):
        rad = math.radians(self.angle)
        x = CENTER[0] + self.distance * math.cos(rad)
        y = CENTER[1] + self.distance * math.sin(rad)
        return int(x), int(y)

    def draw(self, surface):
        # Draw history trail

        if self.distance <= RADIUS:
            for a, d in self.history:
                hx, hy = polar_to_cartesian(a, d)
                pygame.draw.circle(surface, (0, 100, 0), (hx, hy), 2)
                
            # Draw current position
            x, y = self.get_pos()
            pygame.draw.circle(surface, self.color, (x, y), 5)

            # Draw label
            label_surf = font.render(self.label, True, self.color)
            surface.blit(label_surf, (x + 10, y - 10))

            # Draw predicted trajectory
            pred_angle = (self.angle + self.v_angle * 10) % 360
            pred_dist = self.distance + self.v_dist * 10
            #pred_dist = max(50, min(RADIUS, pred_dist))
            px, py = polar_to_cartesian(pred_angle, pred_dist)
            pygame.draw.line(surface, (0, 255, 255), (x, y), (px, py), 1)

# Convert polar coords to screen coords
def polar_to_cartesian(angle_deg, distance):
    rad = math.radians(angle_deg)
    x = CENTER[0] + distance * math.cos(rad)
    y = CENTER[1] + distance * math.sin(rad)
    return int(x), int(y)

# Initialize targets
labels = ["🚀 Missile", "✈️ Jet", "🛸 Drone"]
targets = []

def spawn_target():
    angle = random.randint(0, 359)
    dist = random.uniform(RADIUS + 50, RADIUS + 150)  # outside radar circle
    label = random.choice(labels)
    
    if "✈️" in label:
        # Planes fly inward first
        v_dist = -random.uniform(0.5, 1.0)  # move inward
        v_angle = 0  # or small angular speed
    else:
        # Missiles/drones fly straight inward
        v_dist = -random.uniform(1.0, 2.0)  # faster inward
        v_angle = 0
    
    targets.append(Target(angle, dist, v_angle, v_dist, label))


# Game loop
running = True
spawn_cooldown = 0

while running:
    screen.fill((0, 0, 0))

    # Draw radar circle
    pygame.draw.circle(screen, (0, 255, 0), CENTER, RADIUS, 1)

    # Sweep
    sweep_x = CENTER[0] + RADIUS * math.cos(math.radians(angle))
    sweep_y = CENTER[1] + RADIUS * math.sin(math.radians(angle))
    pygame.draw.line(screen, (0, 255, 0), CENTER, (sweep_x, sweep_y), 2)
    angle = (angle + 1) % 360

    # Crosshairs
    pygame.draw.line(screen, (0, 100, 0), (CENTER[0], CENTER[1]-RADIUS), (CENTER[0], CENTER[1]+RADIUS), 1)
    pygame.draw.line(screen, (0, 100, 0), (CENTER[0]-RADIUS, CENTER[1]), (CENTER[0]+RADIUS, CENTER[1]), 1)

    # Update and draw targets
    for target in targets[:]:
        alive = target.update()
        if not alive:
            targets.remove(target)
        else:
            target.draw(screen)

    # Spawn new targets
    if spawn_cooldown <= 0:
        spawn_target()
        spawn_cooldown = 120  # frames
    else:
        spawn_cooldown -= 1

    pygame.display.flip()
    clock.tick(60)

    # Quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
