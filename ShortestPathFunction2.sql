CREATE OR REPLACE FUNCTION find_shortest_path_with_depth_limit(start_person INT, end_person INT, max_depth INT)
RETURNS TEXT AS $$
DECLARE
    current_person INT;
    next_person INT;
    current_depth INT := 0;
    queue INT[] := ARRAY[start_person]; -- Initialize queue with the start person
    next_level_queue INT[] := ARRAY[]::INT[]; -- Explicitly cast to integer array
    visited JSONB := jsonb_build_object(start_person::text, ''); -- Using JSONB to map person to path
    path TEXT;
    path_found BOOLEAN := FALSE;
BEGIN
    -- BFS Loop
    WHILE array_length(queue, 1) IS NOT NULL AND current_depth < max_depth LOOP
        current_person := queue[1];
        queue := array_remove(queue, current_person); -- Dequeue

        -- Check if the end person is reached
        IF current_person = end_person THEN
            path_found := TRUE;
            EXIT;
        END IF;

        -- Enqueue all connected, unvisited persons
        FOR next_person IN
            SELECT person2id FROM Person_knows_Person WHERE person1id = current_person
            UNION
            SELECT person1id FROM Person_knows_Person WHERE person2id = current_person
        LOOP
            IF NOT (visited ? next_person::text) THEN
                visited := visited || jsonb_build_object(next_person::text, (visited ->> current_person::text || ',' || current_person)::text);
                next_level_queue := array_append(next_level_queue, next_person);
            END IF;
        END LOOP;

        -- Move to the next level if the current level is exhausted
        IF array_length(queue, 1) IS NULL AND array_length(next_level_queue, 1) IS NOT NULL THEN
            queue := next_level_queue;
            next_level_queue := ARRAY[]::INT[]; -- Reset with explicit type
            current_depth := current_depth + 1;
        END IF;
    END LOOP;

    -- Construct the path from the JSONB if path is found
    IF path_found THEN
        path := visited ->> end_person::text;
        RETURN TRIM(both ',' from path) || ',' || end_person; -- Return the complete path
    ELSE
        RETURN 'No path found';
    END IF;
END;
$$ LANGUAGE plpgsql;
