# By Pramod Jacob

import random, sys, time, pygame
from pygame.locals import *

# game characteristics
FPS = 30
WINWIDTH = 1366
WINHEIGHT = 768
WINWIDTH_HALF = int(WINWIDTH/2)
WINHEIGHT_HALF = int(WINHEIGHT/2)

# colors
WHITE = (255, 255, 255)
LITEGRAY = (200, 200, 200)
DARKGRAY = (100, 100, 100)
BLACK = (0, 0, 0)

# constants
ARCHER_SCALE = 200 ## scale up archer object size 
ARCHER_YADJ = 60 ## adjust archer's y position to account for ground
ARCHER_ROLLADJ = 70

class GameCharacter:

    def __init__(self, action, direction, pos_x, pos_xprev, pos_y, pos_yprev, move_speed, move_freq, sprint_speed, shoot_freq,
                 jump_speed_UD, jump_speed_LR, jump_freq, jump_height, roll_speed, roll_freq, roll_dist, surf, rect):
        
        self.action = action
        self.direction = direction
        self.pos_x = pos_x 
        self.pos_xprev = pos_xprev 
        self.pos_y = pos_y ## y position in current iteration of loop during jump
        self.pos_yprev = pos_yprev ## y position in previous iteration of loop during jump
        self.move_speed = move_speed
        self.move_freq = move_freq
        self.sprint_speed = sprint_speed
        self.shoot_freq = shoot_freq
        self.jump_speed_UD = jump_speed_UD ## up & down
        self.jump_speed_LR = jump_speed_LR ## left & right
        self.jump_freq = jump_freq
        self.jump_height = jump_height
        self.roll_speed = roll_speed
        self.roll_freq = roll_freq
        self.roll_dist = roll_dist
        self.surf = surf
        self.rect = rect
        
def main():

    global FPSCLOCK, DISPLAYSURF
    global IMG_ARCHER_L, IMG_ARCHER_R

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    pygame.display.set_caption('Archer')

    # all right-facing archer images
    IMG_ARCHER_R = {'STAND': pygame.image.load('Archer\Standing.png'),
                    'GRAB': pygame.image.load('Archer\Grab.png'),
                    'DRAW': pygame.image.load('Archer\Draw.png'),
                    'RELEASE': pygame.image.load('Archer\Release.png'),
                    'UP_GRAB': pygame.image.load('Archer\\Up_Grab.png'),
                    'UP_DRAW': pygame.image.load('Archer\\Up_Draw.png'),
                    'UP_RELEASE': pygame.image.load('Archer\\Up_Release.png'),
                    'RUN_1': pygame.image.load('Archer\Run1.png'),
                    'RUN_2': pygame.image.load('Archer\Run2.png'),
                    'RUN_3': pygame.image.load('Archer\Run3.png'),
                    'RUN_4': pygame.image.load('Archer\Run4.png'),
                    'JUMPROLL_1': pygame.image.load('Archer\JumpRoll1.png'),
                    'JUMPROLL_2': pygame.image.load('Archer\JumpRoll2.png'),
                    'JUMPROLL_3': pygame.image.load('Archer\JumpRoll3.png'),
                    'JUMPROLL_4': pygame.image.load('Archer\JumpRoll4.png'),
                    'JUMP_GRAB': pygame.image.load('Archer\Jump_Grab.png'),
                    'JUMP_DRAW': pygame.image.load('Archer\Jump_Draw.png'),
                    'JUMP_RELEASE': pygame.image.load('Archer\Jump_Release.png'),
                    'CROUCH': pygame.image.load('Archer\Crouch.png'),
                    'CROUCH_GRAB': pygame.image.load('Archer\Crouch_Grab.png'),
                    'CROUCH_DRAW': pygame.image.load('Archer\Crouch_Draw.png'),
                    'CROUCH_RELEASE': pygame.image.load('Archer\Crouch_Release.png')}
  
    # all left-facing archer images
    IMG_ARCHER_L = {}
    for key in IMG_ARCHER_R:
        IMG_ARCHER_L[key] = pygame.transform.flip(IMG_ARCHER_R[key], True, False)

        # scale all images to size
        IMG_ARCHER_L[key] = pygame.transform.scale(IMG_ARCHER_L[key], (ARCHER_SCALE, ARCHER_SCALE)) 
        IMG_ARCHER_R[key] = pygame.transform.scale(IMG_ARCHER_R[key], (ARCHER_SCALE, ARCHER_SCALE))

    while True:
        runGame()
    
