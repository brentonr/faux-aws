import os
import re

class Filter:
    def __init__(self, index, name=None, values=[]):
        self.index = index
        self.name = name
        self.values = values

    def setName(self, name):
        self.name = name

    def setValues(self, values):
        self.values = values

    def appendValue(self, value):
        self.values.append(value)

    def __str__(self):
        return "[" + self.index + "] " + self.name + " ( " + ' , '.join(self.values) + " )"

def getFilters(args):
    filters = {}
    for key,value in args.iteritems():
        matchGroup = re.match(r'^Filter\.([0-9]+).(Name|(Value)\.([0-9]+))$', key)
        if matchGroup:
            filterIndex = matchGroup.group(1)
            filterName = None
            filterValue = None

            if matchGroup.group(2) == 'Name':
                filterName = value
            elif matchGroup.group(3) == 'Value':
                filterValue = value

            if filterIndex in filters:
                if not filterName is None:
                    filters[filterIndex].setName(filterName)
                else:
                    filters[filterIndex].appendValue(filterValue)
            else:
                if not filterName is None:
                    filters[filterIndex] = Filter(filterIndex, name=filterName)
                else:
                    filters[filterIndex] = Filter(filterIndex, values=[filterValue])
    return filters.values()
