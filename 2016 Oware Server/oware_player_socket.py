'''
Created on 7 Aug 2014

@author: Lilian
'''
class PlayerSocket(object):
    """
    class used for calling functions from the client player. This represents the communication protocol between 
    server and client. To synchronise the client and the server, each request from the server expect a reply from 
    the client.
    """
    
    def __init__(self, playerSocket, playerAddress):
        self._socket = playerSocket
        self._addr = playerAddress
        self._name = ""
        self._description = ""
        
    def acknowledgeConnection(self):
        self._socket.send("CONNECTED".encode())
        return self._socket.recv(1024).decode() # used for client/server synchronisation purpose
        
    def newPlayer(self, name):
        self._socket.send(("NEW_PLAYER, " + name).encode())
        return self._socket.recv(1024).decode()
        

    def newRound(self):
        self._socket.send("NEW_ROUND".encode())
        return self._socket.recv(1024).decode()
    
    def getName(self):
        if self._name == "":
            self._socket.send("GET_NAME".encode())
            self._name = self._socket.recv(1024).decode()
        
        return self._name

    def getDescription(self):
        if self._description == "":
            self._socket.send("GET_DESCRIPTION".encode())
            self._description = self._socket.recv(1024).decode()
        
        return self._description
    
    
    def chooseMove(self, boardState):
        self._socket.send(("CHOOSE_MOVE," + boardState).encode())
        return int(self._socket.recv(1024).decode())
    
     
    def getOpponentMove(self, move, boardState):
        self._socket.send(("GET_OPPONENT_MOVE, "+str(move)+", "+boardState).encode())
        return self._socket.recv(1024).decode()
            
    def close(self, boardState):
        self._socket.send(("GAME_OVER"+", "+boardState).encode())
        self._socket.recv(1024).decode() # used for client/server synchronisation purpose
        self._socket.close()
    
    