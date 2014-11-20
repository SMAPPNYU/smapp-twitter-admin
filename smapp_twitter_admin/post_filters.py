"""
Module for introspective interfacing with `smappPy.tweet_filter` functions.

@jonathanronen
"""

from smappPy import tweet_filter

available_filters = [fname for fname in dir(tweet_filter) if not fname.startswith('_')]

def filter_choices():
    """
    Choices for dropdown menu for filter functions.
    """
    return [(fname, fname) for fname in available_filters]

def filter_docstring(fname):
    if fname not in available_filters:
        return 'NA'
    return tweet_filter.__getattribute__(fname).func_doc