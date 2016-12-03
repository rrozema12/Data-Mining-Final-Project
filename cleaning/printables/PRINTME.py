#####################
# hw1.py
#####################

import csv
import file_system
import util
import copy
import summary
import join
import clean

# Here to keep consistent breaks
LINE_BREAK = '----------------'

# Makes an array pretty printable
def arrayWithLineEnds(array):
    string = ""
    for row in array:
        string += str(row) + "\n"
    return string

# Prints out a file with duplicates and counts
def printFile(filename, matches, header):
    """ Prints out those header files in Step 2"""
    fileObj = file_system.loadFile(filename, matches)
    print LINE_BREAK
    print header
    print LINE_BREAK
    print 'No. of instances: ',  str(fileObj['count'])
    duplicates = arrayWithLineEnds(fileObj['duplicates'])
    if not duplicates.strip(): duplicates = '[]'
    print 'Duplicates:', duplicates

# Prints out a header
def printHeader(text):
    print LINE_BREAK
    print text
    print LINE_BREAK

# Creates combined column
def setup():
    # Left side is auto-mpg col index
    # Right side is auto-prices col index
    onColumns = {8 : 0, 6 : 1}

    # Join the clean data
    mpgTable = file_system.loadTable('auto-mpg-clean.csv')
    pricesTable = file_system.loadTable('auto-prices-clean.csv')
    combinedTable = join.fullOuter(mpgTable, pricesTable, onColumns)

    file_system.write(combinedTable, 'auto-data.csv')

def main():
    setup()

    printFile('auto-mpg-nodups.csv', [8, 6], 'auto-mpg-nodups.csv')
    print ''
    printFile('auto-prices-nodups.csv', [0, 1], 'auto-prices-nodups.csv')
    print ''
    printFile('auto-mpg-clean.csv', [8, 6], 'auto-mpg-clean.csv')
    print ''
    printFile('auto-prices-clean.csv', [0, 1], 'auto-prices-clean.csv')
    print ''
    printFile('auto-data.csv', [8, 6], 'Combined table (saved as auto-data.csv)')
    print ''

    # Cleaned Combined data
    cleaned = file_system.loadFile('auto-data.csv', [8, 6])['table']
    cleaned = util.tableToCorrectType(cleaned)
    summary.summary(cleaned)

    # Combined table with rows missing
    removedRowsTable = clean.removeNA(cleaned)
    printHeader('Combined table (rows w/ missing values removed):')
    summary.summary(removedRowsTable)

    # Combined tables with average values
    averageRowsTable = clean.replaceWithAverages(cleaned)
    printHeader('Combined table (rows w/ average values):')
    summary.summary(averageRowsTable)

    # Combined Table with average values by row
    averageByYearTable = clean.replaceWithAveragesRelativeToYear(cleaned)
    printHeader('Combined table (rows w/ average values as year):')
    summary.summary(averageByYearTable)

if __name__ == '__main__':
    main()


#####################
# summary.py
#####################


import util

attributeNames = ['mpg', 'cylinders', 'displacement', 'horsepower', 'weight', 'acceleration', 'year', 'origin', 'name', 'msrp']

def arrayWithLineEnds(array):
    string = ""
    for row in array:
        string += str(row) + "\n"
    return string

def printHeader():
    print "Summary Stats:"
    print "=============  =======  =======  =======  =======  ========"
    print "attribute      min      max      mid      avg      med"
    print "=============  =======  =======  =======  =======  ========"

def printSummaryRow(attribute, min_, max_, mid, avg, med):
    print attribute.ljust(13), '', str(min_).ljust(7), '', str(max_).ljust(7), '', str(mid).ljust(7), '', str(avg).ljust(7), '', str(med).ljust(9)

def summary(table):
    printHeader()
    for index, attribute in enumerate(attributeNames):
        calcAttribute(table, index)

