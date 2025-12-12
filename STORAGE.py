import csv
#import json
import os
import pickle

### <--------- Helper Functions ---------> ###
def to_bool(val):
    """Converting "True"/"False" strings to Python boolean"""
    return val.strip().lower() == "true" if val else False

def to_number(val):
    """Converting string to int or float if possible, else leave as string"""
    try:
        return int(val)
    except ValueError:
        try:
            return float(val)
        except ValueError:
            return val

def to_list(val):
    """Converting comma-separated string to list of strings"""
    return [item.strip() for item in val.split(",")] if val.strip() else []

### <--------- KEY FUNCTIONALITY ---------> ###
def initialize_next_key_to_insert(records_dic): 
    """
    Calculates the highest existing key (NEW UNIQUE KEY) in the movie dictionary and sets 
    the next_key counter one higher. This operation is O(N), but is 
    only performed once at startup. Will be used in self._next_key_to_insert (STORAGE_DATASET)
    """
    #Using max(keys) to ensure the highest number is found, even if
    #earlier keys were deleted (ex. max of {0, 5, 10} is 10)
    max_key = max(records_dic.keys())
    next_key = max_key + 1
    return next_key
### <--------- KEY FUNCTIONALITY ---------> ###
### <--------- Helper Functions ---------> ###


class STORAGE_DATASET:
    def __init__(self, csv_path="project/data/raw/movies.csv", pickle_path="project/data/pickle/records_dic.pkl"):
        self.csv_path = os.path.abspath(csv_path)
        self.pickle_path = os.path.abspath(pickle_path)
        self.records_dic = {}
        ### <--------- KEY FUNCTIONALITY ---------> ###
        self._next_key_to_insert = 0
        ### <--------- KEY FUNCTIONALITY ---------> ###
    
    ### <--------- KEY FUNCTIONALITY ---------> ###
    def getter_next_key_to_insert(self):
        return self._next_key_to_insert
    
    def setter_next_key_to_insert(self, increment):
        self._next_key_to_insert = increment
    ### <--------- KEY FUNCTIONALITY ---------> ###
    

    ### <--------- Main Conversion Function ---------> ###
    def load_movie_csv(self):
        """
        Load CSV into a dictionary of movies (dics) keyed by index.
        Each movie record is represented as a dictionary with typed fields
        """

        with open(self.csv_path, encoding="utf-8") as f:
            data = csv.DictReader(f)
            for new_index, row in enumerate(data):
                record = {
                    #"id":                  new_index,      #to_number(row["id"]),  # !! NO NEED !! #
                    "title":                row["title"],
                    "vote_average":         to_number(row["vote_average"]),
                    "vote_count":           to_number(row["vote_count"]),
                    "status":               row["status"],
                    "release_date":         row["release_date"],
                    "revenue":              to_number(row["revenue"]),
                    "runtime":              to_number(row["runtime"]),
                    "adult":                to_bool(row["adult"]),
                    "backdrop_path":        row["backdrop_path"],
                    "budget":               to_number(row["budget"]),
                    "homepage":             row["homepage"] if row["homepage"].strip() else None,
                    "imdb_id":              row["imdb_id"],
                    "original_language":    row["original_language"],
                    "original_title":       row["original_title"],
                    "overview":             row["overview"],
                    "popularity":           to_number(row["popularity"]),
                    "poster_path":          row["poster_path"],
                    "tagline":              row["tagline"],
                    "genres":               to_list(row["genres"]),
                    "production_companies": to_list(row["production_companies"]),
                    "production_countries": to_list(row["production_countries"]),
                    "spoken_languages":     to_list(row["spoken_languages"]),
                    "keywords":             to_list(row["keywords"])
                }
                self.records_dic[new_index] = record
        return self.records_dic
    ### <--------- Main Conversion Function ---------> ###


    ### <--------- PICKLE Functions ---------> ###
    def save_DATASET_pickle(self):
        with open(self.pickle_path, "wb") as f:
            pickle.dump(self.records_dic, f) #indent=2

    def load_DATASET_pickle(self):
        with open(self.pickle_path, "rb") as f:
            return pickle.load(f)
    ### <--------- PICKLE Functions ---------> ###

    ### <--------- UNIFIED Loader ---------> ###
    def load_DATASET_final(self):
        if os.path.exists(self.pickle_path):
            self.records_dic = self.load_DATASET_pickle() #load from pickle if it exists
        else:  #load from CSV if pickle doesn't exist
            self.load_movie_csv()
            self.save_DATASET_pickle()
        ### <--------- KEY FUNCTIONALITY ---------> ###
        find_max_key = initialize_next_key_to_insert(self.records_dic)
        self.setter_next_key_to_insert(find_max_key)
        ### <--------- KEY FUNCTIONALITY ---------> ###
        return self.records_dic  #return the records directly (no need to load again)
    ### <--------- UNIFIED Loader ---------> ###



storager_obj = STORAGE_DATASET()
STORAGE_movie_dic = storager_obj.load_DATASET_final() #Load dataset ONCE at the start

#©Vardan Grigoryan
