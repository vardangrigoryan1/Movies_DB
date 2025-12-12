from ds_collection import *
from STORAGE import STORAGE_movie_dic #*
import pickle
import os

class AVLTreeMap(TreeMap):
    """A sorted map implementation using an AVL-balanced binary search tree."""

    def __init__(self):
        """Create an empty AVLTreeMap using a balanceable binary tree."""
        self._tree = BalanceableBinaryTree()
        self._tree.add_root(None)

    # -------------------------- Height and balance utilities --------------------------
    def _height(self, p):
        """Return the cached height of the given tree position."""
        return self._tree.get_aux(p)

    def _recompute_height(self, p):
        """Recompute the height of the given position based on its children's heights."""
        self._tree.set_aux(
            p,
            1 + max(
                self._height(self._tree.left(p)),
                self._height(self._tree.right(p))
            ),
        )

    def _is_balanced(self, p):
        """Return True if position p has balance factor between -1 and 1 (inclusive)."""
        return abs(
            self._height(self._tree.left(p)) - self._height(self._tree.right(p))
        ) <= 1

    def _taller_child(self, p):
        """Return the child of p with height no smaller than that of the other child."""
        left_height = self._height(self._tree.left(p))
        right_height = self._height(self._tree.right(p))

        if left_height > right_height:
            return self._tree.left(p)
        elif left_height < right_height:
            return self._tree.right(p)
        else:
            if self._tree.is_root(p):
                return self._tree.left(p)
            parent = self._tree.parent(p)
            if p == self._tree.left(parent):
                return self._tree.left(p)
            else:
                return self._tree.right(p)

    # -------------------------- Rebalancing utilities --------------------------
    def _rebalance(self, p):
        """Utility to restore AVL balance up the path from p."""
        while p is not None:
            old_height = self._height(p)
            if not self._is_balanced(p):
                p = self._tree.restructure(self._taller_child(self._taller_child(p)))
                self._recompute_height(self._tree.left(p))
                self._recompute_height(self._tree.right(p))
            self._recompute_height(p)
            new_height = self._height(p)
            if old_height == new_height:
                break
            p = self._tree.parent(p)

    def _rebalance_insert(self, p):
        """Rebalancing hook called after insertion."""
        self._rebalance(p)

    def _rebalance_delete(self, p):
        """Rebalancing hook called after deletion."""
        if not self._tree.is_root(p):
            self._rebalance(self._tree.parent(p))

    # -------------------------- Overridden Map methods --------------------------
    def put(self, k, v):
        """Insert or replace entry (k, v) in the map, rebalancing as necessary."""
        self._check_key(k)
        p = self._subtree_search(self._tree.root(), k)

        if self._tree.is_external(p):
            self._expand_external(p, self._MapEntry(k, v))
            self._rebalance_insert(p)
            return None
        else:
            old_value = p.get_element()._set_value(v)
            return old_value

    def remove(self, k):
        """Remove the entry with key k and return its value, rebalancing as necessary."""
        if self.is_empty():
            return None

        p = self._subtree_search(self._tree.root(), k)
        if self._tree.is_external(p):
            return None

        old_value = p.get_element().get_value()

        if self._tree.is_internal(self._tree.left(p)) and self._tree.is_internal(self._tree.right(p)):
            replacement = self._tree_max(self._tree.left(p))
            self._tree.set(p, replacement.get_element())
            p = replacement

        child_sentinel = self._tree.left(p) if self._tree.is_external(self._tree.left(p)) else self._tree.right(p)
        sibling = self._tree.sibling(child_sentinel)

        self._tree.remove(child_sentinel)
        self._tree.remove(p)
        self._rebalance_delete(sibling)

        return old_value


    ### <----------------------------------------> ###
    def entry_set(self): #key_set(self) -> Iterable: AND values(self) -> Iterable:

        def in_order_trav(p):
                if p is None or self._tree.is_external(p):
                    return
                yield from in_order_trav(self._tree.left(p))
                yield p.get_element()
                yield from in_order_trav(self._tree.right(p))
        
        return in_order_trav(self._tree.root())

    
    def get_keys_with_prefix(self, prefix):
        results = []

        start_entry = self.ceiling_entry(prefix) #optimal starting point
        if start_entry is None:
            return []

        def in_order_trav(p):
            if p is None or self._tree.is_external(p):
                return
            
            in_order_trav(self._tree.left(p))
            key = p.get_element().get_key()
            value_i = p.get_element().get_value()

            if key.startswith(prefix):
                results.append(value_i)
            elif not key.startswith(prefix):
                return
                #Optimization. Stop traversal once it has passed the prefix
            in_order_trav(self._tree.right(p))
        
        #finding the position corresponding to start_entry
        #_subtree_search returns the node with exact key, ceiling_entry returns an entry
        start_pos = self._subtree_search(self._tree.root(), start_entry.get_key())
        in_order_trav(start_pos)
        return results
    ### <----------------------------------------> ###
    
    ### <----------------------------------------> ###
    #def _get_many_list(self, k): #(logn + m) **SOLUTION 1** X
    #    list_of_movies = self.get(k) #### discusion ####
    #    if not list_of_movies:
    #        return []
    #    return [movie["id"] for movie in list_of_movies]
    ### <----------------------------------------> ###
            

