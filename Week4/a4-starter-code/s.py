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
from google import genai 
from dotenv import load_dotenv
import os

load_dotenv()

AUTHORS = 'Randolph Jenkins and Aidan Lee' 

import time # You'll probably need this to avoid losing a
 # game due to exceeding a time limit.

# Create your own type of agent by subclassing KAgent:

class OurAgent(KAgent):  # Keep the class name "OurAgent" so a game master
    # knows how to instantiate your agent class.

    def __init__(self, twin=False):
        self.twin=twin
        self.nickname = ''
        if twin: self.nickname = 'Evil '
        self.nickname += 'FletchBot'
        self.long_name = 'Terrence Fletchbot '
        if twin: self.long_name += ' 2000'
        else: self.long_name += ' 1000'
        self.persona = 'terence fletcher'
        self.voice_info = {'Chrome': 10, 'Firefox': 2, 'other': 0}
        self.playing = "don't know yet" # e.g., "X" or "O".
        self.alpha_beta_cutoffs_this_turn = -1
        self.num_static_evals_this_turn = -1
        self.zobrist_table_num_entries_this_turn = -1
        self.zobrist_table_num_hits_this_turn = -1
        self.current_game_type = None
        self.client = None
        self.sys_instruct = None
        
    def introduce(self):
        intro = 'Are you rushing, or are you dragging? Doesn\'t matter. I\'m Fletchbot. Terence Fletchbot.\n'+\
            'And in this... game, let\'s call it, you\'ll learn the true meaning of tempo. \n'+\
            'You think you know what a winning move is? You think you understand the dynamics of this board? You don\'t.\n'+\
            'Not yet. Now, let\'s see if you can keep up. Or if you\'ll simply fold under the pressure.\n'
        if self.twin: intro = 'And I\'m EVIL Fletchbot. Terence Fletchbot. And this isn\'t some playground scribble.\n'+\
            'This is a contest of precision, of drive. You think you can just haphazardly drop your little \'X\' or \'O\' wherever\n'+\
            'you please? You\'re wrong. Every move, every single move, has to have purpose. It has to have... soul.\n'+\
            'Now, show me what you\'ve got. Or don\'t. And just admit you\'re a waste of my time.\n'
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

        utterances_matter=False):      # If False, just return 'OK' for each utterance,
                                      # or something simple and quick to compute
                                      # and do not import any LLM or special APIs.
                                      # During the tournament, this will be False..
       if utterances_matter:
            self.sys_instruct = f"You are Terence Fletcher from the 2014 film Whiplash. You are a utterance commentor for an Adversarial Search \n" +\
                    f"K-in-a-row game, and you will comment on each move they play based on \n" +\
                    f"the opponent's previous move or their utterance last move, or say something irrelevant but still in character.\n" +\
                    f"You are playing {what_side_to_play} against {opponent_nickname}.\n" +\
                    "Limit your response to at most two sentences.\n" 
            self.client = genai.Client(api_key=os.getenv('GEMINI_KEY')) 

     
       # Write code to save the relevant information in variables
       # local to this instance of the agent.
       # Game-type info can be in global variables.
    
       self.current_game_type = game_type
       self.playing = what_side_to_play
       self.opponent = opponent_nickname
       self.time_per_move = expected_time_per_move

       return "OK"
   
   # The core of your agent's ability should be implemented here:             
    def make_move(self, current_state, current_remark, time_limit=None,
                  autograding=True, use_alpha_beta=True,
                  use_zobrist_hashing=False, max_ply=3,
                  special_static_eval_fn=None):
        
        self.autograding = autograding
        self.use_zobrist_hashing = use_zobrist_hashing
        self.special_eval_fn = special_static_eval_fn

        self.alpha_beta_cutoffs_this_turn = 0  
        self.num_static_evals_this_turn = 0
        self.zobrist_table_num_entries_this_turn = 0
        self.zobrist_table_num_hits_this_turn = 0

        self.start_time = time.time()
        self.time_limit = time_limit
        print(f"Time limit after setting: {self.time_limit}")  # And this
        new_state = State(current_state)
        new_state_stat = self.minimax(new_state, max_ply,
                                use_alpha_beta,
                                float('-inf'), float('inf'))
        
        best_move, curr_stat = new_state_stat[1], new_state_stat[2]

        if best_move:
            new_state = State(current_state)
            i, j = best_move
            new_state.board[i][j] = self.playing

            new_remark = ''
            prompt = (
                # f"Explain how you would comment this move players mode based on "
                # f"the alpha_beta_cutoffs_this_turn {self.alpha_beta_cutoffs_this_turn}"
                # f"and the num_static_evals_this_turn {self.num_static_evals_this_turn}"
                f"You are playing {self.playing}\n"+\
                f"Here is the previous K-in-a-row board: {current_state}\n"+\
                f"And here is the board after your move: {new_state.board}\n"+\
                f"Comment on the state of the game.\n"
                f"or respond to your opponent's comment: {current_remark}\n"
            )
            if self.client is not None:
                try:
                    response = self.client.models.generate_content(
                        model="gemini-2.0-flash-lite-preview",
                        config=genai.types.GenerateContentConfig(
                            system_instruction=self.sys_instruct),
                        contents=[prompt]
                    )
                except Exception as e:
                    response = self.client.models.generate_content(
                        model="gemini-2.0-flash",
                        config=genai.types.GenerateContentConfig(
                            system_instruction=self.sys_instruct),
                        contents=[prompt]
                    )
                new_remark += response.text
            else: 
                response = "Ok."
                new_remark += response
            if new_state.whose_move == "O": 
                new_state.whose_move = "X"
            elif new_state.whose_move == "X": 
                new_state.whose_move = "O"
            return [[best_move, new_state], new_remark]

        print("Returning from make_move")
        if current_state.whose_move == "O": 
                current_state.whose_move = "X"
        elif current_state.whose_move == "X": 
                current_state.whose_move = "O"
        return [[(0, 0), current_state], "No valid moves found"]

    # The main adversarial search function:
    def minimax(self,
            state,
            depth_remaining,
            pruning=False,
            alpha=float('-inf'),
            beta=float('inf')):
        
        best_move = None
        best_score = float('-inf') if state.whose_move == "X" else float('inf')

        stats = [self.alpha_beta_cutoffs_this_turn,
                 self.num_static_evals_this_turn,
                 self.zobrist_table_num_entries_this_turn,
                 self.zobrist_table_num_hits_this_turn]
        
        if (self.time_limit is not None and self.start_time is not None 
                and  time.time() - self.start_time >= self.time_limit):
            print("WARNING:Time limit reached, current best move will be choosen")
            return [best_score, None, stats]

        empty_space = self.count_empty_spaces(state)
            
        if depth_remaining == 0 or empty_space == 0:
            self.num_static_evals_this_turn += 1
            if self.special_eval_fn:
                return [self.special_eval_fn(state), None, stats]
            return [self.static_eval(state, self.current_game_type), None, stats]

        if state.whose_move == "X":  # Maximizing player (X)
            for i in range(len(state.board)):
                for j in range(len(state.board[0])):
                    if state.board[i][j] == ' ':
                        new_state = State(state)
                        new_state.board[i][j] = state.whose_move
                        new_state.whose_move = "O"
                        
                        score = self.minimax(new_state, depth_remaining - 1,
                                            pruning, alpha, beta)[0]
                        
                        if score > best_score:
                            best_score = score
                            best_move = (i, j)
                        
                        if pruning:
                            alpha = max(alpha, best_score)
                            if beta <= alpha:
                                self.alpha_beta_cutoffs_this_turn += 1
                                return [best_score, best_move, stats]  # Beta cutoff
                            
        else:  # Minimizing player (O)
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
                                return [best_score, best_move, stats]  # Alpha cutoff
    
        return [best_score, best_move, stats]
        # Only the score is required here but other stuff can be returned
        # in the list, after the score, in case you want to pass info
        # back from recursive calls that might be used in your utterances,
        # etc. 

    def count_empty_spaces(self, state):
        count = 0
        for row in state.board:
            count += row.count(' ')
        return count
 
    def static_eval(self, state, game_type=None, depth_remaining=0):
        k = game_type.k
        board = state.board
        rows, cols = len(board), len(board[0])
        depth_mult = 1 if depth_remaining == 0 else depth_remaining
        
        WIN_VALUE = 100000
        NEAR_WIN_VALUE = 100
        
        def evaluate_window(window):
            x_count = window.count('X')
            o_count = window.count('O')
            block_count = window.count('-')
            empty_count = len(window) - x_count - o_count - block_count
            
            if x_count == k and empty_count == 0:
                return WIN_VALUE if self.playing == 'X' else WIN_VALUE // 10
            if o_count == k and empty_count == 0:
                return -WIN_VALUE if self.playing == 'O' else -WIN_VALUE // 10
                
            if empty_count == 0:
                if x_count == k - 1 and o_count == 0:
                    return NEAR_WIN_VALUE
                if o_count == k - 1 and x_count == 0:
                    return -NEAR_WIN_VALUE
                    
            if block_count > 0:
                return 0
            return x_count - o_count - empty_count

        score = 0
        
        # Evaluate rows (with optimization to avoid unnecessary slicing)
        for row in board:
            for i in range(cols - k + 1):
                score += evaluate_window(row[i:i + k])

        for c in range(cols):
            col = [board[r][c] for r in range(rows)]
            for i in range(rows - k + 1):
                score += evaluate_window(col[i:i + k])
        
        for r in range(rows - k + 1):
            for c in range(cols - k + 1):
                diag = [board[r + i][c + i] for i in range(k)]
                score += evaluate_window(diag)
        
        for r in range(rows - k + 1):
            for c in range(k - 1, cols):
                diag = [board[r + i][c - i] for i in range(k)]
                score += evaluate_window(diag)
        
        return score
    
    
# OPTIONAL THINGS TO KEEP TRACK OF:

#  WHO_MY_OPPONENT_PLAYS = other(WHO_I_PLAY)
#  MY_PAST_UTTERANCES = []
#  OPPONENT_PAST_UTTERANCES = []
#  UTTERANCE_COUNT = 0
#  REPEAT_COUNT = 0 or a table of these if you are reusing different utterances

