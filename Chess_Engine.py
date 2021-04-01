# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 07:33:52 2020

@author: jayan
"""
import copy
class GameState():
    def __init__(self):
        #2d list each element has two charcarters,b/w indicates Color
        #2nd character indicates the type of piece
        #'--' represents empty space
        self.board=[
                ['bR','bN','bB','bQ','bK','bB','bN','bR'],
                ['bp','bp','bp','bp','bp','bp','bp','bp'],
                ['--','--','--','--','--','--','--','--'],
                ['--','--','--','--','--','--','--','--'],
                ['--','--','--','--','--','--','--','--'],
                ['--','--','--','--','--','--','--','--'],
                ['wp','wp','wp','wp','wp','wp','wp','wp'],
                ['wR','wN','wB','wQ','wK','wB','wN','wR']
            ]
        self.moveFunctions={"p":self.getPawnMoves,"R":self.getRookMoves,"N":self.getKnightMoves,"B":self.getBishopMoves,"Q":self.getQueenMoves,"K":self.getKingMoves}
        self.whiteToMove=True
        self.moveLog=[]
        self.whiteKingLocation=(7,4)
        self.blackKingLocation=(0,4)
        self.inCheck=False
        self.pins=[]
        self.checks=[]
        self.CheckMate=False
        self.StaleMate=False
        self.enpassant=()
        self.currentCastlingRights=CastlingRights(True,True,True,True)
        self.castleRightsLog=[CastlingRights(self.currentCastlingRights.wks,self.currentCastlingRights.wqs,self.currentCastlingRights.bks,self.currentCastlingRights.bqs)]
        self.GameState=1
        self.whitescore=1290
        self.blackscore=1290
    
    def copy(self):
        temp=copy.deepcopy(self)
        return temp

    def makeMove(self,move,Promotion="Q"):
        self.board[move.startRow][move.startCol]= "--"
        self.board[move.endRow][move.endCol]= move.pieceMoved
        self.moveLog.append(move)
        if(move.pieceMoved=="wK"):
            self.whiteKingLocation=(move.endRow,move.endCol)
        elif(move.pieceMoved=="bK"):
            self.blackKingLocation=(move.endRow,move.endCol)
        self.whiteToMove= not self.whiteToMove
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol]="--"
        if move.pieceMoved[1]=="p" and abs(move.startRow-move.endRow)==2:
            self.enpassant=((move.startRow+move.endRow)//2,move.startCol)
        else:
            self.enpassant=()
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol]=move.pieceMoved[0]+Promotion
        if move.isCastle:
            if move.endCol-move.startCol==2:
                self.board[move.startRow][move.endCol-1]=self.board[move.startRow][move.endCol+1]
                self.board[move.startRow][move.endCol+1]="--"
            else:
                self.board[move.startRow][move.endCol+1]=self.board[move.startRow][move.endCol-2]
                self.board[move.startRow][move.endCol-2]="--"
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastlingRights(self.currentCastlingRights.wks,self.currentCastlingRights.wqs,self.currentCastlingRights.bks,self.currentCastlingRights.bqs))


    def undoMove(self):
        if len(self.moveLog) !=0:
            move=self.moveLog.pop()
            self.board[move.endRow][move.endCol]=move.pieceCaptured
            self.board[move.startRow][move.startCol]=move.pieceMoved
            if(move.pieceMoved=="wK"):
                self.whiteKingLocation=(move.startRow,move.startCol)
            elif(move.pieceMoved=="bK"):
                self.blackKingLocation=(move.startRow,move.startCol)
            if move.isEnpassantMove:
                self.board[move.startRow][move.endCol]="wp" if self.whiteToMove else "bp"
            self.whiteToMove= not self.whiteToMove
            self.castleRightsLog.pop()
            self.currentCastlingRights =self.castleRightsLog[-1]
            if move.isCastle:
                if move.endCol-move.startCol==2:
                    self.board[move.startRow][move.endCol+1]=self.board[move.startRow][move.endCol-1]
                    self.board[move.startRow][move.endCol-1]="--"
                else:
                    self.board[move.startRow][move.endCol-2]=self.board[move.startRow][move.endCol+1]
                    self.board[move.startRow][move.endCol+1]="--"
                    
    
    def updateCastleRights(self,move):
        if move.pieceMoved =="wK":
            self.currentCastlingRights.wks=False
            self.currentCastlingRights.wqs=False
        elif move.pieceMoved=="bK":
            self.currentCastlingRights.bks=False
            self.currentCastlingRights.bqs=False
        elif move.pieceMoved == "wR":
            if move.startRow==7:
                if move.startCol==0:
                    self.currentCastlingRights.wqs=False
                elif move.startCol==7:
                    self.currentCastlingRights.wks=False
        elif move.pieceMoved == "bR":
            if move.startRow==0:
                if move.startCol==0:
                    self.currentCastlingRights.bqs=False
                elif move.startCol==7:
                    self.currentCastlingRights.bks=False
        
    def getValidMoves(self):
        moves=[]
        self.inCheck,self.pins,self.checks=self.checkForPinsAndChecks()        
        if self.whiteToMove:
            kingRow=self.whiteKingLocation[0]
            kingCol=self.whiteKingLocation[1]
        else:
            kingRow=self.blackKingLocation[0]
            kingCol=self.blackKingLocation[1]
            
        if self.inCheck:
            if len(self.checks)==1:
                moves=self.getAllMoves()
                check=self.checks[0]
                checkRow=check[0]
                checkCol=check[1]
                pieceChecking=self.board[checkRow][checkCol]
                validSquares=[]
                if pieceChecking[1]=="N":
                    validSquares=[(checkRow,checkCol)]
                else:
                    for i in range(1,8):
                        validSquare=(kingRow+check[2]*i,kingCol+check[3]*i)
                        validSquares.append(validSquare)
                        if validSquare[0]==checkRow and validSquare[1]==checkCol:
                            break
                for i in range(len(moves)-1,-1,-1):
                    if moves[i].pieceMoved[1]=="K":
                        continue
                    if not (moves[i].endRow,moves[i].endCol) in validSquares:
                        moves.remove(moves[i])
            else:
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves=self.getAllMoves()
            self.getCastleMoves(kingRow,kingCol, moves)
        if not moves:
            if self.inCheck:
                self.CheckMate=True
            else:
                self.StaleMate=True
        return moves

    def checkForPinsAndChecks(self):
        pins=[]
        checks=[]
        inCheck=False
        if self.whiteToMove:
            enemyColor="b"
            allyColor="w"
            startRow=self.whiteKingLocation[0]
            startCol=self.whiteKingLocation[1]
        else:
            enemyColor="w"
            allyColor="b"
            startRow=self.blackKingLocation[0]
            startCol=self.blackKingLocation[1]
        directions=((-1,0),(1,0),(0,-1),(0,1),(1,1),(1,-1),(-1,1),(-1,-1))
        for j in range(len(directions)):
            d=directions[j]
            possiblePin=()
            for i in range(1,8):
                endRow=startRow+d[0]*i
                endCol=startCol+d[1]*i
                if 0<=endRow<8 and 0<=endCol<8:
                    endPiece=self.board[endRow][endCol]
                    if(endPiece[0]==allyColor and endPiece[1]!="K"):
                        if possiblePin==():
                            possiblePin=(endRow,endCol,d[0],d[1])
                        else:
                            break
                    elif endPiece[0]==enemyColor:
                        typ=endPiece[1]
                        if(0<=j<=3 and typ=="R") or \
                            (4<=j<=7 and typ=="B") or \
                            (typ=="Q") or (i==1 and typ=="K") or \
                            (i==1 and typ=="p" and ((enemyColor=="w" and 4<=j<=5) or (enemyColor=="b" and 6<=j<=7))):
                                if possiblePin==():
                                    inCheck=True
                                    checks.append((endRow,endCol,d[0],d[1]))
                                else:
                                    pins.append(possiblePin)
                                    break
                        else:
                            break
                else:
                    break
        knightMoves=[(-2,-1),(-2,1),(2,-1),(2,1),(1,-2),(1,2),(-1,-2),(-1,2)]
        for i in range(8):
            d=knightMoves[i]
            endRow=startRow+d[0]
            endCol=startCol+d[1]
            if 0<=endRow<8 and 0<=endCol<8:
                endPiece=self.board[endRow][endCol]
                if(endPiece[0]==enemyColor and endPiece[1]=="N"):
                    inCheck=True
                    checks.append((endRow,endCol,d[0],d[1]))
        return inCheck,pins,checks

    def getAllMoves(self):
        moves=[]
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn=="w" and self.whiteToMove) or (turn=="b" and not self.whiteToMove):
                    piece=self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves)
        return moves

    def getPawnMoves(self,r,c,moves):
        piecePinned=False
        pinDirection=()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piecePinned=True
                pinDirection=(self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
            
        if self.whiteToMove:
            if self.board[r-1][c]=="--":
                if not piecePinned or pinDirection==(-1,0):
                    moves.append(Move((r,c),(r-1,c),self.board))
                    if r==6 and self.board[r-2][c]=="--":
                        moves.append(Move((r,c),(r-2,c),self.board))
            if c!=7:
                if self.board[r-1][c+1][0]=="b":
                    if not piecePinned or pinDirection==(-1,1):
                        moves.append(Move((r,c),(r-1,c+1),self.board))
                elif (r-1,c+1)==self.enpassant and r==3:
                    if not piecePinned or pinDirection==(-1,1):
                        moves.append(Move((r,c),(r-1,c+1),self.board))
                    
            if c!=0:
                if self.board[r-1][c-1][0]=="b":
                    if not piecePinned or pinDirection==(-1,-1):
                        moves.append(Move((r,c),(r-1,c-1),self.board))
                elif (r-1,c-1)==self.enpassant and r==3:
                    if not piecePinned or pinDirection==(-1,-1):
                        moves.append(Move((r,c),(r-1,c-1),self.board))
        else:
            if self.board[r+1][c]=="--":
                if not piecePinned or pinDirection==(1,0):
                    moves.append(Move((r,c),(r+1,c),self.board))
                    if r==1 and self.board[r+2][c]=="--":
                        moves.append(Move((r,c),(r+2,c),self.board))
            if c!=7:
                if self.board[r+1][c+1][0]=="w":
                    if not piecePinned or pinDirection==(1,1):
                        moves.append(Move((r,c),(r+1,c+1),self.board))
                elif (r+1,c+1)==self.enpassant and r==4:
                    if not piecePinned or pinDirection==(1,1):
                        moves.append(Move((r,c),(r+1,c+1),self.board))
            if c!=0:
                if self.board[r+1][c-1][0]=="w":
                    if not piecePinned or pinDirection==(1,-1):
                        moves.append(Move((r,c),(r+1,c-1),self.board))
                elif (r+1,c-1)==self.enpassant and r==4:
                    if not piecePinned or pinDirection==(1,-1):
                        moves.append(Move((r,c),(r+1,c-1),self.board))
    
    def getRookMoves(self,r,c,moves):
        piecePinned=False
        pinDirection=()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piecePinned=True
                pinDirection=(self.pins[i][2],self.pins[i][3])
                if not self.board[r][c][1]=="Q":
                    self.pins.remove(self.pins[i])
                break
        directions=((-1,0),(0,-1),(0,1),(1,0))
        color="w" if self.whiteToMove else "b"
        for d in directions:
            if not piecePinned or pinDirection==d or (pinDirection[0]==-d[0] and pinDirection[1]==-d[1]):
                for i in range(1,8):
                    endRow=r+d[0]*i
                    endCol=c+d[1]*i
                    if (0<=endRow<8) and (0<=endCol<8):
                        if(self.board[endRow][endCol][0]=="-"):
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                        elif(self.board[endRow][endCol][0]!=color):
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                            break
                        else:
                            break
                    else:
                        break
    
    def getKnightMoves(self,r,c,moves):
        piecePinned=False
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piecePinned=True
                self.pins.remove(self.pins[i])
                break
        if not piecePinned:
            color="w" if self.whiteToMove else "b"
            movers=[[r-2,c-1],[r-2,c+1],[r+2,c+1],[r+2,c-1],[r-1,c+2],[r-1,c-2],[r+1,c+2],[r+1,c-2]]
            for k in movers:
                i=k[0]
                j=k[1]
                if i<8 and i>-1 and j<8 and j>-1:
                    if(self.board[i][j][0]!=color):
                        moves.append(Move((r,c),(i,j),self.board))
    
    def getBishopMoves(self,r,c,moves):
        piecePinned=False
        pinDirection=()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piecePinned=True
                pinDirection=(self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        color="w" if self.whiteToMove else "b"
        directions=((-1,-1),(-1,1),(1,-1),(1,1))
        for d in directions:
            if not piecePinned or pinDirection==d or (pinDirection[0]==-d[0] and pinDirection[1]==-d[1]):
                for i in range(1,8):
                    endRow=r+d[0]*i
                    endCol=c+d[1]*i
                    if (0<=endRow<8) and (0<=endCol<8):
                        if(self.board[endRow][endCol][0]=="-"):
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                        elif(self.board[endRow][endCol][0]!=color):
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                            break
                        else:
                            break
                    else:
                        break            
    
    def getQueenMoves(self,r,c,moves):
        piecePinned=False
        pinDirection=()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piecePinned=True
                pinDirection=(self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        color="w" if self.whiteToMove else "b"
        directions=((-1,-1),(-1,1),(1,-1),(1,1),(-1,0),(1,0),(0,-1),(0,1))
        for d in directions:
            if not piecePinned or pinDirection==d or (pinDirection[0]==-d[0] and pinDirection[1]==-d[1]):
                for i in range(1,8):
                    endRow=r+d[0]*i
                    endCol=c+d[1]*i
                    if (0<=endRow<8) and (0<=endCol<8):
                        if(self.board[endRow][endCol][0]=="-"):
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                        elif(self.board[endRow][endCol][0]!=color):
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                            break
                        else:
                            break
                    else:
                        break  
    def getKingMoves(self,r,c,moves):
        rowMoves=(-1,-1,-1,0,0,1,1,1)
        colMoves=(-1,0,1,-1,1,-1,0,1)
        allyColor="w" if self.whiteToMove else "b"
        for i in range(8):
            endRow=r+rowMoves[i]
            endCol=c+colMoves[i]
            if 0<=endRow<8 and 0<=endCol<8:
                endPiece=self.board[endRow][endCol]
                if endPiece[0]!=allyColor:
                    if allyColor=="w":
                        self.whiteKingLocation=(endRow,endCol)
                    else:
                        self.blackKingLocation=(endRow,endCol)
                    inCheck,pins,checks=self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    if allyColor=="w":
                        self.whiteKingLocation=(r,c)
                    else:
                        self.blackKingLocation=(r,c)
        
    def getCastleMoves(self,r,c,moves):
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r,c,moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r,c,moves)
    
    def getKingsideCastleMoves(self,r,c,moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2]=="--":
            if not self.squareUnderAttack(r,c+1) and not self.squareUnderAttack(r,c+2):
                moves.append(Move((r,c),(r,c+2),self.board))
    
    def getQueensideCastleMoves(self,r,c,moves):
        if self.board[r][c-1]=="--" and self.board[r][c-2]=="--" and self.board[r][c-3]=="--":
            if not self.squareUnderAttack(r,c-1) and not self.squareUnderAttack(r,c-2):
                moves.append(Move((r,c),(r,c-2),self.board))
    
    def squareUnderAttack(self,r,c):
        self.whiteToMove=not self.whiteToMove
        moves=self.getAllMoves()
        self.whiteToMove=not self.whiteToMove
        for i in moves:
            if(i.endRow==r and i.endCol==c):
                return True
        return False
    def evaluate(self):
        material=self.material_Count(1)-self.material_Count(0)
        positional_adv=0
        for i in range(8):
            for j in range(8):
                peice=self.board[i][j][1]
                if(peice=="p"):
                    positional_adv+=self.Pawn_eval(i,j)
                elif(peice=="R"):
                    positional_adv+=self.Rook_eval(i, j)
#        if(k==1):
            #reward central pawns
            #punish undeveloped peices
            #punish Knights if at edge of board
            #punish low mobility peices with 30% value
#            pass
#        if(k==2):
            #punish low mobility peices with 30% value
            #punish undeveloped peices
            #punish Knights if at edge of board
#            pass
#        if(k==3):
            #punish low mobility peices with 30% value
            #punish undeveloped peices
            #punish Knights if at edge of board
        return material+positional_adv
    
    def Pawn_eval(self,i,j):
        value=0.0
        k=[(3,3),(3,4),(4,3),(4,4)]
        if self.board[i][j]=="wp":
            value+=0.1*((abs(j-1))**0.5)
            if (i,j) in k:
                if self.GameState==1:
                    value+=0.2
            elif self.board[i][j]=="bp":
                value-=0.1*((abs(6-j))**0.5)
                if (i,j) in k:
                    if self.GameState==1:
                        value-=0.3
        return value
    
    def Rook_eval(self,i,j):
        value=0
        if self.GameState==1:
            return value
        direct=((0,1),(0,-1),(1,0),(-1,0))
        k=1 if(self.board[i][j][0]=="w") else -1
        for d in direct:
            for z in range(8):
                endRow=i + (z*d[0])
                endCol=j + (z*d[1])
                if(i<8 and j<8 and i>-1 and j>-1):
                    break
                elif(self.board[endRow][endCol][0]==self.board[i][j][0]):
                    break
                elif(self.board[endRow][endCol][0]=="-"):
                    value+=0.1*k
                else:
                    value+=0.1*k
                    break
    def material_Count(self,turn):
        color="w" if turn else "b"
        if self.CheckMate:
            if color=="w":
                return -1000000
            else:
                return 1000000
        value={"K":0,"Q":9,"R":5,"N":3,"B":3,"p":1}
        count=0
        for i in self.board:
            for j in i:
                if j[0]==color:
                    count+=value[j[1]]
        return count
    
class CastlingRights():
    def __init__(self,wks,wqs,bks,bqs):
        self.wks=wks
        self.bks=bks
        self.wqs=wqs
        self.bqs=bqs
class Move():
    ranksToRows={"1":7,"2":6,"3":5,"4":4,"5":3,"6":2,"7":1,"8":0}
    rowsToRanks={v:k for k,v in ranksToRows.items()}
    filesToCols={"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}
    colsToFiles={v:k for k,v in filesToCols.items()}
    
    def __init__(self,startSq,endSq,board):
        self.startRow=startSq[0]
        self.startCol=startSq[1]
        self.endRow=endSq[0]
        self.endCol=endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured=board[self.endRow][self.endCol]
        self.moveID = self.startRow*1000 + self.startCol*100 + self.endRow*10 +self.endCol
        self.isPawnPromotion=((self.pieceMoved=="wp" and self.endRow==0) or (self.pieceMoved=="bp" and self.endRow==7))
        self.isEnpassantMove=(self.pieceMoved[1]=="p" and self.pieceCaptured=="--" and self.endCol!=self.startCol)
        if self.pieceMoved[1]=="K" and (self.endCol-self.startCol==-2 or self.endCol-self.startCol==2):
            self.isCastle=True
        else:
            self.isCastle=False
    
    def __eq__(self,other):
        if isinstance(other,Move):
            return self.moveID==other.moveID
        return False
    def getChessNotation(self):
        if self.isCastle:
            return "O-O"
        capture=""
        if(self.isEnpassantMove):
            return self.getRankFiles(0,self.starit.col)[0]+"X"+self.getRankFiles(self.endRow,self.endCol)
        if(self.pieceCaptured!="--"):
            capture="X"
        if self.pieceMoved[1]!='p':
            return self.pieceMoved[1]+capture+self.getRankFiles(self.endRow,self.endCol)
        else:
            if capture=="X":
                return self.getRankFiles(0,self.startCol)[0]+capture+self.getRankFiles(self.endRow,self.endCol)
            return self.getRankFiles(self.endRow,self.endCol)
    
    def getRankFiles(self,r,c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

class MINIMAX():
    def __init__(self,gs,depth):
        self.gs=gs
        self.children=[]
        self.depth=depth
        self.eval=0
        if(depth==0):
            self.eval=self.gs.evaluate()
        else:
            vald=gs.getValidMoves()
            for i in vald:
                T=gs.copy()
                T.makeMove(i)
                self.children.append(MINIMAX(T, depth-1))
    