MATCH p = (start:Person {id: 772})-[:KNOWS*8]-(fof:Person)
WHERE start <> fof
RETURN DISTINCT fof.id AS person2id
ORDER BY person2id;
