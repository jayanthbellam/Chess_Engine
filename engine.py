class GameState():
    white_pieces='PRNBQK'
    black_pieces='prnbqk'
    def __init__(self,fen_notation="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        self.board=[['-','-','-','-','-','-','-','-'],
                    ['-','-','-','-','-','-','-','-'],
                    ['-','-','-','-','-','-','-','-'],
                    ['-','-','-','-','-','-','-','-'],
                    ['-','-','-','-','-','-','-','-'],
                    ['-','-','-','-','-','-','-','-'],
                    ['-','-','-','-','-','-','-','-'],
                    ['-','-','-','-','-','-','-','-']]
        self.white_to_move=True
        self.half_move=0
        self.move_count=1
        self.white_king_location=[0,4]
        self.black_king_location=[7,4]
        self.move_functions={"p":self.get_pawn_moves,"P":self.get_pawn_moves,"R":self.get_rook_moves,"r":self.get_rook_moves,"N":self.get_knight_moves,"n":self.get_knight_moves,"B":self.get_bishop_moves,"b":self.get_bishop_moves,"q":self.get_queen_moves,"Q":self.get_queen_moves,"k":self.get_king_moves,"K":self.get_king_moves}
        self.move_log=[]
        self.current_castling_rights=CastlingRights(True,True,True,True)
        self.castle_log=[CastlingRights(self.current_castling_rights.wks,self.current_castling_rights.wqs,self.current_castling_rights.bks,self.current_castling_rights.bqs)]
        self.enpassant=()
        self.enpassant_log=[]
        self.pins=[]
        self.checks=[]
        self.in_check=False
        self.check_mate=False
        self.stale_mate=False
        if fen_notation:
            fen_mod=fen_notation.split('/')
            last=fen_mod[-1]
            fen_mod.pop()
            fen_mod+=last.split()
        FEN(self,fen_mod)

    def make_move(self,move,promotion=None):
        '''Makes the move on the board'''
        promotion="q" if move.piece_moved in self.black_pieces else "Q"
        self.board[move.start_row][move.start_col]="-"
        self.board[move.end_row][move.end_col]=move.piece_moved
        self.move_log.append(move)
        self.enpassant_log.append(self.enpassant)
        if move.piece_moved=="K":
            self.white_king_location=(move.end_row,move.end_col)
        elif move.piece_moved=="k":
            self.black_king_location=(move.end_row,move.end_col)
        if move.enpassant_move:
            self.board[move.start_row][move.end_col]="-"
        if move.piece_moved in ["p","P"] and abs(move.start_row-move.end_row)==2:
            self.enpassant=((move.start_row+move.end_row)//2,move.start_col)
        else:
            self.enpassant=()
        if move.pawn_promotion:
            self.board[move.end_row][move.end_col]=promotion
        if move.castle_move:
            if move.end_col-move.start_col==2:
                self.board[move.start_row][move.end_col-1]=self.board[move.start_row][move.end_col+1]
                self.board[move.start_row][move.end_col+1]="-"
            else:
                self.board[move.start_row][move.end_col+1]=self.board[move.start_row][move.end_col-2]
                self.board[move.start_row][move.end_col-2]="-"
        if not self.white_to_move:
            self.move_count+=1
        if move.piece_captured=="-" or not move.piece_moved in ["p","P"]:
            self.half_move+=1
        else:
            self.half_move=0
        self.white_to_move=not self.white_to_move
        self.update_catle_rights(move)
        self.castle_log.append(CastlingRights(self.current_castling_rights.wks,self.current_castling_rights.wqs,self.current_castling_rights.bks,self.current_castling_rights.bqs))

    def undo_move(self):
        '''Undo the last move made'''
        if self.move_log:
            self.check_mate=False
            self.stale_mate=False
            move=self.move_log.pop()
            if self.white_to_move:
                self.move_count-=1
            self.board[move.end_row][move.end_col]=move.piece_captured
            self.board[move.start_row][move.start_col]=move.piece_moved
            if move.piece_moved=="k":
                self.black_king_location=(move.start_row,move.start_col)
            elif move.piece_moved=="K":
                self.white_king_location=(move.start_row,move.start_col)
            self.white_to_move=not self.white_to_move
            self.castle_log.pop()
            self.current_castling_rights=self.castle_log[-1]
            self.enpassant=self.enpassant_log.pop()
            if move.castle_move:
                if move.end_col-move.start_col==2:
                    self.board[move.start_row][move.end_col+1]=self.board[move.start_row][move.end_col-1]
                    self.board[move.start_row][move.end_col-1]="-"
                else:
                    self.board[move.start_row][move.end_col-2]=self.board[move.start_row][move.end_col+1]
                    self.board[move.start_row][move.end_col+1]="-"
            if move.enpassant_move:
                self.board[move.start_row][move.end_col]="p" if self.white_to_move else "P"
    
    def update_catle_rights(self,move):
        if move.piece_moved=="K":
            self.current_castling_rights.wks=False
            self.current_castling_rights.wqs=False
        elif move.piece_moved=="k":
            self.current_castling_rights.bks=False
            self.current_castling_rights.bqs=False
        elif move.piece_moved=="R" and move.start_row==7:
            if move.start_col==0:
                self.current_castling_rights.wqs=False
            elif move.start_col==7:
                self.current_castling_rights.wks=False
        elif move.piece_moved=="r" and move.start_row==0:
            if move.start_col==0:
                self.current_castling_rights.bqs=False
            elif move.start_col==7:
                self.current_castling_rights.bks=False
    
    def get_valid_moves(self):
        '''Returns all the valid moves possible from the given game state'''
        moves=[]
        self.in_check,self.pins,self.checks=self.check_for_pins_and_checks()
        king_row,king_col=self.white_king_location if self.white_to_move else self.black_king_location
        
        if self.in_check:
            if len(self.checks)==1:
                moves=self.get_all_moves()
                check=self.checks[0]
                check_row=check[0]
                check_col=check[1]
                piece_checking=self.board[check_row][check_col]
                valid_sqaures=[]
                if piece_checking in ['n',"N"]:
                    valid_sqaures=[(check_row,check_col)]
                else:
                    for i in range(1,8):
                        valid_sqaure=(king_row+check[2]*i,king_col+check[3]*i)
                        valid_sqaures.append(valid_sqaure)
                        if valid_sqaure[0]==check_row and valid_sqaure[1]==check_col:
                            break
                for i in range(len(moves)-1,-1,-1):
                    if moves[i].piece_moved in ["K","k"]:
                        continue
                    if not (moves[i].end_row,moves[i].end_col) in  valid_sqaures:
                        moves.remove((moves[i]))
            else:
                self.get_king_moves(king_row,king_col,moves)
        else:
            moves=self.get_all_moves()
            self.get_castle_moves(king_row,king_col,moves)
        if not moves:
            if self.in_check:
                self.check_mate=True
            else:
                self.stale_mate=True
        return moves

    def check_for_pins_and_checks(self):
        '''Returns if in_check(true if king in check else false),pins,checks'''
        pins=[]
        checks=[]
        in_check=False
        if self.white_to_move:
            enemy_pieces='rnbqkp'
            ally_pieces='RNBQKP'
            start_row=self.white_king_location[0]
            start_col=self.white_king_location[1]
        else:
            ally_pieces='rnbqkp'
            enemy_pieces='RNBQKP'
            start_row=self.black_king_location[0]
            start_col=self.black_king_location[1]
        directions=[(-1,0),(1,0),(0,-1),(0,1),(1,1),(1,-1),(-1,1),(-1,-1)]
        for j in range(len(directions)):
            d=directions[j]
            possible_pin=()
            for i in range(1,8):
                end_row=start_row+d[0]*i
                end_col=start_col+d[1]*i
                if not(0<=end_row<8 and 0<=end_col<8):
                    break
                end_piece=self.board[end_row][end_col]
                if end_piece in ally_pieces and end_piece not in ['k','K']:
                    if possible_pin:
                        break
                    possible_pin=(end_row,end_col,d[0],d[1])
                elif end_piece in enemy_pieces:
                    if(0<=j<=3 and end_piece in ["R","r"]) or \
                            (4<=j<=7 and end_piece in ["B","b"]) or \
                            (end_piece in ["Q","q"]) or (i==1 and end_piece in ["K","k"]) or \
                            (i==1 and end_piece in ["p","P"] and (("K" in enemy_pieces and 4<=j<=5) or ("k" in enemy_pieces and 6<=j<=7))):
                        if possible_pin==():
                            in_check=True
                            checks.append((end_row,end_col,d[0],d[1]))
                        else:
                            pins.append(possible_pin)
                            break
                    else:
                        break
        knight_moves=[(-2,-1),(-2,1),(2,-1),(2,1),(1,-2),(1,2),(-1,-2),(-1,2)]
        for i in range(8):
            d=knight_moves[i]
            end_row=start_row+d[0]
            end_col=start_col+d[1]
            if 0<=end_row<8 and 0<=end_col<8:
                end_piece=self.board[end_row][end_col]
                if(end_piece in enemy_pieces and end_piece in ["N","n"]):
                    in_check=True
                    checks.append((end_row,end_col,d[0],d[1]))
        return in_check,pins,checks
    
    def get_all_moves(self):
        '''all moves without taking Catling moves,pins and checks into account'''
        moves=[]
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                if (self.white_to_move and self.board[r][c] in self.white_pieces) or (not self.white_to_move and self.board[r][c] in self.black_pieces):
                    piece=self.board[r][c]
                    self.move_functions[piece](r,c,moves)
        return moves
    
    def get_pawn_moves(self,r,c,moves):
        '''all the possible moves for the given pawn'''
        piece_pinned=False
        pin_direction=()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piece_pinned=True
                pin_direction=(self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.white_to_move:
            king_row,king_col=self.white_king_location
            if self.board[r-1][c]=="-" and (not piece_pinned or pin_direction==(-1,0)):
                moves.append(Move((r,c),(r-1,c),self.board))
                if r==6 and self.board[r-2][c]=="-":
                    moves.append(Move((r,c),(r-2,c),self.board))
            if c!=7:
                if (self.board[r-1][c+1] in self.black_pieces and ( not piece_pinned or pin_direction==(-1,1))):
                        moves.append(Move((r,c),(r-1,c+1),self.board))
                elif (r-1,c+1)==self.enpassant and r==3:
                    attacking_piece=blocking_piece=False
                    if king_row==r:
                        if king_col<c:
                            inside_range=range(king_col+1,c)
                            outside_range=range(c+2,8)
                        else:
                            inside_range=range(king_col-1,c+1,-1)
                            outside_range=range(c-1,-1,-1)
                        for i in inside_range:
                            if self.board[r][i]!="-":
                                blocking_piece=True
                                break
                        for i in outside_range:
                            if self.board[r][i] in ["r","q"]:
                                attacking_piece=True
                                break
                            elif self.board[r][i]!="-":
                                blocking_piece=True
                                break
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((r,c),(r-1,c+1),self.board))
            if c!=0:
                if (self.board[r-1][c-1] in self.black_pieces and ( not piece_pinned or pin_direction==(-1,-1))):
                        moves.append(Move((r,c),(r-1,c-1),self.board))
                elif (r-1,c-1)==self.enpassant:
                    attacking_piece=blocking_piece=False
                    if king_row==r:
                        if king_col<c:
                            inside_range=range(king_col+1,c-1)
                            outside_range=range(c+1,8)
                        else:
                            inside_range=range(king_col-1,c,-1)
                            outside_range=range(c-2,-1,-1)
                        for i in inside_range:
                            if self.board[r][i]!="-":
                                blocking_piece=True
                                break
                        for i in outside_range:
                            if self.board[r][i] in ["r","q"]:
                                attacking_piece=True
                                break
                            elif self.board[r][i]!="-":
                                blocking_piece=True
                                break
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((r,c),(r-1,c-1),self.board))
        else:
            king_row,king_col=self.black_king_location
            if self.board[r+1][c]=="-" and (not piece_pinned or pin_direction==(1,0)):
                moves.append(Move((r,c),(r+1,c),self.board))
                if r==1 and self.board[r+2][c]=="-":
                    moves.append(Move((r,c),(r+2,c),self.board))
            if c!=7:
                if self.board[r+1][c+1] in self.white_pieces and ( not piece_pinned or pin_direction==(1,1)):
                    moves.append(Move((r,c),(r+1,c+1),self.board))
                elif (r+1,c+1)==self.enpassant:
                    attacking_piece=blocking_piece=False
                    if king_row==r:
                        if king_col<c:
                            inside_range=range(king_col+1,c)
                            outside_range=range(c+2,8)
                        else:
                            inside_range=range(king_col-1,c+1,-1)
                            outside_range=range(c-1,-1,-1)
                        for i in inside_range:
                            if self.board[r][i]!="-":
                                blocking_piece=True
                                break
                        for i in outside_range:
                            if self.board[r][i] in ["r","q"]:
                                attacking_piece=True
                                break
                            elif self.board[r][i]!="-":
                                blocking_piece=True
                                break
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((r,c),(r+1,c+1),self.board))
            if c!=0:
                if self.board[r+1][c-1] in self.white_pieces and ( not piece_pinned or pin_direction==(1,-1)):
                    moves.append(Move((r,c),(r+1,c-1),self.board))
                elif (r+1,c-1)==self.enpassant:
                    attacking_piece=blocking_piece=False
                    if king_row==r:
                        if king_col<c:
                            inside_range=range(king_col+1,c-1)
                            outside_range=range(c+1,8)
                        else:
                            inside_range=range(king_col-1,c,-1)
                            outside_range=range(c-2,-1,-1)
                        for i in inside_range:
                            if self.board[r][i]!="-":
                                blocking_piece=True
                                break
                        for i in outside_range:
                            if self.board[r][i] in ["r","q"]:
                                attacking_piece=True
                                break
                            elif self.board[r][i]!="-":
                                blocking_piece=True
                                break
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((r,c),(r+1,c-1),self.board))

    def get_rook_moves(self,r,c,moves):
        '''all the possible moves for the given rook (Castling not included)'''
        piece_pinned=False
        pin_direction=()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piece_pinned=True
                pin_direction=(self.pins[i][2],self.pins[i][3])
                if not self.board[r][c] in ["q","Q"]:
                    self.pins.remove(self.pins[i])
                break
        directions=((-1,0),(1,0),(0,1),(0,-1))
        ally_pieces=self.white_pieces if self.white_to_move else self.black_pieces
        for d in directions:
            if not piece_pinned or pin_direction==d or (pin_direction[0]==-d[0] and pin_direction[1]==-d[1]):
                end_row=r+d[0]
                end_col=c+d[1]
                while (0<=end_row<8) and (0<=end_col<8):
                    if self.board[end_row][end_col]=="-":
                        moves.append(Move((r,c),(end_row,end_col),self.board))
                    elif self.board[end_row][end_col] not in ally_pieces:
                        moves.append(Move((r,c),(end_row,end_col),self.board))
                        break
                    else:
                        break
                    end_row+=d[0]
                    end_col+=d[1]
    
    def get_knight_moves(self,r,c,moves):
        '''all the possible moves for the given Knight'''
        piece_pinned=False
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piece_pinned=True
                self.pins.remove(self.pins[i])
                break
        if not piece_pinned:
            ally_pieces=self.white_pieces if self.white_to_move else self.black_pieces
            movers=[[r-2,c-1],[r-2,c+1],[r+2,c+1],[r+2,c-1],[r-1,c+2],[r-1,c-2],[r+1,c+2],[r+1,c-2]]
            for k in movers:
                i=k[0]
                j=k[1]
                if i<8 and i>-1 and j<8 and j>-1 and self.board[i][j] not in ally_pieces:
                    moves.append(Move((r,c),(i,j),self.board))
    
    def get_bishop_moves(self,r,c,moves):
        '''all the possible moves for the given bishop'''
        piece_pinned=False
        pin_direction=()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piece_pinned=True
                pin_direction=(self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        ally_pieces=self.white_pieces if self.white_to_move else self.black_pieces
        directions=((-1,-1),(-1,1),(1,-1),(1,1))
        for d in directions:
            if not piece_pinned or pin_direction==d or (pin_direction[0]==-d[0] and pin_direction[1]==-d[1]):
                end_row=r+d[0]
                end_col=c+d[1]
                while (0<=end_row<8) and (0<=end_col<8):
                    if self.board[end_row][end_col]=="-":
                        moves.append(Move((r,c),(end_row,end_col),self.board))
                    elif self.board[end_row][end_col] in ally_pieces:
                        break
                    else:
                        moves.append(Move((r,c),(end_row,end_col),self.board))
                        break
                    end_row+=d[0]
                    end_col+=d[1]
    
    def get_queen_moves(self,r,c,moves):
        '''all the possible moves for the given Queen'''
        self.get_rook_moves(r,c,moves)
        self.get_bishop_moves(r,c,moves)
    
    def get_king_moves(self,r,c,moves):
        '''all the possible moves for the king'''
        movers=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
        ally_pieces=self.white_pieces if self.white_to_move else self.black_pieces
        for i in movers:
            end_row=r+i[0]
            end_col=c+i[1]
            if 0<=end_row<8 and 0<=end_col<8:
                end_piece=self.board[end_row][end_col]
                if end_piece not in ally_pieces:
                    if self.white_pieces==ally_pieces:
                        self.white_king_location=(end_row,end_col)
                    else:
                        self.black_king_location=(end_row,end_col)
                    in_check,_,_=self.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(Move((r,c),(end_row,end_col),self.board))
                    if ally_pieces==self.white_pieces:
                        self.white_king_location=(r,c)
                    else:
                        self.black_king_location=(r,c)
    
    def get_castle_moves(self,r,c,moves):
        '''Catling moves'''
        if (self.white_to_move and self.current_castling_rights.wks) or (not self.white_to_move and self.current_castling_rights.bks):
            self.get_kingside_castle_moves(r,c,moves)
        if (self.white_to_move and self.current_castling_rights.wqs) or (not self.white_to_move and self.current_castling_rights.bqs):
            self.get_queenside_castle_moves(r,c,moves)
    
    def get_kingside_castle_moves(self,r,c,moves):
        '''King-side Castle Moves'''
        if (self.board[r][c+1]=="-" and self.board[r][c+2]=="-" and self.board[r][c+3] in ["r","R"]) and (not self.square_under_attack(r,c+1) and not self.square_under_attack(r,c+2)):
            moves.append(Move((r,c),(r,c+2),self.board))
    
    def get_queenside_castle_moves(self,r,c,moves):
        '''Queen side Catle moves'''
        if (self.board[r][c-1]=="-" and self.board[r][c-2]=="-" and self.board[r][c-3]=="-" and self.board[r][c-4] in ["r","R"]) and (not self.square_under_attack(r,c-1) and not self.square_under_attack(r,c-2)):
            moves.append(Move((r,c),(r,c-2),self.board))
    
    def square_under_attack(self,r,c):
        self.white_to_move=not self.white_to_move
        moves=self.get_all_moves()
        self.white_to_move= not self.white_to_move
        for i in moves:
            if i.end_row==r and i.end_col==c:
                return True
        return False

class FEN():

    def __init__(self,gs,fen):
        '''Converts a position given in FEN notation to board'''
        for i in range(len(fen)):
            if i<8:
                self.rank_fen(fen,i,gs)
            elif i==8:
                gs.white_to_move=True if fen[i]=='w' else False
            elif i==9:
                self.castling_rights(fen[i],gs)
            elif i==10:
                gs.enpassant_square=fen[i]
            elif i==11:
                gs.half_move=int(fen[i])
            elif i==12:
                gs.move_count=int(fen[i])
    
    def rank_fen(self,fen,rank,gs):
        '''Sub_function for fen_converter deals with a rank'''
        rank_det=fen[rank]
        col=0
        for j in rank_det:
            if j in 'prnbqkPRNBQK':
                gs.board[rank][col]=j
                col+=1
            else:
                col+=int(j)
            if j=="k":
                gs.black_king_location=[rank,col-1]
            elif j=="K":
                gs.white_king_location=[rank,col-1]
    
    def castling_rights(self,line,gs):
        wks=False
        wqs=False
        bks=False
        bqs=False
        for i in line:
            if i=="K":
                wks=True
            elif i=="Q":
                wqs=True
            elif i=="k":
                bks=True
            elif i=="q":
                bqs=True
        gs.current_castling_rights=CastlingRights(wks,wqs,bks,bqs)

class CastlingRights():
    def __init__(self,wks,wqs,bks,bqs):
        self.wks=wks
        self.bks=bks
        self.wqs=wqs
        self.bqs=bqs

class Move():
    ranks_to_rows={"1":7,"2":6,"3":5,"4":4,"5":3,"6":2,"7":1,"8":0}
    rows_to_ranks={v:k for k,v in ranks_to_rows.items()}
    files_to_cols={"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}
    cols_to_files={v:k for k,v in files_to_cols.items()}

    def __init__(self,start_sq,end_sq,board):
        self.start_row=start_sq[0]
        self.start_col=start_sq[1]
        self.end_row=end_sq[0]
        self.end_col=end_sq[1]
        self.piece_moved=board[self.start_row][self.start_col]
        self.piece_captured=board[self.end_row][self.end_col]
        self.move_id=self.get_move_id(self.start_row,self.start_col,self.end_row,self.end_col)
        self.pawn_promotion= (self.piece_moved=="p" and self.end_row==7) or (self.piece_moved=="P" and self.end_row==0)
        self.castle_move=(self.piece_moved=="K" or self.piece_moved=="k") and abs(self.end_col-self.start_col)==2
        self.enpassant_move=self.piece_moved in ["p","P"] and self.piece_captured=="-" and self.end_col!=self.start_col
    
    def get_move_id(self,start_row,start_col,end_row,end_col):
        '''Mapping all moves to number'''
        return start_row*(8*64)+start_col*64+end_row*8+end_col
    
    def __eq__(self,other):
        if isinstance(other,Move):
            return self.move_id==other.move_id
        return False

    def get_chess_notation(self):
        if self.castle_move:
            if self.start_col<self.end_col:
                return "O-O"
            else:
                return "O-O-O"
        capture=""
        if(self.enpassant_move):
            return self.get_rank_files(0,self.start_col)[0]+"X"+self.get_rank_files(self.end_row,self.end_col)
        if(self.piece_captured!="-"):
            capture="X"
        if self.piece_moved not in ['p','P']:
            return self.piece_moved+capture+self.get_rank_files(self.end_row,self.end_col)
        else:
            if capture=="X":
                return self.get_rank_files(0,self.start_col)[0]+capture+self.get_rank_files(self.end_row,self.end_col)
            return self.get_rank_files(self.end_row,self.end_col)
    
    def get_rank_files(self,r,c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]