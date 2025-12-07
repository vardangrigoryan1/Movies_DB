from ds_collection import *
from indexing import *

"""-------------- Query Engine -------------------"""
class QueryEngine:
    def __init__(self, raw_data, title_idx, year_idx, genre_idx):
        """
        raw_data: list of movie dictionaries
        title_idx: AVLTreeMap mapping title -> movie_id
        year_idx: AVLTreeMap mapping year -> [movie_ids]
        genre_idx: AVLTreeMap mapping genre -> [movie_ids]
        """
        self.data = raw_data
        self.by_id = {m["id"]: m for m in raw_data}
        
        self.title_idx = title_idx
        self.year_idx = year_idx
        self.genre_idx = genre_idx

    """-------Search Operations-------"""
    def search_by_id(self, movie_id):
        """O(1) - dictionary lookup"""
        return self.by_id.get(movie_id)

    def search_by_title(self, title):
        """O(log n) - AVL tree search"""
        movie_id = self.title_idx.get(title)
        return self.by_id.get(movie_id) if movie_id else None

    def search_by_prefix(self, prefix):
        """O(log n + m) where m is number of matches"""
        ids = self.title_idx.get_keys_with_prefix(prefix)
        return [self.by_id[mid] for mid in ids]

    def search_by_year(self, year):
        """O(log n + k) where k is movies in that year"""
        ids = self.year_idx.get(year) or []
        return [self.by_id[mid] for mid in ids]

    def search_by_year_range(self, start_year, end_year):
        """O(log n + k) where k is movies in range"""
        entries = self.year_idx.sub_map(start_year, end_year + 1)
        result = []
        for entry in entries:
            for mid in entry.get_value():
                result.append(self.by_id[mid])
        return result

    def search_by_genre(self, genre):
        """O(log n + k) where k is movies with that genre"""
        ids = self.genre_idx.get(genre) or []
        return [self.by_id[mid] for mid in ids]
    



    """-------Insertion-------"""
    def insert(self, movie):
        """
        Insert a new movie into storage and all indexes.
        Time Complexity: O(log n * g) where g is number of genres
        """
        # Validate required fields
        if "id" not in movie or "title" not in movie or "release_date" not in movie:
            raise ValueError("Movie must have id, title, and release_date")
        
        # Check if movie already exists
        if movie["id"] in self.by_id:
            raise ValueError(f"Movie with id {movie['id']} already exists")
        
        # Add to raw storage
        self.data.append(movie)
        self.by_id[movie["id"]] = movie
        
        # Add to title index - O(log n)
        self.title_idx.put(movie["title"], movie["id"])
        
        # Add to year index - O(log n)
        year = int(movie["release_date"][:4])
        existing_year_list = self.year_idx.get(year)
        if existing_year_list is None:
            self.year_idx.put(year, [movie["id"]])
        else:
            existing_year_list.append(movie["id"])
        
        # Add to genre index - O(log n * g)
        if "genres" in movie:
            for genre in movie["genres"]:
                existing_genre_list = self.genre_idx.get(genre)
                if existing_genre_list is None:
                    self.genre_idx.put(genre, [movie["id"]])
                else:
                    existing_genre_list.append(movie["id"])




    """-------Deletion-------"""
    def delete(self, movie_id):
        """
        Delete a movie by ID from all indexes.
        Time Complexity: O(log n * g + k) where g is genres, k is list sizes
        Returns: True if deleted, False if not found
        """
        movie = self.by_id.get(movie_id)
        if not movie:
            return False

        # Remove from raw storage - O(n) for list.remove
        self.data.remove(movie)
        del self.by_id[movie_id]

        # Remove from title index - O(log n)
        self.title_idx.remove(movie["title"])

        # Remove from year index - O(log n + k)
        year = int(movie["release_date"][:4])
        year_list = self.year_idx.get(year)
        if year_list:
            # Using list comprehension is O(k) but more Pythonic
            # Alternative: year_list.remove(movie_id) is also O(k)
            try:
                year_list.remove(movie_id)
                # If list is empty, remove the year key entirely
                if len(year_list) == 0:
                    self.year_idx.remove(year)
            except ValueError:
                pass  # movie_id not in list

        # Remove from genre indexes - O(log n * g + k)
        if "genres" in movie:
            for genre in movie["genres"]:
                genre_list = self.genre_idx.get(genre)
                if genre_list:
                    try:
                        genre_list.remove(movie_id)
                        if len(genre_list) == 0:
                            self.genre_idx.remove(genre)
                    except ValueError:
                        pass

        return True
    



    """-------Modification-------"""
    def modify(self, movie_id, new_data):
        """
        Modify a movie by updating specified fields.
        Time Complexity: Depends on what fields are changed
        - If title/year/genres change: O(log n * g)
        - If only other fields: O(1)
        Returns: True if modified, False if movie not found
        """
        old_movie = self.by_id.get(movie_id)
        if not old_movie:
            return False
        
        # Don't allow changing the ID
        if "id" in new_data and new_data["id"] != movie_id:
            raise ValueError("Cannot change movie ID")
        
        # Check which indexed fields are being changed
        title_changed = "title" in new_data and new_data["title"] != old_movie.get("title")
        date_changed = "release_date" in new_data and new_data["release_date"] != old_movie.get("release_date")
        genres_changed = "genres" in new_data and new_data["genres"] != old_movie.get("genres", [])
        
        # If indexed fields changed, update indexes
        if title_changed:
            # Remove old title, add new
            self.title_idx.remove(old_movie["title"])
            self.title_idx.put(new_data["title"], movie_id)
        
        if date_changed:
            # Remove from old year, add to new
            old_year = int(old_movie["release_date"][:4])
            new_year = int(new_data["release_date"][:4])
            
            old_year_list = self.year_idx.get(old_year)
            if old_year_list:
                old_year_list.remove(movie_id)
                if len(old_year_list) == 0:
                    self.year_idx.remove(old_year)
            
            new_year_list = self.year_idx.get(new_year)
            if new_year_list is None:
                self.year_idx.put(new_year, [movie_id])
            else:
                new_year_list.append(movie_id)
        
        if genres_changed:
            # Remove from old genres
            old_genres = set(old_movie.get("genres", []))
            new_genres = set(new_data["genres"])
            
            # Remove from genres that are no longer present
            for genre in old_genres - new_genres:
                genre_list = self.genre_idx.get(genre)
                if genre_list:
                    genre_list.remove(movie_id)
                    if len(genre_list) == 0:
                        self.genre_idx.remove(genre)
            
            # Add to new genres
            for genre in new_genres - old_genres:
                genre_list = self.genre_idx.get(genre)
                if genre_list is None:
                    self.genre_idx.put(genre, [movie_id])
                else:
                    genre_list.append(movie_id)
        
        # Update the movie data in storage
        old_movie.update(new_data)
        
        return True
    


    """-------Range Query-------"""

    def range_query(self, field, min_val, max_val):
        """
        Generic range query for numeric fields.
        For year: use search_by_year_range instead (more efficient)
        For other fields: O(n) - must scan all movies
        """
        result = []
        for movie in self.data:
            if field in movie:
                val = movie[field]
                if min_val <= val <= max_val:
                    result.append(movie)
        return result
