import difflib
import testimony.nameutils as nameutils

def has_been_chunked_approximate(s, chunklist, threshold=3):
    for chunk in chunklist:
        approx_chunk = filter(lambda sliver: nameutils.are_close_tokens(s, sliver, threshold), chunk)
        if approx_chunk: return True
    return False

def has_been_chunked(s, chunklist):
    for chunk in chunklist:
        if s in chunk: return True
    return False

def has_been_chunked_approx(s, chunklist):
    new_chunklist = []
    chunked_s = False
    for chunk in chunklist:
        if s in chunk:
            chunked_s = True
        close_matches = difflib.get_close_matches(s, chunk, 200, 0.85)
        if close_matches and not chunked_s:
            chunk.append(s)
            chunked_s = True
        new_chunklist.append(chunk)
    return (new_chunklist, chunked_s)


def chunk_list(l):
    chunklist = []
    for s in l:
        res = has_been_chunked_approx(s, chunklist)
        if res[1]: #already been chunked
            chunklist = res[0]
        else:
            close_matches = difflib.get_close_matches(s, l, 200, 0.85)
            chunklist.append(close_matches)
    return chunklist

def chunk_with_priority(a, b):
    """
    Two lists, makes priority a.
    if something in b doesn't sync up with something in a, it's not added.
    Otherwise, it chunks elements of b with elements of a.
    """
    to_be_chunked = a
    for s in b:
        close_matches = difflib.get_close_matches(s, a, 200, 0.85)
        if close_matches:
            to_be_chunked.append(s)
    chunklist = chunk_list(to_be_chunked)
    return chunklist
# def chunk_list(l):
#     chunklist = []
#     for s in l:
#         if has_been_chunked(s, chunklist):
#             continue
#         close_matches = difflib.get_close_matches(s, l, 200, 0.85)
#         chunklist.append(close_matches)

#     return chunklist
