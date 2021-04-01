import pygame as p
import Chess_Engine

WIDTH=HEIGHT=512
DIMENSION=8
SQ_SIZE=HEIGHT//DIMENSION
MAX_FPS=100
IMAGES={}
'''
Initialize a global dictionary of images. This is called exactly once
'''
def load_Images():
    pieces=['wp','wR','wN','wB','wQ','wK','bp','bR','bN','bB','bQ','bK']
    for piece in pieces:
        IMAGES[piece]=p.transform.scale(p.image.load("C:/Users/jayan/Coding_Stuff/py_games/Chess/images/"+piece+".png"),(SQ_SIZE,SQ_SIZE))
'''
Main Driver code
Handle user input
Update the graphics
'''
def main():
    p.init()
    screen=p.display.set_mode((WIDTH,HEIGHT))
    clock=p.time.Clock()
    screen.fill(p.Color("white"))
    gs=Chess_Engine.GameState()
    validMoves=gs.getValidMoves()
    animate=False
    moveMade=False
    load_Images()
    running=True
    sqselected=() #keep track of selected square
    playerClicks=[] #keep track of player clicks
    gameOver=False
    player=False
    promotion=False
    while running:
        if gs.whiteToMove==player or True:
            for e in p.event.get():
                if e.type==p.QUIT:
                    running=False
                    p.quit()
                elif e.type == p.MOUSEBUTTONDOWN:
                    if not gameOver:
                        location=p.mouse.get_pos() #(x,y) loaction of mouse
                        col = location[0]//SQ_SIZE
                        row = location[1]//SQ_SIZE
                        if(sqselected==(row,col)):
                            sqselected=()
                            playerClicks=[]
                        elif(len(playerClicks)==0 and gs.board[row][col]=="--"):
                                sqselected=()
                                playerClicks=[]                    
                        else:
                            sqselected=(row,col)
                            playerClicks.append(sqselected)
                        if len(playerClicks) == 2:
                            move=Chess_Engine.Move(playerClicks[0],playerClicks[1],gs.board)
                            for i in range(len(validMoves)):
                                if move == validMoves[i]:
                                    if move.isPawnPromotion:
                                        promotion=True
                                        while promotion:
                                            for e in p.event.get():
                                                
                                                if e.type==p.KEYDOWN:
                                                    if e.key==p.K_q:
                                                        gs.makeMove(move,"Q")
                                                        promotion=False
                                                    if e.key==p.K_r:
                                                        gs.makeMove(move,"R")
                                                        promotion=False
                                                    if e.key==p.K_n:
                                                        gs.makeMove(move,"N")
                                                        promotion=False
                                                    if e.key==p.K_b:
                                                        gs.makeMove(move,"B")
                                                        promotion=False
                                    else:
                                        gs.makeMove(move)
                                    moveMade=True
                                    animate=True
                                    sqselected=()
                                    playerClicks=[]
                                if not moveMade:
                                    playerClicks=[sqselected]
                elif e.type==p.KEYDOWN:
                    if e.key==p.K_z:
                        gs.undoMove()
                        moveMade=True
                        animate=False
                        gameOver=False
                        gs.CheckMate=False
                        gs.StaleMate=False
                    if e.key==p.K_t:
                        gs=Chess_Engine.GameState()
                        validMoves=gs.getValidMoves()
                        animate=False
                        moveMade=False
                        sqselected=() #keep track of selected square
                        playerClicks=[]
                        gameOver=False
                    if e.key==p.K_f:
                        if validMoves:
                            gs.makeMove(validMoves[0])
                            moveMade=True
                            animate=True
        else:
            for e in p.event.get():
                if e.type==p.QUIT:
                    running=False
                    p.quit()
                elif e.type==p.KEYDOWN:
                    if e.key==p.K_z:
                        gs.undoMove()
                        moveMade=True
                        animate=False
                        gameOver=False
                        gs.CheckMate=False
                        gs.StaleMate=False
                    if e.key==p.K_t:
                        gs=Chess_Engine.GameState()
                        validMoves=gs.getValidMoves()
                        animate=False
                        moveMade=False
                        sqselected=() #keep track of selected square
                        playerClicks=[]
                        gameOver=False
                    if e.key==p.K_f:
                        if validMoves:
                            gs.makeMove(validMoves[0])
                            moveMade=True
                            animate=True
            
        if moveMade:
            print(gs.evaluate())
            MM=Chess_Engine.MINIMAX(gs,2)
            if animate:
                animateMove(gs.moveLog[-1],screen,gs.board,clock)
            validMoves=gs.getValidMoves()
            moveMade=False
            animate=False
        drawGameState(screen,gs,validMoves,sqselected)
        if gs.CheckMate:
            gameOver=True
            if gs.whiteToMove:
                drawText(screen,"Black Wins by checkmate")
            else:
                drawText(screen,"White wins by checkmate")
        if gs.StaleMate:
            gameOver=True
            drawText(screen,"Game Drawn due to Stalemate")
        clock.tick(MAX_FPS)
        p.display.flip()
        
