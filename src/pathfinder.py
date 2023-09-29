'''
CMSI 2130 - Homework 1
Author: <ISAIAH PAJARILLO>

Modify only this file as part of your submission, as it will contain all of the logic
necessary for implementing the A* pathfinder that solves the target practice problem.
'''
from queue import PriorityQueue
from maze_problem import MazeProblem
from dataclasses import *
from typing import *
import itertools

@dataclass
class SearchTreeNode:
    """
    SearchTreeNodes contain the following attributes to be used in generation of
    the Search tree:

    Attributes:
        player_loc (tuple[int, int]):
            The player's location in this node.
        action (str):
            The action taken to reach this node from its parent (or empty if the root).
        parent (Optional[SearchTreeNode]):
            The parent node from which this node was generated (or None if the root).
    """
    player_loc: tuple[int, int]
    action: str
    parent: Optional["SearchTreeNode"]


    # TODO: Add any other attributes and method overrides as necessary!
    
def pathfind(problem: "MazeProblem") -> Optional[list[str]]:
    """
    The main workhorse method of the package that performs A* graph search to find the optimal
    sequence of actions that takes the agent from its initial state and shoots all targets in
    the given MazeProblem's maze, or determines that the problem is unsolvable.

    Parameters:
        problem (MazeProblem):
            The MazeProblem object constructed on the maze that is to be solved or determined
            unsolvable by this method.

    Returns:
        Optional[list[str]]:
            A solution to the problem: a sequence of actions leading from the 
            initial state to the goal (a maze with all targets destroyed). If no such solution is
            possible, returns None.
    """
    # TODO: Implement A* Graph Search for the Pathfinding Biathlon!

    targets: set[tuple[int, int]] = problem.get_initial_targets()
    initial_loc: tuple[int, int] = problem.get_initial_loc()
    goal_point: tuple[int, int] = get_best_goal_point(problem, targets, initial_loc)
    counter = itertools.count()
    frontier: PriorityQueue[tuple[int, int ,SearchTreeNode]] = PriorityQueue()
    frontier.put((get_heuristic(goal_point,initial_loc),next(counter), SearchTreeNode(initial_loc, "", None)))
    iter: int = 0

    #case for if target is unreachable
    for target in targets:
        test_case: dict = problem.get_transitions(target,targets)
        if not test_case:
            return None

    while not frontier.empty():
    #case for if target is unreachable
        iter += 1
        if iter == 10:
            return None
    # Fetch the node with the highest priority from the frontier and retrieve possible moves from the current location.
    # For each move, determine the subsequent state and update targets if a shot is taken.
    # updates goal states once a shot is taken
    # Adjust child priorities if they are equal and then insert the child nodes back into the frontier.

        _ , w, expanding_node = frontier.get()
        location: tuple[int, int] = expanding_node.player_loc
        moves: dict = problem.get_transitions(location, targets)

        children: list[tuple[int, SearchTreeNode]] = []
        for key in moves:
            if key == "S" and location == goal_point and targets:
               targets = targets - problem.get_visible_targets_from_loc(location,targets)
               if not targets:
                   return _create_goal_path("S", expanding_node)
               else:
                    children.append((-1,(SearchTreeNode(location,"S",expanding_node)))) #?????
                    goal_point = get_best_goal_point(problem, targets, location)
            else:
                children.append((get_heuristic(goal_point,moves[key]["next_loc"]) + moves[key]["cost"],SearchTreeNode(moves[key]["next_loc"], key, expanding_node)))
        for i in range(len(children)):
            for j in range(i+1, len(children)):
                if children[i][0] == children[j][0]:
                    updated_value = children[j][0] + 1
                    children[j] = (updated_value, children[j][1])
        for integer, node in children:
                count = next(counter)
                frontier.put((integer, count, node))
    return None


def get_heuristic(goal_point: tuple[int, int], player_loc: tuple[int, int]) -> int:
    """
    takes in goal point and player location
    returns the manhattan distance 
    """
    x, y = player_loc
    x_goal, y_goal = goal_point
    return abs(x_goal - x) + abs(y_goal - y)

def get_best_goal_point(problem: "MazeProblem", targets: set[tuple[int,int]], initial_loc: tuple[int,int]) -> tuple[int,int]:
    """
    takes in targets, problem, and initial location
    find best vantage spot in which the most targets can be hit
    if only 1 target left, find the closest vantage spot to character
    returns vantage spot tuple
    """
    x_in, y_in = initial_loc
    if len(targets) == 1:
        xl, yl = list(targets)[0]
        pot_best_points = {(xl, y_in), (x_in, yl)}
    else:
        xs: list = [t[0] for t in targets]
        ys: list = [t[1] for t in targets]
        pot_best_points:set[tuple[int, int]] = {(x, y) for x in xs for y in ys if (x, y) not in targets}

    vis_best_points: dict = {}

    for point in pot_best_points:
        temp:set[tuple[int, int]] = problem.get_visible_targets_from_loc(point, targets)
        target_count: int = len(temp)
        vis_best_points[point] = target_count

    temp_target_counts: list[int] = []
    for x in vis_best_points.values():
        temp_target_counts.append(x)
    max_target_vis: int = max(temp_target_counts)

    final_points:list[tuple[int, int]] = []
    for best_points, best_count in vis_best_points.items():
        if best_count == max_target_vis:
            final_points.append(best_points)

    distances = [abs(xf - x_in) + abs(yf - y_in) for xf, yf in final_points]
    min_distance_index = distances.index(min(distances))
    goal_point = final_points[min_distance_index]
    return goal_point



def _create_goal_path(last_move: str, current: Optional[SearchTreeNode]) -> list[str]:
    """
    If the goal has been reached, then this method, _create_goal_path, will create the list[str] path from the initial
    state to the goal state. 

    Parameters:
        last_move (str):
            The last_move string is essentially the last move made from the maze to reach the goal.
        last_node_expanded (SearchTreeNode):
            The last_node_expanded is the final node that is expaneded from the tree that showed the goal state.

    Returns:
        list[str]:
            The solution to the problem: a sequence of actions leading from the 
            initial state to the goal.
    """

    path: str = last_move

    # Test Case: if the last_node_expanded is None, then return the last move made in a list.
    if current == None:
        return [last_move]

    while current is not None: # updates path with each move and assigns current to be parent
        path += current.action
        current = current.parent
    path = path[::-1]
    return list(path)