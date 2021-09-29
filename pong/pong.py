from graphics import *
from random import random, randrange
import time
import json
from sys import platform
import os
try:
    import winsound
except:
    pass


class Window(GraphWin):
    def __init__(self, title='myWindow', width=800, height=600, autoflush=True, bgColor='black'):
        super().__init__(title=title, width=width, height=height, autoflush=autoflush)
        self._height = height
        self._width = width
        self.setBackground(bgColor)
        self.bind_all("<KeyPress>",   self._onKeyPress)
        self.bind_all("<KeyRelease>", self._onKeyRelease)
        self.keys = dict()

        if platform == "linux" or platform == "linux2":
            self._os = "linux"

        elif platform == "darwin":
            self._os = "mac"

        elif platform == "win32" or platform == "cygwin":
            self._os = "windows"

    def _onKeyPress(self, event):
        self.keys[event.keysym] = True

    def _onKeyRelease(self, event):
        self.keys[event.keysym] = False

    def playSound(self, soundFile):
        if self._os == 'windows':
            winsound.PlaySound(soundFile, winsound.SND_ASYNC)
        elif self._os == 'linux':
            os.system(f'aplay {soundFile}&')
        elif self._os == 'mac':
            os.system(f'afplay {soundFile}&')

    def clear(self):
        for item in self.items[:]:
            item.undraw()
        self.update()


