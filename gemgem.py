
import random, time, pygame, sys, copy
from pygame.locals import *

FPS = 30 # frames per second to update the screen
WINDOWWIDTH = 600  # width
WINDOWHEIGHT = 600 # height

BOARDWIDTH = 8 # columns in the board
BOARDHEIGHT = 8 #rows in the board
GEMIMAGESIZE = 64 # width and height of each space in pixels

NUMGEMIMAGES = 7
assert NUMGEMIMAGES >= 5 #min 5 types of gem

NUMMATCHSOUNDS = 6

MOVERATE = 25 #objectspeed
DEDUCTSPEED = 0.8 # reduces 1 point every DEDUCTSPEED seconds in score.

#             R    G    B  (predefined values)
PURPLE    = (255,   0, 255)
LIGHTBLUE = (170, 190, 255)
BLUE      = (  0,   0, 255)
RED       = (255, 100, 100)
BLACK     = (  0,   0,   0)
BROWN     = ( 85,  65,   0)
HIGHLIGHTCOLOR = PURPLE
BGCOLOR = LIGHTBLUE
GRIDCOLOR = PURPLE
GAMEOVERCOLOR = RED
GAMEOVERBGCOLOR = BLACK
SCORECOLOR = BROWN

# The amount of space to the sides of the board to the edge of the window
# is used several times, so calculate it once here and store in variables.
XMARGIN = int((WINDOWWIDTH - GEMIMAGESIZE * BOARDWIDTH) / 2)
YMARGIN = int((WINDOWHEIGHT - GEMIMAGESIZE * BOARDHEIGHT) / 2)

# constants for direction values
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

EMPTY_SPACE = -1 # an arbitrary, nonpositive value
ROWABOVEBOARD = 'row above board' # an arbitrary, noninteger value

def main():
    global FPSCLOCK, DISPLAYSURF, GEMIMAGES, GAMESOUNDS, BASICFONT, BOARDRECTS

    # Initial set up.
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('GemDazzle')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 36)

    # Load the images
    GEMIMAGES = []
    for i in range(1, NUMGEMIMAGES+1):
        gemImage = pygame.image.load('gem%s.png' % i)
        if gemImage.get_size() != (GEMIMAGESIZE, GEMIMAGESIZE):
            gemImage = pygame.transform.smoothscale(gemImage, (GEMIMAGESIZE, GEMIMAGESIZE))
        GEMIMAGES.append(gemImage)

    # Load the sounds.
    GAMESOUNDS = {}
    GAMESOUNDS['bad swap'] = pygame.mixer.Sound('badswap.wav')
    GAMESOUNDS['match'] = []
    for i in range(NUMMATCHSOUNDS):
        GAMESOUNDS['match'].append(pygame.mixer.Sound('match%s.wav' % i))


    BOARDRECTS = []
    for x in range(BOARDWIDTH):
        BOARDRECTS.append([])
        for y in range(BOARDHEIGHT):
            r = pygame.Rect((XMARGIN + (x * GEMIMAGESIZE),
                             YMARGIN + (y * GEMIMAGESIZE),
                             GEMIMAGESIZE,
                             GEMIMAGESIZE))
            BOARDRECTS[x].append(r)

    while True:
        runGame()


