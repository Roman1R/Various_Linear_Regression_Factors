import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler


def compute_metrics(y_true, y_pred):
    mse = np.mean((y_true - y_pred) ** 2)
    rmse = np.sqrt(mse)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_total = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = 1 - (ss_res / ss_total)
    return mse, rmse, r2


def fit_linear_regression(X, y, learning_rate=0.05, epochs=1000):
    X = np.array(X)
    y = np.array(y).reshape(-1, 1)
    
    ones = np.ones((X.shape[0], 1))
    X_bias = np.hstack((ones, X))
    
    n_samples, n_features = X_bias.shape
    weights = np.zeros((n_features, 1))
    
    for epoch in range(epochs):
        y_pred = np.dot(X_bias, weights)
        error = y_pred - y
        gradient = (2 / n_samples) * np.dot(X_bias.T, error)
        weights -= learning_rate * gradient
    
    b = weights[0][0]
    w = weights[1:].flatten()
    return w, b


def predict(X, w, b):
    return np.dot(np.array(X), w) + b


def load_data(filepath, sample_size=None):
    df = pd.read_csv(filepath)
    if sample_size is not None and sample_size < len(df):
        df = df.head(sample_size)
    
    X = df.drop(columns=['Цена_log'])
    y = df['Цена_log']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    return X_scaled, y.values, scaler


def load_test_data(filepath, scaler):
    df = pd.read_csv(filepath)
    X = df.drop(columns=['Цена_log'])
    y = df['Цена_log']
    X_scaled = scaler.transform(X)
    return X_scaled, y.values

