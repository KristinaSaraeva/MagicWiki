from argparse import ArgumentParser, BooleanOptionalAction
import json
import math
import igraph as ig



def parser_args() -> tuple[str, str, bool]:
    parser = ArgumentParser(description="Find shortest path between two pages")
    parser.add_argument(
        "--from",
        type=str,
        help="Starting page",
        dest="from_",
    )
    parser.add_argument(
        "--to",
        type=str,
        help="Finishing page",
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="Render the graph",
    )

    args = parser.parse_args()
    return args.from_, args.to, args.render


def load_data(file_path: str) -> dict:
    with open(file_path, 'r') as f:
        data = json.load(f)   
    return data

def preprocess_vertices(data: dict) -> dict:
    key_vertices = data.keys()
    preprocessed_vertices = {
        key_vertex: [vertex for vertex in connected_vertices if vertex in key_vertices]
        for key_vertex, connected_vertices in data.items()
    }
    return preprocessed_vertices

def create_graph(edge_list: list) -> ig.Graph:
    g = ig.Graph.TupleList(edge_list, directed=True)
    return g

def visualize_graph(g: ig.Graph, key_vertices: dict) -> ig.Plot:
    layout = g.layout("kk")
    degrees = g.degree()
    max_degree = max(degrees) if degrees else 1
    min_vertex_size = 1
    vertex_scaler = 20
    log_sizes = [math.log(deg + 1) / math.log(max_degree + 1) * vertex_scaler + min_vertex_size for deg in degrees]

    vertex_labels = [f"{vertex}" for vertex in g.vs["name"]]

    plot = ig.plot(
        g,
        layout=layout,
        bbox=(2048, 2048),
        edge_arrow_size=0,
        edge_width=0.1,
        vertex_size=log_sizes,
        margin=20,
        vertex_label=vertex_labels,
    )
    
    return plot


def start_path(data: dict,start: str,
    end: str,render: bool=False) -> None:
    preprocessed_vertices = preprocess_vertices(data)
    edge_list = [(source, target) for source, targets in preprocessed_vertices.items() for target in targets]
    g = create_graph(edge_list)
    if start is not None or end is not None:
        try:
            start_vertex_id = g.vs.find(name=start).index
            end_vertex_id = g.vs.find(name=end).index
            pathes = g.get_shortest_paths(start_vertex_id, to=end_vertex_id, output="vpath")
            path_indices = pathes[0]
            path_vertex_names = [g.vs[idx]["name"] for idx in path_indices]
            print(f"Shortest path from {start} to {end} is:")
            print(" -> ".join(path_vertex_names))
        except:
            print(f"Vertex {start} or {end} not found. Check the spelling and try again.")
    if render:
        plot=visualize_graph(g,preprocessed_vertices)
        plot.save("wiki_graph.png")
    


if __name__ == "__main__":
    try:
        wiki_file_name = "wiki.json"
        start, end, render = parser_args()
    except KeyError:
        print("Database not found")
    try:
        with open(wiki_file_name, "r") as wiki_file:
            data = json.load(wiki_file)
    except FileNotFoundError as ex:
        print("Database not found")
    except json.decoder.JSONDecodeError as ex:
        print("Error in json file")   
    start_path(data, start, end, render)
