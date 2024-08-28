MATCH p = (start:Person {id: 33})-[:KNOWS*8]-(fof:Person)
WHERE start <> fof
RETURN COUNT(DISTINCT fof.id) AS countOfPersons;
