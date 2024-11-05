import heapq
import time

class Nodo:
    def __init__(self, dato, padre, costo, heuristica):
        self.dato = dato
        self.padre = padre
        self.costo = costo
        self.heuristica = heuristica

    def __lt__(self, other):
        return (self.costo + self.heuristica) < (other.costo + other.heuristica)

    def GenerarSucesores(self, grid):
        x, y = self.dato
        sucesores = []
        movimientos = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for mov in movimientos:
            nuevo_x, nuevo_y = x + mov[0], y + mov[1]
            if 0 <= nuevo_x < len(grid) and 0 <= nuevo_y < len(grid[0]) and grid[nuevo_x][nuevo_y] == 0:
                sucesores.append((nuevo_x, nuevo_y))
        return sucesores

def heuristica(estado, estado_final):
    return abs(estado[0] - estado_final[0]) + abs(estado[1] - estado_final[1])

def Astar(estado_inicial, estado_final, grid):
    nodoactual = Nodo(estado_inicial, None, 0, heuristica(estado_inicial, estado_final))
    nodosgenerado = []
    nodosvisitados = set()
    heapq.heappush(nodosgenerado, nodoactual)

    inicio = time.perf_counter()

    while nodosgenerado:
        nodoactual = heapq.heappop(nodosgenerado)
        if nodoactual.dato == estado_final:
            break

        sucesores = nodoactual.GenerarSucesores(grid)
        for sucesor in sucesores:
            temp = Nodo(sucesor, nodoactual, nodoactual.costo + 1, heuristica(sucesor, estado_final))
            if temp.dato not in nodosvisitados:
                heapq.heappush(nodosgenerado, temp)
        nodosvisitados.add(nodoactual.dato)

    camino = []
    while nodoactual:
        camino.append(nodoactual.dato)
        nodoactual = nodoactual.padre
    camino.reverse()
    fin = time.perf_counter()
    return camino, len(nodosvisitados), fin - inicio