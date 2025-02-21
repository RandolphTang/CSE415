'''
<yourUWNetID>_KInARow.py
Authors: Jenkins, Randolph; Aidan Lee 

An agent for playing "K-in-a-Row with Forbidden Squares" and related games.
CSE 415, University of Washington

THIS IS A TEMPLATE WITH STUBS FOR THE REQUIRED FUNCTIONS.
YOU CAN ADD WHATEVER ADDITIONAL FUNCTIONS YOU NEED IN ORDER
TO PROVIDE A GOOD STRUCTURE FOR YOUR IMPLEMENTATION.

'''

from agent_base import KAgent
from game_types import State, Game_Type, deep_copy

AUTHORS = 'Randolph Jenkins and Aidan Lee' 

import time # You'll probably need this to avoid losing a
 # game due to exceeding a time limit.

# Create your own type of agent by subclassing KAgent:

class OurAgent(KAgent):  # Keep the class name "OurAgent" so a game master
    # knows how to instantiate your agent class.

    def __init__(self, twin=False):
        self.twin=twin
        self.nickname = 'mommy'
        if twin: self.nickname += '2'
        self.long_name = 'daddy'
        if twin: self.long_name += ' II'
        self.persona = 'terence fletcher'
        self.voice_info = {'Chrome': 10, 'Firefox': 2, 'other': 0}
        self.playing = "don't know yet" # e.g., "X" or "O".
        self.alpha_beta_cutoffs_this_turn = -1
        self.num_static_evals_this_turn = -1
        self.zobrist_table_num_entries_this_turn = -1
        self.zobrist_table_num_hits_this_turn = -1
        self.current_game_type = None

    def introduce(self):
        intro = '\nMy name is daddy,\n'+\
            '"Randolph and Aidan" made me, they are GOAT.\n'+\
            'Somebody please turn me into a real game-playing agent!\n'
        if self.twin: intro += "By the way, I'm the your another daddy II.\n"
        return intro

    # Receive and acknowledge information about the game from
    # the game master:
    def prepare(
        self,
        game_type,
        what_side_to_play,
        opponent_nickname,
        expected_time_per_move = 0.1, # Time limits can be
                                      # changed mid-game by the game master.

        utterances_matter=True):      # If False, just return 'OK' for each utterance,
                                      # or something simple and quick to compute
                                      # and do not import any LLM or special APIs.
                                      # During the tournament, this will be False..
       if utterances_matter:
           pass
           # Optionally, import your LLM API here.
           # Then you can use it to help create utterances.
     
       # Write code to save the relevant information in variables
       # local to this instance of the agent.
       # Game-type info can be in global variables.

       self.current_game_type = game_type
       self.playing = what_side_to_play
       self.opponent = opponent_nickname
       self.time_per_move = expected_time_per_move

       print("Change this to return 'OK' when ready to test the method.")
       return "OK"
   
    # The core of your agent's ability should be implemented here:             
    def make_move(self, current_state, current_remark, time_limit=1000,
                  autograding=True, use_alpha_beta=True,
                  use_zobrist_hashing=False, max_ply=3,
                  special_static_eval_fn=None):
        print(f"Alpha-beta enabled: {use_alpha_beta}")
        print("make_move has been called")

        print("code to compute a good move should go here.")

        self.alpha_beta_cutoffs_this_turn = 0  
        self.num_static_evals_this_turn = 0
        self.special_eval_fn = special_static_eval_fn

        new_state =State(current_state)

        best_move = self.minimax(new_state, max_ply,
                                use_alpha_beta, 
                                float('-inf'), float('inf'))[1]

        stats = [self.alpha_beta_cutoffs_this_turn,
                 self.num_static_evals_this_turn,
                 self.zobrist_table_num_entries_this_turn,
                 self.zobrist_table_num_hits_this_turn]
   
        if best_move:
            new_state = State(current_state)
            i, j = best_move
            new_state.board[i][j] = self.playing
            new_remark = f"I played at position ({i}, {j})"
            return [[best_move, new_state]+stats, new_remark]
    
        new_remark = "I need to think of something appropriate.\n" +\
        "Well, I guess I can say that this move is probably illegal."

        print("Returning from make_move")
        return [[(0, 0), current_state], "No valid moves found"]

    # The main adversarial search function:
    def minimax(self,
            state,
            depth_remaining,
            pruning=False,
            alpha=None,
            beta=None):
        print(f"Pruning enabled: {pruning}")
        print("Calling minimax. We need to implement its body.")

        if depth_remaining == 0:
            self.num_static_evals_this_turn += 1
            if self.special_eval_fn:
                return [self.special_eval_fn(state), None]
            return [self.static_eval(state, self.current_game_type), None]

        best_move = None

        if state.whose_move == "X":  # Maximizing player (X)
            best_score = float('-inf')
            for i in range(len(state.board)):
                for j in range(len(state.board[0])):
                    if state.board[i][j] == ' ':
                        new_state = State(state)
                        new_state.board[i][j] = state.whose_move
                        new_state.whose_move = "O"
                        
                        # Recursively evaluate this move
                        score = self.minimax(new_state, depth_remaining - 1,
                                            pruning, alpha, beta)[0]
                        
                        
                        if score > best_score:
                            best_score = score
                            best_move = (i, j)
                        
                        if pruning:
                            alpha = max(alpha, best_score)
                            if beta <= alpha:
                                self.alpha_beta_cutoffs_this_turn += 1
                                return [best_score, best_move]  # Beta cutoff
                            
        else:  # Minimizing player (O)
            best_score = float('inf')
            for i in range(len(state.board)):
                for j in range(len(state.board[0])):
                    if state.board[i][j] == ' ':
                        new_state = State(state)
                        new_state.board[i][j] = state.whose_move
                        new_state.whose_move = "X"
                        
                        score = self.minimax(new_state, depth_remaining - 1,
                                            pruning, alpha, beta)[0]
                        
                        if score < best_score:
                            best_score = score
                            best_move = (i, j)
                        
                        if pruning:
                            beta = min(beta, best_score)
                            if beta <= alpha:
                                self.alpha_beta_cutoffs_this_turn += 1
                                return [best_score, best_move]  # Alpha cutoff
    
        return [best_score, best_move]
        # Only the score is required here but other stuff can be returned
        # in the list, after the score, in case you want to pass info
        # back from recursive calls that might be used in your utterances,
        # etc. 
 
    def static_eval(self, state, game_type=None):
        print('calling static_eval. Its value needs to be computed!')
        # Values should be higher when the states are better for X,
        # lower when better for O.
        k = game_type.k
        score = 0
        
        # Check all rows, columns, and diagonals
        def evaluate_line(line):
            line_score = 0
            for i in range(len(line) - k + 1):
                window = line[i:i + k]
                if 'X' in window and 'O' not in window:
                    line_score += 10 ** window.count('X')
                elif 'O' in window and 'X' not in window:
                    line_score -= 10 ** window.count('O')
            return line_score
        
        # Evaluate rows
        for row in state.board:
            score += evaluate_line(row)
        
        # Evaluate columns
        for col in range(len(state.board[0])):
            score += evaluate_line([state.board[row][col] for row in range(len(state.board))])
        
        # Evaluate diagonals
        def get_diagonals(board):
            diagonals = []
            rows, cols = len(board), len(board[0])
            
            # Main diagonals (top-left to bottom-right)
            for r in range(rows - k + 1):
                diagonals.append([board[r + i][i] for i in range(min(rows - r, cols))])
            for c in range(1, cols - k + 1):
                diagonals.append([board[i][c + i] for i in range(min(rows, cols - c))])
            
            # Anti-diagonals (top-right to bottom-left)
            for r in range(rows - k + 1):
                diagonals.append([board[r + i][cols - 1 - i] for i in range(min(rows - r, cols))])
            for c in range(1, cols - k + 1):
                diagonals.append([board[i][cols - 1 - (c + i)] for i in range(min(rows, cols - c))])
            
            return diagonals
        
        for diagonal in get_diagonals(state.board):
            score += evaluate_line(diagonal)
        
        return score
 
# OPTIONAL THINGS TO KEEP TRACK OF:

#  WHO_MY_OPPONENT_PLAYS = other(WHO_I_PLAY)
#  MY_PAST_UTTERANCES = []
#  OPPONENT_PAST_UTTERANCES = []
#  UTTERANCE_COUNT = 0
#  REPEAT_COUNT = 0 or a table of these if you are reusing different utterances

