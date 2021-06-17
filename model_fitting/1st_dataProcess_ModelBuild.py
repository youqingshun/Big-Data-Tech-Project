from numpy.lib.function_base import append
import pymysql
import numpy as np
import pandas as pd
import datetime
from sklearn.decomposition import PCA

import matplotlib as mpl
import numpy as np
import warnings 
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.utils.validation import column_or_1d


startTime = datetime.datetime(2021, 5, 18, 18, 0, 0)
days = 26
timeGap  = [6, 9, 4, 5]*days
rowTime = [startTime]
time_1 = startTime
for gap in timeGap:
    delta = datetime.timedelta(hours = gap)
    time_2 = time_1 + delta
    rowTime.append(time_2)
    time_1 = time_2
print(rowTime)


columns = ['carDrivingRate', 'bikeRidingRate'] # the two columns represents the traffic situation of cars and bikes

conn = pymysql.connect(
        host = '127.0.0.1',
        port = 3306,
        user = 'root',
        passwd = '123456',
        db = 'bdt_station',
        charset = 'utf8')

cur = conn.cursor()

sql_0= "select parameters from weatherAndTraffic;"
cur.execute(sql_0)
paras = cur.fetchall()
parameters = []
for i in paras:
    if list(i)[0] not in parameters:
        parameters.append(list(i)[0])
colParams = columns+parameters
# print(colParams)

matrix = np.zeros((len(rowTime), len(colParams)))
initial_df = pd.DataFrame(matrix, columns=colParams, index=rowTime)
# print(initial_df)

# initial_df.loc['2021-05-18 18:00:00','carDrivingrate'] = 100

## average car driving rate
for t in rowTime:
    dalt = datetime.timedelta(hours = 1)
    sql = f"select slotsTotal, slotsAvailable from parking where `timestamp` >= '{t-dalt}' and `timestamp` <= '{t+dalt}';" # format( t-datetime.timedelta(hours = 1), t+datetime.timedelta(hours= 1) )
    cur.execute(sql)
    vals = cur.fetchall()
    total = 0
    cardrivings = 0
    for val in vals:
        total += val[0]
        cardrivings += (val[0] - val[1])
    if total == 0:
        carDrivingRate = 0.5
    else:
        carDrivingRate = cardrivings/total
    initial_df.loc[t, "carDrivingRate"] = carDrivingRate
    
## average bike riding rate
for t in rowTime:
    dalt = datetime.timedelta(hours = 1)
    sql = f"select slots, bikes from bikesharing where `timestamp` >= '{t-dalt}' and `timestamp` <= '{t+dalt}';" # format( t-datetime.timedelta(hours = 1), t+datetime.timedelta(hours= 1) )
    cur.execute(sql)
    vals = cur.fetchall()
    total = 0
    bikeRidings = 0
    for val in vals:
        total += (val[0] + val[1])
        bikeRidings += val[0] 
    if total == 0:      
        bikeRidingRate = 0.5
    else:
        bikeRidingRate = bikeRidings/total
    initial_df.loc[t, "bikeRidingRate"] = bikeRidingRate

print(initial_df)


## average the parameters of weather and meteorology
for parm in parameters:
    for t in rowTime:
        dalt = datetime.timedelta(hours = 1)
        sql = f"select parameters, `value` from weatherandtraffic where parameters = '{parm}' and `timestamp` >= '{t-dalt}' and `timestamp` <= '{t+dalt}';" 
        cur.execute(sql)
        vals = cur.fetchall()
        length = len(vals)
        total  = 0
        for val in vals:
            total +=  val[1] 
  
        ave_val = total/length
        initial_df.loc[t, parm] = ave_val

initial_df.to_csv("initialData.csv", index = False)


# print(initial_df)
weatherAndMeteo = initial_df.iloc[:,2:]
# print(weatherAndMeteo)
# print(weatherAndMeteo.columns)
weatherAndMeteo.to_csv("weatherData.csv", index = False)

# we have 12 variable about the weather and meterology
# we just have the 105 rows data, hence here we apply PCA algorithm to reduce 

weatherAndMeteo = pd.read_csv("weatherData.csv")
# print(weatherAndMeteo)

## check the all principle components 
pca = PCA(n_components=12)
new_weather = pca.fit_transform(weatherAndMeteo)
# print(new_weather)
print(pca.explained_variance_ratio_) ## find the first 2 principle contribute the 99% variance, hence choose the first two priciple components


pca_0 = PCA(n_components=2)
newWeather = pca_0.fit_transform(weatherAndMeteo)
trafficData = pd.read_csv("initialData.csv").iloc[:,0:2]

