from dataProcess_ModelBuild import DataSet
import pandas as pd 

def dset(days, trafficDataPath):
        trafficData = pd.read_csv(trafficDataPath)
        gaps = days*4
        cars = trafficData.iloc[:-gaps,:]
        yCars = list(trafficData.iloc[gaps:,0])
        yBikes = list(trafficData.iloc[gaps:,1])
        cars.loc[0: , "preCars"] =  yCars
        bikes = trafficData.iloc[:-gaps,:]
        bikes.loc[0: ,"preBikes"] = yBikes
        return cars, bikes


def callModel(days, trafficDataPath):
    dt = DataSet(days)
    output = dt.output(days, trafficDataPath)
    # plotOut = dt.plot_output(days, trafficDataPath)
    return output

callModel(1, "trafficData.csv")



