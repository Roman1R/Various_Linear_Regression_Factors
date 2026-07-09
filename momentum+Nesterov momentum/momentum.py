import csv

def gradient(w, b,   data, number_of_sings=19):
    grad = [0 for i in range(number_of_sings)]#градиент
    gradb = 0#градиент свободного члена
    for i in range(len(data)):
        pred = b
        for j in range(number_of_sings):
            pred += w[j]*data[i][j]
        err = pred - data[i][-1]
        for j in range(number_of_sings):
            grad[j] += err*data[i][j]*2
        gradb += err*2
        #считаем градиент по каждой квартире и складываем потом усредним
    for i in range(number_of_sings):
        grad[i] /= len(data)#усредняем
    gradb /= len(data)
    return grad, gradb#возвращает градиент по перменным и градиент по свободному члену отдельно

def data_normalized(list_dt, mean=None, std=None):
    if mean is None or std is None:#считаем среднее на тренировочных данных
        mean = [0 for i in range(len(list_dt[0])-1)]
        for i in range(len(list_dt)):
            for j in range(len(list_dt[i])-1):
                mean[j] += list_dt[i][j]
        for i in range(len(mean)):
            mean[i] /= len(list_dt)
        std = [0 for i in range(len(mean))]
        for i in range(len(list_dt)):
            for j in range(len(list_dt[i])-1):
                std[j] += (list_dt[i][j] - mean[j])**2
        for i in range(len(std)):
            std[i] /= len(list_dt)
            std[i] = std[i] ** 0.5
    else:#если поданы просто присваеваем без вычислений
        mean = mean
        std = std
    new_list_dt = []
    for i in range(len(list_dt)):
        row_i = []
        for j in range(len(list_dt[i])-1):
            x_i_j = (list_dt[i][j]-mean[j])/std[j]#z-стандартизация превращает данные в числа от -1 до 1
            row_i.append(x_i_j)
        row_i.append(list_dt[i][-1])#добавляем целевую переменную
        new_list_dt.append(row_i)
    return new_list_dt, mean, std

def prev_csv(data):#функция переводит данные в список мне так проще хотя может и неэффективней
    list_data = []
    flag = 0
    for row in data:
        if flag == 0:
            flag+=1
        else:
            l = list(row)
            t = [float(i) for i in l]
            list_data.append(t)
    return list_data

def find_weights_simple(data, number_of_epochs=1000, rate_learning = 0.05):#стандартный градиент
    v = [0.0 for i in range(19)]
    b = sum(data[i][-1] for i in range(len(data)))/len(data)
    for i in range(number_of_epochs):
        g, gradb = gradient(v, b, data)
        for j in range(len(v)):
            v[j] -= (rate_learning*g[j])
        b-=gradb*rate_learning
    return v, b

def find_weight_momentum(data, number_of_epochs = 12, rate_learning = 0.05, rate_inertion = 0.3):
    x = [0.0 for i in range(19)]
    v = [0.0 for i in range(19)]
    v_b = 0
    b = sum(data[i][-1] for i in range(len(data)))/len(data)
    for i in range(number_of_epochs):
        g, gradb = gradient(x, b, data)
        for j in range(len(x)):
            v[j] = v[j]*rate_inertion- (rate_learning*g[j])
            x[j]+=v[j]
        v_b = v_b*rate_inertion- (rate_learning*gradb)
        b+=v_b
    return x, b

def find_weight_Nesterov_momentum(data, number_of_epochs = 12, rate_learning = 0.05, rate_inertion = 0.3):
    x = [0.0 for i in range(19)]
    v = [0.0 for i in range(19)]
    b = sum(data[i][-1] for i in range(len(data)))/len(data)
    v_b = 0
    for i in range(number_of_epochs):
        new_x = [x[j]+v[j]*rate_inertion for j in range(len(x))]
        g, gradb = gradient(new_x, b, data)
        for j in range(len(x)):
            v[j] = v[j]*rate_inertion- (rate_learning*g[j])
            x[j]+=v[j]
        v_b = v_b*rate_inertion- (rate_learning*gradb)
        b+=v_b
    return x, b

def elipsoid_method(data, number_of_epochs = 500, radius = 150):
    elipsoid = [[0.0 for i in range(20)] for i in range(20)]
    center = [0 for i in range(20)]
    center[19] = 10
    for i in range(20):
        elipsoid[i][i] = radius
    for i in range(number_of_epochs):
        x = center[:19]
        b = center[19]
        g, gradb = gradient(x, b, data)
        g.append(gradb)
        start_h = g
        elipsoid1 = [0 for i in range(20)]
        for i in range(20):
            for j in range(20):
                elipsoid1[i] += elipsoid[i][j] * start_h[j]
        elipsoid2 = 0
        for i in range(20):
            elipsoid2 += elipsoid1[i] * start_h[i]
        h = [0 for i in range(20)]
        for i in range(20):
            h[i] = elipsoid1[i] / (elipsoid2 ** 0.5)

        for i in range(20):
            center[i] -= h[i] / 21

        for i in range(20):
            for j in range(20):
                elipsoid[i][j] -= (2 / 21) * h[i] * h[j]
                elipsoid[i][j] *= (400 / 399)
    return center[:19], center[19]


def errors(data, v, b):
    mse = 0
    mn = 0
    for i in range(len(data)):
        pred = b
        for j in range(len(v)):
            pred += v[j] * data[i][j]
        err = data[i][-1] - pred
        mse += err * err
        mn += data[i][-1]
    mse /= len(data)
    rmse = mse ** 0.5

    mn /= len(data)
    ss_total = 0
    ss_res = 0
    for i in range(len(data)):
        pred = b
        for j in range(len(v)):
            pred += v[j] * data[i][j]
        ss_total += (mn - data[i][-1]) ** 2
        ss_res += (data[i][-1] - pred) ** 2

    r = 1 - ss_res / ss_total

    print("mse:", mse)
    print("rmse:", rmse)
    print("r:", r)
    return mse, rmse, r


file = open('dataset_sample_1000 (1).csv','r')
train_data = csv.reader(file)
train_list_data = prev_csv(train_data)
file.close()
train_list_data, mean, std = data_normalized(train_list_data)


x, b = find_weight_Nesterov_momentum(train_list_data)

file = open('dataset_prepared (1).csv','r')
test_data = csv.reader(file)
test_list_data = prev_csv(test_data)
file.close()
test_list_data, mean, std = data_normalized(test_list_data, mean, std)


mse_test, rmse_test, r_test = errors(test_list_data, x, b)