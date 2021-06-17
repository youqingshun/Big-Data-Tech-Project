from SST import StationManager,  MySQLStationManager, Station, MySQLStationManager
import pymysql


# 连接数据库
conn = pymysql.connect(
        host = '127.0.0.1',
    #端口号
        port = 3306,
    #用户名
        user = 'root',
    #密码
        passwd = '123456',
    #数据库名称
        db = 'bdt_station',
    #字符编码格式
        charset = 'utf8')

cur = conn.cursor()


# 建表语句，字段要与json中的key值对应
createTableSql = 'CREATE table IF NOT EXISTS 0518_0522bikesharing (id int NOT NULL AUTO_INCREMENT,\
station_id varchar(128) DEFAULT NULL,\
name varchar(128) DEFAULT NULL,\
lat float DEFAULT NULL,\
lon float DEFAULT NULL,\
slots int DEFAULT NULL,\
bikes int DEFAULT NULL,\
timestamp timestamp NULL DEFAULT NULL,\
address varchar(128) DEFAULT NULL,\
city varchar(128) DEFAULT NULL,\
PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=utf8;'
#json在我本地的路径
jsonPath = 'D:/courses and slides/bdt-2021-master/src/stations.json'


cur.execute(createTableSql)
conn.commit()
conn.close()


station_manager = StationManager()

stations = station_manager.list()

json_to_mysql = MySQLStationManager(host = '127.0.0.1', port = 3306, database = "bdt_station", user = "root", password = "123456")

json_to_mysql.save(stations)
print("tasks are done !")