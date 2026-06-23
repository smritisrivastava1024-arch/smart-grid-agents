# Grid represented as a graph: each node connects to others via transmission lines
grid = {
    "solar_panel": ["transformer_1"],
    "transformer_1": ["solar_panel", "house_1", "house_2", "battery"],
    "battery": ["transformer_1"],
    "house_1": ["transformer_1"],
    "house_2": ["transformer_1"],
}

def show_grid():
    for node, connections in grid.items():
        print(f"{node} -> {connections}")

show_grid()