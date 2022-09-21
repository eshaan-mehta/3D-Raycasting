#fov and mouse sens sliders, minimap, raycasting, background picture

import pygame, math

from pygame.locals import *

pygame.init()
pygame.display.set_caption("raycasting")

s_width = 1100
s_height = 650

screen = pygame.display.set_mode((s_width, s_height))

is_running = True

frames = 0

class Level:
    color = (10, 10, 10)
    rects = []
    minimap = pygame.Surface((800 * 13/50, 650 * 13/50))

    def rect(self, x, y, w, h):
        r = pygame.Rect(x, y, w, h)
        self.rects.append(r)
    
    def __init__(self):     
        self.rect(0, 0, 800, 10)#walls
        self.rect(0, 640, 800, 10)
        self.rect(0, 10, 10, 630)
        self.rect(790, 10, 10, 630)
        
        #self.rect(390, 10, 10, 85)#upside down t
        self.rect(275,  95, 250, 20)
        self.rect(515, 10, 10, 175)#stick
        
        self.rect(150, 10, 10, 180)#top-left L
        self.rect(90, 180, 70, 10)

        self.rect(630, 400, 160, 10)#right wall stick

        self.rect(600, 50, 30, 30)#blocks
        self.rect(700, 90, 30, 30)
        self.rect(630, 250, 30, 30)
        self.rect(580, 140, 30, 30)
        self.rect(680, 180, 30, 30)

        self.rect(515, 300, 10, 240)#U
        self.rect(160, 530, 365, 10)
        self.rect(150, 300, 10, 240)

        self.rect(230, 400, 200, 60) #thick block

        self.rect(80, 480, 70, 10) #horizontal walls on left side
        self.rect(10, 350, 70, 10)
        
        
    def draw(self, screen):
        for rect in self.rects:
            pygame.draw.rect(screen, self.color, rect)

class Ray:
    size = 5
    
    def __init__(self, x, y, direction):
        self.d = pygame.Vector2(x, y)
        self.origin = pygame.Vector2(x, y)
        self.v = self.size
        self.hitbox = pygame.Rect(0, 0, self.size, self.size)
        self.dir = direction

    def collide(self):
        self.hitbox.center = self.d
        for rect in Level.rects:
            if self.hitbox.colliderect(rect):
                return True
            
        return False  

    def move(self, velo):
        self.d.x += velo * math.cos(math.radians(self.dir))
        self.d.y -= velo * math.cos(math.radians(self.dir))
        
    def update(self, player, direction):
        self.origin = player
        self.d = player
        self.dir = direction
        while not self.collide():
            self.move(self.v)
            self.hitbox.center = self.d

        while self.collide():
            self.move(-1)
            self.hitbox.center = self.d

    
    def draw(self, screen):
        pygame.draw.rect(screen, (240, 240, 0), self.hitbox)
        pygame.draw.line(screen, (0,0,218), self.origin, self.hitbox.center, 5)


class Raycaster:
    rays = []
    
    def __init__(self, fov, x, y, direction):
        self.fov = fov
        self.center = direction

        for i in range(fov):
            r = Ray(x, y, self.center)
            self.rays.append(r)
            
    def update(self, player, direction):
        for ray in self.rays:
            ray.update(player, direction)

    def draw(self, screen):
        for ray in self.rays:
            ray.draw(screen)
        

