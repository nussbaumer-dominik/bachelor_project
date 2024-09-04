MATCH p = shortestPath((start: Person {id: 1})-[:KNOWS*..10]-(end: Person {id: 4999}))
RETURN p