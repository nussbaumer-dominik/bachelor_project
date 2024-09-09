WITH RECURSIVE friend_distance_graph (from_person_id, to_person_id, path, depth) AS (
  SELECT pkp.person1id, pkp.person2id, ARRAY[pkp.person1id, pkp.person2id] AS path, 0 AS depth
  FROM Person_knows_Person AS pkp
  UNION ALL
  SELECT g.from_person_id, pkp.person2id, g.path || ARRAY[pkp.person2id], g.depth + 1
  FROM Person_knows_Person AS pkp
  JOIN friend_distance_graph AS g
    ON pkp.person1id = g.to_person_id
    AND pkp.person2id != ALL(g.path)
  WHERE g.depth < 2
)
SELECT * FROM friend_distance_graph;