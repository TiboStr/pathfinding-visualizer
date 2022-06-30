from queue import PriorityQueue


def reconstruct_path(came_from, current):
    while current in came_from:
        current = came_from[current]
        current.make_path()


def h(node, end):
    return abs(node.x - end.x) + abs(node.y - end.y)  # Manhattan distance because not diagonal


def algorithm(grid, start, goal):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))  # f_score, count, node
    open_set_values = {start}

    came_from = {}

    f_score = {square: float("inf") for row in grid.grid for square in row}
    f_score[start] = h(start, goal)

    g_score = {square: float("inf") for row in grid.grid for square in row}
    g_score[start] = 0

    while not open_set.empty():
        current = open_set.get()[2]
        open_set_values.remove(current)

        if current == goal:
            reconstruct_path(came_from, goal)
            return

        neighbors = grid.get_neigbors(current)

        for n in neighbors:
            tentative_g_score = g_score[current] + 1
            if tentative_g_score < g_score[n]:
                came_from[n] = current
                g_score[n] = tentative_g_score
                f_score[n] = tentative_g_score + h(n, goal)
                if n not in open_set_values:
                    count += 1
                    open_set.put((f_score[n], count, n))
                    open_set_values.add(n)
                    n.make_possible_path()

        if current != start:
            current.make_no_path()

    # goal never reached
    return
