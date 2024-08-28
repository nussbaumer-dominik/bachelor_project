WITH RECURSIVE path(start_id, end_id, path, depth) AS (
    SELECT 
        person1id AS start_id, 
        person2id AS end_id, 
        ARRAY[person1id, person2id]::bigint[] AS path, 
        1 AS depth
    FROM 
        Person_knows_Person
    WHERE 
        person1id = 14

    UNION ALL

    SELECT 
        p.start_id,
        pkp.person2id AS end_id,
        p.path || pkp.person2id,
        p.depth + 1
    FROM 
        path p
    JOIN 
        Person_knows_Person pkp ON p.end_id = pkp.person1id
    WHERE 
        pkp.person2id != ALL(p.path)
    AND 
        p.depth < 10
)
SELECT path, depth
FROM path
WHERE end_id = 66
ORDER BY depth ASC
LIMIT 1;