BEGIN TRANSACTION;

/*
    Table:           status
    Purpose:         Stores status information
    Columns:
    - id:            SERIAL PRIMARY KEY
    - status_desc:   Status description
*/
CREATE TABLE IF NOT EXISTS task_status (
    id              SERIAL PRIMARY KEY,
    status_desc     text NOT NULL
);

/*
    Table:           task
    Purpose:         Stores tasks
    Columns:
    - id:            SERIAL PRIMARY KEY
    - title          Title of the task
    - description    Description of the task (optional)
    - status_id:     The status of the task
    - due:           Date and time the task is due
*/
CREATE TABLE IF NOT EXISTS task (
    id              SERIAL PRIMARY KEY,
    task_title      text NOT NULL,
    task_desc       text,
    status_id       integer REFERENCES task_status (id),
    due             timestamp NOT NULL
);

END TRANSACTION;