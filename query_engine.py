from ds_collection import *
from indexing import INDEX_searching_engine #*
from STORAGE import STORAGE_movie_dic, storager_obj #*

 ### <--------- QUERY Engine ---------> ###
class QueryEngine:
    def __init__(self, movie_dic = STORAGE_movie_dic, indexer = INDEX_searching_engine):
        """
            movie_dic (dict): The main dictionary {movie_id: movie_record}
            indexer (MovieIndex): An instance containing the loaded/built AVL trees.
        """
        self.by_id = movie_dic
        self.title_idx = indexer.AVL_title
        self.year_idx = indexer.AVL_year
        self.genre_idx = indexer.AVL_genre

        self.indexer = indexer
        self.storager = storager_obj


    ### <--------- Helper Function for Lists (GENRE, YEAR) ---------> ###
    def _fetch_records(self, movie_ids):
        """
        Helper method to look up records by ID from the main dictionary. O(K) complexity.
        """
        if not movie_ids:
            return []
        
        # Ensure it's iterable
        if not isinstance(movie_ids, list):
            movie_ids = [movie_ids]
        
        # O(1) lookup for each ID
        return [self.by_id[i] for i in movie_ids if i in self.by_id]
    ### <--------- Helper Function for Lists (GENRE, YEAR) ---------> ###


    ### <--------- SEARCHING ---------> ###
    def search_by_id(self, movie_id): #O(1)
        return self.by_id.get(movie_id)
    
    def search_by_title(self, movie_title):
        mov_id = self.title_idx.get(movie_title) # O(log N) AVL lookup
        return self.search_by_id(mov_id) # O(1) dictionary lookup
    
    def search_by_year(self, movie_year) -> list[dict]: #O(log N + K)
        mov_ids = self.year_idx.get(movie_year) # O(log N) AVL lookup returns a list of IDs
        return self._fetch_records(mov_ids) # [self.by_id[i] for i in movie_ids] #O(K)
    
    def search_by_genre(self, movie_genre) -> list[dict]: #O(log N + K)
        mov_ids = self.genre_idx.get(movie_genre) # O(log N) AVL lookup returns a list of IDs
        return self._fetch_records(mov_ids) # [self.by_id[i] for i in movie_ids] #O(K)
    ### <--------- SEARCHING ---------> ###


    def insert_movie(self, movie):
        """
        Insert a new movie into storage and all indexes.
        Time Complexity: O(logn * g) where g is the number of genres.
        """
        required_fields = ["title", "release_date", "genres"]
        if not all(field in movie for field in required_fields):
            raise ValueError(f"Movie must have the following fields: {', '.join(required_fields)}")
        
        #1. Generate O(1) Unique Key (already implemented and stored in STORAGE at startup)
        new_movie_key = self.storager.getter_next_key_to_insert()
        update_next_unique = new_movie_key + 1
        self.storager.setter_next_key_to_insert(update_next_unique)

        #2. Update the AVL Indices O(log n * g)
        self.indexer.inserting_process(movie, new_movie_key)
     
        #3. Update the MAIN DIC - self.by_id = movie_dic = STORAGE_movie_dic
        self.by_id[new_movie_key] = movie

        self.indexer.save_AVL_pickle()

        return new_movie_key


    def delete_movie(self, movie_id):
        movie = self.by_id.get(movie_id)
        if not movie:
            return False
        
        #1. Update the AVL Indices O(log n * g)
        self.indexer.deleting_process(movie_id)

        #2. Update the MAIN DIC - self.by_id = movie_dic = STORAGE_movie_dic
        del self.by_id[movie_id]

        self.indexer.save_AVL_pickle()

        return True
    
#©Vardan Grigoryan
