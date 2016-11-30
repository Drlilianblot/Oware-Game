'''

This module handle the client side of the client/server communication of the game.
It calls the functions defined in the Player_strategy module and send the output/input 
information needed by the server.

RPI Competition rule:
YOU SHOULD NOT CHANGE THIS FILE: If you change the file and a communication error occurs
during a game, you will forfeit that game.


Created on 7 Jul 2016

@author: Lilian Blot
'''

import sys, getopt, socket 

import oware_player_strategy as player # import the module created by the student containing the strategy
import const

verbose = False # option to display communication between client\server
manual = False  # option to play as a human player (True). You will be prompt to 
                # enter your chosen move manually.


def parseMessage(message):
    '''
    The message sent by the game server is comma separated if more than one instruction must 
    be sent. This method create a list of upper case str items, without space at the start and 
    end of the string.    
    '''
    parsed = message.split(',')
    cleaned = []
    for item in parsed:
        cleaned.append(item.strip().upper())
    
    return cleaned

def get_board_state(parsedMessage):
    '''
    This function decodes the part of the message send by the server representing the state of 
    the board game. This message has already been transform into a list of string. The format
    is as follow:
     - The first element of the list contains the number of seeds capture by the player 
     - The second element of the list contains the number of seeds capture by the opponent
     - the following const.GRID_SIZE elements contain the number of seeds in each house of
       the player
     - the remaining const.GRID_SIZE elements contain the number of seeds in each house of 
       the opponent
       
    The function returns a tuple of four elements:
     - the first element is the board of the player
     - the second element is the board of the opponent
     - the third element is the number of seeds captured by the player
     - the fourth element is the number of seeds captured by the opponent
     
    The function raises an Exception if the state of the board is not valid, e.g. some data
    is missing.
    '''
    if len(parsedMessage) == (const.GRID_SIZE * const.ROWS + 2):
        
        seeds1 = int(parsedMessage[0])
        seeds2 = int(parsedMessage[1])
        
        board1 = []
        for i in range(2, const.GRID_SIZE + 2):
            board1.append(int(parsedMessage[i]))
            
        board2 = []
        for i in range(const.GRID_SIZE + 2, const.ROWS * const.GRID_SIZE + 2):
            board2.append(int(parsedMessage[i]))
            
        return board1, board2, seeds1, seeds2
    else:
        raise Exception("invalid board state")
 

def displayHelp():
    print ('\n dummy_player_clientside.py  -g -v -h <host_IP> -p <port_number>\n')
    print ('  --help:          display this help message')
    print ('  -m or --manual:  option to play as a human player. You will be prompt')
    print ('                   to enter your chosen move manually.')
    print ('  -t or --text:    display the GUI (optional)')
    print ('  -v or --verbose: display the text output (optional)')
    print ('  -h or --host:    set the IP address of the game server.')
    print ('                   If omitted the address is set to localhost.')
    print ('  -p or --port:    set the port number used for the socket communication.')
    print ('                   The port number must be greater than 4096. if omitted,')
    print ('                   the default port number used is 12345.')
    
def main(argv):
    '''
    Body of the communication process between the client and the server.
    '''

    global verbose, manual
    
    try:
        opts, args = getopt.getopt(argv,"mgtvh:p:",["manual","verbose","help","graphics","text","host=", "port="])
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
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-m", "--manually"):
            manual = True
        elif opt in ("-t", "--text"):
            player.SHOW_OUTPUT = True
        elif opt in ("-g", "--graphics"):
            player.SHOW_GUI = True
            

    game_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a socket object
    if const.GAME_SERVER_ADDR == '':        
        host = socket.gethostname() # Get local machine name
        game_server.connect((host, const.GAME_SERVER_PORT))
    else:
        game_server.connect((const.GAME_SERVER_ADDR, const.GAME_SERVER_PORT))
        
    status = game_server.recv(1024).decode()         # used for client/server synchronisation purpose
    game_server.send(const.ACKNOWLEDGED.encode())    # used for client/server synchronisation purpose    
    if verbose : print (status)
    
    if status == "CONNECTED":
        while True:
            request = game_server.recv(1024).decode()
            if verbose : print ("not so dumb side rqt:", request, "|") # used for visual checking of client/server communication
            request = parseMessage(request)
            
            if request[0] == "GET_NAME":
                game_server.send(str(player.player_name).encode())
                
            elif request[0] == "NEW_PLAYER":
                player.newPlayer()
                game_server.send(const.ACKNOWLEDGED.encode())    # used for client/server synchronisation purpose
                
            elif request[0] == "NEW_ROUND":
                player.newRound()
                game_server.send(const.ACKNOWLEDGED.encode())    # used for client/server synchronisation purpose
                
            elif request[0] == "GET_DESCRIPTION":
                game_server.send(str(player.player_description).encode())
                
            elif request[0] == "CHOOSE_MOVE":
                player_board, opponent_board, player_seeds, opponent_seeds = get_board_state(request[1:])
                if manual:
                    move = str(player.chooseMoveManually(player_board, opponent_board, 
                                                       player_seeds, opponent_seeds))
                else:
                    move = str(player.chooseMove(player_board, opponent_board, 
                                                       player_seeds, opponent_seeds))
                game_server.send(move.encode())
                                
            elif request[0] == "GET_OPPONENT_MOVE":
                move = int(request[1])
                player_board, opponent_board, player_seeds, opponent_seeds = get_board_state(request[2:])
                player.getOpponentMove(move, player_board, opponent_board, 
                                       player_seeds, opponent_seeds)                    
                game_server.send(const.ACKNOWLEDGED.encode())    # used for client/server synchronisation purpose

            elif request[0] == "GAME_OVER":
                if player.SHOW_OUTPUT:
                    player_board, opponent_board, player_seeds, opponent_seeds = get_board_state(request[1:])
                    print(player.displayBoard(player_board, opponent_board, player_seeds, opponent_seeds))
                game_server.send(const.ACKNOWLEDGED.encode())    # used for client/server synchronisation purpose
                
            else:
                # unknown request so must be either end of game or a fatal error. Exit the game loop
                if verbose : print (request)
                game_server.send(const.ACKNOWLEDGED.encode())    # used for client/server synchronisation purpose
                break
            

    game_server.close # Close the socket when done

        
if __name__ == "__main__":
   main(sys.argv[1:])