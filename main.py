import pygame
import sys
import random

# Initialisierung von Pygame
pygame.init()

# Screen size and colors
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
BG_COLOR = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Background size
BACKGROUND_WIDTH = 3200
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
TRANSITION_SPEED = 8000 # Less milisecs, means faster transition

# Infos about the actual screen size of user
info = pygame.display.Info()
ACTUAL_SCREEN_WIDTH, ACTUAL_SCREEN_HEIGHT = info.current_w, info.current_h
is_fullscreen = False

# Car lanes y positions  for fullscreen and windowed
car_lanes_windowed = [
    SCREEN_HEIGHT // 3 - 20,
    SCREEN_HEIGHT // 3 + 80,
    SCREEN_HEIGHT // 3 + 185,
    SCREEN_HEIGHT // 3 + 290
]

car_lanes_fullscreen = [
    ACTUAL_SCREEN_HEIGHT // 3 + 20,
    ACTUAL_SCREEN_HEIGHT // 3 + 125,    
    ACTUAL_SCREEN_HEIGHT // 3 + 230,
    ACTUAL_SCREEN_HEIGHT // 3 + 335    
]

# Bike lanes y positions for fullscreen and windowed
bike_lanes_windowed = [
    SCREEN_HEIGHT // 3 - 80,
    SCREEN_HEIGHT // 3 + 380
]

bike_lanes_fullscreen = [
    ACTUAL_SCREEN_HEIGHT // 3 - 40,
    ACTUAL_SCREEN_HEIGHT // 3 + 425
]

# Defining the scale factor for fullscreen scalling - I decided not to use this method, as it decreases the quality
'''GAME_ASPECT_RATIO = SCREEN_WIDTH / SCREEN_HEIGHT
SCREEN_ASPECT_RATIO = ACTUAL_SCREEN_WIDTH / ACTUAL_SCREEN_HEIGHT
        
if GAME_ASPECT_RATIO > SCREEN_ASPECT_RATIO:
    scale_factor_fullscreen = ACTUAL_SCREEN_WIDTH / SCREEN_WIDTH
else:
    scale_factor_fullscreen = ACTUAL_SCREEN_HEIGHT / SCREEN_HEIGHT

scale_factor_windowed = 1
scale_factor = scale_factor_windowed'''

# Tracking game time
start_time = pygame.time.get_ticks()

# Important for night to day transition and reverse transition
transition_start_time = None
reverse_transition = False

# Initiate screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("ESA_3")

# Initiate game surface - this works together with "screen" and "scale_factor" to switch between fullscreen and windowed
game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))


# Laden des Hintergrundbilds
# current_background = pygame.image.load("backgrounds/background_2.png").convert()
# current_background = pygame.transform.rotate(current_background, 90)  # Drehe den Hintergrund um 90 Grad nach rechts
# current_background = pygame.transform.scale(current_background, (BACKGROUND_WIDTH, BACKGROUND_HEIGHT))  # Verkleinere die Hintergrunddatei

