import csv
from copy import deepcopy

"""
A pair of simple idioms for CSV slurping + saving, to cut down on boilerplate
in our test + demo suites (and avoid dependencies on much heavier external packages
that provide similar conveniences).
"""

class TinyFrame(object):
    """
    An extremely primitive "data frame"-like object, which projects just
    enough abstraction to make our CSV i/o a little bit easier, for our needs.

    Namely: reads from a row iterator (most like a csv.reader instance);
    expects header (or not) as the row yielded by that iterator; and stashes
    a list of types to apply on emitted rows (on the way out).
    """

    def __init__(self,stream,types=None,expect_header=True):
        """
        Creates a dataframe instance, fully ingesting the rowset of interest (from the
        given :stream object) at instantiation time.

        :stream: - a row iterator from our input source (most likely a csv.reader object)
        :types: - a list of types to apply to logical row values (on the way out, via self.rows)
        :expect_header: - a directive specifying whether to skip the first row from our
            input source (presumably a header) upon ingestion.  Note that the 'header' as
            such is simply skipped, and not kept or made use of in any functional way.
        """
        self._rowset = None
        self._types  = deepcopy(types)
        self._ingest(stream,expect_header)

    def _ingest(self,stream,expect_header):
        if expect_header:
            next(stream)
        self._rowset = list(stream)

    def rows(self):
        """Yields from our rowset of interest, applying the type list (supplied to
        the constructor) to emitted values the way out."""
        types = self._types
        if types is None:
            yield from self._rowset
        else:
            for row in self._rowset:
                yield list(apply_types(types,row))


def apply_types(types,values):
    """Applies an iterable of :types to an iterable of :values (unless they
    already match, in which case we pass the value through, to spare the expense
    of copying)."""
    if types is None:
        raise ValueError("need a types list")
    for t,v in zip(types,values):
        if type(v) is t:
            yield v
        else:
            yield t(v)


def _load_csv(path,encoding='utf-8',types=None,expect_header=True,csvargs=None):
    if csvargs is None:
        csvargs = {}
    with open(path,"rt",encoding=encoding) as f:
        reader = csv.reader(f,**csvargs)
        return TinyFrame(reader,types=types,expect_header=expect_header)

#
# These are the functions you'd actually want to export.
#

def slurp_csv(*args,**kwargs):
    tiny = _load_csv(*args,**kwargs)
    return list(tiny.rows())

def save_csv(path,rowset,encoding='utf-8',header=None,csvargs=None):
    if csvargs is None:
        csvargs = {}
    writer = csv.writer(f,**csvargs)
    if header:
        writer.writerow(header)
    for row in rowset:
        writer.writerow(row)


