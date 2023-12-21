import pygame
import sys
import random
import time

# Initialisierung von Pygame
pygame.init()
print(pygame.mixer.get_init())
pygame.mixer.init()


# Defining a Button class to use buttons in the start screen and also the game screen
# I am not sure if the color strategy (hover_color, initial_color, font_color) is the most efficient, but it does work for now
# - might need to take another look later
class Button:
    def __init__(self, x, y, text, font_size=80, 
                 font_color=(0, 0, 0), hover_color=(255, 255, 255)):
        self.font = pygame.font.Font('fonts/Pixeltype.ttf', font_size)
        self.text = text
        self.colors = {'default': font_color, 'hover': hover_color}
        self.current_color = 'default'
        self.text_img = self.font.render(self.text, True, self.colors[self.current_color])
        self.rect = self.text_img.get_rect(center=(x, y))

    def draw(self, surface):
        # Update color based on hover state
        self.current_color = 'hover' if self.is_hovered(pygame.mouse.get_pos()) else 'default'
        self.text_img = self.font.render(self.text, True, self.colors[self.current_color])
        surface.blit(self.text_img, self.rect)

    def is_hovered(self, pos):
        return self.rect.collidepoint(pos)

    def move(self, new_x, new_y):
        self.rect.center = (new_x, new_y)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered(pygame.mouse.get_pos()):
                return True
        return False