class UI:
    def __init__(self, window, pauseKey='Escape', upKey='Up', downKey='Down', confirmKey='x', p1Score=0, p2Score=0, toWin=5):
        self._win = window
        self._pauseKey = pauseKey
        self._upKey = upKey
        self._downKey = downKey
        self._confirmKey = confirmKey
        #self._p1 = p1
        #self._p2 = p2
        #self._ball = ball
        self._p1Score = p1Score
        self._p2Score = p2Score
        self._scoreBody = Text(Point(self._win._width/2, 10),
                               f'Player One: {p1Score}    Player Two: {p2Score}')
        self._gameMode = ['pvp', 'normal']
        self._toWin = toWin

    def createScore(self, color='white'):
        self._scoreBody.setTextColor(color)
        self._scoreBody.draw(self._win)

    def updateScore(self):
        ballX = self._ball.getCenterTuple()[0]
        if ballX >= self._win._width:
            self._p1Score += 1
            self._ball.changeDirection(resetSpeed=True)

        elif ballX <= 0:
            self._p2Score += 1
            self._ball.changeDirection(resetSpeed=True)

        self._scoreBody.setText(
            f'Player One: {self._p1Score}    Player Two: {self._p2Score}')

    def saveState(self):
        p1Start, p1End = self._p1.getCoords()
        p2Start, p2End = self._p2.getCoords()
        ballCenter = self._ball.getCenterTuple()
        saveFile = {'p1': (p1Start, p1End),
                    'p2': (p2Start, p2End),
                    'ball': (ballCenter, self._ball._dx, self._ball._dy),
                    'gamemode': self._gameMode
                    }
        if self._gameMode[1] == 'obstacle':
            obsStart, obsEnd = self._obstacle.getCoords()
            saveFile['obs'] = (obsStart, obsEnd)
        """
        idx = 0
        for item in self._win.items[:]:
            try:
                point = item.getCenter()
                x, y = point.getX(), point.getY()
                saveFile[idx] = [UI.extractClass(item), x, y]
                idx += 1
            except:
                continue
        """
        with open('saveState.json', 'w') as sFile:
            json.dump(saveFile, sFile)

    def drawGame(self, file='saveState.json'):
        self._win.clear()
        with open(file, 'r') as sFile:
            data = json.load(sFile)
        self._gameMode = data['gamemode']
        p1 = data["p1"]
        p2 = data["p2"]
        bl = data["ball"]
        try:
            obs = data["obs"]
            self._obstacle = Paddle(obs[0][0], obs[0][1], obs[1]
                                    [0], obs[1][1], self._win)
        except:
            pass
        self._p1 = Paddle(p1[0][0], p1[0][1], p1[1]
                            [0], p1[1][1], self._win)
        if self._gameMode[0] == 'pvp':
            self._p2 = Paddle(p2[0][0], p2[0][1], p2[1][0],
                              p2[1][1], self._win, upKey='Up', downKey='Down', rightKey='Right', leftKey='Left')
        else:
            self._p2 = IA(p2[0][0], p2[0][1], p2[1][0],
                          p2[1][1], self._win)
        self._ball = Ball(bl[0][0], bl[0][1], 5, self._win, 1)
        self._ball._dx, self._ball._dy = bl[1], bl[2]
        self.createScore()

    def drawNewGame(self):
        self._win.clear()
        self._p1Score = 0
        self._p2Score = 0
        self._p1 = Paddle(50, self._win._height/2-40, 60,
                          self._win._height/2+40, self._win)
        if self._gameMode[0] == 'pvp':
            self._p2 = Paddle(self._win._width-50, self._win._height/2-40, self._win._width-60,
                              self._win._height/2+40, self._win, upKey='Up', downKey='Down', rightKey='Right', leftKey='Left')
        else:
            self._p2 = IA(self._win._width-50, self._win._height/2-40, self._win._width-60,
                          self._win._height/2+40, self._win)

        if self._gameMode[1] == 'obstacle':
            obsP = randrange(15, self._win._height-15)
            obsHt = randrange(30, self._win._height/6)
            self._obstacle = Paddle(self._win._width/2 - 5, obsP, self._win._width/2 + 5,
                                    obsP + obsHt, self._win)
        else:
            self._obstacle = ''
        self._ball = Ball(self._win._width/2,
                          self._win._height/2, 5, self._win, 1)
        self.createScore()

    def runGame(self):
        if self._gameMode[0] == 'ia':
            self._p2.movement(5, self._ball)
            if self._gameMode[1] == 'free':
                self._p1.freeMovement(5)
            else:
                self._p1.movement(5)
        else:
            if self._gameMode[1] == 'free':
                self._p1.freeMovement(5)
                self._p2.freeMovement(5)
            else:
                self._p1.movement(5)
                self._p2.movement(5)

        self._ball.movement()
        if self._ball.checkCollision(self._p1) or self._ball.checkCollision(self._p2):
            self._ball.changeDirection()
        if self._gameMode[1] == 'obstacle':
            if self._ball.checkCollision(self._obstacle):
                self._ball.changeDirection()

        self.updateScore()

        if self._p1Score == self._toWin:
            self.winScreen(1)
        elif self._p2Score == self._toWin:
            self.winScreen(2)

        self._win.update()
        time.sleep(.01)

    def modeSelection(self, boxWidth=140, boxHeight=50):
        self._win.clear()
        action = 0
        gameName = Text(Point(self._win._width/2,
                              self._win._height/4), 'Pong')
        pvpText = Text(Point(self._win._width/2,
                             self._win._height/2 - boxHeight*3/4), 'PvP')
        pvpBox = Rectangle(Point(self._win._width/2 - boxWidth/2, self._win._height/2 - boxHeight/4),
                           Point(self._win._width/2 + boxWidth/2, self._win._height/2 - boxHeight*5/4))
        iaText = Text(Point(self._win._width/2,
                            self._win._height/2 + boxHeight*3/4), 'IA')
        iaBox = Rectangle(Point(self._win._width/2 - boxWidth/2, self._win._height/2 + boxHeight/4),
                          Point(self._win._width/2 + boxWidth/2, self._win._height/2 + boxHeight*5/4))
        items = [pvpBox, iaBox, pvpText, iaText]
        pvpBox.setFill('grey')
        iaBox.setFill('grey')
        gameName.setFace('courier')
        gameName.setSize(16)
        gameName.setTextColor('white')
        pvpText.setFace('courier')
        pvpText.setSize(16)
        iaText.setFace('courier')
        iaText.setSize(16)

        for item in items:
            item.draw(self._win)

        while not self._win.isClosed():
            if self._win.keys.get(self._upKey):
                action -= 1
                action = abs(action % 2)
                self._win.keys[self._upKey] = False

            if self._win.keys.get(self._downKey):
                action += 1
                action = abs(action % 2)
                self._win.keys[self._downKey] = False

            if action == 0:
                pvpBox.setFill('red')
                iaBox.setFill('grey')

            elif action == 1:
                pvpBox.setFill('grey')
                iaBox.setFill('red')

            if self._win.keys.get(self._confirmKey):
                self._win.keys[self._confirmKey] = False
                if action == 0:
                    self._gameMode[0] = 'pvp'
                    break
                elif action == 1:
                    self._gameMode[0] = 'ia'
                    break
        for item in items:
            item.undraw()
        self._win.update()

        normalText = Text(Point(self._win._width/2,
                                self._win._height/2 - boxHeight*3/4), 'Normal')
        normalBox = Rectangle(Point(self._win._width/2 - boxWidth/2, self._win._height/2 - boxHeight/4),
                              Point(self._win._width/2 + boxWidth/2, self._win._height/2 - boxHeight*5/4))
        obstacleText = Text(Point(self._win._width/2,
                                  self._win._height/2 + boxHeight*3/4), 'Obstacle')
        obstacleBox = Rectangle(Point(self._win._width/2 - boxWidth/2, self._win._height/2 + boxHeight/4),
                                Point(self._win._width/2 + boxWidth/2, self._win._height/2 + boxHeight*5/4))
        freeText = Text(Point(self._win._width/2,
                              self._win._height/2 + boxHeight*9/4), 'Free Mov.')
        freeBox = Rectangle(Point(self._win._width/2 - boxWidth/2, self._win._height/2 + boxHeight*7/4),
                            Point(self._win._width/2 + boxWidth/2, self._win._height/2 + boxHeight*11/4))
        items = [normalBox, obstacleBox, freeBox,
                 gameName, normalText, obstacleText, freeText]
        normalBox.setFill('grey')
        obstacleBox.setFill('grey')
        freeBox.setFill('grey')
        normalText.setFace('courier')
        normalText.setSize(16)
        obstacleText.setFace('courier')
        obstacleText.setSize(16)
        freeText.setFace('courier')
        freeText.setSize(16)

        for item in items:
            item.draw(self._win)

        while not self._win.isClosed():
            if self._win.keys.get(self._upKey):
                action -= 1
                action = abs(action % 3)
                self._win.keys[self._upKey] = False

            if self._win.keys.get(self._downKey):
                action += 1
                action = abs(action % 3)
                self._win.keys[self._downKey] = False

            if action == 0:
                normalBox.setFill('red')
                obstacleBox.setFill('grey')
                freeBox.setFill('grey')

            elif action == 1:
                normalBox.setFill('grey')
                obstacleBox.setFill('red')
                freeBox.setFill('grey')

            elif action == 2:
                normalBox.setFill('grey')
                obstacleBox.setFill('grey')
                freeBox.setFill('red')

            if self._win.keys.get(self._confirmKey):
                self._win.keys[self._confirmKey] = False
                if action == 0:
                    self._gameMode[1] = 'normal'
                    break
                elif action == 1:
                    self._gameMode[1] = 'obstacle'
                    break
                else:
                    self._gameMode[1] = 'free'
                    break
        for item in items:
            item.undraw()
        self._win.update()

    def menuScreen(self, boxWidth=140, boxHeight=50):
        self._win.clear()
        action = 0
        gameName = Text(Point(self._win._width/2,
                              self._win._height/4), 'Pong')
        continueText = Text(Point(self._win._width/2,
                                  self._win._height/2 - boxHeight*3/4), 'Continue')
        continueBox = Rectangle(Point(self._win._width/2 - boxWidth/2, self._win._height/2 - boxHeight/4),
                                Point(self._win._width/2 + boxWidth/2, self._win._height/2 - boxHeight*5/4))
        newGameText = Text(Point(self._win._width/2,
                                 self._win._height/2 + boxHeight*3/4), 'New Game')
        newGameBox = Rectangle(Point(self._win._width/2 - boxWidth/2, self._win._height/2 + boxHeight/4),
                               Point(self._win._width/2 + boxWidth/2, self._win._height/2 + boxHeight*5/4))
        configText = Text(Point(self._win._width/2,
                                self._win._height/2 + boxHeight*9/4), 'Settings')
        configBox = Rectangle(Point(self._win._width/2 - boxWidth/2, self._win._height/2 + boxHeight*7/4),
                              Point(self._win._width/2 + boxWidth/2, self._win._height/2 + boxHeight*11/4))
        items = [continueBox, newGameBox, configBox,
                 gameName, continueText, newGameText, configText]
        continueBox.setFill('grey')
        newGameBox.setFill('grey')
        configBox.setFill('grey')
        gameName.setFace('courier')
        gameName.setSize(16)
        gameName.setTextColor('white')
        continueText.setFace('courier')
        continueText.setSize(16)
        newGameText.setFace('courier')
        newGameText.setSize(16)
        configText.setFace('courier')
        configText.setSize(16)
        if not os.path.isfile('saveState.json'):
            continueText.setTextColor('white')

        for item in items:
            item.draw(self._win)

        while not self._win.isClosed():
            if self._win.keys.get(self._upKey):
                action -= 1
                action = abs(action % 3)
                self._win.keys[self._upKey] = False

            if self._win.keys.get(self._downKey):
                action += 1
                action = abs(action % 3)
                self._win.keys[self._downKey] = False

            if action == 0:
                continueBox.setFill('red')
                newGameBox.setFill('grey')
                configBox.setFill('grey')

            elif action == 1:
                continueBox.setFill('grey')
                newGameBox.setFill('red')
                configBox.setFill('grey')

            elif action == 2:
                continueBox.setFill('grey')
                newGameBox.setFill('grey')
                configBox.setFill('red')

            if self._win.keys.get(self._confirmKey):
                self._win.keys[self._confirmKey] = False
                if action == 0 and os.path.isfile('saveState.json'):
                    try:
                        self.drawGame()
                        break
                    except:
                        pass
                elif action == 1:
                    self.modeSelection()
                    self.drawNewGame()
                    break
                else:
                    self.settingsScreen()
                    break

            self._win.update()
        for item in items:
            item.undraw()

    def pauseScreen(self, boxWidth=140, boxHeight=50):
        self._win.clear()
        action = 0
        pauseText = Text(Point(self._win._width/2,
                               self._win._height/4), 'Game paused')
        resumeText = Text(Point(self._win._width/2,
                                self._win._height/2 - boxHeight*3/4), 'Resume')
        resumeBox = Rectangle(Point(self._win._width/2 - boxWidth/2, self._win._height/2 - boxHeight/4),
                              Point(self._win._width/2 + boxWidth/2, self._win._height/2 - boxHeight*5/4))
        menuText = Text(Point(self._win._width/2,
                              self._win._height/2 + boxHeight*3/4), 'Menu')
        menuBox = Rectangle(Point(self._win._width/2 - boxWidth/2, self._win._height/2 + boxHeight/4),
                            Point(self._win._width/2 + boxWidth/2, self._win._height/2 + boxHeight*5/4))
        items = [menuBox, resumeBox, pauseText, menuText, resumeText]
        resumeBox.setFill('grey')
        menuBox.setFill('grey')
        pauseText.setFace('courier')
        pauseText.setSize(16)
        pauseText.setTextColor('white')
        menuText.setFace('courier')
        menuText.setSize(16)
        resumeText.setFace('courier')
        resumeText.setSize(16)

        for item in items:
            item.draw(self._win)

        while not self._win.isClosed():
            if self._win.keys.get(self._upKey):
                action -= 1
                action = abs(action % 2)
                self._win.keys[self._upKey] = False

            if self._win.keys.get(self._downKey):
                action += 1
                action = abs(action % 2)
                self._win.keys[self._downKey] = False

            if action == 1:
                resumeBox.setFill('grey')
                menuBox.setFill('red')

            else:
                resumeBox.setFill('red')
                menuBox.setFill('grey')

            if self._win.keys.get(self._confirmKey):
                self._win.keys[self._confirmKey] = False
                break

            if self._win.keys.get(self._pauseKey):
                self._win.keys[self._pauseKey] = False
                break

            self._win.update()
        for item in items:
            item.undraw()

        if action == 1:
            self.menuScreen()

        else:
            self.drawGame()

    def winScreen(self, winner):
        try:
            os.remove('saveState.json')
        except:
            pass
        self._win.clear()
        winText = Text(Point(self._win._width / 2, self._win._height / 2),
                       f'Player {winner} wins!!!\nPress "{self._confirmKey}" to continue.')
        winText.setFace('courier')
        winText.setSize(16)
        winText.setTextColor('white')
        winText.draw(self._win)

        while not self._win.isClosed():
            if self._win.keys.get(self._confirmKey):
                self._win.keys[self._confirmKey] = False
                break
            self._win.update()

        self.menuScreen()

    def settingsScreen(self):
        self._win.clear()
        setText = Text(Point(self._win._width / 2, self._win._height / 2),
                       f'To be implemented...\nPress "{self._confirmKey}" to return to menu.')
        setText.setFace('courier')
        setText.setSize(16)
        setText.setTextColor('white')
        setText.draw(self._win)
        while not self._win.isClosed():
            if self._win.keys.get(self._confirmKey):
                self._win.keys[self._confirmKey] = False
                break
            self._win.update()
        self.menuScreen()

    def pause(self):
        if self._win.keys.get(self._pauseKey):
            self._win.keys[self._pauseKey] = False
            self.saveState()
            return True

    @staticmethod
    def extractClass(className):
        return(type(className).__name__)


