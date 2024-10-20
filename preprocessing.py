import pandas as pd

def preprocess_datasets():
    # Load the datasets
    books = pd.read_csv('books.csv')
    ratings = pd.read_csv('ratings.csv')
    users = pd.read_csv('users.csv')

    # Preprocess 'books' dataset
    # Drop duplicate rows based on ISBN
    books.drop_duplicates(subset='ISBN', inplace=True)
    # Remove rows with missing values for important columns
    books.dropna(subset=['Book-Title', 'Book-Author', 'Year-Of-Publication', 'Publisher'], inplace=True)

    # Preprocess 'ratings' dataset
    # Remove rows with missing ISBN or User-ID
    ratings.dropna(subset=['ISBN', 'User-ID'], inplace=True)
    # Filter out rows where the rating is not in a valid range (0-10)
    ratings = ratings[(ratings['Book-Rating'] >= 0) & (ratings['Book-Rating'] <= 10)]

    # Preprocess 'users' dataset
    # Remove duplicate rows based on User-ID
    users.drop_duplicates(subset='User-ID', inplace=True)
    # Fill missing values in 'Age' with the median age
    users['Age'].fillna(users['Age'].median(), inplace=True)

    # Merge datasets
    # Merge books with ratings on ISBN
    books_ratings = pd.merge(ratings, books, on='ISBN', how='inner')
    # Merge the result with users on User-ID
    final_data = pd.merge(books_ratings, users, on='User-ID', how='inner')

    # Save the final merged file
    final_data.to_csv('final_merged_file.csv', index=False)

    print("Preprocessing and merging completed successfully!")
    return final_data

# Run the function
final_merged_data = preprocess_datasets()

# Display a sample of the final merged data
print(final_merged_data.head())