def runGame():
    gameBoard = getBlankBoard()
    score = 0
    fillBoardAndAnimate(gameBoard, [], score) # Drop the initial gems.

    # initialize variables
    firstSelectedGem = None
    lastMouseDownX = None
    lastMouseDownY = None
    gameIsOver = False
    lastScoreDeduction = time.time()
    clickContinueTextSurf = None

    while True: # main game loop
        clickedSpace = None
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP and event.key == K_BACKSPACE:
                return # start a new game

            elif event.type == MOUSEBUTTONUP:
                if gameIsOver:
                    return # after games ends, click to start a new game

                if event.pos == (lastMouseDownX, lastMouseDownY):
                    #mouse click position
                    clickedSpace = checkForGemClick(event.pos)
                else:
                    #end of a mouse drag
                    firstSelectedGem = checkForGemClick((lastMouseDownX, lastMouseDownY))
                    clickedSpace = checkForGemClick(event.pos)
                    if not firstSelectedGem or not clickedSpace:
                        # if not part of a valid drag, deselect both
                        firstSelectedGem = None
                        clickedSpace = None
            elif event.type == MOUSEBUTTONDOWN:
                # this is the start of a mouse click or mouse drag
                lastMouseDownX, lastMouseDownY = event.pos

        if clickedSpace and not firstSelectedGem:
            #first gem clicked on.
            firstSelectedGem = clickedSpace
        elif clickedSpace and firstSelectedGem:
            #Swap the gems.
            firstSwappingGem, secondSwappingGem = getSwappingGems(gameBoard, firstSelectedGem, clickedSpace)
            if firstSwappingGem == None and secondSwappingGem == None:
                # If both are None, then the gems were not adjacent
                firstSelectedGem = None # deselect the first gem
                continue

            #swap animation on the screen.
            boardCopy = getBoardCopyMinusGems(gameBoard, (firstSwappingGem, secondSwappingGem))
            animateMovingGems(boardCopy, [firstSwappingGem, secondSwappingGem], [], score)

            # Swap the gems in the board data structure.
            gameBoard[firstSwappingGem['x']][firstSwappingGem['y']] = secondSwappingGem['imageNum']
            gameBoard[secondSwappingGem['x']][secondSwappingGem['y']] = firstSwappingGem['imageNum']

            #check for a matching move.
            matchedGems = findMatchingGems(gameBoard)
            if matchedGems == []:
                # Was not a matching move; swap the gems back
                GAMESOUNDS['bad swap'].play()
                animateMovingGems(boardCopy, [firstSwappingGem, secondSwappingGem], [], score)
                gameBoard[firstSwappingGem['x']][firstSwappingGem['y']] = firstSwappingGem['imageNum']
                gameBoard[secondSwappingGem['x']][secondSwappingGem['y']] = secondSwappingGem['imageNum']
            else:
                # This was a matching move.
                scoreAdd = 0
                while matchedGems != []:
                    points = []
                    for gemSet in matchedGems:
                        scoreAdd += (10 + (len(gemSet) - 3) * 10)
                        for gem in gemSet:
                            gameBoard[gem[0]][gem[1]] = EMPTY_SPACE
                        points.append({'points': scoreAdd,
                                       'x': gem[0] * GEMIMAGESIZE + XMARGIN,
                                       'y': gem[1] * GEMIMAGESIZE + YMARGIN})
                    random.choice(GAMESOUNDS['match']).play()
                    score += scoreAdd

                    # Drop the new gems.
                    fillBoardAndAnimate(gameBoard, points, score)

                    # Check for any new matches.
                    matchedGems = findMatchingGems(gameBoard)
            firstSelectedGem = None

            if not canMakeMove(gameBoard):
                gameIsOver = True

        # Draw the board.
        DISPLAYSURF.fill(BGCOLOR)
        drawBoard(gameBoard)
        if firstSelectedGem != None:
            highlightSpace(firstSelectedGem['x'], firstSelectedGem['y'])
        if gameIsOver:
            if clickContinueTextSurf == None:
                clickContinueTextSurf = BASICFONT.render('Final Score: %s (Click to continue)' % (score), 1, GAMEOVERCOLOR, GAMEOVERBGCOLOR)
                clickContinueTextRect = clickContinueTextSurf.get_rect()
                clickContinueTextRect.center = int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2)
            DISPLAYSURF.blit(clickContinueTextSurf, clickContinueTextRect)
        elif score > 0 and time.time() - lastScoreDeduction > DEDUCTSPEED:
            # score drops over time
            score -= 1
            lastScoreDeduction = time.time()
        drawScore(score)
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def getSwappingGems(board, firstXY, secondXY):
    firstGem = {'imageNum': board[firstXY['x']][firstXY['y']],
                'x': firstXY['x'],
                'y': firstXY['y']}
    secondGem = {'imageNum': board[secondXY['x']][secondXY['y']],
                 'x': secondXY['x'],
                 'y': secondXY['y']}
    highlightedGem = None
    if firstGem['x'] == secondGem['x'] + 1 and firstGem['y'] == secondGem['y']:
        firstGem['direction'] = LEFT
        secondGem['direction'] = RIGHT
    elif firstGem['x'] == secondGem['x'] - 1 and firstGem['y'] == secondGem['y']:
        firstGem['direction'] = RIGHT
        secondGem['direction'] = LEFT
    elif firstGem['y'] == secondGem['y'] + 1 and firstGem['x'] == secondGem['x']:
        firstGem['direction'] = UP
        secondGem['direction'] = DOWN
    elif firstGem['y'] == secondGem['y'] - 1 and firstGem['x'] == secondGem['x']:
        firstGem['direction'] = DOWN
        secondGem['direction'] = UP
    else:
        # These gems are not adjacent and can't be swapped.
        return None, None
    return firstGem, secondGem


def getBlankBoard():
    # Create and return a blank board data structure.
    board = []
    for x in range(BOARDWIDTH):
        board.append([EMPTY_SPACE] * BOARDHEIGHT)
    return board


