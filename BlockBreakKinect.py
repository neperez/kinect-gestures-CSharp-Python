# CSC 322 Spring 2012
# Final Project: Game programming with Python and Kinect

from pykinect import nui
from pykinect.nui import SkeletonTrackingState,JointId
import sys
import pygame
from pygame.color import THECOLORS
from pygame.locals import *
import winsound
import time

# this allows for translation between skeletal coordinates and the display screen
skeleton_to_depth_image = nui.SkeletonEngine.skeleton_to_depth_image

# Sets up the event id for a Kinect event
KINECTEVENT = pygame.USEREVENT

#Get skeleton events from the Kinect device and post them into the PyGame event queue
def post_frame(frame):
    try:
        pygame.event.post(pygame.event.Event(KINECTEVENT, skeletons = frame.SkeletonData))
    except:
        # event queue full
        pass

# Object dimension constants
SCREEN_SIZE   = 640,480
BRICK_WIDTH   = 60
BRICK_HEIGHT  = 15
PADDLE_WIDTH  = 60
PADDLE_HEIGHT = 12
BALL_DIAMETER = 16
BALL_RADIUS   = BALL_DIAMETER / 2
FONT_SIZE = 30

# movement restriction constants
MAX_PADDLE_X = SCREEN_SIZE[0] - PADDLE_WIDTH
MAX_BALL_X   = SCREEN_SIZE[0] - BALL_DIAMETER
MAX_BALL_Y   = SCREEN_SIZE[1] - BALL_DIAMETER
PADDLE_Y = SCREEN_SIZE[1] - PADDLE_HEIGHT - 10

# Color constants
BLACK = (0,0,0)
BALL_COLOR = (255,127,0)
PADDLE_COLOR  = (255,0,0)
BRICK_COLOR = (128,128,128)
FONT_COLOR = (255,127,0)

# State constants
STATE_READY = 0
STATE_PLAYING = 1
STATE_WON = 2
STATE_GAME_OVER = 3

# Initial values
INIT_LIVES = 3
INIT_SCORE = 0
FWD_VEL = 5
RWD_VEL = -5

