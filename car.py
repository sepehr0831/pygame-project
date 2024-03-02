from shutil import move
from ssl import DER_cert_to_PEM_cert
from tkinter import HORIZONTAL, Pack
from tkinter.messagebox import NO
from numpy import rint
import pygame
import time
import math
from utils import scale_image , blit_rotate_center , blit_text_center
pygame.font.init()





GRASS = scale_image(pygame.image.load("grass.jpg"),2.5)
TRACK = scale_image(pygame.image.load("track.png"),0.9)

TRACK_BORDER =scale_image( pygame.image.load("track-border.png"),0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

FINISH = pygame.image.load("finish.png")
#for clloide with finish line
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION =(130, 250)

RED_CAR = scale_image(pygame.image.load("red-car.png"),0.55)
GREEN_CAR = scale_image(pygame.image.load("green-car.png"),0.55)


WIDTH , HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

MAIN_FONT = pygame.font.SysFont("comicsans",30)

pygame.display.set_caption("Racing Game!")

FPS = 60
PATH=[(174, 104), (113, 71), (59, 126), (64, 295), (64, 454), (163, 578), (292, 715), 
(373, 724), (405, 652), (406, 547), (446, 497), (517, 484), (580, 518), (598, 577), (611, 704), (664, 730), (726, 710), (735, 626), (733, 522), (736, 435), (704, 
366), (591, 366), (432, 363), (395, 309), (440, 256), (569, 259), (721, 253), (736, 177), (719, 90), (597, 73), (471, 69), (314, 79), (287, 131), (282, 268), (270, 393), (197, 403), (174, 326), (174, 253), (174, 263), (174, 121), (111, 63), (58, 135), (64, 454), (308, 727), (406, 639), (431, 505), (501, 466), (596, 553), (617, 714), (732, 692), (724, 378), (544, 362), (403, 306), (461, 258), (732, 241), (733, 101), (554, 77), (286, 89), (273, 378), (164, 388)]


class GameInfo:
    LEVELS = 10

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0

    def next_level(self):
        self.level += 1
        self.started = False

    def reset(self):
        self.level = 1 
        self.started = False
        self.level_start_time = 0

    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def get_level_time(self):
        if not self.started :
            return 0
        return round( time.time() - self.level_start_time)





class AbstractCar :
    IMG = RED_CAR
    def __init__(self,max_vel,rotation_vel):
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.image = self.IMG
        self.x , self.y = self.START_POS
        self.acceleration =  0.1  


    def rotate (self,left=False,right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self,win):
        blit_rotate_center(win,self.IMG ,(self.x , self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration , self.max_vel)
        self.move()


    def move_backward(self):
        self.vel = max(self.vel - self.acceleration , -self.max_vel/2)
        self.move()


    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians)* self.vel
        horizantal = math.sin(radians)* self.vel

        self.y -= vertical
        self.x -= horizantal
    
    def collide(self, mask , x=0 , y=0):
        car_mask = pygame.mask.from_surface(self.IMG)
        offset = (int( self.x - x),int(self.y - y))
        poi = mask.overlap(car_mask,offset)
        return poi

    def reset(self):
        self.x , self.y = self.START_POS
        self.angle = 0
        self.vel = 0





class PlayerCar(AbstractCar):
    IMG = RED_CAR
    START_POS = (180,200)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration /2,0 )
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()

class  ComputerCar(AbstractCar):
    IMG = GREEN_CAR
    START_POS = (150,200)

    def __init__(self,max_vel,rotation_vel,PATH=[]):
        super().__init__(max_vel,rotation_vel)
        self.path = PATH
        self.current_point = 0
        self.vel = max_vel



    def  draw_points(self,win):
        for point in self.path:
            pygame.draw.circle(win,(255,0,0), point,5)



    def draw(self,win):
        super().draw(win)
        #self.draw_points(win)



    def Calculate_angle(self):
        target_x , target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0 :
            desired_radian_angle = math.pi/2
        else: 
            desired_radian_angle= math.atan(x_diff/y_diff)

        if target_y > self.y :
            desired_radian_angle += math.pi
        differnce_in_angle = self.angle - math.degrees(desired_radian_angle)
        if differnce_in_angle >= 180 :
            differnce_in_angle -= 360 
        if differnce_in_angle > 0 :
            self.angle -= min(self.rotation_vel , abs(differnce_in_angle))
        else:
            self.angle += min(self.rotation_vel , abs(differnce_in_angle))


    def update_path_point(self):
        target = self.path[self.current_point]
        rect= pygame.Rect(self.x , self.y , self.IMG.get_width(), self.IMG.get_height())
        if rect.collidepoint(*target):
            self.current_point+=1


    def move(self):
        if self.current_point >= len(self.path):
            return

            
        self.Calculate_angle()
        self.update_path_point()
        super().move()
    
    def next_level(self,level):
        self.reset()
        self.vel = self.max_vel + (level-1) * 0.2
        self.current_point = 0
        

         


