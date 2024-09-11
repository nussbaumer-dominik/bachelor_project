WITH RECURSIVE shortest_path AS (
  SELECT
    person1id AS start_id,
    ARRAY[person1id] AS path,
    person2id AS current_id,
    0 AS path_length  -- Start path length from 0
  FROM Person_knows_Person
  WHERE person1id = 772  -- Start from person ID 772

  UNION

  SELECT
    sp.start_id,
    sp.path || pkp.person2id,  -- Extend the path array
    pkp.person2id AS current_id,
    sp.path_length + 1  -- Increment path length
  FROM shortest_path sp
  JOIN Person_knows_Person pkp ON pkp.person1id = sp.current_id
  WHERE NOT (pkp.person2id = ANY(sp.path))  -- Avoid cycles
  AND sp.path_length < 4   -- Prevent overly deep recursion
)
SELECT *
FROM shortest_path
WHERE current_id = 1628  -- Ensure the path ends at target ID 1628
  AND 1628 = ANY(path)  -- Verify that 1628 is indeed in the path
ORDER BY path_length
/*LIMIT 1;*/
