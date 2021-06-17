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
createTableSql = 'CREATE table IF NOT EXISTS 0519_0522parking (id int NOT NULL AUTO_INCREMENT,\
description varchar(128) DEFAULT NULL,\
name varchar(128) DEFAULT NULL,\
slotsTotal int DEFAULT NULL,\
slotsAvailable int DEFAULT NULL,\
monitored text,\
parkAndRide text,\
city varchar(128) DEFAULT NULL,\
lat float DEFAULT NULL,\
lon float DEFAULT NULL,\
timestamp timestamp(6) NULL DEFAULT NULL,\
PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=utf8;'
#json在我本地的路径
jsonPath = 'D:/courses and slides/data/park0519_0522.json'


cur.execute(createTableSql)
conn.commit()
conn.close()


station_manager = StationManager()

stations = station_manager.list()

json_to_mysql = MySQLStationManager(host = '127.0.0.1', port = 3306, database = "bdt_station", user = "root", password = "123456")

json_to_mysql.save(stations)
print("tasks are done !")


'''
# 打开json文件
with open(jsonPath,'r',encoding='utf_8_sig') as f:
    # 读取json文件
    for line in f.readlines():
        # 读取json文件格式为python的dict字典类型
        dic = json.loads(line)
        
        # 拼接key值为：name,age
        keys = ','.join(dic.keys())
        
        # 将value值存为列表类型：['tom', '28'] <class 'list'>
        valuesList = [dici for dici in dic.values()]
        
        # 将value值存为元组类型：('tom', '28')
        valuesTuple = tuple(valuesList)
        
        # 拼接values为：%s, %s
        values = ', '.join(['%s']*len(dic)) 
        
        # 插入的表名
        table = 'test.jsontest'
        
        # 插入sql语句
        insertSql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table, keys=keys, values=values)
        
        #执行建表与插入sql
        cur.execute(createTableSql)
        cur.execute(insertSql,valuesTuple)
        
        # 提交commit
        conn.commit()
    
    # 关闭数据库连接
    conn.close()
'''