class Paddle:
    def __init__(self, startX, startY, endX, endY, window, upKey='w', downKey='s', rightKey='d', leftKey='a', color='white'):
        self._body = Rectangle(Point(startX, startY), Point(endX, endY))
        self._height = abs(startY-endY)
        self._width = abs(startX-endX)
        self._win = window
        self._upKey = upKey
        self._downKey = downKey
        self._rightKey = rightKey
        self._leftKey = leftKey
        self._color = color
        self.create()

    def create(self):
        self._body.setFill(self._color)
        self._body.draw(self._win)

    def getCenterTuple(self):
        x = self._body.getCenter().getX()
        y = self._body.getCenter().getY()
        return x, y

    def getHeightPoints(self):
        y = self.getCenterTuple()[1]
        y1, y2 = y-self._height/2, y+self._height/2
        return y1, y2

    def getWidthPoints(self):
        x = self.getCenterTuple()[0]
        x1, x2 = x-self._width/2, x+self._width/2
        return x1, x2

    def getCoords(self):
        x1, x2 = self.getWidthPoints()
        y1, y2 = self.getHeightPoints()
        return (x1, y1), (x2, y2)

    def getUpKey(self, key):
        self._upKey = key

    def getDownKey(self, key):
        self._downKey = key

    def setPosition(self, x, y):
        currentX, currentY = self.getCenterTuple()
        self._body.move(x-currentX, y-currentY)

    def movement(self, step):
        y1, y2 = self.getHeightPoints()

        if self._win.keys.get(self._upKey) and y1 > 0:
            self._body.move(0, -step)

        if self._win.keys.get(self._downKey) and y2 < self._win._height:
            self._body.move(0, step)

    def freeMovement(self, step):
        y1, y2 = self.getHeightPoints()
        x1, x2 = self.getWidthPoints()

        if self._win.keys.get(self._upKey) and y1 > 0:
            self._body.move(0, -step)

        if self._win.keys.get(self._downKey) and y2 < self._win._height:
            self._body.move(0, step)

        if self._win.keys.get(self._leftKey) and x1 > 0:
            self._body.move(-step/2, 0)

        if self._win.keys.get(self._rightKey) and x2 < self._win._width:
            self._body.move(step/2, 0)


