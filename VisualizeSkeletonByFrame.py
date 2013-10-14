import csv
import gtk
import pygame
import sys
from svmutil import *

class Viz_Skeleton:
        
    # Constructor for Viz_Skeleton class
    def __init__(self):

        # State constants
        self.STATE_WAITING = 0
        self.STATE_PLAY_FWD = 1
        self.STATE_PLAY_BKWD = 2
        self.STATE_ONE_FRAME_RIGHT = 3
        self.STATE_ONE_FRAME_LEFT = 4
        self.STATE_PREV_SAMPLE = 5
        self.STATE_NEXT_SAMPLE = 6

        # Color constants
        self.BLACK = (0,0,0)#Screen background
        self.WHITE = (255,255,255)# Font color
        self.RED = (255,0,0)# Skeletal joint and bone marker


        # Initial values
        self.SCREEN_SIZE = 640,480
        self.LINE_WIDTH = 3
        self.SCALE = 200
        self.X_OFF = 310
        self.Y_OFF = 265
        self.ifile = ''
        self.reader = ''
        self.cur_frame_number = 1
        self.tot_num_frames = 0
        self.row_number = 1
        self.tot_row_number = 0
        self.line_offset = []
        self.offset = 0
        self.row = ''
        self.file_name = ''

        self.get_file_name()

        pygame.init()

        self.screen = pygame.display.set_mode(self.SCREEN_SIZE)

        pygame.display.set_caption("Skeletal Joint Visualization")

        self.clock = pygame.time.Clock()

        if pygame.font:
            self.font = pygame.font.Font(None,30)
        else:
            self.font = None

        self.state = self.STATE_WAITING
        

    # Gets filename from user using gtk  
    def get_file_name(self):
        
        dialog = gtk.FileChooserDialog("Open..",
                               None,
                               gtk.FILE_CHOOSER_ACTION_OPEN,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        dialog.set_default_response(gtk.RESPONSE_OK)

        response = dialog.run()

        if response == gtk.RESPONSE_OK:
            self.tot_row_number = len(open(dialog.get_filename()).readlines())
            self.ifile  = open(dialog.get_filename())
            self.file_name =  dialog.get_filename()
            self.get_tot_frames(self.ifile.name)
            self.reader = csv.reader(self.ifile)
            self.row = self.reader.next()
            dialog.destroy()
            
        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
            dialog.destroy()
        
    # Gets total number of frames from last element in structured file name
    def get_tot_frames(self,f_name):

        tf_index_temp = f_name.split("_")[::-1]
        tf_index = tf_index_temp[0].split(".")
        self.tot_num_frames = int(tf_index[0])

    # sets desired row in currently open file
    # direction value is negative -> decrement row
    # direction value positive -> increment row
    def change_row(self,direction):

        self.ifile.close()
        self.ifile = open(self.file_name)
        self.reader = csv.reader(self.ifile)
                   
        if direction < 0:
            self.row_number -= 1
            for i in range(self.row_number,1,-1):
                self.row  = self.reader.next()
        else:
            self.row_number += 1
            for i in range(1,self.row_number):
                self.row = self.reader.next()
        
            
    # Change state based on key pressed
    def check_input(self):
        
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            if self.state == self.STATE_WAITING:
                self.state = self.STATE_ONE_FRAME_LEFT
            elif self.state == self.STATE_PLAY_FWD:
                self.state = self.STATE_WAITING
            elif self.state == self.STATE_PLAY_BKWD:
                self.state = self.STATE_WAITING

        if keys[pygame.K_RIGHT]:
            if self.state == self.STATE_WAITING:
                self.state = self.STATE_ONE_FRAME_RIGHT
            elif self.state == self.STATE_PLAY_FWD:
                self.state = self.STATE_WAITING
            elif self.state == self.STATE_PLAY_BKWD:
                self.state = self.STATE_WAITING

        if keys[pygame.K_w]:
            if self.state == self.STATE_WAITING:
                self.state = self.STATE_PLAY_FWD
            elif self.state == self.STATE_PLAY_BKWD:
                self.state = self.STATE_PLAY_FWD

        if keys[pygame.K_s]:
            if self.state == self.STATE_WAITING:
                self.state = self.STATE_PLAY_BKWD
            elif self.state == self.STATE_PLAY_FWD:
                self.state = self.STATE_PLAY_BKWD

        if keys[pygame.K_a]:
            if self.state == self.STATE_WAITING:
                self.state = self.STATE_PREV_SAMPLE
            elif self.state == self.STATE_PLAY_FWD:
                self.state = self.STATE_PREV_SAMPLE
            elif self.state == self.STATE_PLAY_BKWD:
                self.state = self.STATE_PREV_SAMPLE

        if keys[pygame.K_d]:
            if self.state == self.STATE_WAITING:
                self.state = self.STATE_NEXT_SAMPLE
            if self.state == self.STATE_PLAY_FWD:
                self.state = self.STATE_NEXT_SAMPLE
            if self.state == self.STATE_PLAY_BKWD:
                self.state = self.STATE_NEXT_SAMPLE
            
    # Formats sample and frame information and updates relevant section of display
    def show_frame_info(self):
        
        if self.font:
            font_surface = self.font.render("Sample Number: "+ str(self.row_number) + "/" + str(self.tot_row_number) +
                                            " Frame Number: " + str(self.cur_frame_number) + "/" + str(self.tot_num_frames), False, self.WHITE)
            self.screen.blit(font_surface, (175,5))

    #displays visual skeleton based on frame number
    def disp_skeleton_frame(self,frame_num,row):
        
        start = (frame_num - 1) * 60
        end = start + 59
        step = 3
        positions = []

        # get skeletal joint coordinates
        for i in range(start,end,step):
            x = int(self.SCALE * float(self.row[i])) + self.X_OFF
            y = -1*int(self.SCALE * float(self.row[i+1])) + self.Y_OFF
            positions.append((x,y))
        
        # draw skeletal joint markers
        for j in range(0,len(positions),1):
            pygame.draw.circle(self.screen,self.RED,positions[j],5,0)

        # draw bones
        pygame.draw.line(self.screen,self.RED,positions[0],positions[8],self.LINE_WIDTH)
        pygame.draw.line(self.screen,self.RED,positions[8],positions[7],self.LINE_WIDTH)
        pygame.draw.line(self.screen,self.RED,positions[8],positions[9],self.LINE_WIDTH)
        pygame.draw.line(self.screen,self.RED,positions[7],positions[5],self.LINE_WIDTH)
        pygame.draw.line(self.screen,self.RED,positions[9],positions[6],self.LINE_WIDTH)
        pygame.draw.line(self.screen,self.RED,positions[5],positions[3],self.LINE_WIDTH)
        pygame.draw.line(self.screen,self.RED,positions[6],positions[4],self.LINE_WIDTH)
        pygame.draw.line(self.screen,self.RED,positions[3],positions[1],self.LINE_WIDTH)
        pygame.draw.line(self.screen,self.RED,positions[4],positions[2],self.LINE_WIDTH)
        pygame.draw.line(self.screen,self.RED,positions[8],positions[10],self.LINE_WIDTH)
        pygame.draw.line(self.screen,self.RED,positions[10],positions[12],self.LINE_WIDTH)
        pygame.draw.line(self.screen,self.RED,positions[12],positions[11],self.LINE_WIDTH)
        pygame.draw.line(self.screen,self.RED,positions[12],positions[13],self.LINE_WIDTH)
        pygame.draw.line(self.screen,self.RED,positions[11],positions[14],self.LINE_WIDTH)
        pygame.draw.line(self.screen,self.RED,positions[13],positions[15],self.LINE_WIDTH)
        pygame.draw.line(self.screen,self.RED,positions[14],positions[16],self.LINE_WIDTH)
        pygame.draw.line(self.screen,self.RED,positions[15],positions[17],self.LINE_WIDTH)
        pygame.draw.line(self.screen,self.RED,positions[16],positions[18],self.LINE_WIDTH)
        pygame.draw.line(self.screen,self.RED,positions[17],positions[19],self.LINE_WIDTH)
          
    # Main loop           
    def run(self):
        
        while 1:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.ifile.close()
                    pygame.quit()
                    sys.exit()
               
            self.screen.fill(self.BLACK)
            self.check_input()

            if self.state == self.STATE_WAITING:
                self.disp_skeleton_frame(self.cur_frame_number,self.row)
                self.clock.tick(80)
           
            if self.state == self.STATE_ONE_FRAME_LEFT:
                if self.cur_frame_number >= 2:
                    self.cur_frame_number -= 1
                    self.disp_skeleton_frame(self.cur_frame_number,self.row)
                    self.clock.tick(7)
                self.state = self.STATE_WAITING

            if self.state == self.STATE_ONE_FRAME_RIGHT:
                if self.cur_frame_number < self.tot_num_frames:
                    self.cur_frame_number += 1
                    self.disp_skeleton_frame(self.cur_frame_number,self.row)
                    self.clock.tick(7)
                self.state = self.STATE_WAITING

            if self.state == self.STATE_PLAY_FWD:
                if self.cur_frame_number < self.tot_num_frames:
                    self.cur_frame_number += 1
                    self.disp_skeleton_frame(self.cur_frame_number,self.row)
                    self.clock.tick(30)
                else:
                    self.state = self.STATE_WAITING

            if self.state == self.STATE_PLAY_BKWD:
                if self.cur_frame_number >= 2:
                    self.cur_frame_number -= 1
                    self.disp_skeleton_frame(self.cur_frame_number,self.row)
                    self.clock.tick(30)
                else:
                    self.state = self.STATE_WAITING
                    
            if self.state == self.STATE_PREV_SAMPLE:
                if self.row_number > 0:
                    self.change_row(-1)
                    self.cur_frame_number = 1
                    self.disp_skeleton_frame(self.cur_frame_number,self.row)
                    self.clock.tick(7)
                else:
                    self.cur_frame_number = 1
                    self.clock.tick(80)
                self.state = self.STATE_WAITING

            if self.state == self.STATE_NEXT_SAMPLE:
                if self.row_number < self.tot_row_number:
                    self.change_row(1)
                    self.cur_frame_number = 1
                    self.disp_skeleton_frame(self.cur_frame_number,self.row)
                    self.clock.tick(7)
                else:
                    self.cur_frame_number = 1
                    self.clock.tick(80)
                self.state = self.STATE_WAITING
                                    
            self.show_frame_info()
            pygame.display.flip()
    
if __name__ == "__main__":
    
    print('Controls: ')
    print('     left Arrow - Pause or go back one frame')
    print('     right Arrow - Pause or advance one frame')
    print('     w - Display frames in sequential order')
    print('     s - Play frames in reverse order')
    print('     a - Go to previous sample')
    print('     d - Go to next sample')

    Viz_Skeleton().run()
