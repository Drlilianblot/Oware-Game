'''
Created on 8 Jul 2016

@author: Lilian
'''

import tkinter as tk
import time, _thread, threading
import sys, getopt, socket # Import socket module
import const
import random
from oware_player_socket import PlayerSocket


class Application(tk.Frame): 
    
    proceedNextRoundEvent= threading.Event() #thread event to signal that gui update is done and the game thread can continue.
    
    def __init__(self, master=None, tossCoin = False, speed = 0, show_option = True):
        super().__init__(master) 
        self.grid() 
        
        # should a toss be made to select the fist player, default is NO (False) meaning
        # the first player connected plays first.
        self.tossCoin = tossCoin
        self.speed = speed
        self.show_output = show_option
        
        # handle to the GUI red circle widget highlighting a player's move
        self.selectedMove = None
        self.sizeSelectedMoveHighlight = 60
        
        # handle to the GUI text widget showing the player's name
        self.player1_name_txt = None   
        self.player2_name_txt = None   

        # handle to the GUI text widget showing the number of seeds captured
        self.player1_seed_txt = None
        self.player2_seed_txt = None

        # setting up statistics variable for each player
        self.player1_time = 0
        self.player2_time = 0    
        self.player1_shots = 0
        self.player2_shots = 0
        self.player1_avgtime_txt = None
        self.player2_avgtime_txt = None
        
        # setup position of the center of houses in image. The position are stored 
        # in a file
        self._housesPosition = []
        fposition = open('housesposition.txt', 'r')
        for line in fposition:
            entries = line.split(',')
            self._housesPosition.append((int(entries[0]),int(entries[1])))
        fposition.close()
        
        # setup the series of images, from the background image to the series of houses
        # having 0 to 48 seeds
        self._bkgImage = tk.PhotoImage(file='images/awari-board-bkg.gif')
        self._houseImages = [] # contains the 49 tk.photoImage
        for i in range(49):
            self._houseImages.append(tk.PhotoImage(file=('images/' + str(i) + '.gif')))

        # initialise the board for each player     
        self.initBoards() 
        
        # Create the GUI interface   
        self.createWidgets()
        
        # starts the game thread (a different thread than the GUI thread)
        _thread.start_new_thread(self.main, ())
        
    def createWidgets(self):
        self.C = tk.Canvas(self,
                           width = self._bkgImage.width(),
                           height = self._bkgImage.height())
        bkg_image = self.C.create_image(0,0, image = self._bkgImage,
                                 anchor = tk.NW)
        

        # Create the image widget for each houses and store them into a list
        # elements 0 to 5 are for the first player (South), elements 6 to 11 are
        # for the second player (North)
        self._houses = []        
        for i in range(len(self.player1_board)):
