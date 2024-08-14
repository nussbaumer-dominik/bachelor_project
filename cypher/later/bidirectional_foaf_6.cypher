MATCH p = (start:Person {id: 772})-[:KNOWS*6]-(fof:Person)
WHERE start <> fof
RETURN COUNT(DISTINCT fof.id) AS countOfPersons;