def HighlightSquares(screen,gs,validMoves,sqSelected):
    if sqSelected !=():
        r,c,=sqSelected
        color="w" if gs.whiteToMove else "b"
        if gs.board[r][c][0]==color:
            s=p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color("blue"))
            screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow==r and move.startCol==c:
                    screen.blit(s,(SQ_SIZE*move.endCol,SQ_SIZE*move.endRow))
    if gs.inCheck:
        kingRow=gs.whiteKingLocation[0] if gs.whiteToMove else gs.blackKingLocation[0]
        kingCol=gs.whiteKingLocation[1] if gs.whiteToMove else gs.blackKingLocation[1]
        s=p.Surface((SQ_SIZE,SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color("red"))
        screen.blit(s,(kingCol*SQ_SIZE,kingRow*SQ_SIZE))
    if gs.moveLog:
        move=gs.moveLog[-1]
        s=p.Surface((SQ_SIZE,SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color("blue"))
        screen.blit(s,(SQ_SIZE*move.startCol,SQ_SIZE*move.startRow))
        screen.blit(s,(SQ_SIZE*move.endCol,SQ_SIZE*move.endRow))
        
        
        
        
"""
Responsible for all graphics within current game state
"""
def drawGameState(screen,gs,validMoves,sqSelected):
    drawBoard(screen)
    HighlightSquares(screen,gs,validMoves,sqSelected)
    drawPieces(screen,gs.board)

#Draw the sqaures
def drawBoard(screen):
    global colors
    colors=[p.Color("white"),p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color=colors[(r+c)%2]
            p.draw.rect(screen,color,p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

#Draw the peices on the board using current game state
def drawPieces(screen,board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece=board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

                
def animateMove(move,screen,board,clock):
    global colors
    dr=move.endRow-move.startRow
    dc=move.endCol-move.startCol
    framesPerSquare=5
    frameCount=(abs(dr)+abs(dc))*framesPerSquare
    for frame in range(frameCount+1):
        r,c=(move.startRow+ (frame/frameCount)*dr,move.startCol+(frame/frameCount)*dc)
        drawBoard(screen)
        drawPieces(screen,board)
        color=colors[(move.endRow+move.endCol)%2]
        endSquare=p.Rect(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE,SQ_SIZE,SQ_SIZE)
        p.draw.rect(screen,color,endSquare)
        if move.pieceCaptured!="--":
            screen.blit(IMAGES[move.pieceCaptured],endSquare)
        screen.blit(IMAGES[move.pieceMoved],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
        p.display.flip()
        clock.tick(MAX_FPS)

def drawText(screen,text):
    font=p.font.SysFont("Helvitca",32,True,False)
    textObjects=font.render(text,0,p.Color('Gray'))
    textLocation=p.Rect(0,0,WIDTH,HEIGHT).move(WIDTH/2-textObjects.get_width()/2,HEIGHT/2-textObjects.get_height()/2)
    screen.blit(textObjects,textLocation)
    textObjects=font.render(text,0,p.Color("Black"))
    screen.blit(textObjects,textLocation.move(2,2))
if __name__ == "__main__":
    main()