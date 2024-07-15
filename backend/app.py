from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import osmnx as ox
import networkx as nx

app = Flask(__name__)
api = Api(app)

print("Starting Flask application...")

locations = {
    "1300 Residence Hall" : [-75.15635994812898, 39.977970171375404],
    "1700 N. Broad St" : [-75.15831223243522, -39.979235375710694],
    "1800 Liacouras Walk" : [-75.15640443719982, 39.98074455414397],
    "1940 Residence Hall" : [-75.15627709010602, 39.98300135460683],
    "Alter Hall" : [-75.1558188094424, 239.98052681064288],
    "Anderson Hall" : [-75.1520667324351, 39.98110338721654],
    "Annenberg Hall" : [-75.1550073784608, 39.98389454795513],
    "Aramark STAR Complex" : [-75.15938883243506, 39.98082507207647],
    "Architecture Building" : [-75.15416346127054, 39.98376692387779],
    "Atlantic Terminal" : [-75.15049283575551, 39.9795322686302 ],
    "Avenue North Complex" : [-75.1592637459288, 39.97811197120224],
    "Barrack Hall" : [-75.15679944992272, 39.98162326380308],
    "Beasley School of Law" : [-75.15723807476424, 39.97994181649302],
    "Beech International Village" : [-75.16058971099324, 39.97911235561997],
    "Bell Tower" : [-75.1543591882577, 39.9815399254814],
    "Beury Hall" : [-75.15479892633505, 39.98230486512561],
    "Biology Life Sciences Building" : [-75.15360113058674, 39.98203212168543],
    "Carnell Hall" : [-75.1568691305867, 39.980947557310266],
    "Cecil B. Moore Station" : [-75.15798324962549, 39.97887541918765],
    "Charles Library" : [-75.15533672078986, 39.98238780130839],
    "Conwell Hall" : [-75.15713249195454, 39.980429056731985],
    "Conwell Inn" : [-75.15632630359963, 39.981775112604005],
    "Edberg-Olson Football Practice Facility" : [-75.15008975942202, 39.984849621662995],
    "Engineering Building" : [-75.15281190175122, 39.98272917639566],
    "Entertainment and Community Education Center" : [-75.15991563243514, 39.9793092968161],
    "Founder’s Garden" : [-75.15550374777706, 39.981429912733],
    "Howard Gittis Student Center" : [-75.15494855942231, 39.9795201325649],
    "Hilel at Temple Universtiy" : [-75.15841783428343, 39.98366849008919],
    "Geasey Outdoor Field Complex" : [-75.1592785594221, 39.98344158299621],
    "Gladfelter Hall" : [-75.1520796189416, 39.98131627077573],
    "Hardwick Hall" : [-75.1556379999027, 39.98445099806584],
    "Johnson Hall" : [-75.15579581524466, 39.98462823450215],
    "Kardon Building" : [-75.15000184592876, 39.97978994420192],
    "Leon H. Sullivan Charitable Trust" : [-75.15745308825801, 39.97513526330828],
    "Liacouras Center" : [-75.15848764592873, 39.97986727426617],
    "Mitten Hall" : [-75.15686168825765, 39.98218308990017],
    "Morgan Hall" : [-75.15725309010617, 39.978607419004305],
    "Newman Center" : [-75.15596063058655, 39.98577663500407],
    "Oxford Village" : [-75.15975817106757, 39.97816581392628],
    "Pearson & McGonigle Hall" : [-75.1576284612706, 39.98113599774745],
    "Presser Hall" : [-75.15433166311887, 39.983426449250665],
    "Ritner Complex" : [-75.15630398517038, 39.97921651535811],
    "Rock Hall" : [-75.15723753243518, 39.97939673281742], 
    "Science Education and Research Center" : [-75.15290279990285, 39.982082512178756, ],
    "Shusterman Hall" : [-75.15634343058672, 39.981403128181064],
    "Speakman Hall" : [-75.15567290359968, 39.981128971846054],
    "Sullivan Hall" : [-75.1563380612706, 39.98168878459194],
    "Susquehanna-Dauphin Station" : [-75.15608064777685, 39.98713705599797],
    "Temple Performing Arts Center" : [-75.15685637661248, 39.98157084437929],
    "Temple Towers" : [-75.15490274408046, 39.9782026994788],
    "Temple University Regional Rail Station" : [-75.14968409010608, 39.98135088676956],
    "Tomlinson Theater" : [-75.15485590544789, 39.98375793131097],
    "Tuttleman Learning Center" : [-75.15501617291581, 39.98054959055421],
    "Tyler School of Art and Architecture" : [-75.15349521894143, 39.983413874006416],
    "University Village" : [-75.15088864962564, 39.97816418549572],
    "Wachman Hall" : [-75.15708509195444, 39.98114663457736],
    "Weiss Hall" : [-75.15518723243528, 39.97875499145514],
    "Welcome Center" : [-75.15345975428671, 39.98057878922882],
    "James S. White Hall" : [-75.15687403798006, 39.98571137115688]
}

# Creates a graph of Temple University's campus and it's walking paths
G = ox.graph_from_place('Temple University, Philadelphia, PA', network_type='walk')
print("Road network created")

# Converts Locations to Nearest Nodes
location_nodes = {}
for location, coords in locations.items():
    node = ox.distance.nearest_nodes(G, coords[0], coords[1])
    location_nodes[location] = node
print("Nodes have been established")

# Implements Dijkstra's algorithm to find the shortest path between two locations
def dijkstra_osmnx(graph, start, end):
    path = nx.shortest_path(graph, source=start, target=end, weight='length')
    distance = nx.shortest_path_length(graph, source=start, target=end, weight='length')
    return path, distance

def node_to_location_name(node):
    for name, n in location_nodes.items():
        if n == node:
            return name
    return str(node)

class ShortestPath(Resource):
    def get(self):
        print("Received request for shortest path.")
        start = request.args.get('start')
        end = request.args.get('end')
        
        if start not in location_nodes or end not in location_nodes:
            print("Invalid start or end location.")
            return {'error': 'Invalid start or end location'}, 400
        
        start_node = location_nodes[start]
        end_node = location_nodes[end]
        
        path, distance = dijkstra_osmnx(G, start_node, end_node)
        
        # Convert path nodes back to location names
        path_names = [node_to_location_name(node) for node in path]
        
        print("Path found:", path_names)
        return {'path': path_names, 'distance_miles': distance * 0.000621371}  # Convert meters to miles

api.add_resource(ShortestPath, '/shortest_path')

print("Endpoint /shortest_path registered.")

if __name__ == '__main__':
    print("Running Flask app...")
    print("Start node:", location_nodes.get("1300 Residence Hall"))
    print("End node:", location_nodes.get("Alter Hall"))

    app.run(debug=True)