def draw(win,images,Player_Car , Computer_Car, game_info):
    for img , pos in images:
        win.blit(img,pos)

    level_text = MAIN_FONT.render(f"Level{game_info.level}",1,(255,255,255))
    win.blit(level_text, (10,HEIGHT-level_text.get_height() - 70))


    time_text = MAIN_FONT.render(f"time:{game_info.get_level_time()}",1,(255,255,255))
    win.blit(time_text, (10,HEIGHT-level_text.get_height() - 40))


    vel_text = MAIN_FONT.render(f"vel:{round(Player_Car.vel,1)}px/s",1,(255,255,255))
    win.blit(vel_text, (10,HEIGHT-level_text.get_height() - 10))


    Player_Car.draw(win)
    Computer_Car.draw(win)
    pygame.display.update()






def move_player(Player_Car):


    
    keys = pygame.key.get_pressed()
    moved = False


    if keys[pygame.K_a]:
        Player_Car.rotate(left=True)

    if keys[pygame.K_d]:
        Player_Car.rotate(right=True)

    if keys[pygame.K_w]:
        moved = True
        Player_Car.move_forward()

    if keys[pygame.K_s]:
        moved = True
        Player_Car.move_backward()

    if not moved:
        Player_Car.reduce_speed()


def handle_collision(Player_Car, Computer_Car,game_info):


    if Player_Car.collide(TRACK_BORDER_MASK)  != None :
        Player_Car.bounce()


    Computer_finish_poi_collide =  Computer_Car.collide(FINISH_MASK,*FINISH_POSITION)
    if Computer_finish_poi_collide != None:
        blit_text_center(WIN,MAIN_FONT,"You Lost!")
        pygame.display.update()
        pygame.time.wait(5000)
        game_info.reset()
        Computer_Car.reset()
        Player_Car.reset()



    player_finish_poi_collide =  Player_Car.collide(FINISH_MASK,*FINISH_POSITION)
    if player_finish_poi_collide != None :
        if player_finish_poi_collide[1] == 0:
           Player_Car.bounce()

        else:
            game_info.next_level()
            Player_Car.reset()
            Computer_Car.next_level(game_info.level)





run = True
images= [(GRASS,(0,0)),(TRACK,(0,0)) , (FINISH,FINISH_POSITION),(TRACK_BORDER,(0,0))]
clock = pygame.time.Clock()
Player_Car = PlayerCar(4,4)
Computer_Car = ComputerCar(3,4,PATH)
game_info = GameInfo()





while run:
    clock.tick(FPS)


    draw(WIN,images , Player_Car , Computer_Car, game_info)


    while not game_info.started:
        blit_text_center(WIN,MAIN_FONT,f"Prees any key to start level {game_info.level}!")
        pygame.display.update()
        for event in pygame.event.get():
            if event.type is pygame.QUIT:
                pygame.quit()
                break
        
            if event.type == pygame.KEYDOWN:
                game_info.start_level()



    for event in pygame.event.get():
        if event.type is pygame.QUIT:
            run = False
            break

       


    move_player(Player_Car)
    Computer_Car.move()

    handle_collision(Player_Car,Computer_Car,game_info)

    if game_info.game_finished():
        blit_text_center(WIN,MAIN_FONT,"You Won the game!")
        pygame.time.wait(5000)
        game_info.reset()
        Computer_Car.reset()
        Player_Car.reset()


    


pygame.quit()