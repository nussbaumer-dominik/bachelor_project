WITH RECURSIVE ShortestPath AS (
    -- Base case: Initialize the recursion with the start person
    SELECT person1id AS start, person2id AS destination, 1 AS level, 
           CAST(person1id AS VARCHAR) || '->' || CAST(person2id AS VARCHAR) AS path
    FROM Person_knows_Person
    WHERE person1id = 772

    UNION ALL

    -- Recursive case: Expand the path by joining with the edges where the end of the previous path is the start of the next
    SELECT sp.start, p2p.person2id AS destination, sp.level + 1, 
           sp.path || '->' || CAST(p2p.person2id AS VARCHAR) AS path
    FROM ShortestPath sp
    JOIN Person_knows_Person p2p ON p2p.person1id = sp.destination
    WHERE sp.level < 5 OR p2p.person2id = 1628 -- The stopping condition ensures that paths are not excessively long
)
-- Select the shortest path to the target person
SELECT *
FROM ShortestPath
WHERE destination = 1628
ORDER BY level
LIMIT 1;
