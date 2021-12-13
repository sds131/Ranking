"""Subroutines used for computing rankings for CSrankings.
"""
from lxml import etree as ElementTree

# import xml.etree.ElementTree as ElementTree
import csv
import operator
import re
import gzip
import xmltodict
import collections
import json
import csv
import re
import sys

from typing import Dict, List, NewType

Title = NewType("Title", str)
Author = NewType("Author", str)
Area = NewType("Area", str)
Conference = NewType("Conference", str)

# from builtins import str

# Papers must be at least 6 pages long to count.
pageCountThreshold = 6
# Match ordinary page numbers (as in 10-17).
pageCounterNormal = re.compile("([0-9]+)-([0-9]+)")  #  flags=re.ASCII)
# Match page number in the form volume:page (as in 12:140-12:150).
pageCounterColon = re.compile("[0-9]+:([1-9][0-9]*)-[0-9]+:([1-9][0-9]*)")
# Special regexp for extracting pseudo-volumes (paper number) from TECS.
TECSCounterColon = re.compile("([0-9]+):[1-9][0-9]*-([0-9]+):[1-9][0-9]*")
# Extract the ISMB proceedings page numbers.
ISMBpageCounter = re.compile("i(\d+)-i(\d+)")


def startpage(pageStr: str) -> int:
    """Compute the starting page number from a string representing page numbers."""
    if pageStr is None:
        return 0
    pageCounterMatcher1 = pageCounterNormal.match(pageStr)
    pageCounterMatcher2 = pageCounterColon.match(pageStr)
    start = 0

    if not pageCounterMatcher1 is None:
        start = int(pageCounterMatcher1.group(1))
    else:
        if not pageCounterMatcher2 is None:
            start = int(pageCounterMatcher2.group(1))
    return start


def pagecount(pageStr: str) -> int:
    """Compute the number of pages in a string representing a range of page numbers."""
    if pageStr is None:
        return 0
    pageCounterMatcher1 = pageCounterNormal.match(pageStr)
    pageCounterMatcher2 = pageCounterColon.match(pageStr)
    start = 0
    end = 0
    count = 0

    if not pageCounterMatcher1 is None:
        start = int(pageCounterMatcher1.group(1))
        end = int(pageCounterMatcher1.group(2))
        count = end - start + 1
    else:
        if not pageCounterMatcher2 is None:
            start = int(pageCounterMatcher2.group(1))
            end = int(pageCounterMatcher2.group(2))
            count = end - start + 1
    return count


areadict : Dict[Area, List[Conference]] = {
    Area("tcss"):[Conference("TCSS"),Conference("IEEE Transactions on Computational Social Systems"),Conference("IEEE TCSS"),Conference("IEEE Trans. Comput. Soc. Syst.")],
    Area("tsc"):[Conference("TSC"),Conference("tsoco"),Conference("ACM Transactions on Social Computing"),Conference("ACM Trans. Soc. Comput.")],
    Area("socnet"):[Conference("SocNets"),Conference("Social Networks"),Conference("Soc. Networks")],
    Area("jsc"):[Conference("JSC"),Conference("Journal of Social Computing"),Conference("J. Soc. Comput.")],
    Area("snam"):[Conference("Social Network Analysis and Mining"),Conference("Soc. Netw. Anal. Min.")],
}

TCSS_journal = {
    2021: 8,
    2020: 7,
    2019: 6,
    2018: 5,
    2017: 4,
    2016: 3,
    2015: 2,
    2014: 1
}

TSC_journal = {
    2021: {4},
    2020: {2,3},
    2019: {2},
    2018: {1}
}

Soc_journal = {
    2021: {64,65,66},
    2020: {60,61,62,63},
    2019: {56,57,58,59},
    2018: {52,53,54,55},
    2017: {48,49,50,51},
    2016: {44,45,46,47},
    2015: {40,41,42,43},
    2014: {36,37,38,39},
    2013: {35},
    2012: {34},
    2011: {33},
    2010: {32},
    2009: {31},
    2008: {30},
    2007: {29},
    2006: {28},
    2005: {27},
    2004: {26},
    2003: {25},
    2002: {24},
    2001: {23},
    2000: {22},
    1999: {21}
}

JSC_journal = {
    2021: {2},
    2020: {1}
}

SNAM_journal = {
    2021: {11},
    2020: {10},
    2019: {9},
    2018: {8},
    2017: {7},
    2016: {6},
    2015: {5},
    2014: {4},
    2013: {3},
    2012: {2},
    2011: {1},
}

# Build a dictionary mapping conferences to areas.
# e.g., confdict['CVPR'] = 'vision'.
confdict = {}
venues = []
for k, v in areadict.items():
    for item in v:
        confdict[item] = k
        venues.append(item)

# The list of all areas.
arealist = areadict.keys()

# Consider pubs in this range only.
startyear = 1970
endyear = 2269


def countPaper(
    confname: Conference,
    year: int,
    volume: str,
    number: str,
    pages: str,
    startPage: int,
    pageCount: int,
    url: str,
    title: Title,
) -> bool:
    """Returns true iff this paper will be included in the rankings."""
    if year < startyear or year > endyear:
        return False

    if confname =="IEEE Trans. Comput. Soc. Syst.":
        Conf = False
        if year in TCSS_journal:
            vols = str(TCSS_journal[year])
            if volume in vols:
                Conf = True
        if not Conf:
            return False

    if confname =="ACM Trans. Soc. Comput.":
        Conf = False
        if year in TSC_journal:
            vols= str(TSC_journal[year])
            if volume in vols:
                Conf = True
        if not Conf:
            return False

    if confname =="Soc. Networks":
        Conf = False
        if year in Soc_journal:
            vols=str(Soc_journal[year])
            if volume in vols:
                Conf = True
        if not Conf:
            return False

    if confname =="J. Soc. Comput.":
        Conf = False
        if year in JSC_journal:
            vols=str(JSC_journal[year])
            if volume in vols:
                Conf = True
        if not Conf:
            return False

    if confname =="Soc. Netw. Anal. Min.":
        Conf = False
        if year in SNAM_journal:
            vols=str(SNAM_journal[year])
            if volume in vols:
                Conf = True
        if not Conf:
            return False

    return True