class Player:
    length = 25
    
    def __init__(self, x, y, ang):
        self.d = pygame.Vector2(x, y)
        self.v = pygame.Vector3(0.15, 0.05, 0.1)#f, (l/r), b
        self.dir = ang + 90
        self.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load("player.png"), (20, 20)), ang)
        self.copy = self.image
        self.hitbox = self.image.get_rect()
        self.moveX = (True, True, True, True) #l, r, f, b
        self.moveY = (True, True, True, True) #l, r, f, b
        self.colliding = [False, False]
        self.moving = ""
        
        
    def rotate(self, angle):
        self.dir += angle
        if self.dir >= 360:
            self.dir -= 360
        if self.dir < 0:
            self.dir += 360
        
        self.copy = pygame.transform.rotate(self.image, self.dir - 90)
        
    def moveL(self, velo, dt):
        if self.moveX[0]:
            self.d.x -= velo * math.sin(math.radians(self.dir)) * dt
        if self.moveY[0]:
            self.d.y -= velo * math.cos(math.radians(self.dir)) * dt

    def moveR(self, velo,  dt):
        if self.moveX[1]:
            self.d.x += velo * math.sin(math.radians(self.dir)) * dt
        if self.moveY[1]:
            self.d.y += velo * math.cos(math.radians(self.dir)) * dt

    def moveF(self, velo, dt):
        if self.moveX[2]:
            self.d.x += velo * math.cos(math.radians(self.dir)) * dt
        if self.moveY[2]:
            self.d.y -= velo * math.sin(math.radians(self.dir)) * dt

    def moveB(self, velo, dt):
        if self.moveX[3]:
            self.d.x -= velo * math.cos(math.radians(self.dir)) * dt
        if self.moveY[3]:
            self.d.y += velo * math.sin(math.radians(self.dir)) * dt

    def collideX(self, rect, dt):
        e = 4
        if self.moving == "b":
            e = abs(self.v.z * math.cos(math.radians(self.dir))) * dt
        elif self.moving == "l" or self.moving == "r":
            e = abs(self.v.y * math.sin(math.radians(self.dir))) * dt
        else:
            e = abs(self.v.x * math.cos(math.radians(self.dir))) * dt
        
        if abs(self.hitbox.left - rect.right) < e:
            self.colliding[0] = True
            if ((self.dir >= 0 or self.dir >= 360) and self.dir < 90):
                self.moveX = (False, True, True, False)
            if (self.dir >= 90 and self.dir < 180):
                self.moveX = (False, True, False, True)
            if (self.dir >= 180 and self.dir < 270):
                self.moveX = (True, False, False, True)
            if (self.dir >= 270 and self.dir < 360):
                self.moveX = (True, False, True, False)

        if abs(self.hitbox.right - rect.left) < e:
            self.colliding[0] = True
            if ((self.dir >= 0 or self.dir >= 360) and self.dir < 90):
                self.moveX = (True, False, False, True)
            if (self.dir >= 90 and self.dir < 180):
                self.moveX = (True, False, True, False)
            if (self.dir >= 180 and self.dir < 270):
                self.moveX = (False, True, True, False)
            if (self.dir >= 270 and self.dir < 360):
                self.moveX = (False, True, False, True)
                
    def collideY(self, rect, dt):
        if self.moving == "b":
            e = abs(self.v.z * math.sin(math.radians(self.dir))) * dt
        elif self.moving == "l" or self.moving == "r":
            e = abs(self.v.y * math.cos(math.radians(self.dir))) * dt
        else:
            e = abs(self.v.x * math.sin(math.radians(self.dir))) * dt
        
        if abs(self.hitbox.bottom - rect.top) < e:
            self.colliding[1] = True
            if ((self.dir >= 0 or self.dir >= 360) and self.dir < 90):
                self.moveY = (True, False, True, False)
            if (self.dir >= 90 and self.dir < 180):
                self.moveY = (False, True, True, False)
            if (self.dir >= 180 and self.dir < 270):
                self.moveY = (False, True, False, True)
            if (self.dir >= 270 and self.dir < 360):
                self.moveY = (True, False, False, True)
                    
        if abs(self.hitbox.top - rect.bottom) < e:
            self.colliding[1] = True
            if ((self.dir >= 0 or self.dir >= 360) and self.dir < 90):
                self.moveY = (False, True, False, True)
            if (self.dir >= 90 and self.dir < 180):
                self.moveY = (True, False, False, True)
            if (self.dir >= 180 and self.dir < 270):
                self.moveY = (True, False, True, False)
            if (self.dir >= 270 and self.dir < 360):
                self.moveY = (False, True, True, False)
                
    def CheckCollision(self, dt):
        for rect in Level.rects:
            if self.hitbox.right > rect.left and self.hitbox.left < rect.right:
                self.collideY(rect, dt)
                
            if self.hitbox.bottom > rect.top and self.hitbox.top < rect.bottom:
                self.collideX(rect, dt)

    def update(self, dt,  mouse, frames, mouse_click, pressed):
        self.hitbox.center = self.d

        self.moving = ""
        
        self.moveX = (True, True, True, True)
        self.moveY = (True, True, True, True)
        self.colliding = [False, False]
    
    def draw(self, screen):
        #pygame.draw.rect(screen, (255,255,255), self.hitbox)
        screen.blit(self.copy, (self.d.x - int(self.copy.get_width()/2), self.d.y - int(self.copy.get_height()/2)))


