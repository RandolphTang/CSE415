'''Farmer_Fox.py
by Randolph Jenkins
UWNetIDs: tang1125
Student numbers: 2266819

Assignment 2, in CSE 415, Winter 2025
 
This file contains my problem formulation for the problem of
the Farmer, Fox, Chicken, and Grain.
'''

# Put your formulation of the Farmer-Fox-Chicken-and-Grain problem here.
# Be sure your name(s), uwnetid(s), and 7-digit student number(s) are given above in 
# the format shown.

# You should model your code closely after the given example problem
# formulation in HumansRobotsFerry.py

# Put your metadata here, in the same format as in HumansRobotsFerry.
#<METADATA>
PROBLEM_NAME = "Farmer, Fox, Chicken, and Grain"
PROBLEM_VERSION = "1.1"
PROBLEM_SOLVER = ['Randolph Jenkins']
PROBLEM_CREATION_DATE = "10-JAN-2025"

# Context given to human solvers, via either the Text_SOLUZION_Client.
# # or the SVG graphics client.
PROBLEM_DESC=\
 '''In the Farmer, Fox, Chicken, and Grain problem, the player starts 
off with A farmer, a fox, a chicken, and a grain on the left bank of a river.
The object is to execute a sequence of legal moves that transfers them all to 
the right bank of the river. In this puzzle, there is a boat that can carry only
the farmer, and one of the tree items listed above. The fox must never be left 
alone with the chicken, and the chicken must never be left alone
with the grain, either on the left bank, right bank.
In the formulation presented here, the computer will not let you make a
move to such a forbidden situation, and it will only show you moves
that could be executed "safely."
'''

# Start your Common Code section here.
Farmer_on_left = 1
Fox_on_left = 1
Chicken_on_left = 1
Grain_on_left = 1
LEFT=0
RIGHT=1

class State:

    def __init__(self, old=None):
        if old is None:
            self.farmer_on_left = 1
            self.fox_on_left = 1
            self.chicken_on_left = 1
            self.grain_on_left = 1
            self.boat=LEFT
        else:
            self.farmer_on_left = old.farmer_on_left
            self.fox_on_left = old.fox_on_left
            self.chicken_on_left = old.chicken_on_left
            self.grain_on_left = old.grain_on_left
            self.boat = old.boat

    def __eq__(self, s2):
        if self.boat != s2.boat: return False
        if self.farmer_on_left != s2.farmer_on_left: return False
        if self.fox_on_left != s2.fox_on_left: return False
        if self.chicken_on_left != s2.chicken_on_left: return False
        if self.grain_on_left != s2.grain_on_left: return False
        return True

    def __str__(self):
        # Produces a textual description of a state.
        txt = "\n Farmer on left:"+str(self.farmer_on_left)+"\n"
        txt += "\n fox on left:"+str(self.fox_on_left)+"\n"
        txt += "\n chicken on left:"+str(self.chicken_on_left)+"\n"
        txt += "\n grain on left:"+str(self.grain_on_left)+"\n"
        if self.boat == LEFT:
            txt += " boat is on the left.\n"
        else:
            txt += " boat is on the right.\n"
        return txt

    def __hash__(self):
        return (self.__str__()).__hash__()

    def copy(self):
        # Performs an appropriately deep copy of a state,
        # for use by operators in creating new states.
        return State(old=self)

    def can_move(self, f, c, g):
        '''Tests whether it's legal for farmer to move the boat and take
        fox, chicken, or grain.'''
        # Check if only one or zero items are being moved
        if f + c + g > 1: return False

        takeNone = f == 0 and c == 0 and g == 0

        # Check if items are available on the current side
        side = self.boat
        if side == LEFT:
            if f > self.fox_on_left or c > self.chicken_on_left or g > self.grain_on_left: return False
        else:
            if f > (1-self.fox_on_left) or c > (1-self.chicken_on_left) or g > (1-self.grain_on_left): return False

        f_available = self.fox_on_left if side==LEFT else 1-self.fox_on_left
        c_available = self.chicken_on_left if side==LEFT else 1-self.chicken_on_left
        g_available = self.grain_on_left if side==LEFT else 1-self.grain_on_left
        if f_available == c_available and (g==1 or takeNone): return False # If trying to move grain, and fox and chicken are together
        if c_available == g_available and (f==1 or takeNone): return False # If trying to move fox, and chicken and grain are together
        return True

    def move(self, f, c, g):
        '''Assuming it's legal to make the move, this computes
         the new state resulting from moving the boat carrying
         Farmer and fox, chicken, or grain.'''
        news = self.copy()
        # Remove agents from the current side.
        if self.boat == LEFT:
            news.fox_on_left -= f
            news.chicken_on_left -= c
            news.grain_on_left -= g
        else:
            news.fox_on_left += f
            news.chicken_on_left += c
            news.grain_on_left += g
        news.farmer_on_left = 1 - self.farmer_on_left
        news.boat = 1 - self.boat
        return news

    def is_goal(self):
        '''If all fox, chicken, and grain are on the right, then this is a goal state.'''
        if self.fox_on_left == 0 and self.chicken_on_left == 0 and self.grain_on_left == 0: return True
        else: return False

def goal_message(s):
    return "Congratulations on successfully guiding Farmer, fox, chicken, and grain across the river!"

#<INITIAL_STATE>
CREATE_INITIAL_STATE = lambda : State()
#</INITIAL_STATE>

# Put your OPERATORS section here.
class Operator:
    def __init__(self, name, precond, state_transf):
        self.name = name
        self.precond = precond
        self.state_transf = state_transf

    def is_applicable(self, s):
        return self.precond(s)

    def apply(self, s):
        return self.state_transf(s)

#<OPERATORS>
fcg_combinations = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]

OPERATORS = [Operator(
    "Farmer cross the river with "+str(f)+" fox, "+str(c)+" chickens, "+str(g)+" grains",
    lambda s, f1=f, c1=c, g1=g: s.can_move(f1, c1, g1),
    lambda s, f1=f, c1=c, g1=g: s.move(f1, c1, g1))
    for (f, c, g) in fcg_combinations]
#</OPERATORS>

# <GOAL_MESSAGE_FUNCTION> (optional)
GOAL_MESSAGE_FUNCTION = lambda s: goal_message(s)
# </GOAL_MESSAGE_FUNCTION>
