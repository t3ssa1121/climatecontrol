CREATE TABLE manodes (
    manode_id   INTEGER   PRIMARY KEY ON CONFLICT ABORT
                          NOT NULL,
    manode_user TEXT (12) NOT NULL,
    manode_pwd  TEXT (24) NOT NULL,
    diag_queue  TEXT (24),
    temp_queue  TEXT
);