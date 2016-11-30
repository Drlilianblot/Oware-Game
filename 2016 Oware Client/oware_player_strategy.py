'''
This module handle the game strategy (only) of a player. The game server / player (client side) 
communication is done via the player_clientside.py module.

You should modify this file to implement your AI player.

Created on 1 July 2016

@author: Lilian
'''

from random import randint
import const


SHOW_GUI = False
SHOW_OUTPUT = False


# Enter your own player name
# PLEASE ENTER YOUR OWN NAME/BATTLENAME
player_name = "Dumb and Dumber" 

# Enter your own player description, e.g. what kind of strategy has been used.
player_description = "Choose the first house (starting from the left) that yield a valid move."

mySeeds = 0         # The number of seeds you have captured so far
opponentSeeds = 0   # The number of seeds your opponent has captured so far
            

def chooseMoveManually(playerBoard, opponentBoard, playerSeeds, opponentSeeds):
    """
    DO NOT DELETE. You SHOULD NOT change this method. This is a convenience method to enable you to test your 
    strategy manually against another player. For example, you could use an online oware abapa
    game to test your strategy against another player. 
    
    To do this you can open three console windows:
    
        - a) in the first window start the game server:
            python oware_gui_server.py
            
        - b) in the second window start your player strategy using:
            python player_clientside.py -t
        
        - c) in the third window start the opponent player using:
            python player_clientside.py -t -m 
            
            You will be prompt to enter the opponent move.
    
    Note in the example above we assumed your player was the first to play, if your player
    plays in second you should do c) before b).    

    @param playerBoard: you board before the opponent made its move
    @param opponentBoard: the opponent board before it made its move
    @param playerSeeds: you number of seeds captured before the opponent made its move
    @param oppSeeds: the opponent number of seeds captured before it made its move

    @return: an int between 0 and (const.GRID_SIZE - 1) representing the chosen move.
    """

    ## DO NOT REMOVE. This line is used for the option -t in the player_clientside. If the 
    ## option -t is used, this line display the current boards.
    if SHOW_OUTPUT: print(displayBoard(playerBoard, opponentBoard, playerSeeds, opponentSeeds))
    
    moves = getValidMoves(playerBoard, opponentBoard)
    while True:
        try:
            move = int(input("Enter your chosen move (between 0 and " + str(const.GRID_SIZE -1) + ":"))
        except:
            print ("Invalid input, try a number between 0 and " + str(const.GRID_SIZE -1) + ":")
        
        if move in moves: 
            break
        else:
            print( str(move), "is an illegal move. Try another move.")
        
    return move

def chooseMove(playerBoard, opponentBoard, playerSeeds, opponentSeeds):
    """
    DO NOT DELETE. However you should modify this function, this is where you 
    should implement your strategy.

    @param playerBoard: you current board 
    @param opponentBoard: the opponent board
    @param playerSeeds: number of seeds you have captured so far
    @param oppSeeds: number of seeds captured by your opponent

    @return: an int between 0 and (const.GRID_SIZE - 1) representing the chosen move.
    """
    
    ## DO NOT REMOVE. This line is used for the option -t in the player_clientside. If the 
    ## option -t is used, this line display the current boards.
    if SHOW_OUTPUT: print(displayBoard(playerBoard, opponentBoard, playerSeeds, opponentSeeds))
    
    ## This is the current and rather dumb strategy of choosing the first valid move. You 
    ## should replace this code by your own strategy.
    moves = getValidMoves(playerBoard, opponentBoard)     
    print ("\t --> Your move: ", moves[0], "<--")
    return moves[0]
 
    
def getOpponentMove(move, playerBoard, opponentBoard, playerSeeds, opponentSeeds):
    """ 
    DO NOT DELETE. You might like to keep track of your opponent choice of move. This might help you
    define its strategy. You can also ignore it completely, in this case you just leave
    the function as it is.
    
    @param playerBoard: you board before the opponent made its move
    @param opponentBoard: the opponent board before it made its move
    @param playerSeeds: you number of seeds captured before the opponent made its move
    @param oppSeeds: the opponent number of seeds captured before it made its move
    """

    ## DO NOT REMOVE. This line is used for the option -t in the player_clientside. If the 
    ## option -t is used, this line display the current boards.
    if SHOW_OUTPUT: 
        print(displayBoard(playerBoard, opponentBoard, playerSeeds, opponentSeeds))
        print ("\t --> Opponent move: ", move, "<--")
 
   
