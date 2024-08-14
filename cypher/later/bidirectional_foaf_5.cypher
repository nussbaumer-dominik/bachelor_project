MATCH p = (start:Person {id: 772})-[:KNOWS*5]-(fof:Person)
WHERE start <> fof
RETURN COUNT(DISTINCT fof.id) AS countOfPersons;
