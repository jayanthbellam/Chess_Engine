import random
import numpy as np

CHECKMATE=1000000
STALEMATE=0
DEPTH=4
piece_score={"K":0,"k":0,"Q":900,"q":-900,"R":500,"r":-500,"B":370,"b":-370,"N":300,"n":-300,"P":100,"p":-100}
pawn_score=[[8,8,8,8,8,8,8,8],
            [8,8,8,8,8,8,8,8],
            [5,6,6,7,7,6,6,5],
            [2,3,3,5,5,3,3,2],
            [1,2,3,4,4,3,2,1],
            [1,1,2,3,3,2,1,1],
            [1,1,1,0,0,1,1,1],
            [0,0,0,0,0,0,0,0]]
bishop_score=[[4,3,2,1,1,2,3,4],
              [3,4,3,2,2,3,4,3],
              [2,3,4,3,3,4,3,2],
              [1,2,3,4,4,3,2,1],
              [1,2,3,4,4,3,2,1],
              [2,3,4,3,3,4,3,2],
              [3,4,3,2,2,3,4,3],
              [4,3,2,1,1,2,3,4]]
rook_score=[[4,3,4,4,4,4,3,4],
            [4,4,4,4,4,4,3,4],
            [1,1,2,2,2,2,1,1],
            [1,2,3,4,4,3,2,1],
            [1,2,3,4,4,3,2,1],
            [1,1,2,2,2,2,1,1],
            [4,4,4,4,4,4,4,4],
            [4,3,4,4,4,4,3,4]]
queen_score=[[1,1,1,3,1,1,1,1],
             [1,2,3,3,3,1,1,1],
             [1,4,3,3,3,4,2,1],
             [1,2,3,3,3,2,2,1],
             [1,2,3,3,3,2,2,1],
             [1,4,3,3,3,4,2,1],
             [1,1,2,3,3,1,1,1],
             [1,1,1,1,1,1,1,1]]
king_score=[[0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0]]
knight_score=[[1,1,1,1,1,1,1,1],
              [1,2,2,2,2,2,2,1],
              [1,2,3,3,3,3,2,1],
              [1,2,3,4,4,3,2,1],
              [1,2,3,4,4,3,2,1],
              [1,2,3,3,3,3,2,1],
              [1,2,2,2,2,2,2,1],
              [1,1,1,1,1,1,1,1]]
piece_position_Scores={"N":np.multiply(knight_score,10),"n":np.multiply(knight_score,-10),"P":np.multiply(pawn_score,10)}
pawn_score.sort(reverse=True)
piece_position_Scores["p"]=np.multiply(pawn_score,-10)
piece_position_Scores["B"]=np.multiply(bishop_score,10)
piece_position_Scores["b"]=np.multiply(bishop_score,-10)
piece_position_Scores["R"]=np.multiply(rook_score,10)
piece_position_Scores["r"]=np.multiply(rook_score,-10)
piece_position_Scores["Q"]=np.multiply(queen_score,10)
piece_position_Scores["q"]=np.multiply(rook_score,-10)
piece_position_Scores["K"]=np.multiply(rook_score,10)
piece_position_Scores["k"]=np.multiply(rook_score,-10)


def find_random_move(valid_moves):
    return random.choice(valid_moves)

def find_greedy_move(gs,valid_moves):
    worst_score=-CHECKMATE if gs.white_to_move else CHECKMATE
    best_move=None
    for player_move in valid_moves:
        gs.make_move(player_move)
        if gs.check_mate:
            score= worst_score*-1
        elif gs.stale_mate:
            score= 0
        else:
            score=score_material(gs.board)
        if not gs.white_to_move:
            if score>worst_score:
                worst_score=score
                best_move=player_move
        else:
            if score<worst_score:
                worst_score=score
                best_move=player_move
        gs.undo_move()
    return best_move

