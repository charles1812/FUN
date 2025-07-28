import pygame
import math
import random

pygame.init()
WIDTH, HEIGHT = 800, 800
CENTER = WIDTH // 2, HEIGHT // 2
RADIUS = 350

REAL_RADIUS_KM = 100
PIXEL_RADIUS = RADIUS  # keep as 350
KM_PER_PIXEL = REAL_RADIUS_KM / PIXEL_RADIUS  # ~0.2857 km per pixel

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

def kmh_to_pixel_per_frame(kmh):
    km_per_sec = kmh / 3600
    pixel_per_sec = km_per_sec / KM_PER_PIXEL
    return pixel_per_sec / 60  # 60 FPS

# Initialize targets
labels = ["🚀 Missile", "✈️ Jet", "🛸 Drone"]
targets = []

def spawn_swarm(count=20, arrival_time=5.0, label="🛸 Drone"):
    for _ in range(count):
        angle = random.uniform(0, 360)
        dist = random.uniform(RADIUS + 100, RADIUS + 300)  # start outside radar
        v_dist = -kmh_to_pixel_per_frame(300)  # calculate speed to hit center on time
        v_angle = 0
        targets.append(Target(angle, dist, v_angle, v_dist, label))

def spawn_plane():
    angle = random.randint(0, 359)
    dist = random.uniform(RADIUS + 50, RADIUS + 150)  # outside radar circle
    label = "✈️ Jet"
    
    # Planes fly inward first
    v_dist = -kmh_to_pixel_per_frame(2000)  # move inward
    v_angle = 0  # or small angular speed
    
    targets.append(Target(angle, dist, v_angle, v_dist, label))

def spawn_missiles():
    angle = random.randint(0, 359)
    dist = random.uniform(RADIUS + 50, RADIUS + 150)  # outside radar circle
    label = "🚀 Missile"

        # Missiles/drones fly straight inward
    v_dist = -kmh_to_pixel_per_frame(3000)  # faster inward
    v_angle = 0
    
    targets.append(Target(angle, dist, v_angle, v_dist, label))


# Game loop
running = True
spawn_cooldown = 0

while running:
    screen.fill((0, 0, 0))

    # Draw radar circle
    pygame.draw.circle(screen, (0, 255, 0), CENTER, RADIUS, 1)
    for i in range(10, REAL_RADIUS_KM + 1, 10):
        r = int(i / KM_PER_PIXEL)
        pygame.draw.circle(screen, (0, 80, 0), CENTER, r, 1)

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
        spawn_cooldown = 120  # frames
    else:
        spawn_cooldown -= 1

    # Timed drone/missile swarm spawn every 10 seconds

    pygame.display.flip()
    clock.tick(60)

    # Quit
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                swarm_size = random.randint(10, 50)
                spawn_swarm(count=swarm_size, arrival_time=500.0)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                spawn_plane()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                spawn_missiles()
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
