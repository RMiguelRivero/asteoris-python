import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0
started = False

class ImageInfo:
    """
    Sprite class
    """
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        """
        Get attribute center
        """
        return self.center

    def get_size(self):
        """
        Get attribute size
        """
        return self.size

    def get_radius(self):
        """
        Get attribute radius
        """
        return self.radius

    def get_lifespan(self):
        """
        Get attribute lifespan
        """
        return self.lifespan

    def get_animated(self):
        """
        Get attribute animated
        """
        return self.animated


# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim

# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.s2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
# .ogg versions of sounds are also available, just replace .mp3 by .ogg
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.ogg")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.ogg")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.ogg")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.ogg")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(point1, point2):
    """
    Calculate euclidean distance between to points
    """
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


# Ship class
class Ship:
    """
    Ship class
    """
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()

    def draw(self, canvas):
        """
        Draw the ship depending if it`s thrust
        """
        if self.thrust:
            canvas.draw_image(self.image,[self.image_center[0] + self.image_size[0],\
                                self.image_center[1]], self.image_size,\
                                self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size,
                              self.pos, self.image_size, self.angle)
        # canvas.draw_circle(self.pos, self.radius, 1, "White", "White")

    def reset(self):
        """
        Restore the ship
        """
        self.pos = [WIDTH / 2, HEIGHT / 2]
        self.vel = [0, 0]
        self.thrust = False
        self.angle = 0
        self.angle_vel = 0


    def update(self):
        """
        Updating the ship position & velocity
        """
        # update angle
        self.angle += self.angle_vel

        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT

        # update velocity
        if self.thrust:
            acc = angle_to_vector(self.angle)
            self.vel[0] += acc[0] * .1
            self.vel[1] += acc[1] * .1

        self.vel[0] *= .99
        self.vel[1] *= .99

    def set_thrust(self, on):
        """
        Set thrust on or off
        """
        self.thrust = on
        if on:
            ship_thrust_sound.rewind()
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.pause()

    def increment_angle_vel(self):
        """
        Controlling the ship`s angle clockwise anticlockwise
        """
        self.angle_vel += .05

    def decrement_angle_vel(self):
        """
        Controlling the ship`s angle anticlockwise
        """
        self.angle_vel -= .05

    def shoot(self):
        """
        Controlling the missiles
        """
        global missile_group
        # get the ship`s direction
        forward = angle_to_vector(self.angle)
        # set the missile at the front of the ship
        missile_pos = [self.pos[0] + self.radius * forward[0],\
                       self.pos[1] + self.radius * forward[1]]
        # set the missile velocity be greater than the space ship
        missile_vel = [self.vel[0] + 6 * forward[0],\
                       self.vel[1] + 6 * forward[1]]
        # draw missile
        a_missile = Sprite(missile_pos, missile_vel, self.angle, 0,\
                           missile_image, missile_info, missile_sound)
        # add to the group
        missile_group.add(a_missile)

    def get_position(self):
        """
        Get the ship`s position
        """
        return self.pos

    def get_radius(self):
        """
        Get the ship`s radius
        """
        return self.radius

class Sprite:
    """
    Sprite class
    """
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        # controlling sound
        if sound:
            sound.rewind()
            sound.play()

    def draw(self, canvas):
        """
        Draw sprites
        """
        canvas.draw_image(self.image, self.image_center, self.image_size,
                          self.pos, self.image_size, self.angle)

    def update(self):
        # update angle
        self.angle += self.angle_vel

        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT

        #controlling lifespan
        autodestroy = False
        self.age += 1
        if self.age > self.lifespan :
            autodestroy = True
        return autodestroy

    def get_position(self):
        return self.pos

    def get_radius(self):
        return self.radius

    def collide(self, other_object):
        """
        Says if there is collision
        """
        collide = False
        distance = dist(self.get_position(), other_object.get_position())
        if distance < self.get_radius() + other_object.get_radius():
            collide = True
            explosion_sound.rewind()
            explosion_sound.play()
        return collide

