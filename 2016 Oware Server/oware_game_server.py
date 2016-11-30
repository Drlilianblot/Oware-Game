'''
Created on 7 Aug 2014

@author: Lilian
'''
#!/usr/bin/python # This is server.py file
import sys, getopt, socket # Import socket module
import time


import const
from oware_player_socket import PlayerSocket



##########################################
##           PARAMETERS SETTING         ##
##########################################

def initBoards():                
    # Initialise board and captured seeds
    global player1_board, player2_board, player1_seeds, player2_seeds
    
    player1_board   = [const.INITIAL_BEANS]*const.GRID_SIZE
    player2_board   = [const.INITIAL_BEANS]*const.GRID_SIZE
    player1_seeds = 0
    player2_seeds = 0
    
def getBoardState(playerBoard, opponentBoard, playerSeeds = 0, opponentSeeds = 0):
    output = str(playerSeeds) + ", " + str(opponentSeeds) 
    for i in playerBoard:
        output += ", " + str(i)

    for i in opponentBoard:
        output += ", " + str(i)
    return output

def updateMove(playerBoard, opponentBoard, move):
    capturedSeeds = 0
    if move in getValidMoves(playerBoard, opponentBoard):
        moveResult = evaluateMove(playerBoard, opponentBoard, move)
        if moveResult == const.CAPTURE_ALL_MOVE: # cannot capture seeds otherwise starving opponent
            lastSeedBoard, lastSeedHouse = sowSeeds(playerBoard, opponentBoard, move)
        elif moveResult == const.VALID_MOVE: #
            lastSeedBoard, lastSeedHouse = sowSeeds(playerBoard, opponentBoard, move)
            capturedSeeds = captureSeeds(playerBoard, opponentBoard, lastSeedHouse, lastSeedBoard)
        else:
            raise Exception("Unexpected move outcome")
    else:
        raise Exception("Illegal Move!")
    
    return capturedSeeds


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
#         print("evaluate move to CAPTURE_ALL_MOVE")
        return const.CAPTURE_ALL_MOVE
    elif starved and beansCaptured == 0:
#         print("evaluate move to ILLEGAL_MOVE")
        return const.ILLEGAL_MOVE
    else:
#         print("evaluate move to VALID_MOVE")
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


def displayBoard():
    
    output = "\tPlayer 1: " + str(player1_seeds) + " -- seeds = " + player1_name + "\n"
    output += "\t\t" + ("+" + "-" * 2) * const.GRID_SIZE +"+\n"
    output += "\t\t"
    for i in range(const.GRID_SIZE -1 , -1, -1):
        output += str.format("|%2d"%(i))
    output += "|\n"
    output += "\t\t" + ("+" + "-" * 2) * const.GRID_SIZE +"+\n"
    output += "\t\t"
    for i in range(const.GRID_SIZE - 1, -1, -1):
        if player1_board[i] == 0:
            output += str.format("|%2s"%(""))
        else:            
            output += str.format("|%2d"%(player1_board[i]))
            
    output += "|\n"
    output += "\t\t" + ("+" + "=" * 2) * const.GRID_SIZE +"+\n"
    output += "\t\t"
    for i in range(const.GRID_SIZE):
        if player2_board[i] == 0:
            output += str.format("|%2s"%(""))
        else:            
            output += str.format("|%2d"%(player2_board[i]))
    output += "|\n"
    output += "\t\t" + ("+" + "-" * 2) * const.GRID_SIZE +"+\n"
    output += "\t\t"
    for i in range(const.GRID_SIZE):
        output += str.format("|%2d"%(i))    
    output += "|\n"
    output += "\t\t" + ("+" + "-" * 2) * const.GRID_SIZE +"+\n"
    output += "\tPlayer 2: " + str(player2_seeds) + " -- seeds = " + player2_name + "\n"
    
    return output
    



def checkWinner(player_seeds):
    # We just need to test whether the number of hits equals the total number of squares in the fleet
    return player_seeds > const.GRID_SIZE * const.INITIAL_BEANS



