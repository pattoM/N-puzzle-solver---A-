#Written in python 2.7
from copy import deepcopy
#from Queue import PriorityQueue

class PuzzleNode:
    """
    When the class initialization is happening:
    - parent attribute stores the parent node from which this child was generated
    - action attribute defines action that was taken from parent to arrive at current state
    - currentState is a representation of a state in the puzzle. It is a 2-dimensional list
    - children is a list that references the children generated from the current node after all possible actions
    - __str__ function visualizes the state in an easy to read format 
    - g_cost is the cost to arrive at current node. It is the parents g_cost + 1. Every swap has a cost of 1
    """
    def __init__(self, currentState, parent = None, action=None):
        self.currentState = currentState
        self.parent = parent
        self.children = []
        self.action = action
        if parent == None:
            self.g_cost = 0
        else:
            self.g_cost = self.parent.g_cost + 1
        
        
        
        
    def __str__(self):
        string_rep = ''
        for row in self.currentState:
            string_rep += (" | ".join(map(str, row))) + "\n"
        return string_rep
    
def validate_state(size, state):
    """
    Returns True if the start state is valid, False otherwise
    Validation is done by checking for format of the input, the size and if all numbers appear only once
    """
    #check size to be an int, also size is 3 and above 
    if type(size) is not int or size < 3:
        return False
    #check if state is composed of lists and check sizes as well
    if type(state.currentState) is list and len(state.currentState) == size:
        for row in state.currentState:
            if type(row) is list and len(row) == size:
                pass
            else:
                return False
    else:
        return False
    
    #check if only numbers are contained and if required no's are present 
    for i in list(range(size**2)):
        if any(i in sublist for sublist in state.currentState):
            pass
        else:
            return False
        
    #return true if no exception until this stage did not terminate function
    return True

def manhattan(state):
    """
    Heuristic function that takes a state as input and gives a numerical value as the sums
    of the manhattan distances to goal state
    """
    dist = 0
    for m in range(len(state)):
        for n in range(len(state)):
            #if state[m][n] == 0:
                #continue
            #dist += abs(m - state[m][n] / len(state)) + abs(n - (state[m][n] % len(state)))
            x, y = divmod(state[m][n], len(state))
            dist += abs(x-m) + abs(y-n)
    return dist

def misplaced(state):
    """
    A heuristic function that returns a numerical value based on the number of misplaced tiles
    wrt goal state
    """
    #collapse original 2d list into 1d list
    collapsed = [j for sub in state for j in sub]
    count = 0 
    #use a for loop to compare outputs 
    for index, val in enumerate(range(len(state)**2)):
        if collapsed[index] != val:
            count += 1 
    #subtract 1 if zero was counted as misplaced 
    if collapsed[0] == 0:
        return count
    else:
        return count - 1 
    

#a list handler for the heuristic functions 
heuristics = [misplaced, manhattan]

#function to retrieve node with lowest f value from frontier
#replaces a priority queue 
def lowest_f_val(frontierList, heuristic):
    """
    Returns the lowest cost node in frontier as well as the index of the node 
    """
    #start with left most f value and compare the rest against it
    list_rep = deepcopy(frontierList[0].currentState)
    low_f = (heuristics[heuristic](list_rep) + frontierList[0].g_cost) 
    low_f_index = 0
    for i, j in enumerate(frontierList):
        if i == 0:
            continue
        if (heuristics[heuristic](deepcopy(j.currentState)) + j.g_cost) < low_f:
            low_f = (heuristics[heuristic](deepcopy(j.currentState)) + j.g_cost)
            low_f_index = i
    return (frontierList[low_f_index], low_f_index)

def is_goal(state):
    """
    Returns true or false depending on if the current node is the goal state
    """
    collapsed = [j for sub in state for j in sub]
    #use a for loop to compare outputs 
    for index, val in enumerate(range(len(state)**2)):
        if collapsed[index] != val:
            return False
    return True

