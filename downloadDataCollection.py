import csv
import requests
import os
import datetime

# BEFORE YOU RUN:
# > pip install requests 
# Change the file path name based on OS
### if Windows: \\software.csv
### if Mac/Linux: /software.csv

### UTILS ###
# reads the software csv into a usable dict
def readDownloadLinks():
    path = "" + str(os.getcwd()) + "\\software.csv"
    with open(path, encoding="utf8") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0

        # making a dict, formatL {name: url}
        package_dict = {}
        for row in csv_reader:
            # header
            if line_count == 0: 
                line_count += 1

            # body
            package_dict[row["name"]] = row["download_link"]
                                        
        return package_dict

# get start and end dates of every month starting from start_year
def getStartEndDates(start_year):
    # get last day of month
    def last_day_of_month(any_day):
        next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
        return next_month - datetime.timedelta(days=next_month.day)

    # get arrays of start and end dates to iterate over
    start_dates = []
    end_dates = []

    # if current year and (month+1), break
    current_year = datetime.datetime.today().year
    next_month = datetime.datetime.today().month + 1
    to_break = False
    for year in range(start_year,datetime.datetime.today().year+1):
        if (to_break): break
        for month in range(1,13):
            if (year == current_year and month == next_month) :
                to_break = True
            if (to_break): break
            start_dates.append("%d-%02d-01" % (year, month))
            end_dates.append(str(last_day_of_month(datetime.date(year, month, 1))))
    return {"start": start_dates, "end": end_dates}

### END UTILS ###

# get historic bioconductor download stats for the package name
def getHistoricBiocData(name):
    url = "https://bioconductor.org/packages/stats/bioc/%s/%s_stats.tab" % (name, name)
    response = requests.get(url)

    #TODO: format data
    #TODO: take out empty months
    return response.text

# get historic cran download stats for the package name
def getHistoricCranData(name, start_dates, end_dates, start_year):
    data = []

    # iterate over every month starting from 2015
    for i in range(0,len(start_dates)):
        url = "https://cranlogs.r-pkg.org/downloads/total/%s:%s/%s" % (start_dates[i], end_dates[i], name)
        response = requests.get(url)
        data.append(response.json()[0])

    #TODO: format data
    #TODO: take out empty months
    return data

# get pypi download stats for the package name
def getHistoricPypiData(name):
    return 

# get anaconda download stats for the package name
def getHistoricAnacData(name):
    return


if __name__ == "__main__":
    package_dict = readDownloadLinks()
    for name in package_dict:
        data = []
        if "bioconductor" in package_dict[name]:
            # get data
            data = getHistoricBiocData(name)
            print(data)
            # TODO: add data to master array

        elif "cran" in package_dict[name]:
            start_year = 2015 #TODO: change based on paul getting the year of each package
            ret = getStartEndDates(start_year)
            start_dates = ret["start"]
            end_dates = ret["end"]
            data = getHistoricCranData(name, start_dates, end_dates, start_year)
            print(name)
            print(data)

        # elif "pypi" in package_dict[name]:
        #     data = getHistoricPypiData(name)

        # elif "anaconda" in package_dict[name]:
        #     data = getHistoricAnacData(name)

        else:
            data = "none"

            