# Loading start screen
start_screen = pygame.image.load("start_screen3.png").convert()
start_screen = pygame.transform.scale(start_screen, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Loading background transition images
transition_images = [
    # .. and scale backgrounds.
    pygame.transform.scale(
        # .. rotate ..
        pygame.transform.rotate(
            # Load, ..
            pygame.image.load(f"backgrounds/day_to_night_transition_long_roads/background_2_day_to_night_{i}.png").convert(),
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
player_rect.centery = random.choice(car_lanes_windowed)  # Change position on y-achsis to a predefined lane
player_speed_x = 0  # Anfangsgeschwindigkeit in X-Richtung
player_speed_y = 0  # Anfangsgeschwindigkeit in Y-Richtung
acceleration = PLAYER_ACCELERATION  # Beschleunigung

# Gegner-Auto-Eigenschaften
enemy_image = random.choice(enemy_images)
enemy_rect = enemy_image.get_rect()
enemy_rect.centerx = SCREEN_WIDTH  # Startposition des gegnerischen Autos auf der rechten Seite
enemy_rect.centery = random.choice(car_lanes_windowed)
enemy_speed = ENEMY_SPEED

# Game clock
clock = pygame.time.Clock()

# Defining a Button class to use buttons in the start screen and also the game screen
# I am not sure if the color strategy (hover_color, initial_color, font_color) is the most efficient, but it does work for now
# - might need to take another look later
class Button:
    def __init__(self, x, y, text, font_size=80, font_color=(0, 0, 0), hover_color=(255, 255, 255)):
        # Our own font
        self.font = pygame.font.Font('fonts/Pixeltype.ttf', font_size)
        self.text = text
        self.hover_color = hover_color
        self.initial_color = font_color
        self.font_color = font_color
        self.text_img = self.font.render(self.text, True, font_color)
        self.rect = self.text_img.get_rect(center=(x, y))

    def draw(self, surface):
        if self.is_hovered(pygame.mouse.get_pos()):
            self.font_color = self.hover_color
        else:
            self.font_color = self.initial_color

        self.text_img = self.font.render(self.text, True, self.font_color)
        surface.blit(self.text_img, self.rect)
    
    def move(self, new_x, new_y):
        self.rect.center = (new_x, new_y)

    def is_hovered(self, pos):
        return self.rect.collidepoint(pos)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered(pygame.mouse.get_pos()):
                return True
        return False


# Instantiate buttons

# Buttons for start screen
start_button = Button(SCREEN_WIDTH // 2 + 110 , SCREEN_HEIGHT // 2 + 180, "START", font_size=90)
quit_button_start_screen = Button(SCREEN_WIDTH // 2 - 18, SCREEN_HEIGHT // 2 + 60, "Quit", font_size=55)

# Buttons for ingame
quit_button = Button(50, 30, "Quit", font_size=40)


# This is the start screen loop
start_screen_running = True
while start_screen_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()  
        # The start screen loop will terminate, when the start button is clicked - this will bring the player to the main game loop (follow code)
        if start_button.is_clicked(event):
            start_screen_running = False
        # The window will be closed when the quit button is pressed
        if quit_button_start_screen.is_clicked(event):
            pygame.quit()  #
            sys.exit()

    # Drawing
    screen.blit(start_screen, (0, 0))
    start_button.draw(screen)
    quit_button_start_screen.draw(screen)
    pygame.display.update()


# This is the main game loop
game_is_running = True
while game_is_running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Testing the button
        if quit_button.is_clicked(event):
            pygame.quit() 
            sys.exit()
        # Testing fullscreen toggle
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    screen = pygame.display.set_mode((ACTUAL_SCREEN_WIDTH, ACTUAL_SCREEN_HEIGHT), pygame.FULLSCREEN)
                    # We change the position of the car, as we draw the background image at a different background position for the fullscreen mode
                    # The y position of the background image is at "ACTUAL_SCREEN_HEIGHT // 8", so we need to adjust all the cars
                    player_rect.centery += ACTUAL_SCREEN_HEIGHT // 8
                    enemy_rect.centery += ACTUAL_SCREEN_HEIGHT // 8
                else:
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
                    player_rect.centery -= ACTUAL_SCREEN_HEIGHT // 8
                    enemy_rect.centery -= ACTUAL_SCREEN_HEIGHT // 8

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
    for x in range(bg_x, ACTUAL_SCREEN_WIDTH, current_background.get_width()):
        if is_fullscreen:
            y = ACTUAL_SCREEN_HEIGHT // 8
        else:
            y = 0
        screen.blit(current_background, (x, y))  # Zeichne das Hintergrundbild an der aktuellen Position
    screen.blit(player_image, player_rect)
    screen.blit(enemy_image, enemy_rect)

    # Moving the button around based on screen size
    quit_button.draw(screen)
    if not is_fullscreen:
        quit_button.move(50, 30)
    else:
        quit_button.move(50, ACTUAL_SCREEN_HEIGHT // 8 + 30)

    # Kollisionserkennung
    if player_rect.colliderect(enemy_rect):
        print("GAME OVER")
        # Setze das Kollisionsrechteck auf die Position der Kollision
        collision_rect = pygame.Rect(player_rect.x, player_rect.y, player_rect.width, player_rect.height)

        # Beendet das Spiel und das Programm
        pygame.quit()
        sys.exit()

    # Zurücksetzen des gegnerischen Autos

    # Selecting lane (y poisition) based on fullscreen or windowed
    selected_lane = random.choice(car_lanes_fullscreen) if is_fullscreen else random.choice(car_lanes_windowed)

    if enemy_rect.right < 0:
        enemy_rect.centerx = ACTUAL_SCREEN_WIDTH if is_fullscreen else SCREEN_WIDTH
        # Startposition des gegnerischen Autos auf der rechten Seite
        enemy_rect.centery = selected_lane
        enemy_image = random.choice(enemy_images)

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


