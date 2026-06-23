# Same grid structure from earlier
grid = {
    "solar_panel": ["transformer_1"],
    "transformer_1": ["solar_panel", "house_1", "house_2", "battery"],
    "battery": ["transformer_1"],
    "house_1": ["transformer_1"],
    "house_2": ["transformer_1"],
}

def find_battery(grid, start_node):
    """
    Searches the grid graph starting from start_node to find a battery.
    Uses BFS (Breadth-First Search) - explores neighbors level by level.
    """
    visited = set()
    queue = [start_node]

    while queue:
        current = queue.pop(0)  # take the first item in the queue
        
        if current == "battery":
            return current  # found it!
        
        if current not in visited:
            visited.add(current)
            neighbors = grid.get(current, [])
            for neighbor in neighbors:
                if neighbor not in visited:
                    queue.append(neighbor)
    
    return None  # no battery found

# Test it
result = find_battery(grid, "solar_panel")
print(f"Battery search result: {result}")

def dispatch_power(solar_drop_predicted, grid):
    """
    Agent 2's main decision logic.
    If a solar drop is predicted, find the battery and reroute power.
    """
    if solar_drop_predicted:
        battery_node = find_battery(grid, "solar_panel")
        if battery_node:
            print(f"⚠️  Solar drop predicted! Rerouting power from: {battery_node}")
            return battery_node
        else:
            print("⚠️  Solar drop predicted, but NO BATTERY FOUND. Risk of blackout!")
            return None
    else:
        print("✓ Solar generation normal. No action needed.")
        return None

# Test both scenarios
print("\n--- Scenario 1: Solar drop predicted ---")
dispatch_power(solar_drop_predicted=True, grid=grid)

print("\n--- Scenario 2: Normal solar generation ---")
dispatch_power(solar_drop_predicted=False, grid=grid)