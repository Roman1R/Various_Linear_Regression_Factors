from gradient import (
    fit_linear_regression,
    predict,
    compute_metrics,
    load_data,
    load_test_data
)

import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt


print("Готово!")

BASE_PATH = "Dataset (Farhat)/"
TEST_PATH = BASE_PATH + "dataset_prepared.csv"

sizes = [3000, 5000]
train_data = {}

for size in sizes:
    path = BASE_PATH + f"dataset_sample_{size}.csv"
    print(f"Загрузка {path}")
    X, y, scaler = load_data(path)
    train_data[size] = {'X': X, 'y': y, 'scaler': scaler}
    print(f"  Размер: {X.shape}")

X_test, y_test = load_test_data(TEST_PATH, train_data[3000]['scaler'])
print(f"\nТестовые данные: {X_test.shape}")

LEARNING_RATE = 0.05
EPOCHS = 1000

results = {}

for size in sizes:
    print(f"\n{'='*50}")
    print(f"Обучение на {size} строках")
    print('='*50)

    X_train = train_data[size]['X']
    y_train = train_data[size]['y']

    start = time.time()
    w, b = fit_linear_regression(X_train, y_train, LEARNING_RATE, EPOCHS)
    elapsed = time.time() - start

    y_pred = predict(X_test, w, b)
    mse, rmse, r2 = compute_metrics(y_test, y_pred.flatten())

    results[size] = {
        'w': w,
        'b': b,
        'time': elapsed,
        'mse': mse,
        'rmse': rmse,
        'r2': r2
    }

    print(f"Время: {elapsed:.4f} сек")
    print(f"MSE: {mse:.5f}")
    print(f"RMSE: {rmse:.5f}")
    print(f"R2: {r2:.5f}")


df_results = pd.DataFrame({
    'Размер': sizes,
    'Время (сек)': [results[s]['time'] for s in sizes],
    'MSE': [results[s]['mse'] for s in sizes],
    'RMSE': [results[s]['rmse'] for s in sizes],
    'R²': [results[s]['r2'] for s in sizes]
})

print("Сравнение результатов:")
print(df_results.to_string(index=False))

fig, axes = plt.subplots(1, 3, figsize=(14, 4))

# Время обучения
axes[0].bar(sizes, [results[s]['time']
            for s in sizes], color='skyblue', edgecolor='black')
axes[0].set_xlabel('Размер датасета')
axes[0].set_ylabel('Время (сек)')
axes[0].set_title('Время обучения')
axes[0].grid(True, alpha=0.3)

# MSE и RMSE
x = np.arange(len(sizes))
width = 0.35
mse_values = [results[s]['mse'] for s in sizes]
rmse_values = [results[s]['rmse'] for s in sizes]

axes[1].bar(x - width/2, mse_values, width, label='MSE',
            color='coral', edgecolor='black')
axes[1].bar(x + width/2, rmse_values, width, label='RMSE',
            color='lightgreen', edgecolor='black')
axes[1].set_xlabel('Размер датасета')
axes[1].set_ylabel('Значение')
axes[1].set_title('Ошибки')
axes[1].set_xticks(x)
axes[1].set_xticklabels(sizes)
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# R^2
axes[2].bar(sizes, [results[s]['r2']
            for s in sizes], color='gold', edgecolor='black')
axes[2].set_xlabel('Размер датасета')
axes[2].set_ylabel('R²')
axes[2].set_title('Коэффициент детерминации')
axes[2].set_ylim(0.5, 1.0)
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

r3000 = results[3000]
r5000 = results[5000]

print("Изменение при переходе с 3000 на 5000:")
print(f"MSE:  {((r5000['mse'] - r3000['mse']) / r3000['mse'] * 100):+.2f}%")
print(f"RMSE: {((r5000['rmse'] - r3000['rmse']) / r3000['rmse'] * 100):+.2f}%")
print(f"R²:   {((r5000['r2'] - r3000['r2']) / r3000['r2'] * 100):+.2f}%")
print(f"Time: {((r5000['time'] - r3000['time']) / r3000['time'] * 100):+.2f}%")