def playGame(gui, firstPlayer, secondPlayer, turn):
    """
    function handling a game between two players (e.g. one single round).
    @param <BattleshipsGraphics> gui, the graphic interface displaying a round.
    @param <PlayerSocket> firstPlayer, secondPlayer: The player objects.
    @param <int> turn: parameter indicating who is starting the game. 
    if turn == 1 then firstPlayer starts, else if turn == -1 then secondPlayer starts.
    """

    global player1_board, player2_board
    global player1_seeds, player2_seeds
    
    boardStates = []

    initBoards()

    boardStates.append(getBoardState(player1_board, player2_board))     

    haveWinner = False
    shots = 1
    while not haveWinner:
        if turn > 0:
            if hasValidMove(player1_board, player2_board):
                move= firstPlayer.chooseMove(getBoardState(player1_board, player2_board,
                                                           player1_seeds, player2_seeds))

                secondPlayer.getOpponentMove(move, 
                                             getBoardState(player2_board, 
                                                           player1_board,
                                                           player2_seeds, 
                                                           player1_seeds))
                
                captured_seeds =  updateMove(player1_board, player2_board, move)
                player1_seeds += captured_seeds
                
                turn *= -1
                shots += 1
                haveWinner = checkWinner(player1_seeds)
                if SHOW_OUTPUT:
                    print("\n\n\t--> Player 1 picks house " + str(move) +" <--\n")
            else:
                if SHOW_OUTPUT:
                    print("\n\n\t--> No more valid move for Player 1!       <--")
                    print(    "\t--> Players collect seeds on their side of <--")
                    print(    "\t--> the board!                             <--\n")
                haveWinner = True
                player1_seeds += sum(player1_board)
                player2_seeds += sum(player2_board)
                player1_board   = [0]*const.GRID_SIZE #remove remaining seeds from the board
                player2_board   = [0]*const.GRID_SIZE #remove remaining seeds from the board
 
        else:
            if hasValidMove(player2_board, player1_board):
                move = secondPlayer.chooseMove(getBoardState(player2_board, player1_board,
                                                           player2_seeds, player1_seeds))

                firstPlayer.getOpponentMove(move, 
                                             getBoardState(player1_board, 
                                                           player2_board,
                                                           player1_seeds, 
                                                           player2_seeds))

                captured_seeds =  updateMove(player2_board, player1_board, move)
                player2_seeds += captured_seeds
                
                
                turn *= -1
                shots += 1
                haveWinner = checkWinner(player2_seeds)
                if SHOW_OUTPUT:
                    print("\n\n\t--> Player 2 picks house " + str(move) +" <--\n")
             
            else:
                if SHOW_OUTPUT:
                    print("\n\n\t--> No more valid move for Player 2!       <--")
                    print(    "\t--> Players collect seeds on their side of <--")
                    print(    "\t--> the board!                             <--\n")
                haveWinner = True
                player1_seeds += sum(player1_board)
                player2_seeds += sum(player2_board)
                player1_board   = [0]*const.GRID_SIZE #remove remaining seeds from the board
                player2_board   = [0]*const.GRID_SIZE #remove remaining seeds from the board
         
        if SHOW_OUTPUT:
            print(displayBoard()) 
 
        if SPEED > 0:
            time.sleep(SPEED) 
         
        if not haveWinner and getBoardState(player1_board, player2_board) in boardStates:
            haveWinner = True
            player1_seeds += sum(player1_board)
            player2_seeds += sum(player2_board)
            player1_board   = [0]*const.GRID_SIZE #remove remaining seeds from the board
            player2_board   = [0]*const.GRID_SIZE #remove remaining seeds from the board
            
            if SHOW_OUTPUT:
                print("\n\n\t--> This Board configuration has already   <--")
                print("\t--> been encountered, game ends!           <--")
                print("\t--> Players collect seeds on their side of <--")
                print("\t--> the board!                             <--\n")
                
            if SHOW_OUTPUT:
                print(displayBoard()) 
        else:
            boardStates.append(getBoardState(player1_board, player2_board))     
                
            

         
    if player2_seeds > player1_seeds :
        print ("---------------- player 2 is the winner in " + str(shots) + " shots ----------------")
        result = (0,1)
    elif player2_seeds < player1_seeds :
        print ("---------------- player 1 is the winner in " + str(shots) + " shots ----------------")
        result = (1,0)
    else:
        print ("---------------- it's a DRAW in " + str(shots) + " shots ----------------")
        result = (1,1)
             
    return result


def displayHelp():
    print ('\n dummy_player_clientside.py  -g -v -h <host_IP> -p <port_number>\n')
    print ('  --help:          display this help message')
    print ('  -t or --text:    display the GUI (optional)')
    print ('  -s or --speed:   display the text output (optional)')
    print ('  -h or --host:    set the IP address of the game server.')
    print ('                   If omitted the address is set to localhost.')
    print ('  -p or --port:    set the port number used for the socket communication.')
    print ('                   The port number must be greater than 4096. if omitted,')
    print ('                   the default port number used is 12345.')
    

# Main
def main(argv):
    global SPEED, SHOW_OUTPUT
    SPEED = 0
    
    try:
        opts, args = getopt.getopt(argv,"ts:h:p:",["help","text","speed=","host=", "port="])
    except getopt.GetoptError:
        displayHelp()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '--help':
            displayHelp()
            sys.exit()
        elif opt in ("-h", "--host"):
            const.GAME_SERVER_ADDR = arg
        elif opt in ("-p", "--port"):
            const.GAME_SERVER_PORT = arg
        elif opt in ("-t", "--text"):
            SHOW_OUTPUT = True
        elif opt in ("-s", "--speed"):
            SPEED = float(arg)
            

    global player1, player1_name, player2, player2_name
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # Create a socket object
    sock.bind((const.GAME_SERVER_ADDR, const.GAME_SERVER_PORT)) # The same port as used by the server & clients
    sock.listen(2)                                              # Now wait for client connection (max of 2 client at a time).
    while True:
        client1, addr1 = sock.accept()                          # Establish connection with first client.
        print( 'Got connection from', addr1)
        player1 = PlayerSocket(client1, addr1)                  # Create first player with that connection
        player1.acknowledgeConnection()
        player1_name = player1.getName()
        print ("player",player1_name,"is connected..."  )  
    
        client2, addr2 = sock.accept()                          # Establish connection with second client.
        print ('Got connection from', addr2)
        player2 = PlayerSocket(client2, addr2)                  # Create second player with second connection
        player2.acknowledgeConnection()
        player2_name = player2.getName()
        print ("player",player2_name,"is connected...")
     
    #     gui = BattleshipsGraphics(const.GRID_SIZE)
    #     playMatch(gui, player1, player2, const.ROUNDS)
        playGame(None, player1, player2, 1)
        
    
        player1.close(getBoardState(player1_board, player2_board,
                                    player1_seeds, player2_seeds))   # Close the connection
        player2.close(getBoardState(player2_board, player1_board, 
                                    player2_seeds, player1_seeds))   # Close the connection
        
        break                                                   # End of game, exit game loop

if __name__ == "__main__":
    main(sys.argv[1:])
    
   

