import pygame as p
import engine,move_finder
from multiprocessing import Process,Queue


BOARD_WIDTH=BOARD_HEIGHT=720
MOVELOG_PANEL_WIDTH=250
MOVELOG_PANEL_HEIGHT=BOARD_HEIGHT
DIMESION=8
SQ_SIZE=BOARD_WIDTH//DIMESION
MAX_FPS=30
IMAGES={}


def main():
    p.init()
    screen=p.display.set_mode((BOARD_WIDTH+MOVELOG_PANEL_WIDTH,BOARD_HEIGHT))
    clock=p.time.Clock()
    screen.fill(p.Color('white'))
    movelog_font=p.font.SysFont("Helvetica",24,False,False)
    gs=engine.GameState()
    valid_moves=gs.get_valid_moves()
    animate=False
    move_made=False
    load_images()
    running=True
    sq_selected=()
    player_clicks=[]
    game_over=False
    player_one=True
    player_two=False
    ai_thinking=False
    move_finder_process=None
    while running:
        human_turn= (gs.white_to_move and player_one) or (not gs.white_to_move and player_two)
        for e in p.event.get():
            if e.type==p.QUIT:
                running=False
                p.quit()
            elif e.type==p.MOUSEBUTTONDOWN:
                if not game_over and human_turn:
                    location=p.mouse.get_pos()
                    col=location[0]//SQ_SIZE
                    row=location[1]//SQ_SIZE
                    if sq_selected==(row,col) or col>=8:
                        sq_selected=()
                        player_clicks=[]
                    elif len(player_clicks)==0 and gs.board[row][col]=="-":
                        player_clicks=[]
                        sq_selected=()
                    else:
                        sq_selected=(row,col)
                        player_clicks.append(sq_selected)
                    if len(player_clicks)==2:
                        move=engine.Move(player_clicks[0],player_clicks[1],gs.board)
                        for i in range(len(valid_moves)):
                            if move==valid_moves[i]:
                                gs.make_move(move)
                                move_made=True
                                animate=True
                                sq_selected=()
                                player_clicks=[]
                        if not move_made:
                            player_clicks=[sq_selected]
            elif e.type==p.KEYDOWN:
                if e.key==p.K_z:
                    gs.undo_move()
                    move_made=True
                    animate=False
                    game_over=False
                elif e.key==p.K_t:
                    gs=engine.GameState()
                    valid_moves=gs.get_valid_moves()
                    animate=False
                    move_made=False
                    sq_selected=()
                    player_clicks=[]
                    game_over=False
        
        if not game_over and not human_turn:
            ai_move=move_finder.find_best_move(gs,valid_moves)
            if ai_move is None:
                ai_move=move_finder.find_random_move(valid_moves)
            gs.make_move(ai_move)
            move_made=True
            animate=True

        if move_made:
            if animate:
                animate_move(gs.move_log[-1],screen,gs.board,clock)
            valid_moves=gs.get_valid_moves()
            move_made=False
            animate=False
        draw_gamestate(screen,gs,valid_moves,movelog_font,sq_selected)
        if gs.check_mate:
            game_over=True
            text="Black Wins by checkmate" if gs.white_to_move else "White wins by checkmate"
            draw_endgame_text(screen,text)
        if gs.stale_mate:
            game_over=True
            text="Stalemate"
            draw_endgame_text(screen,text)
        clock.tick(MAX_FPS)
        p.display.flip()



'''Graphics'''

