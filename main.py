import pygame
import sys
import random

# Initialisierung von Pygame
pygame.init()

# Fenstergröße und Farben
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
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

# Night day transition
NIGHT_DAY_CYCLE = 20000 # More milisecs, means longer day/night
TRANSITION_SPEED = 5000 # Less milisecs, means faster transition

# Tracking game time
start_time = pygame.time.get_ticks()

# Important for night to day transition and reverse transition
transition_start_time = None
reverse_transition = False

# Pygame-Fenster einrichten
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ESA_3")

# Laden des Hintergrundbilds
# current_background = pygame.image.load("backgrounds/background_2.png").convert()
# current_background = pygame.transform.rotate(current_background, 90)  # Drehe den Hintergrund um 90 Grad nach rechts
# current_background = pygame.transform.scale(current_background, (BACKGROUND_WIDTH, BACKGROUND_HEIGHT))  # Verkleinere die Hintergrunddatei

# Loading background transition images
transition_images = [
    # .. and scale backgrounds.
    pygame.transform.scale(
        # .. rotate ..
        pygame.transform.rotate(
            # Load, ..
            pygame.image.load(f"backgrounds\day_to_night_transition/background_2_day_to_night_{i}.png").convert(),
            90
        ),
        (BACKGROUND_WIDTH, BACKGROUND_HEIGHT)
    )
    for i in range(1, 9)
]

# Loading enemy car images
enemy_images = [
    # .. and scale enemy cars.
    pygame.transform.scale(
        # .. rotate
        pygame.transform.rotate(
            # Load, ..
            pygame.image.load(f"enemies/enemy{i}.png").convert_alpha(),
            90
        ),
        (ENEMY_WIDTH_CAR, ENEMY_HEIGHT_CAR)
    )
    for i in range(1, 5)  # We assume to have 4 enemy car pictures
]


# Default background
current_background = transition_images[0]

# Initialisierung der Hintergrundposition
bg_x = 0

# Spielfigur-Eigenschaften
player_image = pygame.image.load("car2.png").convert_alpha()  # Passe den Pfad zur Spielfigur an
player_image = pygame.transform.rotate(player_image, 90)  # Drehe die Spielfigur um 90 Grad nach links
player_image = pygame.transform.scale(player_image, (PLAYER_WIDTH, PLAYER_HEIGHT))  # Verkleinere die Spielfigur
player_rect = player_image.get_rect()
player_rect.centerx = SCREEN_WIDTH // 4  # Ändere die Position auf der X-Achse
player_rect.centery = SCREEN_HEIGHT // 2   # Ändere die Position auf der Y-Achse
player_speed_x = 0  # Anfangsgeschwindigkeit in X-Richtung
player_speed_y = 0  # Anfangsgeschwindigkeit in Y-Richtung
acceleration = PLAYER_ACCELERATION  # Beschleunigung

# Gegner-Auto-Eigenschaften
enemy_image = random.choice(enemy_images)
enemy_rect = enemy_image.get_rect()
enemy_rect.centerx = SCREEN_WIDTH  # Startposition des gegnerischen Autos auf der rechten Seite
enemy_rect.centery = random.randint(50, SCREEN_HEIGHT - enemy_rect.height)
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
    if bg_x < -current_background.get_width():
        bg_x = 0

    # Bewegung des Spielers basierend auf Geschwindigkeit
    player_rect.centery += player_speed_y
    player_rect.centerx += player_speed_x

    #Zeichnen
    for x in range(bg_x, SCREEN_WIDTH, current_background.get_width()):
        screen.blit(current_background, (x, 0))  # Zeichne das Hintergrundbild an der aktuellen Position
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
        enemy_rect.centerx = SCREEN_WIDTH  # Startposition des gegnerischen Autos auf der rechten Seite
        enemy_rect.centery = random.randint(50, SCREEN_HEIGHT - enemy_rect.height)
        enemy_image = random.choice(enemy_images)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()    


    # Keeping track of time
    elapsed_time = pygame.time.get_ticks() - start_time

    ############################################## Night to day and day to night transition loop ##############################################

    # After 1 minute of daytime driving, we start the transition
    # We give elapsed_time a window due to the inprecision of .get_ticks()
    if NIGHT_DAY_CYCLE <= elapsed_time < 66000 and transition_start_time is None:
        transition_start_time = pygame.time.get_ticks()
    
    # We keep track of when the transition started
    if transition_start_time:
        time_since_transition_start = pygame.time.get_ticks() - transition_start_time

        # While we are not in a reverse transition, we change the background image every 5 seconds
        if not reverse_transition:
            transition_index = time_since_transition_start // TRANSITION_SPEED  # every 5 seconds

            # We only change the background image, when it is fully on screen ((SCREEN_WIDTH - BACKGROUND_WIDTH) < bg_x <= 0) 
            # and while we still have new transition images in our list
            if transition_index < len(transition_images) and (SCREEN_WIDTH - BACKGROUND_WIDTH) < bg_x <= 0:
                current_background = transition_images[transition_index]
            # Once we run out of transition images, we let it be night (last image in list) for the given time (NIGHT_DAY_CYCLE) 
            elif transition_index >= len(transition_images):
                if time_since_transition_start < (len(transition_images) * TRANSITION_SPEED + NIGHT_DAY_CYCLE): 
                    current_background = transition_images[-1]  # This line is mostly for readibility, since this is the latest current_background anyways
                # Once the  time_since_transition has exceeded the given values (it comes out to 1 minute night), we start the reverse transition
                else:  
                    reverse_transition = True
                    transition_start_time = pygame.time.get_ticks()

        # We keep time of when the reverse transition started and make sure the transition_index counts reversly (e.g. 8 to 1)
        if reverse_transition:
            time_since_reverse_transition = pygame.time.get_ticks() - transition_start_time
            transition_index = len(transition_images) - 1 - time_since_reverse_transition // TRANSITION_SPEED

            # We only change the background image, when it is fully on screen ((SCREEN_WIDTH - BACKGROUND_WIDTH) < bg_x <= 0)
            # and while we still have new transition images in our list
            if 0 <= transition_index < len(transition_images) and (SCREEN_WIDTH - BACKGROUND_WIDTH) < bg_x <= 0:
                current_background = transition_images[transition_index]
            # Once we ran out of transitin images, we reset for the next loop
            elif transition_index < 0:
                start_time = pygame.time.get_ticks()
                transition_start_time = None
                reverse_transition = False

    ##########################################################################################################################################

    pygame.display.update()
    clock.tick(120) #Geschwindigkeit des Spiels generell (kann verändert werden, um das Spiel schwieriger zu machen