def runGame(): 

    # movement & action states
    moveLeft = moveRight = shooting = jumping = crouching = rolling = sprinting = lookingUp = False

    # timers
    moveTimer = shootTimer = jumpTimer = rollTimer = time.time()

    # initialize archer object 
    archer = GameCharacter('STAND',                             ## action
                           'RIGHT',                             ## direction
                           WINWIDTH_HALF,                       ## pos_x
                           WINWIDTH_HALF,                       ## pos_xprev
                           WINHEIGHT_HALF,                      ## pos_y
                           WINHEIGHT_HALF,                      ## pos_yprev
                           35,                                  ## move_speed
                           0.125,                               ## move_freq
                           55,                                  ## sprint_speed
                           0.15,                                ## shoot_freq
                           40,                                  ## jump_speed_UD
                           20,                                  ## jump_speed_LR
                           0.05,                                ## jump_freq
                           280,                                 ## jump_height
                           60,                                  ## roll_speed
                           0.1,                                 ## roll_freq
                           300,                                 ## roll_dist
                           IMG_ARCHER_R['STAND'],               ## surf
                           IMG_ARCHER_R['STAND'].get_rect())    ## rect

    # archer animation action tuples
    archerRunning = ('RUN_1', 'RUN_2', 'RUN_3', 'RUN_4')
    archerJumpingRolling = ('JUMPROLL_1', 'JUMPROLL_2', 'JUMPROLL_3', 'JUMPROLL_4')
    archerShooting = ('GRAB', 'DRAW', 'RELEASE')
    archerShootingUp = ('UP_GRAB', 'UP_DRAW', 'UP_RELEASE')
    archerShootingCrouch = ('CROUCH_GRAB', 'CROUCH_DRAW', 'CROUCH_RELEASE')
    archerShootingJump = ('JUMP_GRAB', 'JUMP_DRAW', 'JUMP_RELEASE')

    # various parameters that must be initialized outside of game loop
    groundY = archer.pos_yprev
    initialX = archer.pos_xprev
    rollY = archer.pos_y + ARCHER_ROLLADJ
    
    # main game loop
    while True:

        # input events
        for event in pygame.event.get(): 
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN: 
                if event.key == K_a:
                    moveLeft = True
                    moveRight = False
                elif event.key == K_d:
                    moveRight = True
                    moveLeft = False
                elif event.key == K_w:
                    jumping = True
                elif event.key == K_SPACE:
                    shooting = True
                elif event.key == K_LCTRL:
                    crouching = True
                elif event.key == K_LSHIFT:
                    sprinting = True
                elif event.key == K_UP:
                    lookingUp = True
                elif event.key == K_ESCAPE:
                    terminate()
            elif event.type == KEYUP:
                if event.key == K_a:
                    moveLeft = False
                elif event.key == K_d:
                    moveRight = False
                elif event.key == K_SPACE:
                    shooting = False
                elif event.key == K_LCTRL:
                    crouching = False
                elif event.key == K_LSHIFT:
                    sprinting = False
                elif event.key == K_UP:
                    lookingUp = False

        # input control, to avoid glitches
        if (moveLeft or moveRight) and (shooting or rolling) and not jumping:
            shooting = False
        if rolling and jumping:
            jumping = False
        
        # archer idle
        if not (moveLeft or moveRight or shooting or jumping or rolling):
            archer.action = checkIdleStance(crouching)
    
        # TIER 1
        if not (jumping or rolling):

            # re-initialize x and y values 
            archer.pos_xprev = archer.pos_x

            # archer direction
            if moveLeft:
                archer.direction = 'LEFT'
            elif moveRight:
                archer.direction = 'RIGHT'

            # archer running or sprinting from left and right
            if (moveLeft or moveRight) and time.time() - moveTimer > archer.move_freq:
                moveTimer = time.time()

                if sprinting:
                    moveSpeed = archer.sprint_speed
                else:
                    moveSpeed = archer.move_speed
            
                if moveLeft:
                    archer.pos_x -= moveSpeed
                elif moveRight:
                    archer.pos_x += moveSpeed

                archer.action = animationFrame(archerRunning, archer.action)

            # archer shooting animation
            if shooting and time.time() - shootTimer > archer.shoot_freq:
                shootTimer = time.time()

                if crouching: 
                    archer.action = animationFrame(archerShootingCrouch, archer.action)
                elif lookingUp: 
                    archer.action = animationFrame(archerShootingUp, archer.action)
                else:
                    archer.action = animationFrame(archerShooting, archer.action)

        # TIER 2
        if not jumping: 

            # archer rolling animation
            if crouching and (moveLeft or moveRight):
                rolling = True

            if rolling and time.time() - rollTimer > archer.roll_freq:
                rollTimer = time.time()
                
                archer.pos_y = rollY
                archer.action = animationFrame(archerJumpingRolling, archer.action)

                if archer.direction == 'LEFT':
                    archer.pos_x -= archer.roll_speed
                elif archer.direction == 'RIGHT':
                    archer.pos_x += archer.roll_speed
                
                if abs(archer.pos_x - archer.pos_xprev) > archer.roll_dist:
                    rolling = False
                    archer.pos_y -= ARCHER_ROLLADJ
                    archer.action = checkIdleStance(crouching)

        # TIER 3
        # archer jumping animation
        if jumping and time.time() - jumpTimer > archer.jump_freq:
            jumpTimer = time.time()

            # archer direction
            if moveLeft:
                archer.direction = 'LEFT'
            elif moveRight:
                archer.direction = 'RIGHT'

            if not shooting:
                archer.action = animationFrame(archerJumpingRolling, archer.action)
            else:
                archer.action = animationFrame(archerShootingJump, archer.action)

            if moveLeft:
                archer.pos_x -= archer.jump_speed_LR
            elif moveRight:
                archer.pos_x += archer.jump_speed_LR
                
            if abs(groundY - archer.pos_y) < archer.jump_height and archer.pos_yprev - archer.pos_y >= 0:
                archer.pos_yprev = archer.pos_y
                archer.pos_y -= archer.jump_speed_UD
            else:
                archer.pos_yprev = archer.pos_y
                archer.pos_y += archer.jump_speed_UD
                if archer.pos_y >= groundY:
                    jumping = False
                    archer.pos_yprev = archer.pos_y
            
        # archer flip image
        if  archer.direction == 'LEFT':
            archer.surf = IMG_ARCHER_L[archer.action]
        elif  archer.direction == 'RIGHT':
            archer.surf = IMG_ARCHER_R[archer.action]

        # archer position
        archer.rect.centerx = archer.pos_x
        archer.rect.centery = archer.pos_y - ARCHER_YADJ

        # draw all objects
        DISPLAYSURF.fill(LITEGRAY)
        floorRect = pygame.Rect(0, groundY, WINWIDTH, WINHEIGHT - (WINHEIGHT - groundY))
        pygame.draw.rect(DISPLAYSURF, DARKGRAY, floorRect)
        DISPLAYSURF.blit(archer.surf, archer.rect)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def checkIdleStance(crouching):

    # given crouching Boolean, returns either CROUCHING or STANDING action

    if crouching: 
        return 'CROUCH'
    else:
        return 'STAND'

def animationFrame(animationTuple, action):

    # given tuple of images in order of use and current action, returns next logical frame in animation

    for i in range(len(animationTuple)):
        if action == animationTuple[i]:
            break
    if i == len(animationTuple)-1 or action == 'STAND':
        return animationTuple[0]
    else:
        return animationTuple[i+1]

def terminate():

    # end program
    
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
                                        