def calcAttribute(table, attributeIndex):

    isNA = table[0][attributeIndex] == 'NA'
    isString = isinstance(table[0][attributeIndex], basestring)
    if (isString and not(isNA)):
        return

    _min = None
    _max = None
    mid  = None
    for row in table:

        # Skip NA values
        isNA = row[attributeIndex] == "NA"
        if isNA:
            continue

        # min
        if (_min == None or _min > row[attributeIndex]):
            _min = row[attributeIndex]

        # max
        if (_max == None or _max < row[attributeIndex]):
            _max = row[attributeIndex]

    col = util.getCol(table, attributeIndex)
    med = round(util.median(col), 2)
    mid = round((_max - _min)/2, 2)
    avg = round(util.mean(col), 2)

    printSummaryRow(attributeNames[attributeIndex], _min, _max, mid, avg, med)

if __name__ == '__main__':
    table = [[3.0, 8, 454.0, 220.0, 4354, 9.0, 70, 1, 'chevrolet impala', 3132],
    [2.0, 81, 4534.0, 20.0, 454, 93.0, 40, 4, 'ewjiofjieow impala', 4023]]
    summary(table)


#####################
# clean.py
#####################


import util

# Gets all col averages
def getColAverages(table):
    rowLength = len(table[0])
    averages = []
    for i in range(rowLength):
        col = util.getCol(table, i)
        if (util.colIsString(col)):
            averages.append('NA')
            continue # We can't replace averages for strings

        avg = util.mean(col)
        averages.append(avg)
    return averages

# Gets col averages where col[colTestIndex] == colTestValue
def getColAveragesBy(table, colTestIndex, colTestValue):
    rowLength = len(table[0])
    averages = []
    for i in range(rowLength):
        col = util.getColBy(table, i, colTestIndex, colTestValue)
        if (util.colIsString(col)):
            averages.append('NA')
            continue # We can't replace averages for strings

        avg = util.mean(col)
        averages.append(avg)
    return averages


# First approach removes all instances with missing values
def removeNA(table):
    newTable = []
    for row in table:
        if not util.hasMissing(row):
            newTable.append(row)
    return newTable


# Second approach computes the average for each missing value
def replaceWithAverages(table):
    averages = getColAverages(table)

    newTable = []
    for row in table:
        newRow = []
        for colIndex, col in enumerate(row):
            if (col == 'NA'):
                col = averages[colIndex]
            newRow.append(col)
        newTable.append(newRow)
    return newTable

# Third approach computers averages based on the year of the car
def replaceWithAveragesRelativeToYear(table):
    yearIndex = 6 #in combined datasets, this is the index

    newTable = []
    for row in table:
        year = row[yearIndex]
        averages = getColAveragesBy(table, yearIndex, year)

        newRow = []
        for colIndex, col in enumerate(row):
            if col == 'NA':
                col = averages[colIndex]
            newRow.append(col)
        newTable.append(newRow)
    return newTable

if __name__ == '__main__':
    table = [[0.0, 0, 0.0, 0.0, 0, 0.0, 70, 0, 'chevrolet impala', 0],
    [3.0, 34, 4344.0, 10.0, 452, 23.0, 40, 5, 'Raww impala', 5023],
    [2.0, 81, 4534.0, 20.0, 454, 93.0, 40, 4, 'ewjiofjieow impala', 4023],
    ['NA', 'NA', 'NA', 'NA', 'NA', 93.0, 40, 'NA', 'no Data', 'NA']]

    print replaceWithAveragesRelativeToYear(table)


#####################
# util.py
#####################

import itertools

# Return a col list
def getCol(table, index):
    col = []
    for row in table:
        if (row[index] == 'NA'): continue
        col.append(row[index])
    return col

# Calculate a median
def median(row):
    newRow = filterNA(row)
    middleIndex = len(newRow)/2

    if (len(newRow) % 2 != 0): # odd
        return sorted(newRow)[middleIndex]
    else: # even
        sortedCols = sorted(newRow)
        return (sortedCols[middleIndex] + sortedCols[middleIndex-1])/2