def canMakeMove(board):
    oneOffPatterns = (((0,1), (1,0), (2,0)),
                      ((0,1), (1,1), (2,0)),
                      ((0,0), (1,1), (2,0)),
                      ((0,1), (1,0), (2,1)),
                      ((0,0), (1,0), (2,1)),
                      ((0,0), (1,1), (2,1)),
                      ((0,0), (0,2), (0,3)),
                      ((0,0), (0,1), (0,3)))

    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            for pat in oneOffPatterns:
                # check each possible pattern of "match in next move" to
                # see if a possible move can be made.
                if (getGemAt(board, x+pat[0][0], y+pat[0][1]) == \
                    getGemAt(board, x+pat[1][0], y+pat[1][1]) == \
                    getGemAt(board, x+pat[2][0], y+pat[2][1]) != None) or \
                   (getGemAt(board, x+pat[0][1], y+pat[0][0]) == \
                    getGemAt(board, x+pat[1][1], y+pat[1][0]) == \
                    getGemAt(board, x+pat[2][1], y+pat[2][0]) != None):
                    return True # return True the first time you find a pattern
    return False


def drawMovingGem(gem, progress):
    # Draw a gem sliding in the direction from 0 to 100.
    movex = 0
    movey = 0
    progress *= 0.01

    if gem['direction'] == UP:
        movey = -int(progress * GEMIMAGESIZE)
    elif gem['direction'] == DOWN:
        movey = int(progress * GEMIMAGESIZE)
    elif gem['direction'] == RIGHT:
        movex = int(progress * GEMIMAGESIZE)
    elif gem['direction'] == LEFT:
        movex = -int(progress * GEMIMAGESIZE)

    basex = gem['x']
    basey = gem['y']
    if basey == ROWABOVEBOARD:
        basey = -1

    pixelx = XMARGIN + (basex * GEMIMAGESIZE)
    pixely = YMARGIN + (basey * GEMIMAGESIZE)
    r = pygame.Rect( (pixelx + movex, pixely + movey, GEMIMAGESIZE, GEMIMAGESIZE) )
    DISPLAYSURF.blit(GEMIMAGES[gem['imageNum']], r)


def pullDownAllGems(board):
    # pulls down gems on the board to the bottom to fill in any gaps
    for x in range(BOARDWIDTH):
        gemsInColumn = []
        for y in range(BOARDHEIGHT):
            if board[x][y] != EMPTY_SPACE:
                gemsInColumn.append(board[x][y])
        board[x] = ([EMPTY_SPACE] * (BOARDHEIGHT - len(gemsInColumn))) + gemsInColumn


def getGemAt(board, x, y):
    if x < 0 or y < 0 or x >= BOARDWIDTH or y >= BOARDHEIGHT:
        return None
    else:
        return board[x][y]


def getDropSlots(board):
    #fills the empty gap with gems.
    boardCopy = copy.deepcopy(board)
    pullDownAllGems(boardCopy)

    dropSlots = []
    for i in range(BOARDWIDTH):
        dropSlots.append([])

    # count the number of empty spaces in each column on the board
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT-1, -1, -1): # start from bottom, going up
            if boardCopy[x][y] == EMPTY_SPACE:
                possibleGems = list(range(len(GEMIMAGES)))
                for offsetX, offsetY in ((0, -1), (1, 0), (0, 1), (-1, 0)):
                    neighborGem = getGemAt(boardCopy, x + offsetX, y + offsetY)
                    if neighborGem != None and neighborGem in possibleGems:
                        possibleGems.remove(neighborGem)

                newGem = random.choice(possibleGems)
                boardCopy[x][y] = newGem
                dropSlots[x].append(newGem)
    return dropSlots


def findMatchingGems(board):
    gemsToRemove = [] # a list of lists of gems in matching triplets that should be removed
    boardCopy = copy.deepcopy(board)

    # loop through each space, checking for 3 adjacent identical gems
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            # look for horizontal matches
            if getGemAt(boardCopy, x, y) == getGemAt(boardCopy, x + 1, y) == getGemAt(boardCopy, x + 2, y) and getGemAt(boardCopy, x, y) != EMPTY_SPACE:
                targetGem = boardCopy[x][y]
                offset = 0
                removeSet = []
                while getGemAt(boardCopy, x + offset, y) == targetGem:
                    # keep checking if there's more than 3 gems in a row
                    removeSet.append((x + offset, y))
                    boardCopy[x + offset][y] = EMPTY_SPACE
                    offset += 1
                gemsToRemove.append(removeSet)

            # look for vertical matches
            if getGemAt(boardCopy, x, y) == getGemAt(boardCopy, x, y + 1) == getGemAt(boardCopy, x, y + 2) and getGemAt(boardCopy, x, y) != EMPTY_SPACE:
                targetGem = boardCopy[x][y]
                offset = 0
                removeSet = []
                while getGemAt(boardCopy, x, y + offset) == targetGem:
                    # keep checking, in case there's more than 3 gems in a row(special case)
                    removeSet.append((x, y + offset))
                    boardCopy[x][y + offset] = EMPTY_SPACE
                    offset += 1
                gemsToRemove.append(removeSet)

    return gemsToRemove


