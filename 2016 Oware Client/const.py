# TODO change GRID_SIZE to BOARD_SIZE
GRID_SIZE = 6       # The number of houses per player
ROWS = 2            # The number of rows on the board, default should be 2, one for each player

# TODO change name to INITIAL_SEEDS
INITIAL_BEANS = 4   # The number of seeds per house at the start of a game 

ROUNDS = 3    ## Number of rounds per match

ILLEGAL_MOVE = -1       # When a move is illegal
VALID_MOVE = 1          # To signal a valid move
CAPTURE_ALL_MOVE = 2    # A move that capture all opponent seeds, therefore starving a player
                        # It might not be illegal, it might mean that we are not allowed to
                        # capture the seeds



############################################################
##
## Constants used for the client/server functionalities
##
############################################################
# Constant containing the IP address of the server
GAME_SERVER_ADDR = ''   #meaning the server is on the local host. Comment if server is elsewhere and provide
                        # an address like the one below
# GAME_SERVER_ADDR = '169.254.66.111' 
 
# Port used for the socket communication. You must ensure the same port is used by the client & the server
# Note: another port number could be used
GAME_SERVER_PORT = 12345 

# Constant used in the communication to acknowledge a received message
# Typically this constant is used to synchronise the clients and the server
ACKNOWLEDGED = 'ACK'