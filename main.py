import pygame
import sys
import random

# Initialisierung von Pygame
pygame.init()

# Fenstergröße und Farben
WIDTH, HEIGHT = 1200, 800
BG_COLOR = (0, 0, 0)

# Background size
BACKGROUND_WIDTH = 1600
BACKGROUND_HEIGHT = 800

# Player size
PLAYER_WIDTH = 110
PLAYER_HEIGHT = 55

# Enemy sizes
ENEMY_WIDTH_CAR = 110
ENEMY_HEIGHT_CAR = 55

# Added constants to control game speed in one place
BACKGROUND_SPEED = 3
ENEMY_SPEED = 2

PLAYER_ACCELERATION = 0.5
PLAYER_SPEED_MAX = 5
PLAYER_SPEED_MIN = -5

# Tracking game time
start_time = pygame.time.get_ticks()

# Pygame-Fenster einrichten
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ESA_3")

# Laden des Hintergrundbilds
background_image = pygame.image.load("backgrounds/background_2.png").convert()
background_image = pygame.transform.rotate(background_image, 90)  # Drehe den Hintergrund um 90 Grad nach rechts
background_image = pygame.transform.scale(background_image, (BACKGROUND_WIDTH, BACKGROUND_HEIGHT))  # Verkleinere die Hintergrunddatei

# Loading background transition images
transition_images = [
    pygame.transform.scale(
        pygame.transform.rotate(
            pygame.image.load(f"backgrounds\day_to_night_transition/background_2_day_to_night_{i}.png").convert(),
            90
        ),
        (BACKGROUND_WIDTH, BACKGROUND_HEIGHT)
    )
    for i in range(1, 9)
]


# Initialisierung der Hintergrundposition
bg_x = 0

# Spielfigur-Eigenschaften
player_image = pygame.image.load("car2.png").convert_alpha()  # Passe den Pfad zur Spielfigur an
player_image = pygame.transform.rotate(player_image, 90)  # Drehe die Spielfigur um 90 Grad nach links
player_image = pygame.transform.scale(player_image, (PLAYER_WIDTH, PLAYER_HEIGHT))  # Verkleinere die Spielfigur
player_rect = player_image.get_rect()
player_rect.centerx = WIDTH // 4  # Ändere die Position auf der X-Achse
player_rect.centery = HEIGHT // 2   # Ändere die Position auf der Y-Achse
player_speed_x = 0  # Anfangsgeschwindigkeit in X-Richtung
player_speed_y = 0  # Anfangsgeschwindigkeit in Y-Richtung
acceleration = PLAYER_ACCELERATION  # Beschleunigung

# Gegner-Auto-Eigenschaften
enemy_image = pygame.image.load("enemy2.png").convert_alpha()  # Passe den Pfad zum gegnerischen Auto an
enemy_image = pygame.transform.rotate(enemy_image, 90)  # Drehe das gegnerische Auto um 90 Grad nach links
enemy_image = pygame.transform.scale(enemy_image, (ENEMY_WIDTH_CAR, ENEMY_HEIGHT_CAR))  # Verkleinere das gegnerische Auto
enemy_rect = enemy_image.get_rect()
enemy_rect.centerx = WIDTH  # Startposition des gegnerischen Autos auf der rechten Seite
enemy_rect.centery = random.randint(50, HEIGHT - enemy_rect.height)
enemy_speed = ENEMY_SPEED



clock = pygame.time.Clock()

while True:


    # Bewegung des Spielers
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player_speed_y -= acceleration  # Beschleunigen nach oben
    elif keys[pygame.K_DOWN]:
        player_speed_y += acceleration  # Beschleunigen nach unten
    else:
        if player_speed_y > 0:
            player_speed_y -= acceleration  # Verlangsamen, wenn keine Taste gedrückt ist
        elif player_speed_y < 0:
            player_speed_y += acceleration  # Verlangsamen, wenn keine Taste gedrückt ist

    if keys[pygame.K_LEFT]:
        player_speed_x -= acceleration  # Beschleunigen nach links
    elif keys[pygame.K_RIGHT]:
        player_speed_x += acceleration  # Beschleunigen nach rechts
    else:
        if player_speed_x > 0:
            player_speed_x -= acceleration  # Verlangsamen, wenn keine Taste gedrückt ist
        elif player_speed_x < 0:
            player_speed_x += acceleration  # Verlangsamen, wenn keine Taste gedrückt ist

    # Begrenze die Geschwindigkeit, um zu verhindern, dass sie zu groß wird
    player_speed_y = max(PLAYER_SPEED_MIN, min(PLAYER_SPEED_MAX, player_speed_y))
    player_speed_x = max(PLAYER_SPEED_MIN, min(PLAYER_SPEED_MAX, player_speed_x))

    # Bewegung des gegnerischen Autos
    enemy_rect.centerx -= enemy_speed

    # Bewegung des Hintergrundbilds
    bg_x -= BACKGROUND_SPEED  # Ändere die Geschwindigkeit, wie das Hintergrundbild nach links läuft

    # Wenn das Hintergrundbild aus dem Bildschirm verschwindet, setze es zurück
    if bg_x < -background_image.get_width():
        bg_x = 0

    # Bewegung des Spielers basierend auf Geschwindigkeit
    player_rect.centery += player_speed_y
    player_rect.centerx += player_speed_x

    #Zeichnen
    for x in range(bg_x, WIDTH, background_image.get_width()):
        screen.blit(background_image, (x, 0))  # Zeichne das Hintergrundbild an der aktuellen Position
    screen.blit(player_image, player_rect)
    screen.blit(enemy_image, enemy_rect)

    # Kollisionserkennung
    if player_rect.colliderect(enemy_rect):
        print("GAME OVER")
        # Setze das Kollisionsrechteck auf die Position der Kollision
        collision_rect = pygame.Rect(player_rect.x, player_rect.y, player_rect.width, player_rect.height)

        # Beendet das Spiel und das Programm
        pygame.quit()
        sys.exit()


    # Zurücksetzen des gegnerischen Autos
    if enemy_rect.right < 0:
        enemy_rect.centerx = WIDTH  # Startposition des gegnerischen Autos auf der rechten Seite
        enemy_rect.centery = random.randint(50, HEIGHT - enemy_rect.height)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()    

    pygame.display.update()
    clock.tick(120) #Geschwindigkeit des Spiels generell (kann verändert werden, um das Spiel schwieriger zu machen