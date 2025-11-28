import sys

NIL = -1

def get_path(node, parent):
    path = []
    while node != NIL:
        path.insert(0, node)
        node = parent[node]
    return path

def display_paths(source, dist, parent):
    print(f"{'Source':<8}{'Destination':<12}{'Cost':<8}{'Route'}")
    for i in range(len(dist)):
        if i != source:
            if dist[i] == sys.maxsize:
                cost_str = "∞"
                route_str = "No path"
            else:
                cost_str = str(dist[i])
                route_str = " ".join(map(str, get_path(i, parent)))
            print(f"{source:<8}{i:<12}{cost_str:<8}{route_str}")

def shortest_path(cost, start):
    n = len(cost)
    dist = [sys.maxsize] * n
    visited = [False] * n
    parent = [NIL] * n

    dist[start] = 0

    for _ in range(n - 1):
        u = -1
        min_dist = sys.maxsize
        for v in range(n):
            if not visited[v] and dist[v] < min_dist:
                min_dist = dist[v]
                u = v

        if u == -1:
            break  # All remaining nodes are unreachable

        visited[u] = True

        for v in range(n):
            if cost[u][v] != 0 and not visited[v] and dist[u] + cost[u][v] < dist[v]:
                dist[v] = dist[u] + cost[u][v]
                parent[v] = u

    display_paths(start, dist, parent)

if __name__ == "__main__":
    network = [
        [0, 2, 4, 0, 0, 0],
        [2, 0, 1, 7, 0, 0],
        [4, 1, 0, 0, 3, 0],
        [0, 7, 0, 0, 2, 1],
        [0, 0, 3, 2, 0, 5],
        [0, 0, 0, 1, 5, 0]
    ]

    s = int(input(f"Enter starting router (0 - {len(network) - 1}): "))
    shortest_path(network, s)
