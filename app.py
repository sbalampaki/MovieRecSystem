# This is the implementation for connecting the database with the application using flask and python
from flask import Flask, request, render_template, redirect, url_for
import mysql.connector
from math import ceil

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="surgodriti", # use your database password, this is mine
        database="movie_db" 
    )

def get_unique_genres():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT genre FROM movies ORDER BY genre")
        genres = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return genres
    except mysql.connector.Error as err:
        print(f"Error fetching genres: {err}")
        return []

def get_unique_ratings():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT rating FROM movies WHERE rating IS NOT NULL AND rating != '' ORDER BY rating")
        ratings = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return ratings
    except mysql.connector.Error as err:
        print(f"Error fetching ratings: {err}")
        return []

@app.route('/', methods=['GET'])
def home():
    genres = get_unique_genres()
    ratings = get_unique_ratings()
    return render_template('recommend.html', genres=genres, ratings=ratings)

@app.route('/results', methods=['GET', 'POST'])
def results():
    if request.method == 'GET':
        return redirect(url_for('home'))
        
    movies = []
    total_pages = 0
    current_page = 1
    error = None
    total_results = 0

    genre = request.form.get('genre')
    director = request.form.get('director')
    country = request.form.get('country')
    rating = request.form.get('rating')
    writer = request.form.get('writer')
    star = request.form.get('star')
    current_page = int(request.form.get('page', 1))
    per_page = 27

    if not genre:
        error = "Genre is required"
    else:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            count_query = """
            SELECT COUNT(*) as total
            FROM movies m
            JOIN crew c ON m.movie_id = c.movie_id
            JOIN production p ON m.movie_id = p.movie_id
            WHERE m.genre = %s
            """
            params = [genre]

            if director:
                count_query += " AND c.director LIKE %s"
                params.append(f"%{director}%")
            if country:
                count_query += " AND p.country = %s"
                params.append(country)
            if rating:
                count_query += " AND m.rating = %s"
                params.append(rating)
            if writer:
                count_query += " AND c.writer LIKE %s"
                params.append(f"%{writer}%")
            if star:
                count_query += " AND c.star LIKE %s"
                params.append(f"%{star}%")

            cursor.execute(count_query, params)
            total_results = cursor.fetchone()['total']
            total_pages = ceil(total_results / per_page)

            # For pagination
            query = """
            SELECT m.name, m.year, m.genre, m.rating, m.runtime,
                   c.director, c.writer, c.star,
                   p.country, p.company, p.budget, p.gross
            FROM movies m
            JOIN crew c ON m.movie_id = c.movie_id
            JOIN production p ON m.movie_id = p.movie_id
            WHERE m.genre = %s
            """
            params = [genre]

            if director:
                query += " AND c.director LIKE %s"
                params.append(f"%{director}%")
            if country:
                query += " AND p.country = %s"
                params.append(country)
            if rating:
                query += " AND m.rating = %s"
                params.append(rating)
            if writer:
                query += " AND c.writer LIKE %s"
                params.append(f"%{writer}%")
            if star:
                query += " AND c.star LIKE %s"
                params.append(f"%{star}%")

            query += " LIMIT %s OFFSET %s"
            params.extend([per_page, (current_page - 1) * per_page])

            cursor.execute(query, params)
            movies = cursor.fetchall()
            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            error = f"Database error: {err}"
        except Exception as e:
            error = f"An error occurred: {e}"

    return render_template('results.html',
                         movies=movies,
                         current_page=current_page,
                         total_pages=total_pages,
                         total_results=total_results,
                         error=error,
                         genre=genre,
                         director=director,
                         country=country,
                         rating=rating,
                         writer=writer,
                         star=star)

if __name__ == '__main__':
    app.run(debug=True)
