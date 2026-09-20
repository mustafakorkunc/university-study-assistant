from google import genai
from google.genai import types
import json
from pyvis.network import Network
import config

def extract_knowledge_graph(text_chunks, api_key):
    client = genai.Client(api_key=api_key)
    
    # Combine chunks for graph extraction (use a sample if too large)
    context = "\n".join([c["content"] for c in text_chunks[:20]])
    
    prompt = (
        "Analyze the following educational text and extract a knowledge graph of core entities (concepts, theorems, definitions). "
        "Identify relationships such as 'Dependency', 'Extends', 'Contradicts', or 'Relates_to'. "
        "Return ONLY a JSON object with 'nodes' (list of dicts with 'id' and 'label') and 'edges' (list of dicts with 'source', 'target', and 'type').\n\n"
        f"Text:\n{context}"
    )
    
    try:
        response = client.models.generate_content(
            model=config.MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Graph extraction error: {e}")
        return {"nodes": [], "edges": []}

def generate_pyvis_html(graph_data):
    if not graph_data or not graph_data.get("nodes"):
        return "<div>No graph data available.</div>"
        
    net = Network(height='500px', width='100%', directed=True, notebook=False)
    for node in graph_data["nodes"]:
        net.add_node(node["id"], label=node.get("label", node["id"]), color="#4CAF50")
    for edge in graph_data["edges"]:
        net.add_edge(edge["source"], edge["target"], title=edge.get("type", ""))
        
    return net.generate_html()
