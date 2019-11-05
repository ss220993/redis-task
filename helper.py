import operator

def sortByCount(input):
   sorted_d = dict(sorted(input.items(), key=operator.itemgetter(0),reverse=True))
   return sorted_d