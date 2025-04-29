import mysql.connector
import csv
from mysql.connector import Error

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='surgodriti'  # use your database password, this is mine
        )
        if connection.is_connected():
            print("Connected to MySQL server")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_database(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("DROP DATABASE IF EXISTS movie_db")
        cursor.execute("CREATE DATABASE movie_db")
        cursor.execute("USE movie_db")
    except Error as e:
        print(f"Error creating database: {e}")

def create_tables(connection):
    try:
        cursor = connection.cursor()
        
        cursor.execute("""
        CREATE TABLE movies (
            movie_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            year INT,
            genre VARCHAR(100),
            rating VARCHAR(10),
            runtime DECIMAL(5,1)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE crew (
            crew_id INT AUTO_INCREMENT PRIMARY KEY,
            movie_id INT,
            director VARCHAR(255),
            writer VARCHAR(255),
            star VARCHAR(255),
            FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE
        )
        """)
        
        cursor.execute("""
        CREATE TABLE production (
            production_id INT AUTO_INCREMENT PRIMARY KEY,
            movie_id INT,
            country VARCHAR(100),
            company VARCHAR(255),
            budget BIGINT,
            gross BIGINT,
            FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE
        )
        """)
        
        print("Tables created successfully")
    except Error as e:
        print(f"Error creating tables: {e}")

def import_data(connection):
    try:
        cursor = connection.cursor()
        
        with open('movies_updated.csv', 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                runtime = float(str(row['runtime,']).strip().replace(',', ''))
                
                cursor.execute("""
                    INSERT INTO movies (name, year, genre, rating, runtime)
                    VALUES (%s, %s, %s, %s, %s)
                """, (row['name'], row['year'], row['genre'], row['rating'], runtime))
                
                movie_id = cursor.lastrowid
                
                cursor.execute("""
                    INSERT INTO crew (movie_id, director, writer, star)
                    VALUES (%s, %s, %s, %s)
                """, (movie_id, row['director'], row['writer'], row['star']))
                
                # Converting budget and gross to integers, handling empty values
                try:
                    budget = int(row['budget']) if row['budget'] else None
                except ValueError:
                    budget = None
                
                try:
                    gross = int(row['gross']) if row['gross'] else None
                except ValueError:
                    gross = None
                
                cursor.execute("""
                    INSERT INTO production (movie_id, country, company, budget, gross)
                    VALUES (%s, %s, %s, %s, %s)
                """, (movie_id, row['country'], row['company'], budget, gross))
        
        connection.commit()
        print("Data imported successfully")
    except Error as e:
        print(f"Error importing data: {e}")
    except Exception as e:
        print(f"Error processing data: {e}")

def main():
    connection = create_connection()
    if connection:
        create_database(connection)
        create_tables(connection)
        import_data(connection)
        connection.close()
        print("Database setup successful.")

if __name__ == "__main__":
    main() 