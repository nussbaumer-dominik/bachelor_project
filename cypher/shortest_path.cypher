MATCH (start: Person {id: 1}), (end: Person {id :4999})
MATCH p = shortestPath((start)-[:KNOWS*]-(end))
RETURN p