#             print(i, self.player1_board[i], self._houseImages[self.player1_board[i]])
            self._houses.append(self.C.create_image(self._housesPosition[i][0],
                                                  self._housesPosition[i][1],
                                                  image = self._houseImages[self.player1_board[i]],
                                                  anchor = tk.CENTER))
                
        for i in range(len(self.player2_board)):
            index = i + len(self.player1_board)
            print(index)
            self._houses.append(self.C.create_image(self._housesPosition[index][0],
                                                      self._housesPosition[index][1],
                                                      image = self._houseImages[self.player2_board[i]],
                                                      anchor = tk.CENTER))
        
        # organise the canvas elements        
        self.C.grid()
        
    def displayName(self):
        
        # thread event used to synchronise the GUI thread and the game thread
        Application.proceedNextRoundEvent.clear() 
        
        # create the text widget for the players name
        self.player1_name_txt = self.C.create_text(750, 660,
                                                   text = self.player1_name,
                                                   anchor = tk.W,
                                                   font = ('Verdana', 32),
                                                   fill = 'blue')
        self.player2_name_txt = self.C.create_text(750, 75,
                                                   text = self.player2_name,
                                                   anchor = tk.W,
                                                   font = ('Verdana', 32),
                                                   fill = 'green')
        
        # notify thread waiting for this event they can now proceed
        Application.proceedNextRoundEvent.set()
       
    def displayWinner(self, result):
        
        # thread event used to synchronise the GUI thread and the game thread
        Application.proceedNextRoundEvent.clear()
        
        
        # create the text widget to display the winner's name
        if(result == (1,0)):
            self.C.create_text(670, 355,
                               text = self.player1_name + " WINS!",
                               anchor = tk.CENTER,
                               font = ('Verdana', 48),
                               fill = 'yellow')
        elif result == (0,1):
            self.C.create_text(670, 355,
                               text = self.player2_name + " WINS!",
                               anchor = tk.CENTER,
                               font = ('Verdana', 48),
                               fill = 'yellow')
        else:
            self.C.create_text(670, 355,
                               text = "It's a DRAW!",
                               anchor = tk.CENTER,
                               font = ('Verdana', 48),
                               fill = 'yellow')
            
        # notify thread waiting for this event they can now proceed
        Application.proceedNextRoundEvent.set()
       
        
    def updateBoard(self, player, housePlayed):
        
        # thread event used to synchronise the GUI thread and the game thread
        Application.proceedNextRoundEvent.clear()

        if player < 0:
            houseNo = housePlayed
        else:
            houseNo = housePlayed + len(self.player1_board)
        
        if self.player1_seed_txt == None:
            
            self.player1_seed_txt = self.C.create_text(190, 440,
                                                       text = str(self.player1_seeds),
                                                       anchor = tk.CENTER,
                                                       font = ('Verdana', 32))
        else:
            self.C.itemconfig(self.player1_seed_txt, text = str(self.player1_seeds))

        if self.player2_seed_txt == None:
            
            self.player2_seed_txt = self.C.create_text(1140, 270,
                                                       text = str(self.player2_seeds),
                                                       anchor = tk.CENTER,
                                                       font = ('Verdana', 32))
        else:
            self.C.itemconfig(self.player2_seed_txt, text = str(self.player2_seeds))


        if self.player1_avgtime_txt == None:
            if self.player1_shots == 0:
                avg = 0
            else:
                avg = self.player1_time / self.player1_shots
                
            self.player1_avgtime_txt = self.C.create_text(20, 660,
                                                       text = str("Average time: %.3f s."% round(avg,3)),
                                                       anchor = tk.W,
                                                       font = ('Verdana', 16))
        else:
            if self.player1_shots == 0:
                avg = 0
            else:
                avg = self.player1_time / self.player1_shots
                
            self.C.itemconfig(self.player1_avgtime_txt, text = str("Average time: %.3f s."% round(avg,3)))

        if self.player2_avgtime_txt == None:
            if self.player2_shots == 0:
                avg = 0
            else:
                avg = self.player2_time / self.player2_shots
                
            self.player2_avgtime_txt = self.C.create_text(20, 75,
                                                       text = str("Average time: %.3f s."% round(avg,3)),
                                                       anchor = tk.W,
                                                       font = ('Verdana', 16))
        else:
            if self.player2_shots == 0:
                avg = 0
            else:
                avg = self.player2_time / self.player2_shots
                
            self.C.itemconfig(self.player2_avgtime_txt, text = str("Average time: %.3f s."% round(avg,3)))

        if self.selectedMove == None:
            
            self.selectedMove = self.C.create_oval(self._housesPosition[houseNo][0] - self.sizeSelectedMoveHighlight,
                                    self._housesPosition[houseNo][1] - self.sizeSelectedMoveHighlight,
                                    self._housesPosition[houseNo][0] + self.sizeSelectedMoveHighlight,
                                    self._housesPosition[houseNo][1] + self.sizeSelectedMoveHighlight,
                                    outline = 'red',
                                    width = 5)
        else:
            self.C.itemconfig(self.selectedMove, state = tk.NORMAL)
            self.C.coords(self.selectedMove, 
                          self._housesPosition[houseNo][0] - self.sizeSelectedMoveHighlight,
                          self._housesPosition[houseNo][1] - self.sizeSelectedMoveHighlight,
                          self._housesPosition[houseNo][0] + self.sizeSelectedMoveHighlight,
                          self._housesPosition[houseNo][1] + self.sizeSelectedMoveHighlight)
        time.sleep(self.speed)
        self.C.itemconfig(self.selectedMove, state = tk.HIDDEN)


        for house in range(len(self.player1_board)):            
            self._updateHouse(house, self.player1_board[house])
            
        for house in range(len(self.player2_board)):            
            self._updateHouse(len(self.player2_board) + house, self.player2_board[house])
        
        # give some time for showing the result of the move before updating with next move
        time.sleep(self.speed)
        
        # notify thread waiting for this event they can now proceed
        Application.proceedNextRoundEvent.set()
        
    def displayBoard(self):
        
        output = "     Player 2 -- " + self.player2_name + " -- seeds = " + str(self.player2_seeds) + "\n"
        output += ("+" + "-" * 2) * const.GRID_SIZE +"+\n"
        for i in range(const.GRID_SIZE -1 , -1, -1):
            output += str.format("|%2d"%(i))
        output += "|\n"
        output += ("+" + "-" * 2) * const.GRID_SIZE +"+\n"
        for i in range(const.GRID_SIZE - 1, -1, -1):
            if self.player2_board[i] == 0:
                output += str.format("|%2s"%(""))
            else:            
                output += str.format("|%2d"%(self.player2_board[i]))
                
        output += "|\n"
        output += ("+" + "=" * 2) * const.GRID_SIZE +"+\n"
        for i in range(const.GRID_SIZE):
            if self.player1_board[i] == 0:
                output += str.format("|%2s"%(""))
            else:            
                output += str.format("|%2d"%(self.player1_board[i]))
        output += "|\n"
        output += ("+" + "-" * 2) * const.GRID_SIZE +"+\n"
        for i in range(const.GRID_SIZE):
            output += str.format("|%2d"%(i))    
        output += "|\n"
        output += ("+" + "-" * 2) * const.GRID_SIZE +"+\n"
        output += "     Player 1 -- " + self.player1_name + " -- seeds = " + str(self.player1_seeds) + "\n"
        
        return output
    

    
    def _updateHouse(self, houseNumber, seedsNumber):
        if self._houses[houseNumber] == None:
            self._houses[houseNumber] = self.C.create_image(self._housesPosition[houseNumber][0],
                                                            self._housesPosition[houseNumber][1],
                                                            image = self._houseImages[seedsNumber],
                                                            anchor = tk.CENTER)
        else:
            self.C.itemconfig(self._houses[houseNumber], image  = self._houseImages[seedsNumber])
            
    def initBoards(self):                
        # Initialise board and captured seeds
        self.player1_board   = [const.INITIAL_BEANS]*const.GRID_SIZE
        self.player2_board   = [const.INITIAL_BEANS]*const.GRID_SIZE
        self.player1_seeds = 0
        self.player2_seeds = 0
    
    def getBoardState(self, playerBoard, opponentBoard, playerSeeds = 0, opponentSeeds = 0):
        output = str(playerSeeds) + ", " + str(opponentSeeds) 
        for i in playerBoard:
            output += ", " + str(i)
    
        for i in opponentBoard:
            output += ", " + str(i)
        return output

    def updateMove(self, playerBoard, opponentBoard, move):
        capturedSeeds = 0
        if move in self.getValidMoves(playerBoard, opponentBoard):
            moveResult = self.evaluateMove(playerBoard, opponentBoard, move)
            if moveResult == const.CAPTURE_ALL_MOVE: # cannot capture seeds otherwise starving opponent
                lastSeedBoard, lastSeedHouse = self.sowSeeds(playerBoard, opponentBoard, move)
            elif moveResult == const.VALID_MOVE: #
                lastSeedBoard, lastSeedHouse = self.sowSeeds(playerBoard, opponentBoard, move)
                capturedSeeds = self.captureSeeds(playerBoard, opponentBoard, lastSeedHouse, lastSeedBoard)
            else:
                raise Exception("Unexpected move outcome")
        else:
            raise Exception("Illegal Move!")
        
        return capturedSeeds


    def sowSeeds(self, playerBoard, opponentBoard, move):
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
           
        
    def captureSeeds(self, playerBoard, opponentBoard, lastSeedHouse, lastSeedBoard):  
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
        
                
    def evaluateMove(self, playerBoard, opponentBoard, move):
        
        copyOfPlayerBoard = list(playerBoard)
        copyOfOpponentBoard = list(opponentBoard)
        
        lastSeedBoard, lastSeedHouse = self.sowSeeds(copyOfPlayerBoard, copyOfOpponentBoard, move)
        beansCaptured = self.captureSeeds(copyOfPlayerBoard, copyOfOpponentBoard, lastSeedHouse, lastSeedBoard)
        starved = self.isStarved(copyOfOpponentBoard)
        
        
        if starved and beansCaptured > 0:
    #         print("evaluate move to CAPTURE_ALL_MOVE")
            return const.CAPTURE_ALL_MOVE
        elif starved and beansCaptured == 0:
    #         print("evaluate move to ILLEGAL_MOVE")
            return const.ILLEGAL_MOVE
        else:
    #         print("evaluate move to VALID_MOVE")
            return const.VALID_MOVE 
        
    
    def getValidMoves(self, playerBoard, opponentBoard):
        validMoves = []
        for move in range(const.GRID_SIZE):
            if (playerBoard[move] > 0
                 and self.evaluateMove(playerBoard, opponentBoard, move) != const.ILLEGAL_MOVE):
                validMoves.append(move)
                
        return validMoves
    
    
    def hasValidMove(self, playerBoard, opponentBoard):
        return self.getValidMoves(playerBoard, opponentBoard) != []       
    
    
    def isStarved(self, playerBoard):
        return sum(playerBoard) == 0


    def checkWinner(self, player_seeds):
        # We just need to test whether the number of hits equals the total number of squares in the fleet
        return player_seeds > const.GRID_SIZE * const.INITIAL_BEANS
    
    
    
    def playGame(self, firstPlayer, secondPlayer, turn):
        """
        function handling a game between two players (e.g. one single round).
        @param <BattleshipsGraphics> gui, the graphic interface displaying a round.
        @param <PlayerSocket> firstPlayer, secondPlayer: The player objects.
        @param <int> turn: parameter indicating who is starting the game. 
        if turn == 1 then firstPlayer starts, else if turn == -1 then secondPlayer starts.
        """
            
        boardStates = []
    
        self.initBoards()
    
        boardStates.append(self.getBoardState(self.player1_board, self.player2_board)) 
        
    
        haveWinner = False
        while not haveWinner:
            if turn > 0: # this is the first player turn
                if self.hasValidMove(self.player1_board, self.player2_board):
                    start = time.clock()
                    # ask the player for his/her move
                    move= firstPlayer.chooseMove(self.getBoardState(self.player1_board, 
                                                                    self.player2_board,
                                                                    self.player1_seeds, 
                                                                    self.player2_seeds))
                    
                    end = time.clock()
                    # update the computation time taken by the player since start of game
                    self.player1_time += end - start
                    
                    # Inform the second player of the first player move
                    secondPlayer.getOpponentMove(move, 
                                                 self.getBoardState(self.player2_board, 
                                                                    self.player1_board,
                                                                    self.player2_seeds, 
                                                                    self.player1_seeds))
                    
                    # compute the result of the move and update the captured seeds
                    captured_seeds =  self.updateMove(self.player1_board, self.player2_board, move)
                    self.player1_seeds += captured_seeds
                    
                    # check if we have a winner after the move
                    haveWinner = self.checkWinner(self.player1_seeds)
                    if self.show_output:
                        print("\n\n\t--> Player 1 picks house " + str(move) +" <--\n")
                    
                    # change whose turn it is. negative value means second player turn, 
                    # positive value means first player turn
                    turn *= -1
                    self.player1_shots += 1
                    
                else: # we don't have any valid move so it is the end of the game
                    if self.show_output:
                        print("\n\n\t--> No more valid move for Player 1!       <--")
                        print(    "\t--> Players collect seeds on their side of <--")
                        print(    "\t--> the board!                             <--\n")

                    haveWinner = True
                    
                    # players capture all the seeds in their houses
                    self.player1_seeds += sum(self.player1_board)
                    self.player2_seeds += sum(self.player2_board)
                    self.player1_board   = [0]*const.GRID_SIZE #remove remaining seeds from the board
                    self.player2_board   = [0]*const.GRID_SIZE #remove remaining seeds from the board
                    
                # The turn is finished, so update the GUI
                self.updateBoard(turn, move)
                
                # thread waits until the update from the GUI is finished (on a separate thread)
                Application.proceedNextRoundEvent.wait()
                
                # Display the current state of the board in a textual form
                
            else: # this is the second player turn, for additional comment see the one provided above
                if self.hasValidMove(self.player2_board, self.player1_board):
                    start = time.clock()
                    move = secondPlayer.chooseMove(self.getBoardState(self.player2_board, 
                                                                      self.player1_board,
                                                                      self.player2_seeds, 
                                                                      self.player1_seeds))
    
                    end = time.clock()
                    self.player2_time += end - start
                    
                    firstPlayer.getOpponentMove(move, 
                                                self.getBoardState(self.player1_board, 
                                                                   self.player2_board,
                                                                   self.player1_seeds, 
                                                                   self.player2_seeds))
    
                    captured_seeds =  self.updateMove(self.player2_board, 
                                                      self.player1_board, 
                                                      move)
                    self.player2_seeds += captured_seeds
                    
                    
                    turn *= -1
                    self.player2_shots += 1
                    haveWinner = self.checkWinner(self.player2_seeds)                 
                    if self.show_output:
                        print("\n\n\t--> Player 2 picks house " + str(move) +" <--\n")
                else:
                    if self.show_output:
                        print("\n\n\t--> No more valid move for Player 2!       <--")
                        print("    \t--> Players collect seeds on their side of <--")
                        print("    \t--> the board!                             <--\n")

                    haveWinner = True
                    self.player1_seeds += sum(self.player1_board)
                    self.player2_seeds += sum(self.player2_board)
                    self.player1_board   = [0]*const.GRID_SIZE #remove remaining seeds from the board
                    self.player2_board   = [0]*const.GRID_SIZE #remove remaining seeds from the board
     
                self.updateBoard(turn, move)
                Application.proceedNextRoundEvent.wait()
                
            if self.show_output:
                print(self.displayBoard()) 
                
            # check if the board configuration has been encountered before, e.g. we are looping
            # around. End the game now, and both players capture the seeds in their respective houses
            if (not haveWinner and 
                self.getBoardState(self.player1_board, self.player2_board) in boardStates):
                haveWinner = True
                self.player1_seeds += sum(self.player1_board)
                self.player2_seeds += sum(self.player2_board)
                self.player1_board   = [0]*const.GRID_SIZE #remove remaining seeds from the board
                self.player2_board   = [0]*const.GRID_SIZE #remove remaining seeds from the board
                
                if self.show_output:
                    print("\n\n\t--> ====================================== <--")
                    print("\t--> This Board configuration has already   <--")
                    print("\t--> been encountered, game ends!           <--")
                    print("\t--> Players collect seeds on their side of <--")
                    print("\t--> the board!                             <--")
                    print("\t--> ====================================== <--\n\n")
                self.updateBoard(turn, move)
                Application.proceedNextRoundEvent.wait()
                
                if self.show_output:
                    print(self.displayBoard()) 
                    
            else: # we have not encountered this board configuration yet, so ha it to the list of
                #configurations and continue game
                boardStates.append(self.getBoardState(self.player1_board, self.player2_board))     
                    
    
        # The game is over, we print the result on the command line     
        if self.player2_seeds > self.player1_seeds :
            print ("---------------- player 2 is the winner in " + str(self.player2_shots) + "shots ----------------")
            result = (0,1)
        elif self.player2_seeds < self.player1_seeds :
            print ("---------------- player 1 is the winner in " + str(self.player1_shots) + "shots ----------------")
            result = (1,0)
        else:
            print ("---------------- it's a DRAW in " + str(self.player2_shots) + "shots ----------------")
            result = (1,1)
        
        # The game is finished, so update the GUI
        self.displayWinner(result)
        # thread waits until the update from the GUI is finished (on a separate thread)
        Application.proceedNextRoundEvent.wait()
        time.sleep(self.speed)
        
        return result
    


