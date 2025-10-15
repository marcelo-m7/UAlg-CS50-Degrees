import csv
import sys

from util import Node, StackFrontier, QueueFrontier

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

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

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


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    source_person: str = source
    target_person: str = target
    path: list[tuple[str, str]] = []

    def initialize_frontier(initial_state: str) -> QueueFrontier:
        """
        Inicializa e devolve uma QueueFrontier contendo o nó inicial.

        Args:
            initial_state: id da pessoa do nó inicial.

        Returns:
            Uma instância de QueueFrontier com o nó inicial adicionado.
        """
        start_node = Node(state=initial_state, parent=None, action=None)
        frontier = QueueFrontier()
        frontier.add(start_node)
        return frontier

    def reconstruct_path(node: Node) -> list[tuple[str, str]]:
        """
        Reconstrói o caminho desde `node` até o nó inicial, retornando uma
        lista de pares (id_filme, id_pessoa) em ordem da origem para o destino.

        Args:
            node: o nó objetivo (instância de Node) cuja cadeia de pais leva à origem.

        Returns:
            Lista de tuplas (id_filme, id_pessoa).

        Exemplo:
            Suponha que temos o seguinte caminho:
            - Nó inicial: Node(state="1", parent=None, action=None)
            - Nó intermediário: Node(state="2", parent=nó_inicial, action="A")
            - Nó final: Node(state="3", parent=nó_intermediário, action="B")

            O caminho reconstruído será:
            [("A", "2"), ("B", "3")]
        """
        path: list[tuple[str, str]] = []
        while node.parent is not None:
            # Adiciona o par (id_filme, id_pessoa) ao caminho
            path.append((node.action, node.state))
            node = node.parent  # Move para o nó pai
        path.reverse()  # Inverte o caminho para que fique da origem ao destino
        return path

    def add_neighbors(node: Node, frontier: QueueFrontier, explored: set[str], target: str) -> list[tuple[str, str]] | None:
        """
        Adiciona os vizinhos do nó atual à fronteira, retornando o caminho se o destino for encontrado.

        Args:
            node: nó atual.
            frontier: fronteira de busca.
            explored: conjunto de estados já explorados.
            target: id da pessoa do destino.

        Returns:
            Lista de tuplas (id_filme, id_pessoa) se o destino for encontrado, senão None.
        """
        for movie_id, person_id in neighbors_for_person(node.state):
            if person_id not in explored and not frontier.contains_state(person_id):
                child = Node(state=person_id, parent=node, action=movie_id)
                if person_id == target:
                    return reconstruct_path(child)
                frontier.add(child)
        return None

    frontier = initialize_frontier(source_person)
    explored: set[str] = set()

    while not frontier.empty():
        node = frontier.remove()

        if node.state == target_person:
            return reconstruct_path(node)

        explored.add(node.state)

        # Se um vizinho for o destino, add_neighbors retorna o caminho
        path = add_neighbors(node, frontier, explored, target_person)
        if path is not None:
            return path

    return None


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
