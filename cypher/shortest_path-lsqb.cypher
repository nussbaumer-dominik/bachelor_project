MATCH p = shortestPath((start: Person {id: 14})-[:KNOWS*..10]-(end: Person {id: 66}))
RETURN p