# Kills any "NA"s in the list
def filterNA(row):
    newList = []
    for col in row:
        if (col != "NA" and col != "'NA'"):
            newList.append(col)
    return newList

def mean(row):
    row = filterNA(row)
    return sum(row)/len(row)

# Gets the values of a dictionary
def getValues(dictionary):
    values = []
    for key, value in dictionary.iteritems():
        values.append(value)
    return values

# Gets the keys of a dictionary
def getKeys(dictionary):
    keys = []
    for key, value in dictionary.iteritems():
        keys.append(key)
    return keys

# Sets the value as the key and the key as the value
def flipKeyValues(dictionary):
    newDict = {}
    for key, value in dictionary.iteritems():
        newDict[value] = key
    return newDict

def multiReplace(array, indices, replacements):
    for replace_index, index in enumerate(indices):
        array[index] = replacements[replace_index]
    return array

def replaceWhere(array, oldValue, newValue):
    newArray = []
    for el in array:
        if el == oldValue:
            el = newValue
        newArray.append(el)
    return newArray

def multiGet(array, indices):
    returnable = []
    for i in indices:
        returnable.append(array[i])
    return returnable

def isString(test):
    return isinstance(test, basestring)

def colIsString(col):
    for item in col:
        if item == 'NA':
            continue
        elif isString(item):
            return True
    return False

# Creates a `length`-element list where each element is dummy
# Ex: dummyList("dummy", 3)  would return:
# ["dummy", "dummy", "dummy"]
def dummyList(dummy, length):
    returnable = []
    for _ in itertools.repeat(None, length):
        returnable.append(dummy)
    return returnable

# Deletes many indexes from a list
# Adapted from this
# http://stackoverflow.com/questions/497426/deleting-multiple-elements-from-a-list
# Question
def deleteMany(els, args):
    indexes = sorted(list(args), reverse=True)

    for index in indexes:
        del els[index]
    return els

def tryConvertFloat(test):
    try:
        x = float(test)
        return x
    except ValueError:
        return test

# Makes an array pretty printable
def arrayWithLineEnds(array):
    string = ""
    for row in array:
        string += str(row) + "\n"
    return string

def prettyPrint(table):
    print arrayWithLineEnds(table)

def listToCorrectType(array):
    newArray = []
    for el in array:
        newArray.append(toCorrectType(el))
    return newArray

def tableToCorrectType(table):
    newTable = []
    for row in table:
        newTable.append(listToCorrectType(row))
    return newTable

# Will attempt to convert the element
# to its correct type
def toCorrectType(test):
    try:
        return int(test)
    except ValueError:
        try:
            return float(test)
        except ValueError:
            return test

def problemRows(table):
    newTable = []
    for row in table:
        if 'NA' in row:
            newTable.append(row)
    return newTable

def hasMissing(array):
    for el in array:
        if (el == 'NA'):
            return True
    return False

# Returns col values at the colDesiredIndex
# where the col at the colTestIndex == colTestValue
def getColBy(table, colDesiredIndex, colTestIndex, colTestValue):
    cols = []
    for row in table:
        includeCol = False
        for colIndex, col in enumerate(row):
            if colIndex == colTestIndex:
                includeCol = (col == colTestValue)
        if (includeCol):
            cols.append(row[colDesiredIndex])
    return cols


if __name__ == '__main__':
    table = [[1, "cats"], [2, "dogs"], [1, "tvs"]]
    print getColBy(table, 1, 0, 1)



#####################
# join.py
#####################

import csv
import file_system
import util
import copy
import summary

# Here to keep consistent breaks
LINE_BREAK = '----------------'

def rowMatchesTable(row, table, onColumns):
    for index, testRow in enumerate(table):
        if rowsMatch(row, testRow, onColumns):
            return index
    return -1

# Returns true if the rows match `onColumns`
def rowsMatch(row1, row2, onColumns):
    count = 0
    for r1_index, r2_index in onColumns.iteritems():
        if row1[r1_index] == row2[r2_index]:
            count += 1
    return count == len(onColumns)