trafficData.loc[:,'PC1'] = newWeather[:,0]
trafficData.loc[:, 'PC2'] = newWeather[:,1]
print(trafficData)


newData = pd.DataFrame(trafficData, 'PC1' = newWeather[:,0], 'PC2' = newWeather[:,1])
print(newData)

# data preparation
def dataset(predays: int):
    gaps = predays*4
    cars = trafficData.iloc[:-gaps,:]
    yCars = list(trafficData.iloc[gaps:,0])
    yBikes = list(trafficData.iloc[gaps:,1])
    cars.loc[0: , "preCars"] =  yCars
    bikes = trafficData.iloc[:-gaps,:]
    bikes.loc[0: ,"prebikes"] = yBikes
    return cars, bikes

## try 1 day's prediction to chooose the model
cars = dataset(1)[0]
bikes = dataset(1)[1]


# try to use three models(DECISION TREE, RANDOMFOREST REGRESSOR, EXTRA TREE REGREESSOR) to fit the data
rf1=DecisionTreeRegressor()
rf2=RandomForestRegressor(n_estimators=100)      
rf3=ExtraTreesRegressor()
xCars = cars.iloc[:, :-1]
yCars =  cars.iloc[:, -1]
xBikes = bikes.iloc[:, :-1]
yBikes = bikes.iloc[:, -1]



# three prediction method to predict
# predict the car driving  rate
y_rf1_c =rf1.fit(xCars,yCars).predict(xCars)
y_rf2_c =rf2.fit(xCars,yCars).predict(xCars)
y_rf3_c =rf3.fit(xCars,yCars).predict(xCars)

# predict the bike driving rate
y_rf1_b =rf1.fit(xBikes,yBikes).predict(xBikes)
y_rf2_b =rf2.fit(xBikes,yBikes).predict(xBikes)
y_rf3_b =rf3.fit(xBikes,yBikes).predict(xBikes)


MSE_1_cars = sum((y_rf1_c - yCars)**2)
MSE_2_cars = sum((y_rf2_c - yCars)**2)
MSE_3_cars = sum((y_rf3_c - yCars)**2)

MSE_1_bikes = sum((y_rf1_b - yBikes)**2) 
MSE_2_bikes = sum((y_rf2_b - yBikes)**2)
MSE_3_bikes = sum((y_rf3_b - yBikes)**2)




mseCars = [MSE_1_cars, MSE_2_cars, MSE_3_cars]
mseBikes = [MSE_1_bikes, MSE_2_bikes, MSE_3_bikes]

optiMethod_Cars = mseCars.index(min(mseCars))
optiMethod_Bikes = mseBikes.index(min(mseBikes))
# print(optiMethod_Cars)
# print(optiMethod_Bikes)
print("\n")


## compute the mean and std of the car and bike data
meanCars = np.mean(yCars)
varCars = np.sqrt(np.var(yCars))
meanBikes = np.mean(yBikes)
varBikes = np.sqrt(np.var(yBikes))

## the car and bike data both fit the DESICION TREE REGRESSOR MODEL WELL



# predict traffic situation of the next days from nearest  day's 9:00 to  farest's 18:00, there are the prediction s of 9:00, 13:00, 18:00 and 00:00 everyday 
def output(days):
    cars, bikes = dataset(days)[0], dataset(days)[1]
    rf= DecisionTreeRegressor()
    resCars =rf.fit(cars.iloc[:, :-1],cars.iloc[:, -1]).predict(cars.iloc[:, :-1])
    resBikes = rf.fit(bikes.iloc[:, :-1],bikes.iloc[:, -1]).predict(bikes.iloc[:, :-1])
    carsRate = list(resCars[-(4*days - 1) :])
    bikeRate = list(resBikes[-(4*days - 1):])
    carSituat = [" not heavy" if ( x < meanCars- varCars) else "heavy" if (x > meanCars + varCars) else "medium" for x in carsRate]
    bikeSituat  = [" not heavy" if ( y < meanBikes- varBikes) else "heavy" if (y > meanBikes + varBikes) else "medium" for y in bikeRate]


    rowNames = []
    timeSP = datetime.datetime(2021, 6, 14, 0, 0, 0)
    tGaps = [9, 4, 5, 6]
    for i in range(len(carsRate)):
        delta =  datetime.timedelta(hours = ((i//4)* 24 + sum(tGaps[: i % 4 + 1])))
        rowNames.append(timeSP+delta)

    columNames = ["Car Driving Rate", "Car Stiation", "Bike Riding Rate", "Bike Stiation"]

    
    res = pd.DataFrame((carsRate, carSituat, bikeRate,  bikeSituat))
    res.columns = rowNames
    res.index = columNames
    return res
     
print(output(1))
