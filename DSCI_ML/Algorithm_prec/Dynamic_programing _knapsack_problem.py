import numpy as np

def getUsedItems(w,M):
    # item count
    i = len(M)-1
    currentW =  len(M[0])-1
    # set everything to not marked
    marked = [0]*(len(M))

    while (i >= 0 and currentW >=0):
        if (i==0 and M[i][currentW] >0 )or M[i][currentW] != M[i-1][currentW]:
            marked[i] =1
            currentW = currentW-w[i]
        i = i-1
    return marked

# v = list of item values or profit
# w = list of item weight or cost
# W = max weight or max cost for the knapsack

def zeroOneKnapsack(v, w, W):
    # c is the cost matrix
    n = len(v)
    M = np.zeros((n,W+1))
    for i in range(0,n):
        #for ever possible weight
        for j in range(0,W+1):
            #can we add this item to this?
            if (w[i] > j):
                M[i][j] = M[i-1][j]
            else:
                M[i][j] = max(M[i-1][j],v[i] +M[i-1][j-w[i]])
    print(M)
    return [M[n-1][W], getUsedItems(w,M)]

def unboundedKnapsack(v, w, W):
    # c is the cost matrix
    n = len(v)
    M = np.zeros((n,W+1))
    for i in range(0,n):
        #for ever possible weight
        for j in range(0,W+1):
            #can we add this item to this?
            if (w[i] > j):
                M[i][j] = M[i-1][j]
            else:
                M[i][j] = max(M[i-1][j], v[i]+M[i][j-w[i]])
    print(M)
    return [M[n-1][W], getUsedItems(w,M)]


v = [160, 90, 15]
w = [7, 3, 2]
W = 20
zeroOneKnapsack(v, w, W)
