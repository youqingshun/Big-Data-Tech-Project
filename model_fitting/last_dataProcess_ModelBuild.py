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



class DataSet:
    def __init__(self, days):

        self.startTime = datetime.datetime(2021, 5, 18, 18, 0, 0)
        self.days = days
# days = 26
        self.timeGap  = [6, 9, 4, 5]*days
        rowTime = [self.startTime]
        time_1 = self.startTime
        for gap in self.timeGap:
            delta = datetime.timedelta(hours = gap)
            time_2 = time_1 + delta
            rowTime.append(time_2)
            time_1 = time_2
        self.rowTime = rowTime

    def conMysql_FetchData(self, host, port, user, passwd, database):
        columns = ['carDrivingRate', 'bikeRidingRate'] # the two columns represents the traffic situation of cars and bikes
        conn = pymysql.connect(
                host = host,
                port = port,
                user = user,
                passwd = passwd,
                db = database,
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
        matrix = np.zeros((len(self.rowTime), len(colParams)))
        initial_df = pd.DataFrame(matrix, columns=colParams, index=self.rowTime) # initial the data frame

## average car driving rate
        for t in self.rowTime:
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
        for t in self.rowTime:
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

## average the parameters of weather and meteorology
        for parm in parameters:
            for t in self.rowTime:
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
                weatherAndMeteo = initial_df.iloc[:,2:]

        initial_df.to_csv("initialData.csv", index = False)
        weatherAndMeteo.to_csv("weatherData.csv", index = False)

        return initial_df

# we have 12 variable about the weather and meterology
# we just have the 105 rows data, hence here we apply PCA algorithm to reduce 
    def stanlizeWeatherData(weatherDataPath, initialDataPath):
        weatherAndMeteo = pd.read_csv(weatherDataPath)
        pca = PCA(n_components= 2) # we choose the first two principle componnets after tests
        newWeather = pca.fit_transform(weatherAndMeteo)
        varianceRatio = pca.explained_variance_ratio_  ## find the first 2 principle contribute the 99% variance, hence choose the first two priciple components
        trafficData = pd.read_csv(initialDataPath).iloc[:,0:2]
        trafficData.loc[:,'PC1'] = newWeather[:,0]
        trafficData.loc[:, 'PC2'] = newWeather[:,1]
        trafficData.to_csv("trafficData.csv", index = False)
        return trafficData

# data preparation
    def dataset(predays: int, trafficDataPath: str):
        trafficData = pd.read_csv(trafficDataPath)
        gaps = predays*4
        cars = trafficData.iloc[:-gaps,:]
        yCars = list(trafficData.iloc[gaps:,0])
        yBikes = list(trafficData.iloc[gaps:,1])
        cars.loc[0: , "preCars"] =  yCars
        bikes = trafficData.iloc[:-gaps,:]
        bikes.loc[0: ,"preBikes"] = yBikes
        return cars, bikes


# try to use three models(DECISION TREE, RANDOMFOREST REGRESSOR, EXTRA TREE REGREESSOR) to fit the data
    def chooseModel(self, days, trafficDataPath):
        rf1=DecisionTreeRegressor()
        rf2=RandomForestRegressor(n_estimators=100)      
        rf3=ExtraTreesRegressor()
        cars, bikes = self.dataset(days, trafficDataPath)[0], self.dataset(days, trafficDataPath)[1]
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
        return (optiMethod_Cars, optiMethod_Bikes)


## the car and bike data both fit the DESICION TREE REGRESSOR MODEL WELL
# predict traffic situation of the next days from nearest  day's 9:00 to  farest's 18:00, there are the prediction s of 9:00, 13:00, 18:00 and 00:00 everyday 
    def output(self, days, trafficDataPath):
        cars, bikes = self.dataset(days, trafficDataPath)[0], self.dataset(days, trafficDataPath)[1]
        xCars = cars.iloc[:, :-1]
        yCars =  cars.iloc[:, -1]
        xBikes = bikes.iloc[:, :-1]
        yBikes = bikes.iloc[:, -1]
        meanCars = np.mean(yCars) ## compute the mean and std of the car and bike data
        varCars = np.sqrt(np.var(yCars))
        meanBikes = np.mean(yBikes)
        varBikes = np.sqrt(np.var(yBikes))

# choose models respecitively
        optiMethod_Cars, optiMethod_Bikes = self.chooseModel(days, trafficDataPath)
        rf1=DecisionTreeRegressor()
        rf2=RandomForestRegressor(n_estimators=100)      
        rf3=ExtraTreesRegressor()
        models = [rf1, rf2, rf3]
        rf_c = models[optiMethod_Cars]
        rf_b = models[optiMethod_Bikes]
        resCars =rf_c.fit(xCars,yCars).predict(xCars)
        resBikes = rf_b.fit(xBikes,yBikes).predict(xBikes)
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

        

        ## plot the digrams
        x = [i+1 for i in range(len(rowNames)) ]
        yC = carsRate
        yB = bikeRate
        plt.xlabel("Date time")
        plt.ylabel("Car driving or bike riding rate")
        plt.xticks(x, rowNames)
        plt.ylim(0,1)
        plt.plot(x, yC)
        plt.plot(x, yB)
        plt.legend( labels = ['Cars', 'Bikes'], loc = "upper right")
        plt.show()
        print(res)
        return res

''
    def plot_output(self, days, trafficDataPath):
        output = self.output(self, days, trafficDataPath)
        carsRate = output.iloc[0,:]
        bikeRate = output.iloc[2,:]
        rowNames = output.columns
        x = [i+1 for i in range(len(rowNames)) ]
        yC = carsRate
        yB = bikeRate
        plt.xlabel("Date time")
        plt.ylabel("Car driving or bike riding rate")
        plt.xticks(x, rowNames)
        plt.ylim(0,1)
        plt.plot(x, yC)
        plt.plot(x, yB)
        plt.legend( labels = ['Cars', 'Bikes'], loc = "upper right")
        plt.show()








