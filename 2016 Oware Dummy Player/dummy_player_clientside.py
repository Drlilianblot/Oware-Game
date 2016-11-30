'''
This module handle the client side of the client/server communication of the game.
It calls the functions defined in the Player_strategy module and send the output/input 
information needed by the server.

Created on 7 Aug 2014

@author: Lilian
'''

import sys, getopt, socket 

import dummy_player_strategy as player
import const

verbose = False #option to display communication between client\server

def parseMessage(message):
    parsed = message.split(',')
    cleaned = []
    for item in parsed:
        cleaned.append(item.strip().upper())
    
    return cleaned

def get_board_state(parsedMessage):
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
    print ('  -g or --gui:     display the GUI (optional)')
    print ('  -t or --text:     display the GUI (optional)')
    print ('  -v or --verbose: display the text output (optional)')
    print ('  -h or --host:    set the IP address of the game server.')
    print ('                   If omitted the address is set to localhost.')
    print ('  -p or --port:    set the port number used for the socket communication.')
    print ('                   The port number must be greater than 4096. if ommitter,')
    print ('                   the default port number used is 12345.')
    
def main(argv):
    global verbose
    
    try:
        opts, args = getopt.getopt(argv,"gtvh:p:",["verbose","help","graphics","text","host=", "port="])
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
        
    status = game_server.recv(1024).decode()
    # used for client/server synchronisation purpose
    game_server.send(const.ACKNOWLEDGED.encode())    # used for client/server synchronisation purpose    
    if verbose : print (status)
    
    if status == "CONNECTED":
        while True:
            request = game_server.recv(1024).decode()
            if verbose: print ("dummy side rqt:", request, "|")
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
                game_server.send(str(player.chooseMove(player_board, opponent_board, 
                                                       player_seeds, opponent_seeds)).encode())
                                
            elif request[0] == "GET_OPPONENT_MOVE":
                move = int(request[1])
                player_board, opponent_board, player_seeds, opponent_seeds = get_board_state(request[2:])
                player.getOpponentMove(move, player_board, opponent_board, 
                                       player_seeds, opponent_seeds)                    
                game_server.send(const.ACKNOWLEDGED.encode())    # used for client/server synchronisation purpose
                
            else:
                # unknown request so must be either end of game or a fatal error. Exit the game loop
                print (request)
                game_server.send(const.ACKNOWLEDGED.encode())    # used for client/server synchronisation purpose
                break
            

    game_server.close # Close the socket when done

        
if __name__ == "__main__":
   main(sys.argv[1:])