def generate_children(node):
    """
    Generates and returns all possible child nodes(states) from the current node
    """
    state_list = node.currentState[:]
    #locate the position of zero for swapping
    for i in range(len(state_list)):
        for j in range(len(state_list)):
            if state_list[i][j] == 0:
                x_idx, y_idx = i, j 
                break
    child_states = []
    size = len(state_list)
    #check if swap up, down, left, right is possible and generate the successor states 
    if x_idx - 1 >= 0:
        state_array = deepcopy(state_list)
        state_array[x_idx][y_idx] = state_array[x_idx-1][y_idx]
        state_array[x_idx-1][y_idx] = 0
        new_node = PuzzleNode(state_array, node, 'left')
        child_states.append(new_node)
        
    if x_idx + 1 < size:
        state_array = deepcopy(state_list)
        state_array[x_idx][y_idx] = state_array[x_idx+1][y_idx]
        state_array[x_idx+1][y_idx] = 0
        new_node = PuzzleNode(state_array, node, 'right')
        child_states.append(new_node)
        
    if y_idx - 1 >= 0:
        state_array = deepcopy(state_list)
        state_array[x_idx][y_idx] = state_array[x_idx][y_idx - 1]
        state_array[x_idx][y_idx - 1] = 0
        new_node = PuzzleNode(state_array, node, 'up')
        child_states.append(new_node)
        
    if y_idx + 1 < size:
        state_array = deepcopy(state_list)
        state_array[x_idx][y_idx] = state_array[x_idx][y_idx + 1]
        state_array[x_idx][y_idx + 1] = 0
        new_node = PuzzleNode(state_array, node, 'down')
        child_states.append(new_node)
    
    return child_states

def solvePuzzle(n, state, heuristic, prnt):
    """
    Returns three values: 
    - number of steps to optimally reach goal state from start state 
    - maximum size of the frontier at any time during execution 
    - an error code when an exception/error is encountered
    
    """
    #check if state is valid 
    if validate_state(n, state):
        pass
    else:
        return (0,0,-1)
    #open list
    front = []
    #closed list
    closed = []
    #add state to front initially 
    front.append(state)
    #track frontier size 
    max_frontier_size = 1
    #q = PriorityQueue()
    
    
    while front:
        curNode, idx = lowest_f_val(front, heuristic)
        if is_goal(curNode.currentState):
            step_count = 0
            if prnt:
                print(curNode)
            pre=curNode.parent
            while pre:
                step_count += 1
                if prnt:
                    print(pre)
                    print(manhattan(pre.currentState[:]))
                pre=pre.parent
            return (step_count,max_frontier_size,0)
        front.pop(idx)
        closed.append(curNode)
        
        #generate child nodes from this parent
        children = generate_children(curNode)
        for child in children:
            in_closed = False
            for a, b in enumerate(closed):
                if b.currentState == child.currentState:
                    in_closed = True
                    break
            if not in_closed:
                in_open = False
                
                for k,l in enumerate(front):
                    if l.currentState == child.currentState:
                        in_open = True
                        if child.g_cost < front[k].g_cost:
                            front[k].g_cost = child.g_cost
                            front[k].parent = curNode
                if not in_open:
                    front.append(child)
                    if len(front) > max_frontier_size:
                        max_frontier_size = len(front)
                    
                        
                
    
    
    return False

    
    
size = 3   
a = PuzzleNode([[2,3,7],[1,8,0],[6,5,4]])
b = PuzzleNode([[5,7,6],[2,4,3],[8,1,0]])
c = PuzzleNode([[7,0,8],[4,6,1],[5,3,2]])

#soln1 = solvePuzzle(size, a, 1, True)
#soln1

#soln2 = solvePuzzle(size, b, 1, True)
#soln2
#soln3 = solvePuzzle(size, c, 1, True)
#soln3


        
