import json
import sqlite3
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.decomposition import PCA
import chinese_calendar
import datetime
import pymysql
import dataProcess_ModelBuild


def down(list):
    list = np.array(list)
    pca = PCA(n_components=1)
    out = np.hstack((list[:, 0:1], pca.fit_transform(list[:, 1:])))
    return out.tolist()


def lr(list, pre):
    list = np.array(list)
    clf = LogisticRegression(solver='liblinear')
    clf.fit(list[:, :4], list[:, 4])
    out = clf.predict(pre)
    log = clf.predict_proba(pre)
    return out[0], log[0][0]


def data_process():
    # 环境
    weather = []  # 存原始数据
    weather_out = []  # 存处理后数据

    # 自行车
    bike = []

    # 车位
    slote = []

    # 路况
    env = []
    env_out = []

    # conn = sqlite3.connect('station_parking.db')
    conn = pymysql.connect(host='localhost', user='root', password='root12345', database='bao')
    c = conn.cursor()
    c.execute("select timestamp, slotsAvailable, slotsTotal from parking")
    cursor = c.fetchall()
    for row in cursor:
        slote.append(
            [
                row[0],
                row[1] - row[2],
                row[1],
                0 if (row[1] == 0) else (row[1] - row[2]) / (row[1])
            ]
        )
    conn.close()

    # conn = sqlite3.connect("station_snapshot.db")
    conn = pymysql.connect(host='localhost', user='root', password='root12345', database='bao')
    c = conn.cursor()
    c.execute("select timestamp, bikes, slots from bikesharing")
    cursor = c.fetchall()
    for row in cursor:
        bike.append(
            [
                row[0],
                row[1],
                row[2],
                0 if (row[1] + row[2] == 0) else row[1] / (row[1] + row[2])
            ]
        )
    conn.close()

    with open('BDTdata.json', 'r') as f:
        data = json.load(f)
        tt = data['EnvironmentStation']['carbon-monoxide mg/mc']
        for i in tt:
            env.append([i, tt[i]])
        tt = data['EnvironmentStation']['nitrogen-dioxide ug/mc']
        for i in range(len(tt)):
            env[i].append(tt[env[i][0]])
        tt = data['EnvironmentStation']['ozone ug/mc']
        for i in range(len(tt)):
            env[i].append(tt[env[i][0]])
        tt = data['EnvironmentStation']['particulate-matter10 ug/mc']
        for i in range(len(tt)):
            env[i].append(tt[env[i][0]])
        tt = data['EnvironmentStation']['particulate-matter2.5 ug/mc']
        for i in range(len(tt)):
            env[i].append(tt[env[i][0]])
        tt = data['EnvironmentStation']['sulphur dioxide ug/mc']
        for i in range(len(tt)):
            env[i].append(tt[env[i][0]])
        env_out = down(env)
        for i in env_out:
            if float(i[1]) > 0:
                i[1] = 1
            else:
                i[1] = 2
    # print(env_out)

    return weather_out, bike, slote, env_out


def timecolect(env, bike, slote, road):
    out = {}
    i = 5
    for j in range(1, 32):
        for o in range(24):
            if chinese_calendar.is_workday(datetime.date(2021, i, j)):
                out[str(i).zfill(2) + ' ' + str(j).zfill(2) + ' ' + str(o).zfill(2)] = [0, 0, 0, 1, 0]
            else:
                out[str(i).zfill(2) + ' ' + str(j).zfill(2) + ' ' + str(o).zfill(2)] = [0, 0, 0, 2, 0]
    i = 6
    for j in range(1, 31):
        for o in range(24):
            if chinese_calendar.is_workday(datetime.date(2021, i, j)):
                out[str(i).zfill(2) + ' ' + str(j).zfill(2) + ' ' + str(o).zfill(2)] = [0, 0, 0, 1, 0]
            else:
                out[str(i).zfill(2) + ' ' + str(j).zfill(2) + ' ' + str(o).zfill(2)] = [0, 0, 0, 2, 0]

    for i in env:
        li = i[0].split(' ')
        timest = li[0].split('-')[1] + ' ' + li[0].split('-')[2] + ' ' + li[1].split(':')[0]
        out[timest][0] = i[1]

    for i in bike:
        li = str(i[0]).split(' ')
        timest = li[0].split('-')[1] + ' ' + li[0].split('-')[2] + ' ' + li[1].split(':')[0]
        out[timest][1] = i[-1]

    for i in slote:
        li = str(i[0]).split(' ')
        timest = li[0].split('-')[1] + ' ' + li[0].split('-')[2] + ' ' + li[1].split(':')[0]
        out[timest][2] = i[-1]

    for i in road:
        li = i[0].split(' ')
        timest = li[0].split('-')[1] + ' ' + li[0].split('-')[2] + ' ' + li[1].split(':')[0]
        out[timest][4] = i[1]
    return out.values()


def pre():
    env_out, bike, slote, road_out = data_process()
    data = list(timecolect(env_out, bike, slote, road_out))
    # print(data)
    out, count = lr(data, [[1,0.5,0.5,1]])

    if out == 0:
        out = "crowded"
    elif out == 1:
        out = "loose"
    return out, count
    # return "拥挤", 0.873


def pre1():
    dataset = dataProcess_ModelBuild.DataSet(3)
    print(dataset.output(3, 'trafficData.csv'))


if __name__ == '__main__':

    # print(pre([2, 3, 4, 5]))
    dataset = dataProcess_ModelBuild.DataSet(3)
    print(str(dataset.output(3, 'trafficData.csv')))
