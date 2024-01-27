"""
This script implements a dynamic, interactive car-racing arcade game, using Pygame. 

The game features a player-controlled car, 
dynamic enemy spawns (cars, bikes, pedestrians), fuel canisters for gaining additional lives, 
and a day-to-night transition effect to enhance visual appeal. 
Key functionalities include collision detection, object movement and animation, and sound effect 
management. 

The game operates across different screens (start, main game, game over).
These can be accessed by changing the self.state attribute. 
So our run() method with the "main game loop" looks like this:
    def run(self):
    while True:
        self.state()

Any calculation of length is done with our own unit(s): self.perc_H and self.perc_W
These units represent 1% of the user's actual screen height/width.
This unit is a floating point number and when actually using this unit, 
it has to be multiplied by the wanted percentage, and converted to int (for precision).
Example: int(11*self.perc_H) will return the amount of pixels for 11% of the screen in int.

Key Classes:
    - Game: Manages the main game logic, screen updates, and game states.
    - Pedestrian, Bike, Canister: Handle specific game objects' behaviors and rendering.
    - Button: Facilitates interactive button elements in the game's UI.

The script initializes Pygame, sets up game constants (for tweaking), attributes, loads rescources, and runs the main game loop. 

We have a bunch of functionality in our main_game() method. 
We update object positions, handle user inputs, render the game screen, spawn and remove enemies, 
handle collision logic and keep track of high score and remaining lives.

While a lot of this behaviour is abstracted into methods,
there still is potential for more abstraction and refactoring.
Not only for these methods, but across the board.

Authors: Florian Goldbach, Christian Gerhold
Requires: Pygame library
"""

import pygame
import sys
import random
import time

# Initialisierung von Pygame
pygame.init()
pygame.font.init()
print(pygame.mixer.get_init())
pygame.mixer.init(64)


