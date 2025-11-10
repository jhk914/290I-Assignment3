from fastapi import FastAPI, UploadFile, File
import uvicorn
from utils import create_graph_from_json
from dijkstra import dijkstra

app = FastAPI()
active_graph = None

@app.get("/")
async def root():
    return {"message": "Welcome to the Shortest Path Solver!"}

@app.post("/upload_graph_json/")
async def create_upload_file(file: UploadFile = File(...)):
    global active_graph
    filename = file.filename

    if not filename.lower().endswith(".json"):
        return {"Upload Error": "Invalid file type"}

    active_graph = create_graph_from_json(file)
    return {"Upload Success": filename}

@app.get("/solve_shortest_path/start_node_id={start_node_id}&end_node_id={end_node_id}")
async def get_shortest_path(start_node_id: str, end_node_id: str):
    global active_graph

    if active_graph is None:
        return {"Solver Error": "No active graph, please upload a graph first."}
    if start_node_id not in active_graph.nodes or end_node_id not in active_graph.nodes:
        return {"Solver Error": "Invalid start or end node ID."}

    start_node = active_graph.nodes[start_node_id]
    dijkstra(active_graph, start_node)

    end_node = active_graph.nodes[end_node_id]
    path = []
    cur = end_node
    while cur is not None:
        path.append(cur.id)
        cur = cur.prev
    path.reverse()

    if len(path) == 1 and path[0] != start_node_id:
        return {"shortest_path": None, "total_distance": None}

    return {"shortest_path": path, "total_distance": end_node.dist}

if __name__ == "__main__":
    print("Server running at http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
