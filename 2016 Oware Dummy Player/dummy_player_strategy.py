'''
This module handle the game strategy (only) of a player.

Created on 1 July 2016

@author: Lilian
'''

import const
import random

SHOW_GUI = False
SHOW_OUTPUT = False

# The variable representing our game board,
myBoard = None

# The variable representing our game board,
opponentBoard = None

# Enter your own player name
player_name = "Dumber" 

# Enter your own player description, e.g. what kind of strategy has been used.
player_description = "Moves is the first of all available moves."

mySeeds = 0
opponentSeeds = 0
            

def chooseMove(playerBoard, oppBoard, playerSeeds, oppSeeds):
    """
    Should Decide what move to make based on current state of opponent's board and return it 
    # currently Completely random strategy,
    # Knowledge about opponent's board is completely ignored (hence the name of the player),
    # You definitely want to change that.
    """
    
    if SHOW_OUTPUT: print(displayBoard(playerBoard, oppBoard, playerSeeds, oppSeeds))
    
    moves = getValidMoves(playerBoard, oppBoard)
    random.shuffle(moves)
    return moves[0]
    
def getOpponentMove(move, playerBoard, oppBoard, playerSeeds, oppSeeds):
    """ 
    You might like to keep track of where your opponent
    has missed/hit, but here we just acknowledge it
    """
    pass
   
def newRound():
    """
    This method is called when a new round is starting (new game with same player). This gives you the 
    ability to update your strategy.
    Currently does nothing.
    """
    pass

def newPlayer():
    """
    This method is used for backward compatibility. It will not be used during the competition. 
    You should ignore this function.
    """
    pass

def displayBoard(myBoard, opponentBoard, mySeeds, opponentSeeds):
    output = "     Opponent:" + str(opponentSeeds) + "\n"
    output += ("+" + "-" * 2) * const.GRID_SIZE +"+\n"
    for i in range(const.GRID_SIZE -1 , -1, -1):
        output += str.format("|%2d"%(i))
    output += "|\n"
    output += ("+" + "-" * 2) * const.GRID_SIZE +"+\n"
    for i in range(const.GRID_SIZE - 1, -1, -1):
        if opponentBoard[i] == 0:
            output += str.format("|%2s"%(""))
        else:            
            output += str.format("|%2d"%(opponentBoard[i]))
            
    output += "|\n"
    output += ("+" + "=" * 2) * const.GRID_SIZE +"+\n"
    for i in range(const.GRID_SIZE):
        if myBoard[i] == 0:
            output += str.format("|%2s"%(""))
        else:            
            output += str.format("|%2d"%(myBoard[i]))
    output += "|\n"
    output += ("+" + "-" * 2) * const.GRID_SIZE +"+\n"
    for i in range(const.GRID_SIZE):
        output += str.format("|%2d"%(i))    
    output += "|\n"
    output += ("+" + "-" * 2) * const.GRID_SIZE +"+\n"
    output += "       Me:" + str(mySeeds) + "\n"
    
    return output
    
def sowSeeds(playerBoard, opponentBoard, move):
    board = playerBoard
    houseIndex = move + 1
    beans = board[move]
    board[move] = 0
    beansDropped = 0
    while beans > 1:
        if houseIndex >= const.GRID_SIZE:
            if board is opponentBoard:
                board = playerBoard
            else:
                board = opponentBoard
                
            houseIndex -= const.GRID_SIZE
            
        board[houseIndex] += 1
        beans -= 1
        beansDropped += 1
        if beansDropped % (2 * const.GRID_SIZE -1) == 0:
            houseIndex += 2 # skip the initial house where the beans have been picked up
        else:
            houseIndex += 1
        
        
    # BEGIN adds the last bean in hand    
    if houseIndex >= const.GRID_SIZE:
        if board is opponentBoard:
            board = playerBoard
        else:
            board = opponentBoard
        houseIndex -= const.GRID_SIZE
    board[houseIndex] += 1 
    # END adds the last bean in hand
    
    return board, houseIndex
    
    
        
def captureSeeds(playerBoard, opponentBoard, lastSeedHouse, lastSeedBoard):  
    board = lastSeedBoard  
    houseIndex = lastSeedHouse    
    beansCaptured = 0
    if board is playerBoard: # a player cannot capture is own house
        return beansCaptured
    
    if 2 <= board[houseIndex] <= 3: # capture seeds
        beansCaptured = board[houseIndex]
        board[houseIndex] = 0
        keepCollecting = True
        while keepCollecting:
            houseIndex -= 1
            if houseIndex < 0:
                if board is opponentBoard:
                    board = playerBoard
                else:
                    board = opponentBoard
                    
                houseIndex = const.GRID_SIZE - 1
            
            if board is playerBoard: # a player cannot capture is own house
                break
            
            if 2 <= board[houseIndex] <= 3:
                beansCaptured += board[houseIndex]
                board[houseIndex] = 0
            else:
                break
                            
    return beansCaptured
    
            
def evaluateMove(playerBoard, opponentBoard, move):
    
    copyOfPlayerBoard = list(playerBoard)
    copyOfOpponentBoard = list(opponentBoard)
    
    lastSeedBoard, lastSeedHouse = sowSeeds(copyOfPlayerBoard, copyOfOpponentBoard, move)
    beansCaptured = captureSeeds(copyOfPlayerBoard, copyOfOpponentBoard, lastSeedHouse, lastSeedBoard)
    starved = isStarved(copyOfOpponentBoard)
    
    
    if starved and beansCaptured > 0:
        return const.CAPTURE_ALL_MOVE
    elif starved and beansCaptured == 0:
        return const.ILLEGAL_MOVE
    else:
        return const.VALID_MOVE 
    
def getValidMoves(playerBoard, opponentBoard):
    validMoves = []
    for move in range(const.GRID_SIZE):
        if (playerBoard[move] > 0
             and evaluateMove(playerBoard, opponentBoard, move) != const.ILLEGAL_MOVE):
            validMoves.append(move)
            
    return validMoves

def hasValidMove(playerBoard, opponentBoard):
    return getValidMoves(playerBoard, opponentBoard) != []       

def isStarved(playerBoard):
    return sum(playerBoard) == 0