def find_mini_max(gs,valid_moves):
    turn_multiplier=1 if gs.white_to_move else -1
    opponent_minmax_score=CHECKMATE
    best_player_move=None
    random.shuffle(valid_moves)
    for player_move in valid_moves:
        gs.make_move(player_move)
        opponent_moves=gs.get_valid_moves()
        if gs.check_mate:
            opponent_max_score=-CHECKMATE
        elif gs.stale_mate:
            opponent_max_score=STALEMATE
        else:
            opponent_max_score=-CHECKMATE
            for opponent_move in opponent_moves:
                gs.make_move(opponent_move)
                gs.get_valid_moves()
                if gs.check_mate:
                    score=CHECKMATE
                elif gs.stale_mate:
                    score=STALEMATE
                else:
                    score=-turn_multiplier*score_material(gs.board)
                if score>opponent_max_score:
                    opponent_max_score=score
                gs.undo_move()
        if opponent_minmax_score>opponent_max_score:
            opponent_minmax_score=opponent_max_score
            best_player_move=player_move
        gs.undo_move()
    return best_player_move

def find_move_minmax(gs,valid_moves,depth,white_to_move):
    global next_move
    random.shuffle(valid_moves)
    if depth==0:
        return score_material(gs.board)
    if white_to_move:
        max_score=-CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves=gs.get_valid_moves()
            random.shuffle(next_moves)
            score=find_move_minmax(gs,next_moves,depth-1,False)
            if score>max_score:
                max_score=score
                if depth==DEPTH:
                    next_move=move
            gs.undo_move()
        return max_score
    else:
        min_score=CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves=gs.get_valid_moves()
            random.shuffle(next_moves)
            score=find_move_minmax(gs,next_moves,depth-1,True)
            if score<min_score:
                min_score=score
                if depth==DEPTH:
                    next_move=move
            gs.undo_move()
        return min_score

def find_move_negamax(gs,valid_moves,depth,multiplier):
    global next_move
    if depth==0:
        return multiplier*score_board(gs)
    max_score=-CHECKMATE
    for move in valid_moves:
            gs.make_move(move)
            next_moves=gs.get_valid_moves()
            score=-find_move_negamax(gs,next_moves,depth-1,-multiplier)
            if score>max_score:
                max_score=score
                if depth==DEPTH:
                    next_move=move
            gs.undo_move()
    return max_score

def find_move_negamax_alphabeta(gs,valid_moves,depth,multiplier,alpha,beta):
    global next_move
    if depth==0:
        return multiplier*score_board(gs)
    
    max_score=-CHECKMATE
    for move in valid_moves:
            gs.make_move(move)
            next_moves=gs.get_valid_moves()
            score=-find_move_negamax_alphabeta(gs,next_moves,depth-1,-multiplier,-beta,-alpha)
            if score>max_score:
                max_score=score
                if depth==DEPTH:
                    next_move=move
            gs.undo_move()
            if max_score>alpha:
                alpha=max_score
            if alpha>=beta:
                break
    return max_score

def find_best_move(gs,valid_moves):
    global next_move
    random.shuffle(valid_moves)
    next_move=None
    find_move_negamax_alphabeta(gs,valid_moves,DEPTH,1 if gs.white_to_move else -1,-CHECKMATE,CHECKMATE)
    return next_move

def score_board(gs):
    if gs.check_mate:
        if gs.white_to_move:
            return -CHECKMATE
        else:
            return CHECKMATE
    if gs.stale_mate:
        return STALEMATE
    return score_material(gs)

def score_material(gs):
    score=0
    for rows in range(len(gs.board)):
        row=gs.board[rows]
        for squares in range(len(row)):
            square=row[squares]
            if square !="-":
                score+=piece_score[square]
                score+=piece_position_Scores[square][rows][squares]
    return score

def no_of_moves(gs,moves,depth):
    if depth==0:
        return 1
    count=0
    for move in moves:
        gs.make_move(move)
        next_moves=gs.get_valid_moves()
        count+=no_of_moves(gs,next_moves,depth-1)
        gs.undo_move()
    return count