# main game class
class Blocks:
    
    #constructor for game class
    def __init__(self):

        #start pygame module      
        pygame.init()

        #initialize display and timer
        self.screen = pygame.display.set_mode(SCREEN_SIZE,0,16)    
        pygame.display.set_caption('Python Kinect Game')
        self.screen.fill(THECOLORS["black"])
        self.clock = pygame.time.Clock()

        # set custom font for display   
        if pygame.font:
            self.font = pygame.font.Font("Nights.ttf", FONT_SIZE)
        else: 
            self.font = None

        #initialize a game      
        self.init_game()

    # set the initial values and game state
    def init_game(self):
        self.lives = INIT_LIVES
        self.score = INIT_SCORE
        self.state = STATE_READY
        self.paddle = pygame.Rect(300,PADDLE_Y,PADDLE_WIDTH,PADDLE_HEIGHT)
        self.ball = pygame.Rect(300,PADDLE_Y - BALL_DIAMETER,BALL_DIAMETER,BALL_DIAMETER)
        self.ball_vel = [FWD_VEL,RWD_VEL]
        self.create_bricks()

        # holds skeletal info for current frame
        self.skel_info = None

    #creates a rectangular group of bricks    
    def create_bricks(self):
        y_offset = 35
        self.bricks = []
        for i in range(7):
            x_offset = 35
            for j in range(8):
                self.bricks.append(pygame.Rect(x_offset,y_offset,BRICK_WIDTH,BRICK_HEIGHT))
                x_offset += BRICK_WIDTH + 10
            y_offset += BRICK_HEIGHT + 5

    #draws current brick group
    def draw_bricks(self):
        for brick in self.bricks:
            pygame.draw.rect(self.screen, BRICK_COLOR, brick)

    #moves the ball within the confines of the playing area
    def move_ball(self):
        
        # set velocity
        self.ball.left += self.ball_vel[0]
        self.ball.top  += self.ball_vel[1]
        
        # handle left side of screen
        if self.ball.left <= 0:
            self.ball.left = 0
            self.ball_vel[0] = -self.ball_vel[0]
        elif self.ball.left >= MAX_BALL_X:
            self.ball.left = MAX_BALL_X
            self.ball_vel[0] = -self.ball_vel[0]
        
        #handle top of screen
        if self.ball.top < 0:
            self.ball.top = 0
            self.ball_vel[1] = -self.ball_vel[1]
        elif self.ball.top >= MAX_BALL_Y:            
            self.ball.top = MAX_BALL_Y
            self.ball_vel[1] = -self.ball_vel[1]

    def handle_collisions(self):
        
        # handle collisions with bricks
        for brick in self.bricks:
            if self.ball.colliderect(brick):
                self.score += 3
                self.ball_vel[1] = -self.ball_vel[1]
                self.bricks.remove(brick)
                break
            
        # check for win condition
        if len(self.bricks) == 0:
            self.state = STATE_WON
            
        # handle paddle collision    
        if self.ball.colliderect(self.paddle):
            self.ball.top = PADDLE_Y - BALL_DIAMETER
            self.ball_vel[1] = -self.ball_vel[1]
            print "\a"
        # handle if ball missed by player
        elif self.ball.top > self.paddle.top:
            self.lives -= 1
            if self.lives > 0:
                self.state = STATE_READY
            else:
                self.state = STATE_GAME_OVER
                winsound.Beep(300,500)
                time.sleep(.01)
                winsound.Beep(300,500)
                time.sleep(.01)
                winsound.Beep(300,500)
                
    # Writes game statistics to upper part of screen
    def show_stats(self):
        if self.font:
            font_surface = self.font.render("SCORE: " + str(self.score) + " LIVES: " + str(self.lives), False, FONT_COLOR)

            #updates just font section of drawing surface, saving time
            self.screen.blit(font_surface, (205,5))

    # For displaying messages on center screen
    def show_message(self,message):
        if self.font:
            size = self.font.size(message)
            font_surface = self.font.render(message,False, FONT_COLOR)
            
            # set in center screen
            x = (SCREEN_SIZE[0] - size[0]) / 2
            y = (SCREEN_SIZE[1] - size[1]) / 2
            
            # update font surface only
            self.screen.blit(font_surface, (x,y))

    def move_paddle(self):
        # first run through has no information, pass
        if not self.skel_info:
            pass

        else:
            
            #fetch current hand position
            skeletons = self.skel_info
            right_hand = skeletons.SkeletonPositions[JointId.HandRight]
            right_pos = skeleton_to_depth_image(right_hand, SCREEN_SIZE[0], SCREEN_SIZE[1])

            # set paddle position
            self.paddle.left = right_pos[0]

            #test for game screen bounds
            if self.paddle.left < 0:
                self.paddle.left = 0
            if self.paddle.left > MAX_PADDLE_X:
                self.paddle.left = MAX_PADDLE_X

    def run(self):

        # Enter kinect runtime mode      
        with nui.Runtime() as kinect:
            
            # start Kinect
            kinect.skeleton_engine.enabled = True
            kinect.skeleton_frame_ready += post_frame
                    
            # Main game loop    
            while True:
            
                # wait for a single event from event queue
                e = pygame.event.wait()

                # set timer speed
                self.clock.tick(50)
            
                # set preliminary surface color
                self.screen.fill(BLACK)
            
                #handle events in pygame queue
                if e.type == pygame.QUIT:
                   sys.exit
               
                # collect the skeletal data if someone is being tracked
                elif e.type == KINECTEVENT:
                    #cycle through skeleton data structure and grab info for paddle movement
                    for skeleton in e.skeletons:
                        if skeleton.eTrackingState == SkeletonTrackingState.TRACKED:
                            self.skel_info = skeleton
                            
                            # starts game when human form detected.
                            if self.state == STATE_READY:
                                self.ball_vel = [5,-5]
                                winsound.Beep(800,250)
                                time.sleep(.01)
                                winsound.Beep(1000,250)
                                self.state = STATE_PLAYING

                            
                # handle game state transitions
                if self.state == STATE_PLAYING:
                    self.move_paddle()
                    self.move_ball()
                    self.handle_collisions()
                elif self.state == STATE_READY:
                    # set ball onto paddle
                    self.ball.left = self.paddle.left + self.paddle.width / 2
                    self.ball.top  = self.paddle.top - self.ball.height
                    self.show_message("WALK INTO PLAYING AREA")
                elif self.state == STATE_GAME_OVER:
                    self.show_message("GAME OVER.")
                    
                elif self.state == STATE_WON:
                    self.show_message("YOU WON!")

                # draw game objects to surface
                self.draw_bricks()
                pygame.draw.rect(self.screen, PADDLE_COLOR, self.paddle)
                pygame.draw.circle(self.screen, BALL_COLOR, (self.ball.left + BALL_RADIUS, self.ball.top + BALL_RADIUS), BALL_RADIUS)
                self.show_stats()
            
                # update display surface to screen
                pygame.display.flip() 

if __name__=="__main__":
    Blocks().run()
                