def newRound():
    """
    DO NOT DELETE. This method is called when a new round is starting (new game with same player). This gives 
    you the ability to update your strategy. 
    Currently does nothing.
    THIS METHOD WILL NOT BE USED DURING THE COMPETITION
    """
    pass


def newPlayer():
    """
    DO NOT DELETE. This method is used for backward compatibility. You should ignore this function.
    THIS METHOD WILL NOT BE USED DURING THE COMPETITION

    """
    pass


def displayBoard(playerBoard, opponentBoard, playerSeeds, opponentSeeds):
    '''
    DO NOT DELETE. Function to represent the board as a string ready to be printed in the form show below:
    
            Opponent:27
        +--+--+--+--+--+--+
        | 5| 4| 3| 2| 1| 0|
        +--+--+--+--+--+--+
        |  | 3| 4|  | 1| 1|
        +==+==+==+==+==+==+
        | 2| 1|  | 5| 3| 1|
        +--+--+--+--+--+--+
        | 0| 1| 2| 3| 4| 5|
        +--+--+--+--+--+--+
            Me:0
    
    You SHOULD NOT change this function.

    @param playerBoard: your current board 
    @param opponentBoard: the opponent board 
    @param playerSeeds: number of seeds you have captured 
    @param oppSeeds: number of seeds the opponent has captured 

    @return: a string representation of the current state of the game.
    
    '''
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
        if playerBoard[i] == 0:
            output += str.format("|%2s"%(""))
        else:            
            output += str.format("|%2d"%(playerBoard[i]))
    output += "|\n"
    output += ("+" + "-" * 2) * const.GRID_SIZE +"+\n"
    for i in range(const.GRID_SIZE):
        output += str.format("|%2d"%(i))    
    output += "|\n"
    output += ("+" + "-" * 2) * const.GRID_SIZE +"+\n"
    output += "       Me:" + str(playerSeeds) + "\n"
    
    return output
    




################################################################################
################################################################################
##                                                                            ##
##               OPTIONAL FUNCTION GIVEN FOR YOUR CONVENIENCE                 ##
##                                                                            ##
##                YOU CAN DELETE THESE FUNCTIONS IF YOU WISH                  ##
##                                                                            ##
################################################################################
################################################################################


def sowSeeds(playerBoard, opponentBoard, move):
    '''
    Convenience function that only sow seeds on the board. This function does not 
    do the capture of the seeds. This is done by the function:
    
      captureSeeds(playerBoard, opponentBoard, lastSeedHouse, lastSeedBoard)
      
    playerBoard and opponentBoard might be modified by the function.
      
    @param playerBoard: the board of the player making the move (e.g. you or your
                        opponent's board depending on the player making the move)
    @param opponentBoard: the board of the other player (e.g. you or your
                        opponent's board depending on the player making the move)
    @param move: the move to be done. 
    
    @return (board, houseIndex), where board is the board where the last seed has 
            been sown, and houseIndex is the house index where the last seed has
            been sown (between 0 and (const.GRID_SIZE - 1)). note that board can 
            be either playerBoard or opponentBoard.
     
    '''
    board = playerBoard
    houseIndex = move + 1
    seeds = board[move]
    board[move] = 0
    seedsDropped = 0
    while seeds > 1:
        if houseIndex >= const.GRID_SIZE:
            if board is opponentBoard:
                board = playerBoard
            else:
                board = opponentBoard
                
            houseIndex -= const.GRID_SIZE
            
        board[houseIndex] += 1
        seeds -= 1
        seedsDropped += 1
        if seedsDropped % (2 * const.GRID_SIZE -1) == 0:
            houseIndex += 2 # skip the initial house where the seeds have been picked up
        else:
            houseIndex += 1
        
        
    # BEGIN adds the last seed in hand    
    if houseIndex >= const.GRID_SIZE:
        if board is opponentBoard:
            board = playerBoard
        else:
            board = opponentBoard
        houseIndex -= const.GRID_SIZE
    board[houseIndex] += 1 
    # END adds the last seed in hand
    
    return board, houseIndex
    
        
