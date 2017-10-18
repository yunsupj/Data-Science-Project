from collections import Counter

class KNearestNeighbors(object):
    def __init__(self, k=5, distance=euclidean_distance):
        self.k = k
        self.distance = distance
        self.X_train = None
        self.y_train = None

    def fit(self, X, y):
        self.X_train = X
        self.y_train = y

    def predict(self, X_predict):
        X_predict = X_predict.reshape( (-1, self.X_train.shape[1]) )
        distances = np.zeros((X_predict.shape[0], self.X_train.shape[0]))

        for i in range(len(X_predict)):
            for j in range(len(self.X_train)):
                distances[i][j] = self.distance(X_predict[i], self.X_train[j])
        
        label = []
        for l in distances:
            index = np.argsort(l)[:self.k+1]
            label.append(Counter(self.y_train[index]).most_common(1)[0][0])
        return label

