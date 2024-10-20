from flask import Flask, render_template, request, flash, redirect
import pandas as pd
import numpy as np

# Load the dataset from the CSV file
books_df = pd.read_csv('summarized_books_data.csv')

# Convert 'Book-Rating' to numeric, coercing errors to NaN
books_df['Book-Rating'] = pd.to_numeric(books_df['Book-Rating'], errors='coerce')

# Convert 'Year-Of-Publication' to numeric, coercing errors to NaN
books_df['Year-Of-Publication'] = pd.to_numeric(books_df['Year-Of-Publication'], errors='coerce')

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

@app.route('/')
def index():
    # Filter books containing 'Harry Potter' in the title (case insensitive)
    harry_potter_books = books_df[books_df['Book-Title'].str.contains('Harry Potter', case=False, na=False)]
    
    # Filter out books with missing or invalid image URLs
    harry_potter_books = harry_potter_books[harry_potter_books['Image-URL-M'].notna() & harry_potter_books['Image-URL-M'].str.startswith('http')]

    # Group by 'Book-Title' and get the mean rating, then sort by rating
    popular_books = harry_potter_books.groupby('Book-Title').agg({
        'Book-Rating': 'mean', 
        'Book-Title': 'first', 
        'Book-Author': 'first', 
        'Image-URL-M': 'first', 
        'Year-Of-Publication': 'first'
    }).sort_values(by='Book-Rating', ascending=False).head(10)

    return render_template('index.html',
                           book_name=list(popular_books['Book-Title'].values),
                           author=list(popular_books['Book-Author'].values),
                           image=list(popular_books['Image-URL-M'].values),
                           rating=list(popular_books['Book-Rating'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    authors = books_df['Book-Author'].dropna().unique()
    locations = books_df['Location'].dropna().unique()  # Get unique locations
    return render_template('recommend.html', authors=authors, locations=locations)  # Pass locations to the template

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')
    min_rating = request.form.get('min_rating')
    year_from = request.form.get('year_from')
    year_to = request.form.get('year_to')
    author = request.form.get('author')
    age = request.form.get('age')
    location = request.form.get('location')  # Get the selected location

    # Filter the books dataframe based on the filters applied
    filtered_books = books_df.copy()

    if user_input:
        filtered_books = filtered_books[filtered_books['Book-Title'].str.contains(user_input, case=False, na=False)]

    if min_rating:
        filtered_books = filtered_books[filtered_books['Book-Rating'] >= float(min_rating)]

    if year_from and year_to:
        filtered_books = filtered_books[(filtered_books['Year-Of-Publication'] >= int(year_from)) & 
                                        (filtered_books['Year-Of-Publication'] <= int(year_to))]

    if author:
        filtered_books = filtered_books[filtered_books['Book-Author'] == author]

    if age:
        filtered_books = filtered_books[(filtered_books['Age'] <= int(age) + 5) & 
                                        (filtered_books['Age'] >= int(age) - 5)]

    if location:  # Filter by location if provided
        filtered_books = filtered_books[filtered_books['Location'] == location]

    # Display top 10 books from the filtered dataset
    filtered_books = filtered_books.head(10)

    data = []
    for _, row in filtered_books.iterrows():
        data.append([
            row['Book-Title'],
            row['Book-Author'],
            row['Image-URL-M'],
            row['Book-Rating'],
            row['Year-Of-Publication'],
            row['Location']
        ])

    # If no books match the filters, show a flash message
    if not data:
        flash('No books found matching your criteria. Please adjust the filters.')
        return redirect('/recommend')

    return render_template('recommend.html', data=data, authors=books_df['Book-Author'].dropna().unique(), locations=books_df['Location'].dropna().unique())  # Pass authors and locations again

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
