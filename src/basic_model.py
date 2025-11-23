import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

def linear_model():
    """
    Docstring for liner_model
    """
    # prepare data
    X = np.arange(0,10,0.1)
    Y = 2*X + 5
    # plot data
    plt.plot(X, Y, marker = None) # true line
    noise = np.random.normal(0,6, len(X))
    Y = Y + noise
    plt.plot(X, Y, marker = 'o', linestyle = 'None')

    # linear regression
    reg = LinearRegression().fit(X.reshape(-1, 1), Y)
    response = reg.predict(X.reshape(-1, 1))

    # plot response
    plt.plot(X, response, marker = 'x', color = 'red')
    plt.show()

if __name__ == "__main__":
    linear_model()