# Main game class
class Game:

    # Tankanzeige
    def draw_shrinking_bar(self):
        if self.tank_width > 0:
            self.tank_width -= 1
            self.screen.fill(self.BG_COLOR)

            pygame.draw.rect(self.screen, self.GREEN, self.tank_rect)



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

    # Enemy car sizes
    ENEMY_WIDTH_CAR = 110
    ENEMY_HEIGHT_CAR = 55

    # Enemy bike sizes
    BIKE_WIDTH = 80
    BIKE_HEIGHT = 42

    # Added constants to control game speed in one place
    BACKGROUND_SPEED = 3
    ENEMY_SPEED = 2

    PLAYER_ACCELERATION = 0.5
    PLAYER_SPEED_MAX = 5
    PLAYER_SPEED_MIN = -5

    # Night day transition
    NIGHT_DAY_CYCLE = 20000 # More milisecs, means longer day/night
    TRANSITION_SPEED = 8000 # Less milisecs, means faster transition

    # Car lanes y positions for windowed mode
    car_lanes_windowed = [
        SCREEN_HEIGHT // 3 - 20,
        SCREEN_HEIGHT // 3 + 80,
        SCREEN_HEIGHT // 3 + 185,
        SCREEN_HEIGHT // 3 + 290
    ]

    # Bike lanes y positions for windowed mode
    bike_lanes_windowed = [
        SCREEN_HEIGHT // 3 - 80,
        SCREEN_HEIGHT // 3 + 380
    ]

    # Resources
    transition_images = []
    enemy_images = []

    # Default background
    current_background = None
    # Background Position X
    bg_x = 0

    player_rect = None

    player_speed_x = 0  # Anfangsgeschwindigkeit in X-Richtung
    player_speed_y = 0  # Anfangsgeschwindigkeit in Y-Richtung
    player_acceleration = 0

    #
    # enemy_rect = None
    # enemy_speed = 0

    # start screen
    start_screen_image = None

    # fullscreen
    is_fullscreen = True


    def __init__(self):
    # Infos about the actual screen size of user
        info = pygame.display.Info()
        self.ACTUAL_SCREEN_WIDTH, self.ACTUAL_SCREEN_HEIGHT = info.current_w, info.current_h

        # Minimum and maximum car position - invisible borders that the car can not cross
        self.MIN_Y = self.ACTUAL_SCREEN_HEIGHT // 8
        self.MAX_Y = (self.ACTUAL_SCREEN_HEIGHT // 8) * 7 -10
        self.MIN_X = 0
        self.MAX_X = self.ACTUAL_SCREEN_WIDTH


        self.car_lanes_fullscreen = [
            self.ACTUAL_SCREEN_HEIGHT // 3 + 20,
            self.ACTUAL_SCREEN_HEIGHT // 3 + 125,    
            self.ACTUAL_SCREEN_HEIGHT // 3 + 230,
            self.ACTUAL_SCREEN_HEIGHT // 3 + 335    
        ]

        self.bike_lanes_fullscreen = [
            self.ACTUAL_SCREEN_HEIGHT // 3 - 70,
            self.ACTUAL_SCREEN_HEIGHT // 3 + 395
        ]

        # Tracking game time
        self.start_time = pygame.time.get_ticks()

        # Important for night to day transition and reverse transition
        self.transition_start_time = None
        self.reverse_transition = False

        # Initiate screen - start screen is windowed
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.NOFRAME)


        # Initiate game surface - this works together with "screen" and "scale_factor" to switch between fullscreen and windowed
        self.game_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        # Buttons for start screen
        self.start_button = Button(self.SCREEN_WIDTH // 2 + 110 , self.SCREEN_HEIGHT // 2 + 180, "START", font_size=90)
        self.quit_button_start_screen = Button(self.SCREEN_WIDTH // 2 - 18, self.SCREEN_HEIGHT // 2 + 60, "Quit", font_size=55)

        # Buttons for ingame
        self.quit_button = Button(50, 30, "Quit", font_size=40) 

        # pygame.display.set_caption("ESA_3")

        # Game state
        self.state = self.start_screen  # Start with the start_screen state

        # For spawning cars 
        self.last_spawn_time = pygame.time.get_ticks()

        # Game clock
        self.clock = pygame.time.Clock()
        
        self.load_resources()



    def load_resources(self):
        # Lade Sounds
        self.load_sound()

        # Loading background images 
        self.transition_images = [
            # .. and scale backgrounds.
            pygame.transform.scale(
                # .. rotate ..
                pygame.transform.rotate(
                    # Load, ..
                    pygame.image.load(f"backgrounds/day_to_night_transition_long_roads/background_2_day_to_night_{i}.png").convert(),
                    90
                ),
                (self.BACKGROUND_WIDTH, self.BACKGROUND_HEIGHT)
            )
            for i in range(1, 10)
        ]

        self.current_background = self.transition_images[0]
        
        # Loading enemy car images
        self.enemy_images = [
            # .. and scale enemy cars.
            pygame.transform.scale(
                # .. rotate
                pygame.transform.rotate(
                    # Load, ..
                    pygame.image.load(f"enemies/enemy{i}.png").convert_alpha(),
                    90
                ),
                (self.ENEMY_WIDTH_CAR, self.ENEMY_HEIGHT_CAR)
            )
            for i in range(1, 5)  # We assume to have 4 enemy car pictures
        ]


        self.bike_animation_images = [
            pygame.transform.scale(
                pygame.transform.rotate(
                    pygame.image.load(f"bike1_animation/bike1_animation_part{i}.png").convert_alpha(),
                    90
                ),
                (self.BIKE_WIDTH, self.BIKE_HEIGHT)
            )
            for i in range(1, 4)  # Assuming you have 3 bike images
        ]

        # self.enemy_image = random.choice(self.enemy_images)
        # self.enemy_rect = self.enemy_image.get_rect()

        # This is examplorary to understand how the lists enemy_images and transition_images are formed
        self.player_image = pygame.image.load("car2.png").convert_alpha()  # Loading image
        self.player_image = pygame.transform.rotate(self.player_image, 90)  # Rotating
        self.player_image = pygame.transform.scale(self.player_image, (self.PLAYER_WIDTH, self.PLAYER_HEIGHT)) # Scaling
        self.player_rect = self.player_image.get_rect()

        self.start_screen_image = pygame.image.load("start_screen3.png").convert()
        self.start_screen_image = pygame.transform.scale(self.start_screen_image, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))


    def initialize_behaviour(self):

        # Starting in Fullscreen - Here you can decide in which mode to start
        self.screen = pygame.display.set_mode((self.ACTUAL_SCREEN_WIDTH, self.ACTUAL_SCREEN_HEIGHT), pygame.FULLSCREEN) # Fullscreen
        # self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.NOFRAME) # Windowed
        self.is_fullscreen = True
                           
        self.player_rect.centerx = self.SCREEN_WIDTH // 4  # Ändere die Position auf der X-Achse
        self.player_rect.centery = random.choice(self.car_lanes_fullscreen) if self.is_fullscreen else random.choice(self.car_lanes_windowed)  # Change position on y-axis to a predefined lane
        self.player_speed_x = 0  # Anfangsgeschwindigkeit in X-Richtung
        self.player_speed_y = 0  # Anfangsgeschwindigkeit in Y-Richtung
        self.player_acceleration = self.PLAYER_ACCELERATION  # Beschleunigung

        self.enemies = []
        self.bikes = []

        # self.enemy_rect.centerx = self.SCREEN_WIDTH  # Startposition des gegnerischen Autos auf der rechten Seite
        # self.enemy_rect.centery = random.choice(self.car_lanes_windowed)
        # self.enemy_speed = self.ENEMY_SPEED
        # Spawn an initial car
        self.spawn_car()

    def will_collide(self, new_enemy_rect):
        buffer_space = 20  # 20 pixels buffer, you can adjust
        for enemy in self.enemies:
            # Inflate the existing enemy rect by the buffer space
            if enemy["rect"].inflate(buffer_space, 0).colliderect(new_enemy_rect):
                return True
        return False


    def spawn_car(self):
        enemy_image = random.choice(self.enemy_images)
        enemy_rect = enemy_image.get_rect()

        enemy_rect.centerx = self.ACTUAL_SCREEN_WIDTH if self.is_fullscreen else self.SCREEN_WIDTH
        enemy_rect.centerx += 50 # Adding cars a bit outside of screen, so they drive in
        attempts = 5 # Using a maximum number of attempts to avoid endless loop when screen is crowded

        for _ in range(attempts):
            enemy_rect.centery = random.choice(self.car_lanes_fullscreen) if self.is_fullscreen else random.choice(self.car_lanes_windowed)
            if not self.will_collide(enemy_rect):
                enemy_speed = self.ENEMY_SPEED
                self.enemies.append({"image": enemy_image, "rect": enemy_rect, "speed": enemy_speed})
                break

    # load sound for spawning bike
    def load_bike_sound(self):
        # load bike sound
        self.bike_sound = pygame.mixer.Sound("./sounds/bike.wav")
        self.bike_sound.set_volume(0.15)

    def play_bike_sound(self):
        self.bike_sound.play()
        pygame.mixer.Channel(1).play(self.bike_sound)

    def spawn_bike(self):
        # Position the bike off the screen to the right
        new_bike = Bike(self.ACTUAL_SCREEN_WIDTH +50, random.choice(self.bike_lanes_fullscreen), random.randint(4, 6), self.bike_animation_images)
        self.bikes.append(new_bike)
        # sound for spawning bike
        self.play_bike_sound()  # Aufruf des bike spawn sounds



    def night_day_transition(self):

        # Keeping track of time
        elapsed_time = pygame.time.get_ticks() - self.start_time

        # After "NIGHT_DAY_CYCLE" milliseconds of daytime driving, we start the transition
        # We give elapsed_time a window due to the inprecision of .get_ticks()
        if self.NIGHT_DAY_CYCLE <= elapsed_time < self.NIGHT_DAY_CYCLE + 6000 and self.transition_start_time is None:
            self.transition_start_time = pygame.time.get_ticks()

        # We keep track of when the transition started
        if self.transition_start_time:
            time_since_transition_start = pygame.time.get_ticks() - self.transition_start_time

            # While we are not in a reverse transition (night to day), we change the background image every 5 seconds
            if not self.reverse_transition:
                transition_index = time_since_transition_start // self.TRANSITION_SPEED  # every 5 seconds

                # We only change the background image, when it is fully on screen ((SCREEN_WIDTH - BACKGROUND_WIDTH) < bg_x <= 0) 
                # and while we still have new transition images in our list
                if transition_index < len(self.transition_images) and (self.SCREEN_WIDTH - self.BACKGROUND_WIDTH) < self.bg_x <= 0:
                    self.current_background = self.transition_images[transition_index]
                # Once we run out of transition images, we let it be night (last image in list) for the given time (NIGHT_DAY_CYCLE) 
                elif transition_index >= len(self.transition_images):
                    if time_since_transition_start < (len(self.transition_images) * self.TRANSITION_SPEED + self.NIGHT_DAY_CYCLE): 
                        self.current_background = self.transition_images[-1]  # This line is mostly for readibility, since this is the latest current_background anyways
                    # Once the  time_since_transition has exceeded the given values (it comes out to 1 minute night), we start the reverse transition
                    else:  
                        self.reverse_transition = True
                        self.transition_start_time = pygame.time.get_ticks()

            # We keep time of when the reverse transition started and make sure the transition_index counts reversly (e.g. 8 to 1)
            if self.reverse_transition:
                time_since_reverse_transition = pygame.time.get_ticks() - self.transition_start_time
                transition_index = len(self.transition_images) - 1 - time_since_reverse_transition // self.TRANSITION_SPEED

                # We only change the background image, when it is fully on screen ((SCREEN_WIDTH - BACKGROUND_WIDTH) < bg_x <= 0)
                # and while we still have new transition images in our list
                if 0 <= transition_index < len(self.transition_images) and (self.SCREEN_WIDTH - self.BACKGROUND_WIDTH) < self.bg_x <= 0:
                    self.current_background = self.transition_images[transition_index]
                # Once we ran out of transitin images, we reset for the next loop
                elif transition_index < 0:
                    self.start_time = pygame.time.get_ticks()
                    self.transition_start_time = None
                    self.reverse_transition = False
    

    def update_player_position(self):

        # Movement of player based on speed (y-axis)
        self.player_rect.centery += self.player_speed_y

        # Check and adjust if the player car is out of the bounds:
        if self.player_rect.top < self.MIN_Y:
            self.player_rect.top = self.MIN_Y
        elif self.player_rect.bottom > self.MAX_Y:
            self.player_rect.bottom = self.MAX_Y

        # Movement of player based on speed (x-axis)
        self.player_rect.centerx += self.player_speed_x

        # Check and adjust if the player car is out of the x-bounds:
        if self.player_rect.left < self.MIN_X:
            self.player_rect.left = self.MIN_X
        elif self.player_rect.right > self.MAX_X:
            self.player_rect.right = self.MAX_X



    # Start Screen sound
    def load_sound(self):
        # load start screen sound
        self.start_screen_sound = pygame.mixer.Sound("./sounds/start_screen.wav")
        self.start_screen_sound.set_volume(0.2)

        # load start button sound
        self.start_button_sound = pygame.mixer.Sound("./sounds/button_start_sound.wav")
        self.start_button_sound.set_volume(0.5)

        # load quit button sound
        self.quit_button_sound = pygame.mixer.Sound("./sounds/button_quit_sound.wav")
        self.quit_button_sound.set_volume(0.5)

        # load soundtrack file
        self.soundtrack = pygame.mixer.Sound("./sounds/soundtrack.wav")
        self.soundtrack.set_volume(0.3)

        # load collision file
        self.collision = pygame.mixer.Sound("./sounds/collision.wav")
        self.collision.set_volume(0.5)

        # load vroom file
        self.vroom = pygame.mixer.Sound("./sounds/vroom.wav")
        self.vroom.set_volume(0.5)

    # start_screen sound play
    def play_soundtrack(self):
        pygame.mixer.Channel(5).play(self.soundtrack, loops=-1)  # sound plays forever // extra channel
        self.soundtrack.play()

    # stop soundtrack
    def stop_soundtrack(self):
        # Stoppt den Sound auf Kanal 3 (der Soundtrack-Kanal)
        self.soundtrack.stop() # hier gab es Überlagerungen

    # start_screen sound play
    def play_start_screen_sound(self):
        pygame.mixer.Channel(2).play(self.start_screen_sound, loops=-1) # start screen sound plays forever // extra channel
        self.start_screen_sound.play()

    # start button sound play
    def play_start_button_sound(self):
        pygame.mixer.Channel(0).play(self.start_button_sound) # mixer setting to play sounds on different channels
        self.start_button_sound.play()

    # stop start_screen sound
    def stop_start_screen_sound(self, fadeout_time=1):
        # Stoppt den Sound auf Kanal 2 (der Hintergrundmusik-Kanal)
        pygame.mixer.Channel(2).fadeout(fadeout_time)

    # quit button sound play
    def play_quit_button_sound(self):
        pygame.mixer.Channel(0).play(self.quit_button_sound) # mixer setting to play sounds on different channels
        self.quit_button_sound.play()

    # collision sound play
    def play_collision(self):
        pygame.mixer.Channel(5).play(self.collision) # mixer setting to play sounds on different channels
        self.collision.play()

    # Vroom sound play
    def play_vroom(self):
        pygame.mixer.Channel(5).play(self.vroom) # mixer setting to play sounds on different channels
        self.vroom.play()

    # Start screen state - start screen loop
    def start_screen(self):
        self.stop_soundtrack()
        self.play_start_screen_sound()  # Sound nur im Startbildschirm abspielen
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()  
                # The start screen loop will terminate, when the start button is clicked - this will bring the player to the main game loop (follow code)
                if self.start_button.is_clicked(event):
                    self.stop_start_screen_sound()
                    self.play_start_button_sound() # Aufruf des start button
                    self.start_time = pygame.time.get_ticks() # Start time of main game
                    self.state = self.main_game
                    return
                # The window will be closed when the quit button is pressed
                if self.quit_button_start_screen.is_clicked(event):
                    self.play_quit_button_sound() # Aufruf des start button sounds

                    ### delay damit der sound abgespielt wird bevor das fenster schließt
                    time.sleep(1)
                    # exit game / start screen
                    pygame.quit()
                    sys.exit()

            # Drawing
            self.screen.blit(self.start_screen_image, (0, 0))
            self.start_button.draw(self.screen)
            self.quit_button_start_screen.draw(self.screen)
            pygame.display.update()


    # This is the main game state - main game loop
    def main_game(self):
        self.play_soundtrack()  # Aufruf des soundtracks

        # We need to re-/initialize the behaviour of all game objects, before starting/restarting the game
        self.initialize_behaviour()

        # Initializing self.last_bike_spawn_time for spawning bikes every x milisecs
        self.last_bike_spawn_time = pygame.time.get_ticks()

        # Tankanzeige
        self.tank_width = 300
        self.tank_height = 20


        while True:
            # Zeichnen und Aktualisieren der Tankanzeige
            self.draw_shrinking_bar()
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # Testing the button
                if self.quit_button.is_clicked(event):
                    self.state = self.start_screen
                    self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.NOFRAME)
                    return
                # Testing fullscreen toggle
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        self.is_fullscreen = not self.is_fullscreen
                        if self.is_fullscreen:
                            self.screen = pygame.display.set_mode((self.ACTUAL_SCREEN_WIDTH, self.ACTUAL_SCREEN_HEIGHT), pygame.FULLSCREEN)
                            # We change the position of the car, as we draw the background image at a different background position for the fullscreen mode
                            # The y position of the background image is at "ACTUAL_SCREEN_HEIGHT // 8", so we need to adjust all the cars
                            self.player_rect.centery += self.ACTUAL_SCREEN_HEIGHT // 8
                            for enemy in self.enemies:
                                enemy["rect"].centery += self.ACTUAL_SCREEN_HEIGHT // 8
                        else:
                            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.NOFRAME)
                            self.player_rect.centery -= self.ACTUAL_SCREEN_HEIGHT // 8
                            for enemy in self.enemies:
                                enemy["rect"].centery -= self.ACTUAL_SCREEN_HEIGHT // 8

            # Bewegung des Spielers
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.player_speed_y -= self.player_acceleration  # Beschleunigen nach oben
                # sound
            elif keys[pygame.K_DOWN]:
                self.player_speed_y += self.player_acceleration  # Beschleunigen nach unten
                # sound
            else:
                if self.player_speed_y > 0:
                    self.player_speed_y -= self.player_acceleration  # Verlangsamen, wenn keine Taste gedrückt ist
                elif self.player_speed_y < 0:
                    self.player_speed_y += self.player_acceleration  # Verlangsamen, wenn keine Taste gedrückt ist

            if keys[pygame.K_LEFT]:
                self.player_speed_x -= self.player_acceleration  # Beschleunigen nach links
                # sound
            elif keys[pygame.K_RIGHT]:
                self.player_speed_x += self.player_acceleration  # Beschleunigen nach rechts
                #self.play_vroom()
            else:
                if self.player_speed_x > 0:
                    self.player_speed_x -= self.player_acceleration  # Verlangsamen, wenn keine Taste gedrückt ist
                elif self.player_speed_x < 0:
                    self.player_speed_x += self.player_acceleration  # Verlangsamen, wenn keine Taste gedrückt ist

            # Begrenze die Geschwindigkeit, um zu verhindern, dass sie zu groß wird
            self.player_speed_y = max(self.PLAYER_SPEED_MIN, min(self.PLAYER_SPEED_MAX, self.player_speed_y))
            self.player_speed_x = max(self.PLAYER_SPEED_MIN, min(self.PLAYER_SPEED_MAX, self.player_speed_x))

            # Update enemy cars
            for enemy in self.enemies:
                enemy["rect"].centerx -= enemy["speed"]


            # Bewegung des Hintergrundbilds
            self.bg_x -= self.BACKGROUND_SPEED  # Ändere die Geschwindigkeit, wie das Hintergrundbild nach links läuft

            # Wenn das Hintergrundbild aus dem Bildschirm verschwindet, setze es zurück
            if self.bg_x < - self.current_background.get_width():
                self.bg_x = 0

            self.update_player_position()

            #Zeichnen
            for x in range(self.bg_x, self.ACTUAL_SCREEN_WIDTH, self.current_background.get_width()):
                if self.is_fullscreen:
                    y = self.ACTUAL_SCREEN_HEIGHT // 8
                else:
                    y = 0
                self.screen.blit(self.current_background, (x, y))  # Zeichne das Hintergrundbild an der aktuellen Position
            self.screen.blit(self.player_image, self.player_rect)

            # Spawing cars
            current_time_for_car_spawn = pygame.time.get_ticks()
            if current_time_for_car_spawn - self.last_spawn_time >= 3000:  # 3 seconds
                self.spawn_car()
                self.last_spawn_time = current_time_for_car_spawn

            # Spawning bikes
            current_time_for_bike_spawn = pygame.time.get_ticks()
            if current_time_for_bike_spawn - self.last_bike_spawn_time >= 10000:  # 10 seconds
                self.spawn_bike()
                self.last_bike_spawn_time = current_time_for_bike_spawn
      

            # Drawing enemy cars
            for enemy in self.enemies:
                self.screen.blit(enemy["image"], enemy["rect"])


            # Moving the button around based on screen size
            self.quit_button.draw(self.screen)
            if not self.is_fullscreen:
                self.quit_button.move(50, 30)
            else:
                self.quit_button.move(50, self.ACTUAL_SCREEN_HEIGHT // 8 + 30)

            # Collision detection
            for enemy in self.enemies:
                if self.player_rect.colliderect(enemy["rect"]):
                    self.play_collision()
                    self.stop_soundtrack() # stops soundtrack
                    print("GAME OVER")
                    self.state = self.main_game
                    return

            # Handle enemy off-screen and spawning
            for enemy in self.enemies:
                if enemy["rect"].right < 0:
                    self.enemies.remove(enemy)
                    self.spawn_car()

            self.night_day_transition()


            # Testing bikes
            for bike in self.bikes:
                bike.animate()
                bike.move()
                bike.draw(self.screen)

                # Remove bikes that are out of the screen
                if bike.rect.right < 0:
                    self.bikes.remove(bike)


            pygame.display.update()
            self.clock.tick(120) #Geschwindigkeit des Spiels generell (kann verändert werden, um das Spiel schwieriger zu machen


    def run(self):
        while True:
            self.state()


class Bike:
    def __init__(self, x, y, speed, bike_animation_images):
        self.x = x
        self.y = y
        self.speed = speed
        self.images = bike_animation_images
        self.current_image = 0  # Start at the first frame
        self.image = self.images[self.current_image]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.animation_time = pygame.time.get_ticks()

    def animate(self):
        # Change to the next frame every 200ms as an example
        if pygame.time.get_ticks() - self.animation_time > 200:
            self.current_image = (self.current_image + 1) % len(self.images)
            self.image = self.images[self.current_image]
            self.animation_time = pygame.time.get_ticks()

    def move(self):
        self.rect.x -= self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)


# Running the game
game = Game()
game.load_bike_sound() # load spawn bike sound
game.run()