def keydown(key):
    """
    keydown handlers to control ship
    """
    if started:
        if key == simplegui.KEY_MAP['left']:
            my_ship.decrement_angle_vel()
        elif key == simplegui.KEY_MAP['right']:
            my_ship.increment_angle_vel()
        elif key == simplegui.KEY_MAP['up']:
            my_ship.set_thrust(True)
        elif key == simplegui.KEY_MAP['space']:
            my_ship.shoot()

def keyup(key):
    """
    keyup handlers to control ship
    """
    if started:
        if key == simplegui.KEY_MAP['left']:
            my_ship.increment_angle_vel()
        elif key == simplegui.KEY_MAP['right']:
            my_ship.decrement_angle_vel()
        elif key == simplegui.KEY_MAP['up']:
            my_ship.set_thrust(False)

def click(pos):
    """
    mouseclick handlers that reset UI and conditions whether
    splash image is drawn
    """
    global started, lives, score
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        lives = 3
        score = 0
        soundtrack.play()

def draw(canvas):
    """
    Handler for the canvas
    """
    global time, started, lives, score

    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), \
                        nebula_info.get_size(),\
                        [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, \
                        (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, \
                        (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # draw UI
    canvas.draw_text("Lives", [50, 50], 22, "White")
    canvas.draw_text("Score", [680, 50], 22, "White")
    canvas.draw_text(str(lives), [50, 80], 22, "White")
    canvas.draw_text(str(score), [680, 80], 22, "White")

    if lives < 1:
        started = False
        soundtrack.rewind()
        for rock in set(rock_group):
            rock_group.discard(rock)
    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(),
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2],
                          splash_info.get_size())
        my_ship.set_thrust(False)
        my_ship.reset()
    else:
        # draw ship and sprites
        my_ship.draw(canvas)
        process_sprite_group(rock_group, canvas)
        process_sprite_group(missile_group, canvas)

        # update ship
        my_ship.update()

        # live update because of collision
        if group_collide(rock_group, my_ship):
            lives -= 1
        # update score
        score += 10 * group_group_collide(rock_group, missile_group)

def rock_spawner():
    """
    timer handler that spawns a rock
    """
    global rock_group
    if len(rock_group) < 12:
        rock_pos = [random.randrange(0, WIDTH), random.randrange(0, HEIGHT)]
        if dist(rock_pos, my_ship.get_position()) >= my_ship.get_radius() + 20:
            rock_vel = [random.random() * .6 - .3, random.random() * .6 - .3]
            rock_avel = random.random() * .2 - .1
            a_rock = Sprite(rock_pos, rock_vel, 0, rock_avel,\
                            asteroid_image, asteroid_info)
            rock_group.add(a_rock)

def process_sprite_group(a_set, canvas):
    """
    draw a group of sprites
    """
    for sprite in set(a_set):
        sprite.draw(canvas)
        if sprite.update():
            a_set.remove(sprite)

def group_collide(group, other_object):
    """
    Manage collision between a sprite and a group of sprites
    """
    collision = False
    for sprite in set(group):
        if sprite.collide(other_object):
            group.remove(sprite)
            collision = True
    return collision

def group_group_collide(group1, group2):
    """
    Manage collision between two group of sprites
    """
    number_collision = 0
    for sprite in set(group1):
        if group_collide(group2, sprite):
            number_collision += 1
            group1.discard(sprite)
    return number_collision

# initialize stuff
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
#a_rock = Sprite([WIDTH / 3, HEIGHT / 3], [1, 1], 0, .1, asteroid_image, asteroid_info)
a_missile = Sprite([2 * WIDTH / 3, 2 * HEIGHT / 3], [-1,1], 0, 0, missile_image, missile_info, missile_sound)

rock_group = set([])
missile_group = set([])

# register handlers
frame.set_keyup_handler(keyup)
frame.set_keydown_handler(keydown)
frame.set_mouseclick_handler(click)
frame.set_draw_handler(draw)

timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
timer.start()
frame.start()
