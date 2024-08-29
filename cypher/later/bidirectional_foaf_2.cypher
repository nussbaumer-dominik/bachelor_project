MATCH p = (start:Person {id: 33})-[:KNOWS*2]-(fof:Person)
WHERE start <> fof
RETURN COUNT(DISTINCT fof.id) AS countOfPersons;