class Slider:
    background = (145, 89, 0)
    textC = (255,255,255)
    radius = 10
    
    def __init__(self, name, x, y, minimum, maximum, value, inc):
        self.box = pygame.Rect(x, y, 250, 70)
        self.name = name
        self.min = minimum
        self.max = maximum
        self.value = value
        self.inc = inc
        self.pos = pygame.Vector2(self.box.x + 20, self.box.y + self.box.height/2 + 10)
        self.delay = 0
        self.font = pygame.font.Font("SourceSansPro-Bold.ttf", 20)
        self.font.set_bold(False)
    
    def update(self, dt, slider_select, pressed):
        if slider_select:
            self.radius = 13
        else:
            self.radius = 10

        if pressed[K_RIGHT]:
            if self.value < self.max and slider_select and self.delay == 0:
                self.value += self.inc
                self.delay = math.floor(20)
                #print(self.delay)
        if pressed[K_LEFT]:
            if self.value > self.min and slider_select and self.delay == 0:
                self.value -= self.inc
                self.delay = math.floor(20)
                #print(self.delay)
                
        self.value = round(self.value, 2)
        self.pos.x = self.box.x + 20 + (((self.box.width - 40) * (self.value - self.min)/(self.max - self.min)))
        
        self.text = self.font.render(self.name + ": " + str(self.value), True, self.textC)
        

        if self.delay > 0:
            self.delay -= 1
            

    def draw(self, screen):
        pygame.draw.rect(screen, self.background, self.box)
        screen.blit(self.text, (self.box.x + 5, self.box.y + 5))
        pygame.draw.line(screen, (0,0,0), (self.box.x + 20, self.box.y + self.box.height/2 + 10), (self.box.x + self.box.width - 20, self.box.y + self.box.height/2 + 10), 10)
        pygame.draw.circle(screen, (255,255,255), self.pos, self.radius)

class walls:
    const = 8
    
    def __init__(self, start, direction):
        self.length = 1
        self.start = start
        self.hitbox = pygame.Rect((self.start), (self.const, self.const))
        self.dir = direction
    
    def FindLength(self, rects):
        colliding = False
        
        while not colliding:
            ind = self.hitbox.collidelist(rects)
            if ind != -1:
                colliding = True                
                    
            else:
                self.hitbox.x += self.const * math.cos(math.radians(self.dir))
                self.hitbox.y -= self.const * math.sin(math.radians(self.dir))

        for i in range(2 * self.const):
            r = rects[ind]
            if self.hitbox.left < r.right and self.dir >= 90 and self.dir < 270:
                pass
                #self.hitbox.x += math.cos(math.radians(self.dir))
            if self.hitbox.right > r.left and (self.dir < 90 or self.dir >= 270):
                #self.hitbox.x -= math.cos(math.radians(self.dir))
                pass

            if self.hitbox.top < r.bottom and ((self.dir >= 0 and self.dir < 180) or self.dir >= 360):
                #self.hitbox.y -= math.sin(math.radians(self.dir))
                pass
            if self.hitbox.bottom > r.top and self.dir >= 180 and self.dir < 360:
                #self.hitbox.y += math.sin(math.radians(self.dir))
                pass
                
        self.length = math.dist(self.hitbox.center, self.start)
        self.height = 15000/self.length
            
        #print(ind)
        #print(self.length)

    def draw(self, screen, x, y, thickness):
        
        pygame.draw.line(screen, (0,0,200), (x, y), (x, y + 2 * self.height), thickness)
        #pygame.draw.line(screen, (0,0,200), self.start, self.hitbox.center, thickness)
        #pygame.draw.rect(screen, (240, 240, 0), self.hitbox)