def animate_move(move,screen,board,clock):
    '''animates the move made'''
    global colors
    dr=move.end_row-move.start_row
    dc=move.end_col-move.start_col
    frame_count=5
    for frame in range(frame_count+1):
        r,c=(move.start_row+(frame/frame_count)*dr,move.start_col+(frame/frame_count)*dc)
        draw_board(screen)
        draw_pieces(screen,board)
        color=colors[(move.end_row+move.end_col)%2]
        end_square=p.Rect(move.end_col*SQ_SIZE,move.end_row*SQ_SIZE,SQ_SIZE,SQ_SIZE)
        p.draw.rect(screen,color,end_square)
        if move.piece_captured!="-":
            screen.blit(IMAGES[move.piece_captured],end_square)
        screen.blit(IMAGES[move.piece_moved],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
        p.display.flip()
        clock.tick(MAX_FPS)

def draw_gamestate(screen,gs,valid_moves,font,sq_selected):
    '''Draws the board, pieces, highlights squares etc'''
    draw_board(screen)
    highlight_sqaures(screen,gs,valid_moves,sq_selected)
    draw_pieces(screen,gs.board)
    draw_move_log(screen,gs,font)

def draw_pieces(screen,board):
    '''Draws the pieces on the board drawn'''
    for r in range(DIMESION):
        for c in range(DIMESION):
            piece=board[r][c]
            if piece!='-':
                screen.blit(IMAGES[piece],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def draw_board(screen):
    '''Draws the Chess Board'''
    global colors
    colors=[p.Color("white"),p.Color("gray")]
    for r in range(DIMESION):
        for c in range(DIMESION):
            color=colors[(r+c)%2]
            p.draw.rect(screen,color,p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def draw_endgame_text(screen,text):
    '''draws the endgame text when game is over'''
    font=p.font.SysFont("Helvitca",32,True,False)
    text_objects=font.render(text,0,p.Color('Gray'))
    text_location=p.Rect(0,0,BOARD_WIDTH,BOARD_HEIGHT).move(BOARD_WIDTH/2-text_objects.get_width()/2,BOARD_HEIGHT/2-text_objects.get_height()/2)
    screen.blit(text_objects,text_location)
    text_objects=font.render(text,0,p.Color("Black"))
    screen.blit(text_objects,text_location.move(2,2))

def draw_move_log(screen,gs,font):
    '''Draws the move-log of the game'''
    movelog_rect=p.Rect(BOARD_WIDTH,0,MOVELOG_PANEL_WIDTH,MOVELOG_PANEL_HEIGHT)
    p.draw.rect(screen,p.Color("black"),movelog_rect)
    movelog=gs.move_log
    padding=5
    textX=padding
    textY=padding
    number=gs.move_count - len(movelog)//2
    for i in movelog:
        text=i.get_chess_notation()
        text_location=movelog_rect.move(textX,textY)
        if i.piece_moved in "RNBQKP":
            text=str(number)+". "+text
            textX=padding*20
        else:
            text=" "+text
            textX=padding
            textY+=text_object.get_height()
            number+=1
        text_object=font.render(text,False,p.Color('white'))
        screen.blit(text_object,text_location)


def highlight_sqaures(screen,gs,valid_moves,sq_selected):
    '''Highlights a selected Square'''
    if sq_selected:
        r,c=sq_selected
        s=p.Surface((SQ_SIZE,SQ_SIZE))
        s.set_alpha((100))
        s.fill(p.Color("blue"))
        screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))
        s.fill(p.Color("yellow"))
        for move in valid_moves:
            if move.start_row==r and move.start_col==c:
                screen.blit(s,(SQ_SIZE*move.end_col,SQ_SIZE*move.end_row))
    if gs.in_check:
        king_row,king_col=gs.white_king_location if gs.white_to_move else gs.black_king_location
        s=p.Surface((SQ_SIZE,SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color("red"))
        screen.blit(s,(king_col*SQ_SIZE,king_row*SQ_SIZE))
    
    if gs.move_log:
        move=gs.move_log[-1]
        s=p.Surface((SQ_SIZE,SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color("blue"))
        screen.blit(s,(SQ_SIZE*move.start_col,SQ_SIZE*move.start_row))
        screen.blit(s,(SQ_SIZE*move.end_col,SQ_SIZE*move.end_row))

def load_images():
    '''Loads images as objects into IMAGES dictionary'''
    images=['wp','wR','wN','wB','wQ','wK','bp','bR','bN','bB','bQ','bK']
    mapping={'wp':'P','wR':'R','wN':'N','wB':'B','wQ':'Q','wK':'K','bp':'p','bR':'r','bN':'n','bB':'b','bQ':'q','bK':'k'}
    for image in images:
        IMAGES[mapping[image]]=p.transform.scale(p.image.load("C:/Users/jayan/Coding_Stuff/py_games/Chess_Latest/images/"+image+".png"),(SQ_SIZE,SQ_SIZE))


def print_board(board):
    for i in board:
        print(i)
    print("-----------------------------\n")

if __name__=="__main__":
    main()
