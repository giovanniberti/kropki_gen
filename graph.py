from collections import defaultdict
from functools import total_ordering


@total_ordering
class Infinity:
    def __lt__(self, other):
        if type(other) in {int, Infinity}:
            return False
        else:
            raise TypeError("Only integers can be compared against `Infinity`")

    def __eq__(self, other):
        return type(other) is Infinity

    def __add__(self, other):
        if type(other) in {int, Infinity}:
            return self


def reconstruct_path(came_from, current):
    total_path = [current]
    while current in came_from.keys():
        current = came_from[current]
        total_path.append(current)

    return list(reversed(total_path))


def a_star(start_node, is_goal, neighbors, h, d):
    openset = {start_node}
    came_from = {}

    best_costs = defaultdict(Infinity)
    best_costs[start_node] = 0

    best_scores = defaultdict(Infinity)
    best_scores[start_node] = h(start_node)

    max_c = -1

    while openset:
        current = min(openset, key=lambda n: best_scores[n])

        if len(current) > max_c:
            max_c = len(current)
            print(f"Current max: {max_c}")

        if is_goal(current):
            return current

        openset.remove(current)
        for neighbor in neighbors(current):
            tentative_cost = best_costs[current] + d(current, neighbor)

            if tentative_cost < best_costs[neighbor]:
                came_from[neighbor] = current
                best_costs[neighbor] = tentative_cost
                best_scores[neighbor] = tentative_cost + h(neighbor)

                if neighbor not in openset:
                    openset.add(neighbor)

    return None