class IA(Paddle):
    def __init__(self, startX, startY, endX, endY, window):
        super().__init__(startX=startX, startY=startY, endX=endX,
                         endY=endY, window=window, upKey='', downKey='')

    def movement(self, step, ball):
        pY1, pY2 = self.getHeightPoints()
        paddleY = self.getCenterTuple()[1]
        ballY = ball.getCenterTuple()[1]

        if ball._dx > 0 and (ballY < pY1 or ballY > pY2):

            if paddleY >= ballY:
                self._body.move(0, -step)

            elif paddleY < ballY:
                self._body.move(0, step)

            else:
                self._body.move(0, -step)


class Ball:
    def __init__(self, startX, startY, radius, window, speed=1, color='white'):
        self._body = Circle(Point(startX, startY), radius)
        self._radius = radius
        self._win = window
        self._initialSpeed = speed
        self._dx = speed
        self._dy = speed
        self._color = color
        self.create()

    def create(self):
        self._body.setFill(self._color)
        self._body.draw(self._win)

    def getCenterTuple(self):
        x = self._body.getCenter().getX()
        y = self._body.getCenter().getY()
        return x, y

    def setPosition(self, x, y):
        currentX, currentY = self.getCenterTuple()
        self._body.move(x-currentX, y-currentY)

    def checkCollision(self, paddle):
        minX, maxX = paddle.getWidthPoints()
        minY, maxY = paddle.getHeightPoints()
        ballX, ballY = self.getCenterTuple()
        direction = 1 if self._dx > 0 else -1
        ballX += self._radius*direction
        if ballY >= minY - self._radius and ballY <= maxY + self._radius and ballX >= minX and ballX <= maxX:
            self._win.playSound('sfx/paddleHit.wav')
            return True
        return False

    def movement(self):
        x, y = self.getCenterTuple()
        if y > self._win._height-self._radius or y < self._radius:
            self._win.playSound('sfx/wallHit.wav')
            self._dy *= -1
        if x >= self._win._width or x <= 0:
            self._win.playSound('sfx/score.wav')
            self.setPosition(self._win._width/2, self._win._height/2)
        else:
            self._body.move(self._dx, self._dy)

    def changeDirection(self, resetSpeed=False):
        self._dx *= -1
        if resetSpeed:
            self._dy = self._initialSpeed
            if self._dx > 0:
                self._dx = -self._initialSpeed
            else:
                self._dx = self._initialSpeed
        else:
            self._dy += random()*(self._dy/abs(self._dy))
            if self._dx < 3:
                if self._dx < 0:
                    self._dx -= 0.3
                else:
                    self._dx += 0.3


def main():
    height, width = 600, 880
    win = Window("Pyng", width, height)
    ui = UI(win)
    ui.createScore()
    ui.menuScreen()
    while not win.isClosed():
        ui.runGame()
        if ui.pause():
            ui.pauseScreen()


if __name__ == '__main__':
    main()
