CREATE TABLE requests(  
    id VARCHAR(70) NOT NULL PRIMARY KEY COMMENT 'Primary Key',
    body JSON NOT NULL COMMENT '',
    duplicates INT UNSIGNED NOT NULL DEFAULT 0
);