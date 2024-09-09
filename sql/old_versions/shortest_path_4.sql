EXPLAIN WITH RECURSIVE traversed AS (
  SELECT
    ARRAY[person1id] AS path,  -- path array starts with the origin node
    person2id AS node_id       -- the current node in path
  FROM Person_knows_Person
  WHERE person1id = 772  -- starting point

  UNION ALL

  SELECT
    traversed.path || pkp.person1id::bigint,  -- extend the current path with explicit casting
    pkp.person2id                     -- new node to explore
  FROM traversed
  JOIN Person_knows_Person pkp ON pkp.person1id = traversed.node_id
  WHERE NOT (pkp.person2id = ANY(traversed.path))  -- prevent cycles by ensuring the new node isn't already in the path
    AND NOT (ARRAY[910::bigint] <@ (traversed.path || pkp.person1id::bigint))  -- continue recursion only if the target node isn't reached yet
)
SELECT path || node_id as path  -- display the path including the current node
FROM traversed
WHERE node_id = 910  -- filter to paths that end with the target node ID
