CREATE TABLE IF NOT EXISTS movies (
    name VARCHAR(255),
    rating VARCHAR(10),
    genre VARCHAR(100),
    year INT,
    released VARCHAR(100),
    score DECIMAL(3,1),
    votes INT,
    director VARCHAR(255),
    writer VARCHAR(255),
    star VARCHAR(255),
    country VARCHAR(100),
    budget BIGINT,
    gross BIGINT,
    company VARCHAR(255),
    runtime DECIMAL(5,1)
);

LOAD DATA INFILE 'movies_updated.csv'
INTO TABLE movies
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS; 