# Combines the rows and removes the duplicate columns defined in
# onColumns
def newRow(row1, row2, onColumns):
    removalIndices = util.getValues(onColumns)
    row2Copy = copy.copy(row2)
    row2Copy = util.deleteMany(row2Copy, removalIndices)
    return [row1 + row2Copy]

# Sets the small row in a bed of 'NA's and puts its elements
# where they're supposed to be.
def floatLeftSmallRow(row2, onColumns, newRowSize):
    canvas = util.dummyList('NA', newRowSize)
    leftIndexes = util.getKeys(onColumns)
    rightIndexes = util.getValues(onColumns)
    return util.multiReplace(canvas, leftIndexes, util.multiGet(row2, rightIndexes))

def fullOuter(table1, table2, onColumns):
    newTable = []
    table1Len = len(table1[0])
    table2Len = len(table2[0])

    # From left side perspective
    for index, row1 in enumerate(table1):
        matchedRow = rowMatchesTable(row1, table2, onColumns)
        if (matchedRow != -1):
            row2 = table2[matchedRow]
            newTable += newRow(row1, row2, onColumns)
            del table2[matchedRow]
        else:
            row1 += util.dummyList('NA', table2Len-len(onColumns))
            newTable += [row1]

    # From right side
    for index, row2 in enumerate(table2):
        matchedRow = rowMatchesTable(row2, table1, util.flipKeyValues(onColumns))
        if (matchedRow != -1):
            row1 = table1[matchedRow]
            print row1
        else:
            newRowSize = table2Len + table1Len - len(row2)
            row2 = table2[index]
            incompleteRow = floatLeftSmallRow(row2, onColumns, newRowSize)
            newTable += newRow(incompleteRow, row2, onColumns)

    return newTable

if __name__ == '__main__':

    onColumns = {8 : 0, 6 : 1}
    left = [[18.0, 8, 307.0, 130.0, 3504, 12.0, 70, 1, 'chevrolet chevelle malibu'],
    [15.0, 8, 350.0, 165.0, 3693, 11.5, 70, 1, 'buick skylark 320']]

    right = [['plymouth satellite', 70, 2831],
    ['buick skylark', 77, 3865],
    ['chevrolet chevelle malibu', 70, 2881]]
    table = fullOuter(left, right, onColumns)
    util.prettyPrint(table)




#####################
# file_system.py
#####################


import csv
import util

def findDuplicates(row, table, keyValues):
    """ Super terrible way to check duplicates
    returns - item rows if duplicates exist
    returns - empty array if no duplicate
    """
    duplicates = []
    for testRow in table:

        # calculate matches
        matches = None
        for key in keyValues:
            test = (row[key] == testRow[key])
            if (matches == None):
                matches = test
                continue
            else:
                matches = matches and test

            if (not(matches)): break

        # If matches, append the row to duplicates
        if matches:
            duplicates.append(row)
            duplicates.append(testRow)
    return duplicates

# Load a table from a file with no fuss
def loadTable(filename):
    the_file = open(filename, 'r')
    the_reader = csv.reader(the_file, dialect='excel')
    table = []
    for row in the_reader:
        if len(row) > 0:
            table.append(util.listToCorrectType(row))
    the_file.close()
    return table

def write(table, filename):
    with open(filename, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        for row in table:
            writer.writerow(row)

def loadFile(filename, matches):
    """ Loads a csv file

    filename - just the name of the file
    returns - an object with all the table information in it
    """
    the_file = open(filename, 'r')
    the_reader = csv.reader(the_file, dialect='excel')
    table = []
    count = 0
    duplicates = []
    for row in the_reader:
        if len(row) > 0:
            count += 1
            duplicate = findDuplicates(row,table, matches)
            if (len(duplicate) > 0):
                duplicates.append(duplicate)
            table.append(row)
    the_file.close()
    return {'table' : table, 'name' : filename, 'count' : count,
        'duplicates' : duplicates}
