from urllib import request
import requests
import json
url0 = "https://mobility.api.opendatahub.bz.it/v2/flat%2Cnode"  #check all the respects of the 
url1 = "https://mobility.api.opendatahub.bz.it/v2/flat%2Cnode"
# url = "https://mobility.api.opendatahub.bz.it/v2/flat%2Cnode/Bicycle?limit=200&where=sactive.eq.true&distinct=true"
# response = request.urlopen(url)
# html = response.read()
# mess = html.decode('utf-8')
vals = ['EnvironmentStation', 'RWISstation','MeteoStation', 'Trafficstation','traffic', 'TrafficSensor','TrafficStreetFactor', 'Streetstation', 'LinkStation', 'BluetoothStation', 'ParkingStation', 'ParkingSensor']
response = requests.request("GET", url1)
data = response.json()
# print(data)
# dt = data["data"]
# print(len(data))

newinfo = []
for val in vals:
    for i in data:
        if i["id"] == val:
            newinfo.append(i['self.stations+datatypes'])  #find all of the respects we ne 

for i in newinfo:
    print("\t")
    print(i)

# https://mobility.api.opendatahub.bz.it/v2/flat%2Cnode/EnvironmentStation/%2A?limit=200&where=and%28smetadata.municipality.in.%28Trento%29%2Csactive.eq.true%29&distinct=true
# https://mobility.api.opendatahub.bz.it/v2/flat,node/EnvironmentStation/*

# print(newinfo) # the 12 basic url
res = {}
spec = "%2A?limit=10000&where=and%28smetadata.municipality.in.%28Trento%29%2Csactive.eq.true%29&distinct=true"
ret = {}
for i in range(len(newinfo)):
    url = newinfo[i].replace(",", "%2C")
    url = url.replace("*", spec)
    # print(url)
    # print("\t")
    resp = requests.request("GET", url)
    dt = resp.json()["data"]
    # res[newinfo[i]] = dt
    params = {}
    lis = []
    for j in dt:
        parm = j['tname']
        if parm not in lis:
            lis.append(parm)
            # values = {}
            newurl = newinfo[i].replace(",", "%2C")
            newurl = newurl.replace("*", parm)
            fixurl = "/2021-04-05/2021-04-06?limit=500&where=and%28smetadata.municipality.in.%28Trento%29%2Csactive.eq.true%29&distinct=true&timezone=UTC"
            # fixurl = "/2021-04-05/2021-04-06?limit=500&where=sname.ire.Trento&distinct=true&timezone=UTC"
            newurl += fixurl

            rp = requests.request("GET", newurl)
            newdt = rp.json()["data"]
            recod = {}
            for x in newdt:
                recod[x["mvalidtime"]] = x["mvalue"]
            # if len(newdt) > 1:
            #     unit = " " + newdt[0]["tunit"]
            #     params[parm + unit ] = recod
            # else:
            #     params[parm] = recod
     
            # for y in newdt:
            #     if len(y) > 0:
            #         for ut in y:
            #             if len(ut) > 0:
            #                 params[parm + " " + newdt[0]["tunit"]]

            if len(newdt) > 0 and "tunit" in newdt[0]:
                params[parm + " " + newdt[0]["tunit"]] = recod
            else:
                params[parm] = recod

    res[vals[i]] = params


filename = "BDTdata.json"
with open(filename, "w") as file_obj:
    json.dump(res, file_obj)  # we can collect the data of 'EnvironmentStation', 



    


        



    

# print("------------")
# envirS = res['list_0']['data']
# print(len(envirS))
# print(type(envirS))
# print(envirS[0].keys())
# # https://mobility.api.opendatahub.bz.it/v2/flat%2Cnode/EnvironmentStation?limit=10000&where=smetadata.municipality.eq.Trento&distinct=true

# param0 = []

# dict = {}
# for i in envirS:
#     param0.append(i["tname"])
# print(list(set(param0)))


# newurl = "https://mobility.api.opendatahub.bz.it/v2/flat,node/EnvironmentStation/*"

# fix = "carbon-monoxide/2021-04-05/2021-04-15?limit=500&where=and%28smetadata.municipality.in.%28Trento%29%2Csactive.eq.true%29&distinct=true&timezone=UTC"
# newurl = newurl.replace("*", fix)
# respo = requests.request("GET", newurl)
# values = respo.json()["data"]

# datas = {}
# for i in values:
#     datas[i["mvalidtime"]] = i["mvalue"]

# # print(datas)
# # print(len(datas))