# Main game class
class Game:
    # Screen size and colors
    SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
    BG_COLOR = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    BLACK = (0,0,0)

    # Game over screen sizes
    GAME_OVER_SCREEN_WIDTH, GAME_OVER_SCREEN_HEIGHT = 1200, 800

    # Timer font size
    TIMER_FONT_SIZE = 80
    HIGH_SCORE_FONT_SIZE = 160

    # Added constants to control game speed in one place
    BACKGROUND_SPEED = 3
    ENEMY_SPEED = 2
    CANISTER_SPEED = 6

    PLAYER_ACCELERATION = 0.5
    PLAYER_SPEED_MAX = 5
    PLAYER_SPEED_MIN = -5

    # Night day transition
    HIGH_NOON_TIME = 20000 # More milisecs, means longer day/night
    TRANSITION_SPEED = 8000 # Less milisecs, means faster transition

    # Enemy Spawning timers
    CAR_SPAWN_TIME = 3000
    BIKE_SPAWN_TIME = 10000
    PEDESTRIAN_SPAWN_TIME = 6000
    CANISTER_SPAWN_TIME = 15000

    # Wave Time
    WAVE_TIME = TRANSITION_SPEED*10
    WAVE_DOWN_TIME = TRANSITION_SPEED*1


    """
    # Not being used right now - START

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

    # Not being used right now - END
    """

    # Resources
    transition_images = []
    enemy_images = []
    cut_out_tree_images = []

    # Default background
    current_background = None
    # Background Position X
    bg_x = 0
    # Default trees
    current_trees = None

    player_rect = None

    player_speed_x = 0  # Anfangsgeschwindigkeit in X-Richtung
    player_speed_y = 0  # Anfangsgeschwindigkeit in Y-Richtung
    player_acceleration = 0

    # start screen
    start_screen_image = None
    game_over_screen_image = None

    # fullscreen
    is_fullscreen = True

    def __init__(self):
    # Infos about the actual screen size of user
        info = pygame.display.Info()
        self.ACTUAL_SCREEN_WIDTH, self.ACTUAL_SCREEN_HEIGHT = info.current_w, info.current_h

        # Font for timer
        self.font_timer = pygame.font.Font('fonts/Pixeltype.ttf', self.TIMER_FONT_SIZE)
        self.font_high_score = pygame.font.Font('fonts/Pixeltype.ttf', self.HIGH_SCORE_FONT_SIZE)

        # High Score - the final timer string
        self.high_score = None

        # Here we create a unit, that is dependent on the actual screen dimension - 1 percent of screen
        # Why? : We ran into trouble testing the game on other screens and the elements were all over the place
        # How does it work? : You have to use int(5*self.perc_W) to get a value that correlates with 5 percent screen width
        self.perc_H = self.ACTUAL_SCREEN_HEIGHT / 100
        self.perc_W = self.ACTUAL_SCREEN_WIDTH / 100

        # Background size
        self.BACKGROUND_WIDTH = int(180*self.perc_W)
        self.BACKGROUND_HEIGHT = int(75*self.perc_H)

        # Player size
        self.PLAYER_WIDTH = int(5.9*self.perc_W)
        self.PLAYER_HEIGHT = int(5*self.perc_H)

        # Enemy car sizes
        self.ENEMY_WIDTH_CAR = int(5.9*self.perc_W)
        self.ENEMY_HEIGHT_CAR = int(5*self.perc_H)

        # Enemy bike sizes
        self.BIKE_WIDTH = int(4.2*self.perc_W)
        self.BIKE_HEIGHT = int(3.4*self.perc_H)

        # Enemy pedestrian sizes
        self.PEDESTRIAN_WIDTH = int(3.5*self.perc_W)
        self.PEDESTRIAN_HEIGHT = int(3*self.perc_H)

        # Minimum and maximum car position - invisible borders that the car can not cross
        self.MIN_Y = self.ACTUAL_SCREEN_HEIGHT // 8 + int(3*self.perc_H)
        self.MAX_Y = (self.ACTUAL_SCREEN_HEIGHT // 8) * 7 - int(2*self.perc_H)
        self.MIN_X = 0
        self.MAX_X = self.ACTUAL_SCREEN_WIDTH

        # Position of car lanes
        self.car_lanes_fullscreen = [
            self.ACTUAL_SCREEN_HEIGHT // 3 + int(2.5*self.perc_H),
            self.ACTUAL_SCREEN_HEIGHT // 3 + int(12*self.perc_H),    
            self.ACTUAL_SCREEN_HEIGHT // 3 + int(21.5*self.perc_H),
            self.ACTUAL_SCREEN_HEIGHT // 3 + int(31*self.perc_H)    
        ]

        self.bike_lanes_fullscreen = [
            self.ACTUAL_SCREEN_HEIGHT // 3 - int(6.5*self.perc_H),
            self.ACTUAL_SCREEN_HEIGHT // 3 + int(38*self.perc_H)
        ]

        self.side_walk_lanes = [
            self.ACTUAL_SCREEN_HEIGHT // 3 - int(14.5*self.perc_H),
            self.ACTUAL_SCREEN_HEIGHT // 3 + int(45*self.perc_H)
        ]


        # Enemy cars, bikes an pedestrians (list to keep track of all on screen)
        self.enemies = []
        self.bikes = []
        self.pedestrians = []

        # Pedestrian spawn time - used to spawn a pedestrian every x milisecs
        self.last_pedestrian_spawn_time = None

        # Tracking game time
        self.start_time = pygame.time.get_ticks()

        # Is there a wave at the moment?
        self.wave = True

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

        # Buttons for game over screen
        self.continue_button = Button(self.SCREEN_WIDTH // 2 + 310 , self.SCREEN_HEIGHT // 2 + 110, "CONTINUE", font_size=70)
        self.quit_button_game_over_screen = Button(self.SCREEN_WIDTH // 2 - 260, self.SCREEN_HEIGHT // 2 +110, "QUIT", font_size=60)

        # pygame.display.set_caption("ESA_3")

        # Game state
        self.state = self.start_screen  # Start with the start_screen state

        # For spawning cars 
        self.last_spawn_time = pygame.time.get_ticks()

        # Enemies collision list
        self.enemies_collided = []  # initialisieren

        # Game clock
        self.clock = pygame.time.Clock()
        
        self.load_resources()

        ##### CANISTER ######

        self.remaining_lives = 3
        self.last_canister_spawn_time = 0
        self.canisters = []

    def load_resources(self):
        # Lade Sounds
        self.load_sound()

        # Anmerkung von Florian Goldbach: Es ist nur ein Kanisterbild, benötigt also keine list comprehension
        #canister_images = [
        #    pygame.transform.scale(
        #        pygame.image.load("./items/fuel.png").convert_alpha(), (50, 50))
        #]

        # self.canister_images = canister_images

        self.canister_image = pygame.image.load("./items/fuel.png").convert_alpha()  # Loading image
        self.canister_image = pygame.transform.scale(self.canister_image, (50, 50)) # Scaling

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

        # Loading cut out tree images
        self.cut_out_tree_images = [
            # .. and scale backgrounds.
            pygame.transform.scale(
                # .. rotate ..
                pygame.transform.rotate(
                    # Load, ..
                    pygame.image.load(f"trees/transparent_background_2_day_to_night_{i}.png").convert_alpha(),
                    90
                ),
                (self.BACKGROUND_WIDTH, self.BACKGROUND_HEIGHT)
            )
            for i in range(1, 10)
        ]

        # Initializing current background and trees
        self.current_background = self.transition_images[0]
        self.current_trees = self.cut_out_tree_images[0]
        
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
            for i in range(1, 5)  # We assume to have 4 enemy car images - this is subject to change when new cars are added
        ]

        # Loading bike images
        self.bike_animation_images = [
            pygame.transform.scale(
                pygame.transform.rotate(
                    pygame.image.load(f"enemies/bike1_animation/bike1_animation_part{i}.png").convert_alpha(),
                    90
                ),
                (self.BIKE_WIDTH, self.BIKE_HEIGHT)
            )
            for i in range(1, 4)  # 3 bike animation images
        ]

        # Loading pedestrian images (1 and 2)
        self.pedestrian1_animation_images = [
            pygame.transform.scale(
                pygame.transform.rotate(
                    pygame.image.load(f"enemies/pedestrian1_animation/pedestrian1_{i}.png").convert_alpha(),
                    90
                ),
                (self.PEDESTRIAN_WIDTH, self.PEDESTRIAN_HEIGHT)
            )
            for i in range(1, 4)  # 3 pedestrian animation images
        ]


        self.pedestrian2_animation_images = [
            pygame.transform.scale(
                pygame.transform.rotate(
                    pygame.image.load(f"enemies/pedestrian2_animation/pedestrian2_{i}.png").convert_alpha(),
                    90
                ),
                (self.PEDESTRIAN_WIDTH, self.PEDESTRIAN_HEIGHT)
            )
            for i in range(1, 4)  # 3 pedestrian animation images
        ]  


        # self.enemy_image = random.choice(self.enemy_images)
        # self.enemy_rect = self.enemy_image.get_rect()

        # This is examplorary to understand how the lists enemy_images and transition_images are formed
        self.player_image = pygame.image.load("car2.png").convert_alpha()  # Loading image
        self.player_image = pygame.transform.rotate(self.player_image, 90)  # Rotating
        self.player_image = pygame.transform.scale(self.player_image, (self.PLAYER_WIDTH, self.PLAYER_HEIGHT)) # Scaling
        self.player_rect = self.player_image.get_rect()

        # Preparing the start screen image
        self.start_screen_image = pygame.image.load("start_screen3.png").convert()
        self.start_screen_image = pygame.transform.scale(self.start_screen_image, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        # Preparing the game over screen image
        self.game_over_screen_image = pygame.image.load("game_over_screen_image.png").convert()
        self.game_over_screen_image = pygame.transform.scale(self.game_over_screen_image, (self.GAME_OVER_SCREEN_WIDTH, self.GAME_OVER_SCREEN_HEIGHT))

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

        # Remove eneemy cars and bikes
        self.enemies = []
        self.bikes = []
        self.pedestrians = []
        self.canisters = []

        # Initializing self.last_bike_spawn_time for spawning bikes every x milisecs
        self.last_bike_spawn_time = pygame.time.get_ticks()

        # Initializing self.last_pedestrian_spawn_time for spawning pedestrians every x milisecs
        self.last_pedestrian_spawn_time = pygame.time.get_ticks()

        # Initializing self.last_fuel_spawn_time for spawning fuel every x milisecs
        self.last_fuel_spawn_time = pygame.time.get_ticks()


        # self.enemy_rect.centerx = self.SCREEN_WIDTH  # Startposition des gegnerischen Autos auf der rechten Seite
        # self.enemy_rect.centery = random.choice(self.car_lanes_windowed)
        # self.enemy_speed = self.ENEMY_SPEED
        # Spawn an initial car
        self.spawn_car()




######### neu ##############


    def draw_level(self):
        self.screen.fill(self.BG_COLOR)

        scaled_width = int(2.5*self.perc_W)
        scaled_height = int(4.5*self.perc_H)
        distance_left = int(1.5*self.perc_W)

        fuel_image = pygame.image.load("./items/fuel.png").convert_alpha()
        scaled_image = pygame.transform.scale(fuel_image, (scaled_width, scaled_height))

        # remaining lives
        for i in range(self.remaining_lives):
            self.screen.blit(scaled_image,  (distance_left + i * (scaled_width + int(0.5*self.perc_W)), int(6*self.perc_H)))


    def handle_canister_collision(self, canister):

            print("Picked up canister!")
            self.remaining_lives += 1  # add a canister/live
            self.canisters.remove(canister)



    def spawn_canister(self):

        new_canister = Canister(self.ACTUAL_SCREEN_WIDTH + 50, random.randint(self.MIN_Y, self.MAX_Y - int(3*self.perc_H)), random.choice([7, 8, 9]), self.canister_image)
        self.canisters.append(new_canister)



    def fade_to_black(self, duration=2000):
        fade_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        fade_surface.fill((0, 0, 0))

        for alpha in range(0, 256//4):
            fade_surface.set_alpha(alpha)
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.update()
            pygame.time.delay(duration // (256//4))  # Total duration divided by number of alpha increments

        # At this point, the screen is completely black.


    def will_collide(self, new_enemy_rect):
        buffer_space = 20  # 20 pixels buffer, you can adjust
        for enemy in self.enemies:
            # Inflate the existing enemy rect by the buffer space
            if enemy["rect"].inflate(buffer_space, 0).colliderect(new_enemy_rect):
                return True
        return False

    def update_state_of_wave(self):
        current_time = pygame.time.get_ticks()
        # We initialize wave_cycle_start_time when the player presses the start button
        elapsed_time = current_time - self.wave_cycle_start_time

        # Once the wave time and wave down time is over, we reset wave_cycle_start_time -> infinite loop
        # Also we reset wave to True
        if elapsed_time >= self.WAVE_TIME + self.WAVE_DOWN_TIME:
            self.wave = True
            print("wave is on")
            self.wave_cycle_start_time = current_time

        # When we reach the end of the WAVE_TIME the wave is over
        elif self.WAVE_TIME + 100 > elapsed_time >= self.WAVE_TIME:
            self.wave = False
            print("wave is off")



    def spawn_car(self):
        enemy_image = random.choice(self.enemy_images)
        enemy_rect = enemy_image.get_rect()

        enemy_rect.centerx = self.ACTUAL_SCREEN_WIDTH if self.is_fullscreen else self.SCREEN_WIDTH
        enemy_rect.centerx += 50 # Adding cars a bit outside of screen, so they drive in
        attempts = 10 # Using a maximum number of attempts to avoid endless loop when screen is crowded

        for _ in range(attempts):
            # Slighty randomizing Y spawn position
            enemy_rect.centery = random.choice(self.car_lanes_fullscreen) + random.randint(- int(2*self.perc_H), int(2*self.perc_H)) if self.is_fullscreen else random.choice(self.car_lanes_windowed)
            if not self.will_collide(enemy_rect):
                enemy_speed = self.ENEMY_SPEED
                self.enemies.append({"image": enemy_image, "rect": enemy_rect, "speed": enemy_speed})
                break










    # load sound for spawning bike
    def load_bike_sound(self):
        # load bike sound
        self.bike_sound = pygame.mixer.Sound("./sounds/bike.wav")
        self.bike_sound.set_volume(0.1)

    def play_bike_sound(self):
        self.bike_sound.play()
        pygame.mixer.Channel(1).play(self.bike_sound)

    def load_pedestrian_sound(self):
            # load bike sound
            self.pedestrian_sound = pygame.mixer.Sound("./sounds/walking.wav")
            self.pedestrian_sound.set_volume(0.2)

    def play_pedestrian_sound(self):
        self.pedestrian_sound.play()
        pygame.mixer.Channel(1).play(self.pedestrian_sound)

    def spawn_bike(self):
        # Position the bike off the screen to the right
        # Also slighty randomizing Y spawn position
        new_bike = Bike(self.ACTUAL_SCREEN_WIDTH +50, random.choice(self.bike_lanes_fullscreen) + random.randint(-int(0.7*self.perc_H), int(0.7*self.perc_H)), random.randint(4, 6), self.bike_animation_images)
        self.bikes.append(new_bike)
        # sound for spawning bike
        self.play_bike_sound()  # Aufruf des bike spawn sounds

    def spawn_pedestrian(self):

        # Randomly choose between the two types of pedestrians
        chosen_pedestrian_images = random.choice([self.pedestrian1_animation_images, self.pedestrian2_animation_images])
    
        # Position the pedestrian off the screen to the right
        # Also slighty randomizing Y spawn position
        new_pedestrian = Pedestrian(self.ACTUAL_SCREEN_WIDTH + 50, random.choice(self.side_walk_lanes) + random.randint(-int(1.5*self.perc_H), int(1.5*self.perc_H)), random.choice([3.2, 3.3, 3.5]), chosen_pedestrian_images)
        self.pedestrians.append(new_pedestrian)
        self.play_pedestrian_sound() # walking sound with spawning a pedestrian


    def handle_collision(self, collided_with):
        self.high_score = self.get_timer_string()
        self.play_collision()
        self.stop_soundtrack()
        print("GAME OVER")

        # Reduce lives
        self.remaining_lives -= 1

        # List of collided enemies - could be interesting for info at the end of the game - not implemented as of now
        self.enemies_collided.append(collided_with)

    def get_timer_string(self):
        elapsed_time = pygame.time.get_ticks() - self.timer_start_time
        seconds = elapsed_time // 1000
        minutes = seconds // 60
        hours = minutes // 60
        seconds %= 60
        minutes %= 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    
    def display_timer(self):
        timer_string = self.get_timer_string()
        timer_surface = self.font_timer.render(timer_string, True, self.WHITE)
        self.screen.blit(timer_surface, (int(85*self.perc_W), int(7*self.perc_H)))
    
    def display_high_score(self):
        timer_surface = self.font_high_score.render(self.high_score, True, self.BLACK)
        self.screen.blit(timer_surface, (int(20*self.perc_W), int(7*self.perc_H)))

 

    def is_game_over(self):
        if self.remaining_lives < 1:
            self.screen = pygame.display.set_mode((self.GAME_OVER_SCREEN_WIDTH, self.GAME_OVER_SCREEN_HEIGHT), pygame.NOFRAME)
            self.is_fullscreen = False
            self.state = self.game_over_screen
            return

    def change_to_start_screen(self):
        # Change display mode, set is_fullscreen to False and update game state
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.NOFRAME)
        self.is_fullscreen = False
        self.state = self.start_screen

    def night_day_transition(self):

        # Keeping track of time
        elapsed_time = pygame.time.get_ticks() - self.start_time

        # After "HIGH_NOON_TIME" milliseconds of daytime driving, we start the transition
        # We give elapsed_time a window due to the inprecision of .get_ticks()
        if self.HIGH_NOON_TIME <= elapsed_time < self.HIGH_NOON_TIME + 6000 and self.transition_start_time is None:
            self.transition_start_time = pygame.time.get_ticks()

        # We keep track of when the transition started
        if self.transition_start_time:
            time_since_transition_start = pygame.time.get_ticks() - self.transition_start_time

            # While we are not in a reverse transition (night to day), we change the background image every 5 seconds
            if not self.reverse_transition:
                transition_index = time_since_transition_start // self.TRANSITION_SPEED  # e.g. every 5 seconds: time_since_transition_start // 5000

                # We only change the background image, when it is fully on screen ((SCREEN_WIDTH - BACKGROUND_WIDTH) < bg_x <= 0) 
                # and while we still have new transition images in our list
                if transition_index < len(self.transition_images) and (self.ACTUAL_SCREEN_WIDTH - self.BACKGROUND_WIDTH) < self.bg_x <= 0:
                    self.current_background = self.transition_images[transition_index]
                    self.current_trees = self.cut_out_tree_images[transition_index]
                # Once we run out of transition images, we enter the reverse_transition
                elif transition_index >= len(self.transition_images):
                    self.reverse_transition = True
                    self.transition_start_time = pygame.time.get_ticks()

            # We keep time of when the reverse transition started and make sure the transition_index counts reversly (e.g. 7 to 0)
            if self.reverse_transition:
                time_since_reverse_transition = pygame.time.get_ticks() - self.transition_start_time
                transition_index = len(self.transition_images) - 1 - time_since_reverse_transition // self.TRANSITION_SPEED

                # We only change the background image, when it is fully on screen ((SCREEN_WIDTH - BACKGROUND_WIDTH) < bg_x <= 0)
                # and while we still have new transition images in our list
                if 0 <= transition_index < len(self.transition_images) and (self.ACTUAL_SCREEN_WIDTH - self.BACKGROUND_WIDTH) < self.bg_x <= 0:
                    self.current_background = self.transition_images[transition_index]
                    self.current_trees = self.cut_out_tree_images[transition_index]
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
        # load game over screen sound
        self.game_over_screen_sound = pygame.mixer.Sound("./sounds/game_over.wav")
        self.game_over_screen_sound.set_volume(1)

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

        # load scream for pedestrian when being hit
        self.scream = pygame.mixer.Sound("./sounds/scream.wav")
        self.scream.set_volume(0.5)

        # load scream for pedestrian when being hit
        self.scream2 = pygame.mixer.Sound("./sounds/scream2.mp3")
        self.scream2.set_volume(0.5)
        

    # start game over sound
    def play_game_over_screen_sound(self):
        pygame.mixer.Channel(6).play(self.game_over_screen_sound, loops=-1) # plays forever as long as being stuck in the game over screen

    # start_screen sound play
    def play_soundtrack(self):
        pygame.mixer.Channel(5).play(self.soundtrack, loops=-1)  # sound plays forever // extra channel

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
    def stop_start_screen_sound(self, fadeout_time=1000):
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

    def play_scream_sound(self):
        
        
        if random.random() > 0.2:
            pygame.mixer.Channel(7).play(self.scream)
            self.scream.play()
        else:
            pygame.mixer.Channel(7).play(self.scream2)
            self.scream2.play()


    # Stopping all sounds - Needed to add this as there still was overlapping
    def stop_all_sounds(self):
        pygame.mixer.stop()


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

                    # Remove collided enemies for next game
                    self.enemies_collided.clear()
                    self.remaining_lives = 3

                    self.stop_start_screen_sound()
                    self.play_vroom()
                    self.fade_to_black(duration=1200)
                    # self.play_start_button_sound() # Aufruf des start button
                    self.stop_all_sounds()
                    self.start_time = pygame.time.get_ticks() # Start time of main game, used for night day cycle
                    self.wave_cycle_start_time = pygame.time.get_ticks() # Also start time of game, but used for wave cycle
                    self.timer_start_time = pygame.time.get_ticks() # Used for timer
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

    def game_over_screen(self):
        self.stop_all_sounds()  # Stop all sounds
        self.play_game_over_screen_sound()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                
                # The game over screen loop will terminate, when the continue button is clicked - this will bring the player to the main game loop (follow code)
                if self.continue_button.is_clicked(event):

                    # Remove collided enemies for next game
                    self.enemies_collided.clear()
                    self.remaining_lives = 3

                    self.stop_start_screen_sound()
                    self.play_vroom()
                    self.fade_to_black(duration=1200)
                    # self.play_start_button_sound() # Aufruf des start button
                    self.stop_all_sounds()
                    self.start_time = pygame.time.get_ticks() # Start time of main game, used for night day cycle
                    self.wave_cycle_start_time = pygame.time.get_ticks() # Also start time of game, but used for wave cycle
                    self.timer_start_time = pygame.time.get_ticks() # Used for timer
                    self.state = self.main_game
                    return
                # The window will be closed when the quit button is pressed
                if self.quit_button_game_over_screen.is_clicked(event):
                    self.play_quit_button_sound() # Aufruf des start button sounds

                    ### delay damit der sound abgespielt wird bevor das fenster schließt
                    time.sleep(1)
                    # exit game / start screen
                    pygame.quit()
                    sys.exit()

            # Drawing
            self.screen.blit(self.game_over_screen_image, (0, 0))
            self.continue_button.draw(self.screen)
            self.quit_button_game_over_screen.draw(self.screen)
            self.display_high_score()
            pygame.display.update()

    # This is the main game state - main game loop
    def main_game(self):
        self.play_soundtrack()  # Aufruf des soundtracks

        # We need to re-/initialize the behaviour of all game objects, before starting/restarting the game
        self.initialize_behaviour()


        while True:
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

            # When the background is outside of the screen completely, reset bg_x
            if self.bg_x < - self.current_background.get_width():
                self.bg_x = 0

            self.update_player_position()

            # Zeichnen und Aktualisieren der Tankanzeige
            self.draw_level()  # Anzeigen des Level-Indikators
            
            # We are drawing the current background 2 times
            # One time at bg_x and one time at bg_x + self.current_background.get_width())
            # But we only draw it 2 times, when abs(self.bg_x) + self.ACTUAL_SCREEN_WIDTH is equal or larger than self.current_background.get_width())
            for x in range(self.bg_x, self.ACTUAL_SCREEN_WIDTH, self.current_background.get_width()):
                y = self.ACTUAL_SCREEN_HEIGHT // 8
                self.screen.blit(self.current_background, (x, y))

            # Spawne Canister
            current_time_for_canister_spawn = pygame.time.get_ticks()
            if current_time_for_canister_spawn - self.last_canister_spawn_time >= self.CANISTER_SPAWN_TIME:  # 8 Sekunden , kann zum Testen verkleinert werden!
                self.spawn_canister()
                self.last_canister_spawn_time = current_time_for_canister_spawn

            # Drawing, moving, collecting, removing canisters
            for canister in self.canisters:

                canister.draw(self.screen)
                canister.move()

                if self.player_rect.colliderect(canister.rect):
                    self.handle_canister_collision(canister)

                # Remove canisters that are out of the screen
                if canister.rect.right < 0:
                    self.canisters.remove(canister)


            # Drawing player car
            self.screen.blit(self.player_image, self.player_rect)

            # Moving, animating and removing pedestrians
            for pedestrian in self.pedestrians:
                pedestrian.animate()
                pedestrian.move()
                pedestrian.draw(self.screen)    
            
                # Removing pedestrians
                if pedestrian.rect.right < 0:
                        self.pedestrians.remove(pedestrian)



            # We are drawing the trees in the same fashion as the background - 2 times
            # But after the player car and the pedestrians to create a layered effect
            for x in range(self.bg_x, self.ACTUAL_SCREEN_WIDTH, self.current_background.get_width()):
                if self.is_fullscreen:
                    y = self.ACTUAL_SCREEN_HEIGHT // 8
                else:
                    y = 0
                self.screen.blit(self.current_trees, (x, y))

            # Spawing cars
            current_time_for_car_spawn = pygame.time.get_ticks()
            if current_time_for_car_spawn - self.last_spawn_time >= self.CAR_SPAWN_TIME:
                self.spawn_car()
                self.last_spawn_time = current_time_for_car_spawn

            # Drawing enemy cars
            for enemy in self.enemies:
                self.screen.blit(enemy["image"], enemy["rect"])

            # Spawning bikes
            current_time_for_bike_spawn = pygame.time.get_ticks()
            if current_time_for_bike_spawn - self.last_bike_spawn_time >= self.BIKE_SPAWN_TIME:
                self.spawn_bike()
                self.last_bike_spawn_time = current_time_for_bike_spawn
      
            # Spawning pedestrians
            current_time_for_pedestrian_spawn = pygame.time.get_ticks()
            if current_time_for_pedestrian_spawn - self.last_pedestrian_spawn_time >= self.PEDESTRIAN_SPAWN_TIME:
                self.spawn_pedestrian()
                self.last_pedestrian_spawn_time = current_time_for_pedestrian_spawn

            # Moving the button around based on screen size
            self.quit_button.draw(self.screen)
            self.quit_button.move(int(2.5*self.perc_W), self.ACTUAL_SCREEN_HEIGHT // 8 + int(3*self.perc_H))

            # Collision detection for enemy cars
            for enemy in self.enemies:
                if self.player_rect.colliderect(enemy["rect"]):
                    self.handle_collision(enemy)

                    self.is_game_over()

                    # We have to return, as we don't want to loose all lives at once
                    return


            # Updating the state of the wave - either the wave is on or not
            self.update_state_of_wave()

            # Handle enemy off-screen and spawning
            # When an enemy car leaves the screen there is a 90% chance it will respawn during wave
            for enemy in self.enemies:
                if enemy["rect"].right < 0:
                    self.enemies.remove(enemy)

                    # The respawn rate when an enemy car leaves the screen is much less, when there is no wave right now
                    # This gives the player time to breath
                    if self.wave:
                        if random.random() < 0.95:
                            self.spawn_car()
                    else:
                        if random.random() < 0.3:
                            self.spawn_car()

            # Collision detection and movement of enemy bikes
            for bike in self.bikes:

                if self.player_rect.colliderect(bike.rect):

                    self.handle_collision(bike)
                    
                    self.is_game_over()

                    # We have to return the main game loop after one collision detection, 
                    # as we dont want to loose all lives
                    return

                bike.animate()
                bike.move()
                bike.draw(self.screen)

                # Remove bikes that are out of the screen
                if bike.rect.right < 0:
                    self.bikes.remove(bike)

            # Collision detection for pedestrians
            for pedestrian in self.pedestrians:
                if self.player_rect.colliderect(pedestrian.rect):

                    self.handle_collision(pedestrian)
                    self.play_pedestrian_sound() ################################# change to scream
                    ###############################################################
                    self.play_scream_sound() ################################
                    self.is_game_over()

                    # We have to return the main game loop after one collision detection, 
                    # as we dont want to loose all lives
                    return
            


            # Night and day transition
            self.night_day_transition()

            # Displaying timer
            self.display_timer()

            pygame.display.update()
            self.clock.tick(120) #Geschwindigkeit des Spiels generell (kann verändert werden, um das Spiel schwieriger zu machen


    def run(self):
        while True:
            self.state()


# Pedestrian class
class Pedestrian:
    """
    Class for a pedestrian character object.

    This class manages the pedestrian's position, movement, and animation.
    We update the pedestrian's animation image (which is the animation).
    We can move the pedestrian across the screen, and draw the pedestrian on a specified surface.

    Args:
        x (int): initial x-coordinate of the pedestrian's position.
        y (int): initial y-coordinate of the pedestrian's position.
        speed (int): The speed at which the pedestrian will move.
        pedestrian_animation_images (list): A list of pygame.Surface objects representing the animation frames (will be 3 images).

    Attributes:
        x (int): x-coordinate of the pedestrian's position.
        y (int): y-coordinate of the pedestrian's position.
        speed (int): The speed at which the pedestrian moves.
        images (list): A list of images for the pedestrian's animation.
        current_image (int): The index of the current image in the animation sequence.
        image (pygame.Surface): The current image of the pedestrian.
        rect (pygame.Rect): The rectangle area of the pedestrian (position and size).
        animation_time (int): Timestamp of the last animation frame update.

    Methods:
        animate(): Updates the pedestrian's animation frame.
        move(): Moves the pedestrian based on the current speed.
        draw(screen): Draws the pedestrian on the given screen (pygame.Surface).
    
    Author:
        Florian Goldbach
    """
    def __init__(self, x, y, speed, pedestrian_animation_images):
        self.x = x
        self.y = y
        self.speed = speed
        self.images = pedestrian_animation_images
        self.current_image = 0
        self.image = self.images[self.current_image]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.animation_time = pygame.time.get_ticks()

    def animate(self):
        # Animation speed is 200ms
        if pygame.time.get_ticks() - self.animation_time > 200:  
            self.current_image = (self.current_image + 1) % len(self.images)
            self.image = self.images[self.current_image]
            self.animation_time = pygame.time.get_ticks()

    def move(self):
        self.x -= self.speed
        self.rect.x = self.x

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)


# The Bike class is analogous to the Pedestrian class.
# The Bike and the Pedestrian class do the same thing.
# I did not use inheritance, but there is opportunity here.
# Author: Florian Goldbach
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
            # self.rect.size = self.image.get_size()

    def move(self):
        self.x -= self.speed
        self.rect.x = self.x  # Update the rect's position

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)



# Canister Class
class Canister:
    """
    Class for a canister object.

    This class manages the canister's position and movement.
    We can move the canister across the screen, and draw the canister on a specified surface.

    Args:
        x (int): initial x-coordinate of the canister's position.
        y (int): initial y-coordinate of the canister's position.
        speed (int): The speed at which the canister will move.
        image (pygame.Surface): A pygame.Surface object - image of the canister.

    Attributes:
        x (int): x-coordinate of the canister's position.
        y (int): y-coordinate of the canister's position.
        speed (int): The speed at which the canister will move.
        image (pygame.Surface): A pygame.Surface object - image of the canister.
        rect (pygame.Rect): The rectangle area of the canister.

    Methods:
        move(): Moves the canister based on the current speed.
        draw(screen): Draws the canister on the given screen (pygame.Surface).
    
    Author:
        Florian Goldbach
    """
    def __init__(self, x, y, speed, image):
        self.x = x
        self.y = y
        self.speed = speed
        self.image = image
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def move(self):
        self.x -= self.speed
        self.rect.x = self.x  # Update the rect's position

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)


class Button:
    """
    Class for a customizable button object.

    This is a button that can display text and respond to mouse events. 
    The button changes color when hovered over. 
    We can move it to different positions and detect mouse clicks.

    Args:
        x (int): x-coordinate of the button's center.
        y (int): y-coordinate of the button's center.
        text (str): The text to be displayed on the button.
        font_size (int, optional): The font size of the button text (default is 80).
        font_color (tuple, optional): The default color of the button text (RGB-tuple) (default is black (0, 0, 0)).
        hover_color (tuple, optional): The color of the button text when hovered over (RGB-tuple) (default is white (255, 255, 255)).

    Attributes:
        font (pygame.font.Font): Font used for the button text.
        text (str): Text displayed on the button.
        colors (dict): Colors the button, including 'default' and 'hover' colors.
        current_color (str): The current color state of the button, either 'default' or 'hover'.
        text_img (pygame.Surface): The rendered image of the text.
        rect (pygame.Rect): The rectangle of the button (position and size).

    Methods:
        draw(surface): Draws the button on the specified surface.
        is_hovered(pos): Checks if the given position (mouse position) is on top of the button.
        move(new_x, new_y): Moves the button to a new position.
        is_clicked(event): Determines if the button is clicked based on a given Pygame event.
    
    Author: Florian Goldbach
    """
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

# Running the game
game = Game()
game.load_bike_sound() # load spawn bike sound
game.load_pedestrian_sound() # loads walking sound for pedestrians

game.run()