# Main
    def main(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # Create a socket object
        sock.bind((const.GAME_SERVER_ADDR, const.GAME_SERVER_PORT)) # The same port as used by the server & clients
        sock.listen(2)                                              # Now wait for client connection (max of 2 client at a time).
        while True:
            
            # wait for first client to connect
            client1, addr1 = sock.accept()                          # Establish connection with first client.
            print( 'Got connection from', addr1)
            playerA = PlayerSocket(client1, addr1)                  # Create first player with that connection
            playerA.acknowledgeConnection()
            print ("player",playerA.getName(),"is connected..."  )  
         
            # wait for second client to connect
            client2, addr2 = sock.accept()                          # Establish connection with second client.
            print ('Got connection from', addr2)
            playerB = PlayerSocket(client2, addr2)                  # Create second player with second connection
            playerB.acknowledgeConnection()
            self.player2_name = playerB.getName()
            print ("player",playerB.getName(),"is connected...")
            
            toss = 0 # first connected will be first player
            if self.tossCoin: # choose randomly who will be first player
                toss = random.randint(0,1)
            
            # both client connected, and toss has been done. Start the game now
            if toss == 0:# playerA is first to play
                self.player1_name = playerA.getName()
                self.player2_name = playerB.getName()
                self.displayName()
                Application.proceedNextRoundEvent.wait()
                self.playGame(playerA, playerB, 1)
                playerA.close(self.getBoardState(self.player1_board, 
                                                 self.player2_board,
                                                 self.player1_seeds, 
                                                 self.player2_seeds))   # Close the connection
                playerB.close(self.getBoardState(self.player2_board, 
                                                 self.player1_board, 
                                                 self.player2_seeds, 
                                                 self.player1_seeds))   # Close the connection
                
            else: # playerB is first to play
                self.player1_name = playerB.getName()
                self.player2_name = playerA.getName()
                self.displayName()
                Application.proceedNextRoundEvent.wait()
                self.playGame(playerB, playerA, 1)
                playerB.close(self.getBoardState(self.player1_board, 
                                                 self.player2_board,
                                                 self.player1_seeds, 
                                                 self.player2_seeds))   # Close the connection
                playerA.close(self.getBoardState(self.player2_board, 
                                                 self.player1_board, 
                                                 self.player2_seeds, 
                                                 self.player1_seeds))   # Close the connection
                    
             
            break                                                   # End of game, exit game loop

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
    

# run the server and the GUI        
if __name__ == "__main__":        
    delay = 0
    show_output = False
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],"ts:h:p:",["help","text","speed=","host=", "port="])
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
            show_output = True
        elif opt in ("-s", "--speed"):
            delay = float(arg)
            
    app = Application(speed = delay, show_option = show_output) 
    app.master.title('Sample application') 
    app.mainloop()