import pygame
import random
windowWidth = 400
windowHeight = 600
gameSideMargin = 10
gameTopMargin = 40
gameBottomMargin = gameTopMargin
gameBorderWidth = 3
wallTop = gameTopMargin + gameBorderWidth
wallLeft = gameSideMargin + gameBorderWidth
wallRight = windowWidth - gameSideMargin - gameBorderWidth
wallBottom = windowHeight - gameBottomMargin - gameBorderWidth
gameSpeed = 60
enemyShotDelay = 0

black = (0,0,0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

pygame.init()

gameDisplay = pygame.display.set_mode((windowWidth, windowHeight))
pygame.display.set_caption('Space Invaders')

titleFont = pygame.font.SysFont('Arial', 40, True)
scoreFont = pygame.font.SysFont('Arial', 25, True)

clock = pygame.time.Clock()
playerImg = pygame.image.load("si-player.gif")
backgroundImg = pygame.image.load("si-background.gif")
enemyImg = pygame.image.load("si-enemy.gif")
bulletImg = pygame.image.load("si-bullet.gif")
#enemyBulletImg = pygame.image.load(".gif")

laserSound = pygame.mixer.Sound('laser.wav')
explosionSound = pygame.mixer.Sound('explode.wav')
voltageSound = pygame.mixer.Sound('voltage.wav')


def isCollision(a, b):
    if a.xcor + a.width > b.xcor and a.xcor < b.xcor + b.width and a.ycor + a.height > b.ycor and a.ycor < b.ycor + b.height:
        return True
    else:
        return False

class GameObject:
    def __init__(self, xcor, ycor, image, speed):
        self.xcor = xcor
        self.ycor = ycor
        self.img = image
        self.speed = speed
        self.width = image.get_width()
        self.height = image.get_height()
    def show(self):
        gameDisplay.blit(self.img, (self.xcor, self.ycor))

class Player(GameObject):
    def __init__(self, xcor, ycor, image, speed):
        super().__init__(xcor, ycor, image, speed)
        self.direction = 0
        self.score = 0
        self.level = 0
        self.isAlive = True
    def show(self):
        movementAmount = self.direction * self.speed
        newX = self.xcor + movementAmount

        if newX < wallLeft or newX > wallRight - playerImg.get_width():
            self.xcor = self.xcor
        else:
            self.xcor =  newX
        
        super().show()
    def moverRight(self):
        self.direction = 1
    def moveLeft(self):
        self.direction = -1
    def stopMoving(self):
        self.direction = 0
    def shoot(self):
        laserSound.play()
        newBullet = Bullet(self.xcor + self.width / 2 - bulletImg.get_width() / 2, self.ycor, bulletImg, 10)
        bullets.append(newBullet)

class Enemy(GameObject):
    def __init__(self, xcor, ycor, image, speed):
        super().__init__(xcor, ycor, image, speed)
        self.direction = 1
    def moveOver(self):
        self.xcor += self.direction * self.speed
    def moveDown(self):
        self.ycor += enemyImg.get_height() / 2
    def changeDirection(self):
        self.direction *= -1
    def shoot(self):
        voltageSound.play()
        newBullet = Bullet(self.xcor + self.width / 2, self.ycor, bulletImg, -2)
        enemyBullets.append(newBullet)
    @staticmethod
    def createEnemies(level):
        newEnemies = []
        for x in range(0, level.enemyColumnCount):
            for y in range(0, level.enemyRowCount):
                newEnemy = Enemy(wallLeft + 1 + enemyImg.get_width() * x, wallTop + enemyImg.get_height() * y, enemyImg, level.enemySpeed)
                newEnemies.append(newEnemy)
        return newEnemies

class Bullet(GameObject):
    
    def __init__(self, xcor, ycor, image, speed):
        super().__init__(xcor, ycor, image, speed)
    def move(self):
        self.ycor -= self.speed

class Level:
    def __init__(self, number, enemyRowCount, enemyColumnCount, enemySpeed):
        self.number = number
        self.enemyRowCount = enemyRowCount
        self.enemyColumnCount = enemyColumnCount
        self.enemySpeed = enemySpeed


pygame.mixer.music.load('sisong.mp3')
pygame.mixer.music.play(-1)


player = Player(windowWidth / 2 - playerImg.get_width() / 2, wallBottom - playerImg.get_height(), playerImg, 5)
pointPerEnemy = 100
bullets = []
enemies = []
levels = []
enemyBullets = []
levels.append(Level(1, 3, 5, 1))
levels.append(Level(2, 5, 6, 2))
levels.append(Level(3, 5, 8, 3))




while player.isAlive:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:    
            player.isAlive = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.moveLeft()
            elif event.key == pygame.K_RIGHT:
                player.moverRight()
            elif event.key == pygame.K_SPACE:
                player.shoot()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                player.stopMoving()
    if len(enemies) == 0:
        player.level += 1
        enemies = Enemy.createEnemies(levels[player.level - 1])

    for enemy in enemies:
        if isCollision(enemy, player):
            player.isAlive = False
        if enemy.xcor + enemyImg.get_width()  > wallRight or enemy.xcor < wallLeft:
            for e in enemies:
                e.changeDirection()
                e.moveDown()
            break
    
    for bullet in bullets:
        if bullet.ycor < wallTop:
            bullets.remove(bullet)
            break
        for enemy in enemies:
            if isCollision(enemy, bullet):
                try:
                    explosionSound.play()
                    enemies.remove(enemy)
                    player.score += pointPerEnemy
                except ValueError:
                    pass
                try:
                    bullets.remove(bullet)
                except ValueError:
                    pass
                break

    for bullet in enemyBullets:
        if bullet.ycor + bullet.height > wallBottom:
            try:
                bullets.remove(bullet)
            except ValueError:
                pass
        if isCollision(player, bullet):
            player.isAlive = False

    enemyShotDelay += 1
    for enemy in enemies:
        if(enemyShotDelay > 100 and random.randint(1, len(enemies) + 1) == 1):
            enemy.shoot()
            enemyShotDelay = 0
        enemy.moveOver()

    for bullet in bullets:
        bullet.move()

    for bullet in enemyBullets:
        bullet.move()

    gameDisplay.blit(gameDisplay, (0, 0))
    gameDisplay.fill(black)
    
    
    gameWidth = wallRight - wallLeft
    gameHeight = wallBottom - wallTop
    # Draw a white rectangle for the game border
    pygame.draw.rect(gameDisplay, white, (gameSideMargin, gameTopMargin, windowWidth - gameSideMargin * 2, windowHeight - gameBottomMargin - gameTopMargin))
    gameDisplay.blit(backgroundImg, (wallLeft, wallTop), (0,0,gameWidth, gameHeight))
    
    for enemy in enemies:
        enemy.moveOver()
        enemy.show()
    for bullet in bullets:
        bullet.show()
    for bullet in enemyBullets:
        bullet.show()
    
    player.show()

    titleText = titleFont.render('SPACE INVADERS', False, blue)
    scoreText = scoreFont.render('SCORE: ' + str(player.score), False, white)
    gameDisplay.blit(titleText, (windowWidth / 2 - titleText.get_width() / 2, 0))
    gameDisplay.blit(scoreText, (wallLeft, wallBottom + gameBorderWidth))
    pygame.display.update()
    clock.tick(gameSpeed)

showEndScreen = True
while showEndScreen:
    pass
pygame.quit()
    
