from flask import Flask, request, render_template
import pymysql
import math
import urllib.parse

app = Flask(__name__)

@app.template_filter('decode_uri')
def decode_uri(s):
    return urllib.parse.unquote(s)

@app.template_filter('replace')
def replace(s, old, new):
    return s.replace(old, new)

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="surgodriti",
        database="movieRecProject",
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    genres = []
    ratings = []
    countries = []

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT Genre FROM movies WHERE Genre IS NOT NULL")
    genres = sorted([row['Genre'] for row in cursor.fetchall()])
    cursor.execute("SELECT DISTINCT Rating FROM movies WHERE Rating IS NOT NULL")
    ratings = sorted([row['Rating'] for row in cursor.fetchall()])
    cursor.execute("SELECT DISTINCT Country FROM movies WHERE Country IS NOT NULL")
    countries = sorted([row['Country'] for row in cursor.fetchall()])
    cursor.close()
    conn.close()

    return render_template('dashboard.html', genres=genres, ratings=ratings, countries=countries)

@app.route('/search', methods=['GET'])
def search():
    try:
        genre = request.args.get('genre')
        rating = request.args.get('rating')
        director = request.args.get('director')
        writer = request.args.get('writer')
        star = request.args.get('star')
        country = request.args.get('country')
        page = int(request.args.get('page', 1))

        if not genre:
            return "Genre is required.", 400

        filters = ["Genre = %s"]
        values = [genre]

        if rating:
            filters.append("Rating = %s")
            values.append(rating)
        if country:
            filters.append("Country = %s")
            values.append(country)
        if director:
            filters.append("Director LIKE %s")
            values.append(f"%{director}%")
        if writer:
            filters.append("Writer LIKE %s")
            values.append(f"%{writer}%")
        if star:
            filters.append("Star LIKE %s")
            values.append(f"%{star}%")

        offset = (page - 1) * 25
        where_clause = " AND ".join(filters)

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT COUNT(*) as count FROM movies WHERE {where_clause}", values)
        total_results = cursor.fetchone()['count']
        total_pages = math.ceil(total_results / 25) if total_results > 0 else 0

        #getting the other details for the the given input and limiting 25 entries per page
        query = f"SELECT name, rating, genre, year, score, director, writer, star, country FROM movies WHERE {where_clause} LIMIT 25 OFFSET %s"
        cursor.execute(query, values + [offset])
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('results.html', 
                             results=results, 
                             page=page, 
                             total_pages=total_pages,
                             request=request)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
