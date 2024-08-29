CREATE OR REPLACE FUNCTION shortest_path(start_person INT, end_person INT)
RETURNS TABLE(path INT[]) AS $$
DECLARE
    queue INT[]; -- To keep track of the nodes to be explored
    current_person INT;
    visited INT[]; -- Array to mark visited persons
    current_path INT[]; -- Path to current node
    paths JSONB; -- Store paths as a JSON object mapping person IDs to path arrays
    person_record RECORD; -- Define a record variable for use in the FOR loop
BEGIN
    -- Initialize queue with the start person and paths
    queue := ARRAY[start_person];
    paths := jsonb_set('{}', ARRAY[CAST(start_person AS TEXT)], '[]');
    visited := ARRAY[start_person];

    -- BFS Loop
    WHILE array_length(queue, 1) > 0 LOOP
        current_person := queue[1];
        queue := queue[2:]; -- Dequeue
        current_path := ARRAY(SELECT jsonb_array_elements_text(paths -> CAST(current_person AS TEXT))::INT);

        -- Check if the current node is the destination
        IF current_person = end_person THEN
            RETURN QUERY SELECT current_path;
            EXIT;
        END IF;

        -- Enqueue all unvisited adjacent nodes
        FOR person_record IN SELECT person2id FROM Person_knows_Person WHERE person1id = current_person AND person2id <> ALL(visited)
        LOOP
            queue := array_append(queue, person_record.person2id);
            visited := array_append(visited, person_record.person2id);
            -- Add new path for the adjacent node
            paths := jsonb_set(paths, ARRAY[CAST(person_record.person2id AS TEXT)], to_jsonb(array_append(current_path, person_record.person2id)));
        END LOOP;
    END LOOP;

    -- If no path is found
    RETURN QUERY SELECT NULL::INT[];
END;
$$ LANGUAGE plpgsql;