### <----------------------------------------> ###
### <----------------------------------------> ###
### <----------------------------------------> ###


class MovieIndex:
    def __init__(self, pickle_path="project/data/pickle/indices_avl.pkl", dataset=None):
        self.pickle_path = os.path.abspath(pickle_path)

        if dataset is None:
            dataset = STORAGE_movie_dic
        self.dataset = dataset

        if self.load_AVL_final(): #True
            print("load exav")
        else: #False
            self.AVL_title = AVLTreeMap()
            self.AVL_year = AVLTreeMap()
            self.AVL_genre = AVLTreeMap()

            self.insert_overall()
            self.save_AVL_pickle()

    ### <--------- INSERT_TO_AVL ---------> ###
    def inserting_process(self, movie_dic, movie_id):
        ### <--------- YEAR_AVL ---------> ###
        date = movie_dic.get("release_date")    #date = movie_dic["release_date"]
        if not date or len(date) < 4:
            return
        year = int(date[:4])

        existing_list = self.AVL_year.get(year)

        if existing_list is None:
            self.AVL_year.put(year, [movie_id])
        else:
            existing_list.append(movie_id)
        ### <--------- YEAR_AVL ---------> ###

        ### <--------- GENRE_AVL ---------> ###
        genres_list = movie_dic.get("genres")   #genres_list = movie_dic["genres"]
        for genre in genres_list:

            existing_list = self.AVL_genre.get(genre)

            if existing_list is None:
                self.AVL_genre.put(genre, [movie_id])
            else:
                existing_list.append(movie_id)
        ### <--------- GENRE_AVL ---------> ###

        ### <--------- TITLE_AVL ---------> ###
        self.AVL_title.put(movie_dic.get("title"), movie_id)  #AVL_title.put(movie_dic["title"], movie_id)
        ### <--------- TITLE_AVL ---------> ###


    def insert_overall(self):
        for movie_id, movie_dic in self.dataset.items():
            self.inserting_process(movie_dic, movie_id)
    ### <--------- INSERT_TO_AVL ---------> ###


    ### <--------- PICKLE Functions ---------> ###
    def save_AVL_pickle(self):
        """Pickle the AVL tree indices"""
        with open(self.pickle_path, "wb") as f:
            pickle.dump({
                "AVL_title": self.AVL_title,
                "AVL_year": self.AVL_year,
                "AVL_genre": self.AVL_genre
            }, f)
        
    def load_AVL_pickle(self):
        with open(self.pickle_path, "rb") as f:
            data = pickle.load(f)
            self.AVL_title = data["AVL_title"]
            self.AVL_year = data["AVL_year"]
            self.AVL_genre = data["AVL_genre"]
    ### <--------- PICKLE Functions ---------> ###

    ### <--------- UNIFIED Loader ---------> ###
    def load_AVL_final(self):
        if os.path.exists(self.pickle_path):
            self.load_AVL_pickle() # Load from pickle if it exists
            return True
        else:  # False ==> create new AVLs
            return False
    ### <--------- UNIFIED Loader ---------> ###



INDEX_searching_engine = MovieIndex()

#print(INDEX_searching_engine.AVL_year.get(2000))

# print(INDEX_searching_engine.AVL_year.get(1996))
# print(INDEX_searching_engine.AVL_genre.get_keys_with_prefix("Dra"))
# print(INDEX_searching_engine.AVL_genre.get("Drama"))
# print(INDEX_searching_engine.AVL_title.get_keys_with_prefix("Jo"))
# print(INDEX_searching_engine.AVL_title.get("Joker"))

# for i in AVL_title.values():
#     print(i)
# for i in AVL_title.key_set():
#     print(i)
# for i in AVL_genre.key_set():
#     print(i)

#©Vardan Grigoryan
