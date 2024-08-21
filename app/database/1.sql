-- Create the enum type
CREATE TYPE subscription_plan_type AS ENUM ('free', 'weekly', 'monthly', 'annual');

-- Users table
CREATE TABLE
    users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        hashed_password VARCHAR(100) NOT NULL,
        subscription_plan VARCHAR(20) NOT NULL,
        subscription_end_date DATE,
        created_at TIMESTAMP
        WITH
            TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

-- Folders table
CREATE TABLE
    folders (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
        name VARCHAR(100) NOT NULL,
        created_at TIMESTAMP
        WITH
            TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

CREATE TABLE
    notes (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
        folder_id INTEGER REFERENCES folders (id) ON DELETE SET NULL,
        title VARCHAR(255) NOT NULL,
        summary TEXT NOT NULL,
        transcript_text TEXT NOT NULL,
        language VARCHAR(10) NOT NULL,
        flashcards JSONB DEFAULT NULL,
        quizzes JSONB DEFAULT NULL,
        created_at TIMESTAMP
        WITH
            TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        WITH
            TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

CREATE TABLE
    note_metadata (
        note_id INTEGER PRIMARY KEY REFERENCES notes (id) ON DELETE CASCADE,
        title VARCHAR(255) NOT NULL,
        content_category VARCHAR(50) NOT NULL,
        emoji_representation VARCHAR(10) NOT NULL,
        date_created TIMESTAMP
        WITH
            TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

CREATE INDEX idx_note_metadata_note_id ON note_metadata (note_id);

CREATE INDEX idx_folders_user_id ON folders (user_id);

CREATE INDEX idx_notes_user_id ON notes (user_id);

CREATE INDEX idx_notes_folder_id ON notes (folder_id);