class game:
    mouse_click = True
    slider_select = [True, False]
    slidernum = 1
    totalsliders = 2
    changing = False
    fov = 60
    sens = 0.5
    res = 15

    
    def __init__(self, s_width, s_height):
        self.p = Player(s_width/2, s_height/2, 0)
        self.l = Level()
        #self.r = Raycaster(1, self.p.d.x, self.p.d.y, self.p.dir) 
        
        self.senS = Slider("Mouse Sensitivity", s_width - 250, 80, 0.05, 1, self.sens, 0.05)
        self.fovS = Slider("FOV", s_width - 250, 0, 30, 90, self.fov, 5)
        
    def update(self, dt, frames, s_width, s_height):
        pressed = pygame.key.get_pressed()
        mouse = pygame.Vector2(pygame.mouse.get_pos())


        self.p.CheckCollision(dt)

        if pygame.mouse.get_pressed()[0]:
            self.mouse_click = True
        #mouse rotation---------------------------------------------------------
        if frames >=2 and self.mouse_click:
            self.p.rotate(math.degrees(-(pygame.mouse.get_rel()[0]) * self.senS.value/100))
            
        #slider switching--------------------------------------------------
        if pressed[pygame.K_UP]:
            if not self.changing:
                self.slider_select[self.slidernum-1] = not self.slider_select[self.slidernum-1]
                if self.slidernum > 1:
                    self.slidernum -= 1
                else:
                    self.slidernum = self.totalsliders
                self.slider_select[self.slidernum-1] = not self.slider_select[self.slidernum-1]
            self.changing = True
            
        elif pressed[pygame.K_DOWN]:
            if not self.changing:
                if self.slidernum < self.totalsliders:
                    self.slidernum += 1
                else:
                    self.slidernum = 1
                self.slider_select[self.slidernum-1] = not self.slider_select[self.slidernum-1]
                self.slider_select[self.slidernum-2] = not self.slider_select[self.slidernum-2]
            self.changing = True
        else:
            self.changing = False

        if self.mouse_click:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)

        #movement---------------------------------------------------------
        if pressed[97] and self.mouse_click:#left
            self.p.moveL(self.p.v.y, dt)
            self.p.moving = "l"
        
        if pressed[100] and self.mouse_click:#right
            self.p.moveR(self.p.v.y, dt)
            self.p.moving = "r"

        if pressed[119] and self.mouse_click:#front
            self.p.moveF(self.p.v.x, dt)
            self.p.moving = "f"
            
        if pressed[115] and self.mouse_click:#back
            self.p.moveB(self.p.v.z, dt)
            self.p.moving = "b"

        self.p.update(dt, mouse, frames, self.mouse_click, pressed)
        #self.r.update(self.p.d, self.p.dir)

        self.senS.update(dt, self.slider_select[0], pressed)
        self.fovS.update(dt, self.slider_select[1], pressed)

        self.sens = self.senS.value
        self.fov = self.fovS.value

        #print(self.fov)

        
        for i in range((self.fov + 1)):
            angle = self.p.dir + self.fov/2 - i
            #print(angle)
            w = walls(self.p.d, angle)
            w.FindLength(self.l.rects)
            w.draw(screen, s_width * i/self.fov, s_height/2 - w.height, self.res)


    def draw(self, screen):
        self.l.draw(screen)
        self.p.draw(screen)
        #self.r.draw(screen)

        self.senS.draw(screen)
        self.fovS.draw(screen)

pt = pygame.time.get_ticks()

g = game(s_width, s_height)



while is_running:
    ct = pygame.time.get_ticks()
    dt = ct - pt
    pt = ct
    pressed = pygame.key.get_pressed()

    screen.fill((210, 210, 210))

    if frames < 2:
        pygame.mouse.set_pos(s_width/2, 0)

    g.l.minimap.fill((210, 0, 0))
    #screen.blit(l.minimap, (0,0))
    
    g.update(dt, frames, s_width, s_height)
    g.draw(screen)
    
    #pygame.draw.rect(screen, (255,255,255), pygame.Rect(mouse.x-6, mouse.y-6, 12, 12))  #replacement cursor

    for event in pygame.event.get():
        if event.type == QUIT:
            is_running = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                g.mouse_click = False
                pygame.mouse.set_visible(True)
                pygame.event.set_grab(False)
                pygame.mouse.set_pos(s_width/2, s_height/2)

    pygame.display.update()

    if frames < 2:
        frames += 1
    
pygame.quit()
