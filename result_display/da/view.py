
import datetime
import web
import main
import dataProcess_ModelBuild

urls = (
    '/(.*)', 'index'
)


class index:
    def GET(self, name):
        fo = open("temp/index.html", 'r')

        con = fo.read()
        # out = con
        conlist = con.split('<<>>')
        so, count = main.pre()

        dataset = dataProcess_ModelBuild.DataSet(3)
        soo = dataset.output(3, 'trafficData.csv')

        out = conlist[0] + "When the threshold is " + str(count) + ", we predict that the traffic of " + str(datetime.date.today()) + " is " + str(so) + conlist[1] + str(soo) + conlist[2]
        return out


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