def captureSeeds(playerBoard, opponentBoard, lastSeedHouse, lastSeedBoard):  
    '''
    Convenience function that only captures the seeds on the board. The capture
    follows the rule of the Oware Abapa game, e.g. a capture cannot starve the
    opponent. If the move means capturing all the seeds of the opponent, then 
    the move is done but no seeds are captured.
      
    playerBoard and opponentBoard might be modified by the function.
      
    @param playerBoard: the board of the player making the move (e.g. you or your
                        opponent's board depending on the player making the move)
    @param opponentBoard: the board of the other player (e.g. you or your
                        opponent's board depending on the player making the move)
    @param lastSeedHouse: the index (int) of the house where the last seed has been
                          dropped 
    @param lastSeedBoard: the board where the last seed has been dropped
    
    @return the number of seeds captured
     
    '''
    board = lastSeedBoard  
    houseIndex = lastSeedHouse    
    seedsCaptured = 0
    if board is playerBoard: # a player cannot capture is own house
        return seedsCaptured
    
    if 2 <= board[houseIndex] <= 3: # capture seeds
        seedsCaptured = board[houseIndex]
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
                seedsCaptured += board[houseIndex]
                board[houseIndex] = 0
            else:
                break
                            
    return seedsCaptured
    
            
def evaluateMove(playerBoard, opponentBoard, move):
    '''
    Convenience function that evaluates the outcome of a given move. The game board 
    is not modified by this function (e.g. the move is not done). There are three 
    possible outcomes:
    
        - const.CAPTURE_ALL_MOVE if the move is valid but capture all the seeds of the
          other player, therefore starving him/her.
          
        - const.ILLEGAL_MOVE if the move is not legal, meaning you must not do that 
          move. For example this move will starve the opponent, whereas another move
          might be possible.
          
        - const.VALID_MOVE if none of the above.


    @param playerBoard: the board of the player making the move (e.g. you or your
                        opponent's board depending on the player making the move)
    @param opponentBoard: the board of the other player (e.g. you or your
                        opponent's board depending on the player making the move)
    @param move: the move to be done. 
    
    @return: int representing the outcome of a move. 
    
    '''
    
    copyOfPlayerBoard = list(playerBoard)
    copyOfOpponentBoard = list(opponentBoard)
    
    lastSeedBoard, lastSeedHouse = sowSeeds(copyOfPlayerBoard, copyOfOpponentBoard, move)
    seedsCaptured = captureSeeds(copyOfPlayerBoard, copyOfOpponentBoard, lastSeedHouse, lastSeedBoard)
    starved = isStarved(copyOfOpponentBoard)
    
    
    if starved and seedsCaptured > 0:
        return const.CAPTURE_ALL_MOVE
    elif starved and seedsCaptured == 0:
        return const.ILLEGAL_MOVE
    else:
        return const.VALID_MOVE 
    

def getValidMoves(playerBoard, opponentBoard):
    '''
    Convenience function returning the list of all valid moves given the current
    state of the game.
    
    @param playerBoard: the board of the player making the move (e.g. you or your
                        opponent's board depending on the player turn)
    @param opponentBoard: the board of the other player (e.g. you or your
                        opponent's board depending on the player turn)
                        
    @return: list of int representing the list of valid moves. The integer inside
             the list must be between 0 and (const.GRID_SIZE - 1).
             If no valid move are possible, returns an empty list.
    '''
    validMoves = []
    for move in range(const.GRID_SIZE):
        if (playerBoard[move] > 0
             and evaluateMove(playerBoard, opponentBoard, move) != const.ILLEGAL_MOVE):
            validMoves.append(move)
            
    return validMoves


def hasValidMove(playerBoard, opponentBoard):
    '''
    Convenience function which returns True if the player making the next move
    can make a valid move, False otherwise.
    
    @param playerBoard: the board of the player making the next move (e.g. you or your
                        opponent's board depending on the player turn)
    @param opponentBoard: the board of the other player (e.g. you or your
                        opponent's board depending on the player turn)
     
    @return: True if there is at least one valid move, False otherwise.                    
    '''
    return getValidMoves(playerBoard, opponentBoard) != []       


def isStarved(playerBoard):
    '''
    Convenience function that returns True is the player has no seed on his board,
    False otherwise.
    
    @param playerBoard: the board of the player (e.g. you or your opponent's board 
                        depending on which player you want to check)
                        
    @return: True is the player has no seed on his board, False otherwise.
    '''
    return sum(playerBoard) == 0


