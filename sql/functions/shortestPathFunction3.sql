CREATE OR REPLACE FUNCTION search_path(start_id bigint, end_id bigint, path_array bigint[], depth int, OUT found boolean)
RETURNS VOID AS $$
DECLARE
    next_id bigint;
BEGIN
    IF start_id = end_id THEN
        found := true;
        IF shortest_path IS NULL OR array_length(path_array, 1) < array_length(shortest_path, 1) THEN
            shortest_path := path_array;
        END IF;
        RETURN;
    ELSIF depth > 10 THEN
        found := false;
        RETURN;
    END IF;

    FOR next_id IN
        SELECT person2id
        FROM Person_knows_Person
        WHERE person1id = start_id
        AND person2id != ALL(path_array)
    LOOP
        PERFORM search_path(next_id, end_id, path_array || next_id, depth + 1, found);
        IF found THEN
            RETURN;
        END IF;
    END LOOP;
    found := false;
END;
$$ LANGUAGE plpgsql;

DO $$
DECLARE
    shortest_path bigint[] := '{}';
    current_path bigint[];
    v_depth int := 14;
    target bigint := 66;
    is_found boolean := false;
BEGIN
    current_path := ARRAY[1];
    PERFORM search_path(1, target, current_path, v_depth, is_found);

    IF shortest_path IS NOT NULL AND is_found THEN
        RAISE NOTICE 'Shortest path found: %, Depth: %', shortest_path, array_length(shortest_path, 1) - 1;
    ELSE
        RAISE NOTICE 'No path found within depth limit.';
    END IF;

END $$;
