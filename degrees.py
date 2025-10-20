import csv
import sys

from util import Node, StackFrontier, QueueFrontier, visualize_path, visualize_path_as_graph, measure_execution_time

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    # Escolher algoritmo
    print("Escolha o algoritmo:")
    print("1: BFS tradicional")
    print("2: Bidirectional BFS")
    choice = input("Digite 1 ou 2 (padrão: 1): ").strip()
    if choice == "2":
        search_func = bidirectional_shortest_path
        print("Usando Bidirectional BFS.")
    else:
        search_func = shortest_path
        print("Usando BFS tradicional.")

    # Solicitar nome de origem até encontrar ou sair
    while True:
        name = input("Name: ")
        if name.lower() == "q":
            sys.exit("Programa encerrado pelo usuário.")
        source = person_id_for_name(name)
        if source is not None:
            break
        print("Person not found. Try again or type 'q' to quit.")

    # Solicitar nome de destino até encontrar ou sair
    while True:
        name = input("Name: ")
        if name.lower() == "q":
            sys.exit("Programa encerrado pelo usuário.")
        target = person_id_for_name(name)
        if target is not None:
            break
        print("Person not found. Try again or type 'q' to quit.")

    path, execution_time = measure_execution_time(search_func, source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")
        visualize_path(path, people, movies)
        visualize_path_as_graph(path, people, movies)
    
    print(f"Tempo de execução: {execution_time:.4f} segundos")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    # Inicialização do BFS: cria o nó inicial (ator de origem) e adiciona à fila (fronteira)
    start = Node(state=source, parent=None, action=None)
    frontier = QueueFrontier()
    frontier.add(start)
    # Conjunto para registrar estados já explorados e evitar revisitas
    explored = set()
    
    # Exploração: enquanto houver nós na fila, processa o próximo da fila (FIFO)
    while not frontier.empty():
        # Remove o nó mais antigo da fila (garante ordem de distância crescente)
        node = frontier.remove()

        # Se o nó atual é o destino, reconstrói e retorna o caminho percorrido
        if node.state == target:
            path = []
            while node.parent is not None:
                path.append((node.action, node.state))
                node = node.parent
            path.reverse()
            return path

        # Marca o nó atual como explorado
        explored.add(node.state)

        # Para cada vizinho (ator conectado por filme), verifica se já foi explorado ou está na fila
        for movie_id, person_id in neighbors_for_person(node.state):
            if person_id not in explored and not frontier.contains_state(person_id):
                # Adiciona vizinho à fila para futura exploração
                child = Node(state=person_id, parent=node, action=movie_id)
                # Se o vizinho é o destino, reconstrói e retorna o caminho imediatamente
                if person_id == target:
                    path = []
                    while child.parent is not None:
                        path.append((child.action, child.state))
                        child = child.parent
                    path.reverse()
                    return path
                frontier.add(child)

    # Se a fila esvaziar sem encontrar o destino, não há caminho possível
    return None


def bidirectional_shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target using bidirectional BFS.

    If no possible path, returns None.
    """
    if source == target:
        return []

    # Inicialização das fronteiras e explorados para source e target
    start = Node(state=source, parent=None, action=None)
    end = Node(state=target, parent=None, action=None)
    frontier_start = QueueFrontier()
    frontier_end = QueueFrontier()
    frontier_start.add(start)
    frontier_end.add(end)
    explored_start = set([source])
    explored_end = set([target])

    # Dicionários para rastrear pais
    parent_start = {source: None}
    parent_end = {target: None}
    action_start = {source: None}
    action_end = {target: None}

    while not frontier_start.empty() and not frontier_end.empty():
        # Expande da fonte
        node_start = frontier_start.remove()
        for movie_id, person_id in neighbors_for_person(node_start.state):
            if person_id not in explored_start:
                explored_start.add(person_id)
                parent_start[person_id] = node_start.state
                action_start[person_id] = movie_id
                frontier_start.add(Node(state=person_id, parent=node_start, action=movie_id))
                if person_id in explored_end:
                    # Encontrou interseção, reconstrói caminho
                    return reconstruct_path(person_id, parent_start, action_start, parent_end, action_end)

        # Expande do alvo
        node_end = frontier_end.remove()
        for movie_id, person_id in neighbors_for_person(node_end.state):
            if person_id not in explored_end:
                explored_end.add(person_id)
                parent_end[person_id] = node_end.state
                action_end[person_id] = movie_id
                frontier_end.add(Node(state=person_id, parent=node_end, action=movie_id))
                if person_id in explored_start:
                    # Encontrou interseção, reconstrói caminho
                    return reconstruct_path(person_id, parent_start, action_start, parent_end, action_end)

    return None


def reconstruct_path(meeting_point, parent_start, action_start, parent_end, action_end):
    """
    Reconstrói o caminho a partir do ponto de encontro.
    """
    path = []
    # Caminho da fonte ao ponto de encontro
    current = meeting_point
    while parent_start[current] is not None:
        path.append((action_start[current], current))
        current = parent_start[current]
    path.reverse()

    # Caminho do alvo ao ponto de encontro
    if parent_end[meeting_point] is not None:
        path.append((action_end[meeting_point], parent_end[meeting_point]))
        current = parent_end[meeting_point]
        while parent_end[current] is not None:
            path.append((action_end[current], parent_end[current]))
            current = parent_end[current]

    return path


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
