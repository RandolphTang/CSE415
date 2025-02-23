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
    def make_move(self, current_state, current_remark, time_limit=1000,
                  autograding=True, use_alpha_beta=True,
                  use_zobrist_hashing=False, max_ply=3,
                  special_static_eval_fn=None):
        self.alpha_beta_cutoffs_this_turn = 0  
        self.num_static_evals_this_turn = 0
        self.special_eval_fn = special_static_eval_fn

        new_state = State(current_state)

        eval, best_move = self.minimax(new_state, max_ply,
                                use_alpha_beta,
                                float('-inf'), float('inf'))
        
        stats = [self.alpha_beta_cutoffs_this_turn,
                 self.num_static_evals_this_turn,
                 self.zobrist_table_num_entries_this_turn,
                 self.zobrist_table_num_hits_this_turn]


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
            alpha=None,
            beta=None):

        empty_space = self.count_empty_spaces(state)

        if depth_remaining == 0 or empty_space == 0:
            self.num_static_evals_this_turn += 1
            if self.special_eval_fn:
                return [self.special_eval_fn(state), None]
            return [self.static_eval(state, self.current_game_type), None]

        best_move = None
        if state.whose_move == "X":  # Maximizing player (X)
            best_score = alpha
            for i in range(len(state.board)):
                for j in range(len(state.board[0])):
                    if state.board[i][j] == ' ':
                        new_state = State(state)
                        new_state.board[i][j] = state.whose_move
                        new_state.whose_move = "O"
                        
                        # Recursively evaluate this move
                        score = self.minimax(new_state, depth_remaining - 1,
                                            pruning, alpha, beta)[0]
                        
                        ##print(f"Evaluating move ({i}, {j}) for {state.whose_move}")
                        if score > best_score:
                            best_score = score
                            best_move = (i, j)
                        
                        if pruning:
                            alpha = max(alpha, best_score)
                            if beta <= alpha:
                                self.alpha_beta_cutoffs_this_turn += 1
                                return [best_score, best_move]  # Beta cutoff
                            
        else:  # Minimizing player (O)
            best_score = beta
            for i in range(len(state.board)):
                for j in range(len(state.board[0])):
                    if state.board[i][j] == ' ':
                        new_state = State(state)
                        new_state.board[i][j] = state.whose_move
                        new_state.whose_move = "X"
                        
                        score = self.minimax(new_state, depth_remaining - 1,
                                            pruning, alpha, beta)[0]
                        
                        ##print(f"Evaluating move ({i}, {j}) for {state.whose_move}")
                        
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

    def count_empty_spaces(self, state):
        count = 0
        for row in state.board:
            count += row.count(' ')
        return count
 
    def static_eval(self, state, game_type=None):
        # Values should be higher when the states are better for X,
        # lower when better for O.
        k = game_type.k
        score = 0
        
        # Check all rows, columns, and diagonals
        def evaluate_line(line):
            line_score = 0
            for i in range(len(line) - k + 1): # for each k-length window in a line
                window = line[i:i + k]
                if window.count('X') == k: # X wins
                    return float('inf')
                elif window.count('O') == k: # O wins
                    return float('-inf')
                
                if 'X' in window and 'O' not in window and '-' not in window: # X is close to a winning move
                    line_score += 10 ** window.count('X')
                elif 'O' in window and 'X' not in window and '-' not in window: # O is close to a winning move
                    line_score -= 10 ** window.count('O')
                else:
                    line_score += window.count('X') - window.count('O')
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