def highlightSpace(x, y):
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, BOARDRECTS[x][y], 4)


def getDroppingGems(board):
    # Find all the gems that have an empty space below them
    boardCopy = copy.deepcopy(board)
    droppingGems = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT - 2, -1, -1):
            if boardCopy[x][y + 1] == EMPTY_SPACE and boardCopy[x][y] != EMPTY_SPACE:
                # This space drops if not empty but the space below it is
                droppingGems.append( {'imageNum': boardCopy[x][y], 'x': x, 'y': y, 'direction': DOWN} )
                boardCopy[x][y] = EMPTY_SPACE
    return droppingGems


def animateMovingGems(board, gems, pointsText, score):
    # pointsText is a dictionary with keys 'x', 'y', and 'points'
    progress = 0 # progress at 0 represents beginning, 100 means finished.
    while progress < 100: # animation loop
        DISPLAYSURF.fill(BGCOLOR)
        drawBoard(board)
        for gem in gems: # Draw each gem.
            drawMovingGem(gem, progress)
        drawScore(score)
        for pointText in pointsText:
            pointsSurf = BASICFONT.render(str(pointText['points']), 1, SCORECOLOR)
            pointsRect = pointsSurf.get_rect()
            pointsRect.center = (pointText['x'], pointText['y'])
            DISPLAYSURF.blit(pointsSurf, pointsRect)

        pygame.display.update()
        FPSCLOCK.tick(FPS)
        progress += MOVERATE # progress the animation a little bit more for the next frame


def moveGems(board, movingGems):
    # movingGems is a list of dicts with keys x, y, direction, imageNum
    for gem in movingGems:
        if gem['y'] != ROWABOVEBOARD:
            board[gem['x']][gem['y']] = EMPTY_SPACE
            movex = 0
            movey = 0
            if gem['direction'] == LEFT:
                movex = -1
            elif gem['direction'] == RIGHT:
                movex = 1
            elif gem['direction'] == DOWN:
                movey = 1
            elif gem['direction'] == UP:
                movey = -1
            board[gem['x'] + movex][gem['y'] + movey] = gem['imageNum']
        else:
            # gem is located above the board (where new gems come from)
            board[gem['x']][0] = gem['imageNum'] # move to top row


def fillBoardAndAnimate(board, points, score):
    dropSlots = getDropSlots(board)
    while dropSlots != [[]] * BOARDWIDTH:
        # do the dropping animation as long as there are more gems to drop
        movingGems = getDroppingGems(board)
        for x in range(len(dropSlots)):
            if len(dropSlots[x]) != 0:
                # cause the lowest gem in each slot to begin moving in the DOWN direction
                movingGems.append({'imageNum': dropSlots[x][0], 'x': x, 'y': ROWABOVEBOARD, 'direction': DOWN})

        boardCopy = getBoardCopyMinusGems(board, movingGems)
        animateMovingGems(boardCopy, movingGems, points, score)
        moveGems(board, movingGems)

        for x in range(len(dropSlots)):
            if len(dropSlots[x]) == 0:
                continue
            board[x][0] = dropSlots[x][0]
            del dropSlots[x][0]


def checkForGemClick(pos):
    # See if the mouse click was on the board
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if BOARDRECTS[x][y].collidepoint(pos[0], pos[1]):
                return {'x': x, 'y': y}
    return None # Click was not on the board.


def drawBoard(board):
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            pygame.draw.rect(DISPLAYSURF, GRIDCOLOR, BOARDRECTS[x][y], 1)
            gemToDraw = board[x][y]
            if gemToDraw != EMPTY_SPACE:
                DISPLAYSURF.blit(GEMIMAGES[gemToDraw], BOARDRECTS[x][y])


def getBoardCopyMinusGems(board, gems):
    # Creates and returns a copy of the passed board data structure,
    # Gems is a list of dicts, with keys x, y, direction, imageNum

    boardCopy = copy.deepcopy(board)

    # Remove some of the gems from this board data structure copy.
    for gem in gems:
        if gem['y'] != ROWABOVEBOARD:
            boardCopy[gem['x']][gem['y']] = EMPTY_SPACE
    return boardCopy


def drawScore(score):
    scoreImg = BASICFONT.render(str(score), 1, SCORECOLOR)
    scoreRect = scoreImg.get_rect()
    scoreRect.bottomleft = (10, WINDOWHEIGHT - 6)
    DISPLAYSURF.blit(scoreImg, scoreRect)



if __name__ == '__main__':
    main()
