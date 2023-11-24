
-- Creates UUID extension if it doesn't exist
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
--
-- Creates film_state enum if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'film_state') THEN
        CREATE TYPE film_state AS ENUM ('NOT_TRANSCODED','TRANSCODING', 'COMPLETE');
    END IF;
END $$;

-- Rating table
CREATE TABLE IF NOT EXISTS rating (
  uuid uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  average float check (
    average BETWEEN 0
    AND 10
  ),
  story integer NOT NULL CHECK (
    story BETWEEN 0
    AND 10
  ),
  positions integer NOT NULL CHECK (
    positions BETWEEN 0
    AND 10
  ),
  pussy integer NOT NULL CHECK (
    pussy BETWEEN 0
    AND 10
  ),
  shots integer NOT NULL CHECK (
    shots BETWEEN 0
    AND 10
  ),
  boobs integer NOT NULL CHECK (
    boobs BETWEEN 0
    AND 10
  ),
  face integer NOT NULL CHECK (
    face BETWEEN 0
    AND 10
  ),
  rearview integer NOT NULL CHECK (
    rearview BETWEEN 0
    AND 10
  )
);

-- Film table
CREATE TABLE IF NOT EXISTS film (
  uuid uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  title text NOT NULL,
  date_added date NOT NULL,
  filename text NOT NULL,
  watched boolean NOT NULL,
  state film_state NOT NULL,
  thumbnail bytea NOT NULL,
  poster bytea NOT NULL,
  actresses text[] NOT NULL,
  rating uuid REFERENCES rating(uuid) ON DELETE CASCADE
);


-- function to get the weighted average of a film and write it to the entry.
CREATE OR REPLACE FUNCTION update_rating_average() RETURNS TRIGGER AS $$
BEGIN
  UPDATE rating SET average = (story * 0.2 + positions * 0.15 + pussy * 0.3 + shots * 0.1 + boobs * 0.15 + rearview * 0.1) / 1.0
  WHERE uuid = NEW.uuid;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger on rating table
CREATE OR REPLACE TRIGGER update_rating_average_trigger
AFTER INSERT OR UPDATE OF story, positions, pussy, shots, boobs, rearview ON rating
FOR EACH ROW
EXECUTE FUNCTION update_rating_average();

-- history table
CREATE TABLE IF NOT EXISTS history (
  uuid UUID,
  table_name VARCHAR(255),
  action VARCHAR(10),
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE OR REPLACE FUNCTION insert_update_delete_history_film()
RETURNS TRIGGER AS $$
BEGIN
  IF (TG_OP = 'INSERT') THEN
    INSERT INTO history (uuid, table_name, action)
    VALUES (uuid_generate_v4(), 'film', 'insert');
    RETURN NEW;
  ELSIF (TG_OP = 'UPDATE') THEN
    INSERT INTO history (uuid, table_name, action)
    VALUES (uuid_generate_v4(), 'film', 'update');
    RETURN NEW;
  ELSIF (TG_OP = 'DELETE') THEN
    INSERT INTO history (uuid, table_name, action)
    VALUES (uuid_generate_v4(), 'film', 'delete');
    RETURN OLD;
  END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER insert_update_delete_history_film_trigger
AFTER INSERT OR UPDATE OR DELETE ON film
FOR EACH ROW
EXECUTE FUNCTION insert_update_delete_history_film();

CREATE OR REPLACE FUNCTION insert_update_delete_history_rating()
RETURNS TRIGGER AS $$
BEGIN
  IF (TG_OP = 'INSERT') THEN
    INSERT INTO history (uuid, table_name, action)
    VALUES (uuid_generate_v4(), 'rating', 'insert');
    RETURN NEW;
  ELSIF (TG_OP = 'UPDATE') THEN
    INSERT INTO history (uuid, table_name, action)
    VALUES (uuid_generate_v4(), 'rating', 'update');
    RETURN NEW;
  ELSIF (TG_OP = 'DELETE') THEN
    INSERT INTO history (uuid, table_name, action)
    VALUES (uuid_generate_v4(), 'rating', 'delete');
    RETURN OLD;
  END IF;
END;
$$ LANGUAGE plpgsql;





-- function to log history
CREATE OR REPLACE TRIGGER  insert_update_delete_history_rating_trigger
AFTER INSERT OR UPDATE OR DELETE ON rating
FOR EACH ROW
EXECUTE FUNCTION insert_update_delete_history_rating();

