 WITH RECURSIVE path(start_id, end_id, path, depth, found) AS (
    SELECT
        person1id AS start_id,
        person2id AS end_id,
        ARRAY[person1id, person2id]::bigint[] AS path,
        1 AS depth,
        person2id = 66 AS found
    FROM
        Person_knows_Person
    WHERE
        person1id = 14

    UNION ALL

    SELECT
        p.start_id,
        pkp.person2id,
        p.path || pkp.person2id,
        p.depth + 1,
        pkp.person2id = 66 AS found
    FROM
        path p
    JOIN
        Person_knows_Person pkp ON p.end_id = pkp.person1id
    WHERE
        p.depth < 100
        AND NOT pkp.person2id = ANY(p.path)
        AND NOT p.found
)
SELECT path, depth
FROM path
WHERE found
LIMIT 1;