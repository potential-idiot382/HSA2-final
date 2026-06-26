import pygame
import sys
import random
import asyncio

class Player: # ----Player Class----
    def  __init__(self, screenWidth, screenHeight): # --- Setting up the attributes for the player entity
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.playerWidth = 50
        self.playerHeight = 60
        self.playerX = (self.screenWidth // 2) - (self.playerWidth // 2)
        self.playerY = self.screenHeight - self.playerHeight - 10
        self.playerSpeed = float(5.3)
        self.image = pygame.image.load("player_ship.png") # --- Loading the player image
        self.image = pygame.transform.scale(self.image, (self.playerWidth, self.playerHeight)) # --- Scales the player to the correct size

    def move(self):   # --- creating Move function to move the player left and right
        pressed =  pygame.key.get_pressed() # --- Setting variable for shorter code,, need to get the state of all keyboard keys
        if (pressed[pygame.K_LEFT] or pressed[pygame.K_a]) and self.playerX > 0:   # --- Moving Player left
            self.playerX -= self.playerSpeed
        if (pressed[pygame.K_RIGHT] or pressed[pygame.K_d]) and self.playerX < self.screenWidth - self.playerWidth: # --- Moving Player right
            self.playerX += self.playerSpeed
    
    def draw(self, screen):     # --- Creating Draw function to draw the player on the screen
        screen.blit(self.image, (self.playerX, self.playerY)) # --- Drawing the player image on the screen

class Projectile: # ----Missile Class----
    def __init__(self, playerWidth, playerHeight):
        self.missileWidth = 7
        self.missileHeight = 14
        self.missileSpeed = 8
        self.missiles = []
        self.playerWidth = playerWidth
        self.playerHeight = playerHeight
        self.image = pygame.image.load("laser.png") # --- Loading the missile image
        self.image = pygame.transform.scale(self.image, (self.missileWidth, self.missileHeight)) # --- Scales the missile to the correct size
        self.lastShot =  0
        self.fireDelay = 270 # --- minimum amount of shots that can be fired via

    
    def fire(self, event, p_x, p_y):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:   # --- Checking if the space bar is pressed and if the event is a keydown event
            now = pygame.time.get_ticks()
            if now - self.lastShot < self.fireDelay:
                return
            self.lastShot = now
            m_x = p_x + (self.playerWidth // 2) - (self.missileWidth // 2)
            m_y = p_y
            newMissile = pygame.Rect(m_x, m_y, self.missileWidth, self.missileHeight) # --- Calculating the x and y position of the missile based on the player's position and the missile's width and height
            self.missiles.append(newMissile)

    def move(self):
        for missile in self.missiles:
            missile.y -= self.missileSpeed
        self.missiles = [missile for missile in self.missiles if missile.y > 0] # --- List comprehension to remove missiles that have gone off the screen, keeping only those that are still visible

    def draw(self, screen):
        for missile in self.missiles:
            screen.blit(self.image, (missile.x, missile.y)) # --- Drawing the missile image on the screen
            
class Enemy: # ----Enemy Class ----
    def __init__(self, worldWidth, worldHeight):
        self.enemyWidth = (125 // 3)
        self.enemyHeight = 50
        self.enemySpeed = float(4.7)
        self.enemies = []
        self.worldWidth = worldWidth
        self.worldHeight = worldHeight
        self.enemyTimer = 0
        self.enemySpawnRate = random.choice(range(1750, 2001, 4))  # --- Number of frames between enemy spawns; spawns every 2 seconds at 60 fps

    def spawn(self, currentTime): # --- Creating Spawn function to spawn enemies at random x positions at the top of the screen
        if currentTime - self.enemyTimer > self.enemySpawnRate: # --- Spawning an enemy at a random x position at the top of the screen
            e_x = random.randint(0, self.worldWidth - self.enemyWidth)
            e_y = 0
            newEnemy = pygame.Rect(e_x, e_y, self.enemyWidth, self.enemyHeight)
            self.enemies.append(newEnemy)
            self.enemyTimer = currentTime
            self.image = pygame.image.load("enemy_ship.png") # --- Loading the enemy image
            self.image = pygame.transform.scale(self.image, (self.enemyWidth, self.enemyHeight))

    def move(self):
        for enemy in self.enemies:
            enemy.y += self.enemySpeed
        self.enemies = [enemy for enemy in self.enemies if enemy.y < self.worldHeight]         # --- List comprehension to remove enemies that have gone off the screen, keeping only those that are still visible

    def draw(self, screen):
        for enemy in self.enemies:
             screen.blit(self.image, (enemy.x, enemy.y)) # --- Drawing the enemy image on the screen

class GameWindow: # ---- Game Window Class ----
    def __init__(self):
        pygame.init() #  ---Always call this at the start of PyGame projects since the library is necessary for the game and window to run
        pygame.display.set_caption("Space Invaders") # --- Set window title

        self.screenHeight = 600
        self.screenWidth = 800
        self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight)) # --- Set window size

        self.clock = pygame.time.Clock() # --- Create a clock object to control the frame rate of the game

        # --- initializing objects for all entity classes
        self.player = Player(self.screenWidth, self.screenHeight) # --- Create a player object
        self.projectile = Projectile(self.player.playerWidth, self.player.playerHeight) # --- Create a projectile object
        self.enemy = Enemy(self.screenWidth, self.screenHeight) # --- Create an enemy object

        # --- State of the game; scoring system/display font
        self.score = 0 # --- Create a score variable to keep track of the player's score
        self.difficultyLevel = 0
        self.is_running = True
        self.font = pygame.font.SysFont("Gotham", 30) # --- Create a font object for displaying the score
    
    def detectCollisions(self, rect1, rect2): # --- Returns True if the two rectangles collide, False otherwise
        return rect1.colliderect(rect2)

    async def runGame(self):
        while True: # --- Putting in the Game Loop
            for event in pygame.event.get(): # --- Handling inputs and events
                if event.type == pygame.QUIT: # --- Checking if the user has clicked the close button on the window
                    pygame.quit()
                    sys.exit() # --- Quits program
                if self.is_running:
                    self.projectile.fire(event, self.player.playerX, self.player.playerY)

            if self.is_running: # --- Updating positions of player, missiles, and enemies only if the game is running
                self.player.move() 
                self.projectile.move() # --- Calling the move function to move the missiles

                currentTime = pygame.time.get_ticks() # --- Getting the current time in milliseconds since the game started
                self.enemy.spawn(currentTime) # --- Calling the spawn function to spawn enemies at random x positions at the top of the screen
                self.enemy.move() # --- Calling the move function to move the enemies
                    
                for missile in self.projectile.missiles[:]: # --- Checking for collisions
                    for enemy in self.enemy.enemies[:]: # -- Putting brackets around the colons allows for slicing within the program --
                        if missile.colliderect(enemy):
                            self.projectile.missiles.remove(missile)
                            self.enemy.enemies.remove(enemy)
                            self.score += 10
                            break
                    
                p_rect = pygame.Rect(self.player.playerX, self.player.playerY, self.player.playerWidth, self.player.playerHeight)
                for enemy in self.enemy.enemies:
                    if self.detectCollisions(p_rect, enemy):
                        self.is_running = False # --- If the player collides with an enemy, the game stops running 

                    if  self.score >= 250 and self.difficultyLevel < 1: # --- difficulty increases
                        self.difficultyLevel = 1
                        self.projectile.fireDelay = 230
                        self.enemy.enemySpeed = float(5.3)
                        self.enemy.enemySpawnRate = random.choice(range(750, 1325, 20))
                        self.score += 15
                    
                    if  self.score >= 400 and self.difficultyLevel < 2: # --- difficulty increases
                        self.difficultyLevel = 2
                        self.projectile.fireDelay = 190
                        self.enemy.enemySpeed = float(5.9)
                        self.enemy.enemySpawnRate = random.choice(range(700, 1100, 15))
                        self.score += 20

            self.screen.fill((0, 0, 0)) # --- Filling the screen with a black color
            self.player.draw(self.screen) # --- Drawing the player on the screen
            self.projectile.draw(self.screen) # --- Drawing the missiles on the screen
            self.enemy.draw(self.screen) # --- Drawing the enemies on the screen

            scoreText = self.font.render(f"Score: {self.score}", True, (255, 255, 255)) # --- Creating a text surface for the score
            self.screen.blit(scoreText, (10, 10)) # --- Drawing the score on

            if not self.is_running: # --- If the game is not running, display "Game Over" message
                msg = self.font.render(f"Game Over!  – Final Score: {self.score}", True, (255, 0, 0)) # --- Creating a text surface for the game over message; displays final score
                self.screen.blit(msg, (self.screenWidth // 2 - 100, self.screenHeight // 2))

            pygame.display.flip() # --- Updating the display
            self.clock.tick(60) # --- Setting the frame rate to 60 frames per second
            await asyncio.sleep(0)

async def main():
    game = GameWindow()
    await game.runGame()

if __name__ == "__main__":  # --- Entry point of the program
    asyncio.run(main())