WITH RECURSIVE friends AS (
    SELECT person1id, person2id, 1 AS depth, ARRAY[person1id, person2id] AS path
    FROM Person_knows_Person
    WHERE person1id = 772

    UNION ALL

    SELECT f.person1id, f.person2id, fr.depth + 1, fr.path || f.person2id
    FROM Person_knows_Person f
    JOIN friends fr ON f.person1id = fr.person2id
    WHERE fr.depth < 3 AND f.person2id <> ALL(fr.path)
)
SELECT DISTINCT person2id
FROM friends
WHERE depth = 3
ORDER BY person2id;