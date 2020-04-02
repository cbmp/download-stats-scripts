import csv
import requests
import os
import datetime
import calendar
import operator
import json
from condastats.cli import overall, pkg_platform, pkg_version, pkg_python, data_source
from google.cloud import bigquery

# BEFORE YOU RUN/WHEN SWITCHING VENVS:
#
# > pip install requests 
# > pip install --upgrade google-cloud-bigquery
# IF WINDOWS: > choco install miniconda3 
#               switch to miniconda venv in VSCode
#             > conda install -c conda-forge condastats
#               install the rest of the packages with pip
# IF MAC:   install miniconda3, rest idk yet TODO: figure it out
#         > conda install -c conda-forge condastats
# 
# If you haven't already, follow this guide for GBQ: https://github.com/ofek/pypinfo
## up until step 10 (moving credential JSON file)
# Follow this guide to set up the credentials in your PATH/env variable
## https://cloud.google.com/bigquery/docs/reference/libraries
#
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
# format: yyyy-mm-dd
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

## UNUSED FOR NOW ##
# get months starting from 2017-01, ending end_year and end_month
def getMonths(end_year, end_month):
    months = []
    to_break = False
    for year in range(2017, end_year+1):
        if (to_break): break
        for month in range(1,13):
            if (year == end_year and month == end_month + 1) :
                to_break = True
            if (to_break): break
            months.append("%d-%02d" % (year, month))
    return months

### take out empty months from beginning and end ###
def removeEmptyMonths(data):
    # sort by month, then year ascending
    data = sorted(data, key=lambda k: list(calendar.month_abbr).index(k['month'])) 
    data = sorted(data, key=lambda k: k['year']) 

    # get ind at which downloads are not 0
    def getNonEmptyInd(data, reverse):
        if reverse:
            for i in range(len(data)-1, 0, -1):
                if (str(data[i]['downloads']) != '0'):
                    return i 
        else:
           for i in range(0,len(data)):
                if (str(data[i]['downloads']) != '0'):
                    return i

        # no downloads
        return None
   
    start_ind = getNonEmptyInd(data, reverse=False)
    end_ind = getNonEmptyInd(data, reverse=True)

    # no downloads
    if (start_ind == end_ind == None):
        data = []
    else:
        data = data[start_ind:end_ind+1]

    return data
### END UTILS ###

# get historic bioconductor download stats for the package name
def getHistoricBiocData(name):
    url = "https://bioconductor.org/packages/stats/bioc/%s/%s_stats.tab" % (name, name)
    response = requests.get(url).text

    ### FORMAT DATA ###
    
    # separating into arrays
    lines = response.split('\n') 
    res_data = [x.split('\t') for x in lines]

    # header is Year / Month / Nb_of_distinct_IPs / Nb_of_downloads
    # cut the header out
    res_data.pop(0)

    # iterate and put into array
    data = []
    for row in res_data:
        if len(row) == 4 and row[1] != "all":
            data.append({
                "year": row[0],
                "month": row[1], # to numbers for sorting
                "downloads": row[3],
            })

    # remove empty months
    data = removeEmptyMonths(data)

    return data

# get historic cran download stats for the package name
def getHistoricCranData(name, start_dates, end_dates):
    data = []

    # iterate over every month from start_year
    for i in range(0,len(start_dates)):
        url = "https://cranlogs.r-pkg.org/downloads/total/%s:%s/%s" % (start_dates[i], end_dates[i], name)
        response = requests.get(url)
        data.append(response.json()[0])

    ### format data ###
    for x in data:
        # get year, month from "start" value
        x["year"] = x["start"][:4]
        x["month"] = calendar.month_abbr[int(x["start"][5:7])]

        # remove start, end, package
        del x["start"]
        del x["end"]
        del x["package"]
    
    # remove empty months
    data = removeEmptyMonths(data)

    return data

# get pypi download stats for the package name
def getHistoricPypiData(name, start_dates, end_dates):
    data = []
    client = bigquery.Client()

    # get the number of downloads per month
    query_job = client.query("""
        SELECT
        COUNT(*) AS num_downloads,
        SUBSTR(_TABLE_SUFFIX, 1, 6) AS `month`
        FROM `the-psf.pypi.downloads*`
        WHERE
        file.project =""" + 
        "'%s'" % (name) + 
        """
        AND _TABLE_SUFFIX
            BETWEEN FORMAT_DATE(
            '%Y%m01', DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH))
            AND FORMAT_DATE('%Y%m%d', CURRENT_DATE())
        GROUP BY `month`
        """
    )

    results = query_job.result()  
    for row in results:
        data.append({
            "month": row.month,
            "downloads": row.num_downloads,
            "package": name
        })
        

    return data

# get manually downloaded pypi donwload stats for the package name
def getManualHistoricPypiData(name):
    path = "" + str(os.getcwd()) + "\\" + name + ".csv"
    data = []
    with open(path, encoding="utf8") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0

        # making a dict, formatL {name: url}
        for row in csv_reader:
            # header
            if line_count == 0: 
                line_count += 1

            # body
            data.append({
                "year": row["month"][:4],
                "month": calendar.month_abbr[int(row["month"][4:])],
                "downloads":row["num_downloads"],
            })
                                        
    return data

# get anaconda download stats for the package name
def getHistoricAnacData(name):
    start_month = "2017-01" # data starts jan 2017 for this api
    end_month = "2020-02" # today.strftime("%Y-%m")
    
    # returns a series - transform to data frame
    df = overall(name.lower(), start_month=start_month, end_month=end_month, monthly=True).to_frame()

    # formatting data
    data = []
    # getting months
    months = [x[1] for x in list(df.index)]
    for i in range(0, df.size):
        data.append({
            "year": months[i][:4],
            "month": calendar.month_abbr[int(months[i][5:])],
            "downloads":int(df.iloc[i].counts),
        })

    return data


if __name__ == "__main__":
    package_dict = readDownloadLinks()
    data = {}
    for name in package_dict:
        if "bioconductor" in package_dict[name]:
            # get data
            ret_data = getHistoricBiocData(name)
            data[name] = ret_data

        elif "cran" in package_dict[name]:
            # getting start and end dates
            start_year = 2005 #TODO: change based on paul getting the year of each package
            ret = getStartEndDates(start_year)
            start_dates = ret["start"]
            end_dates = ret["end"]
            ret_data = getHistoricCranData(name, start_dates, end_dates)
            data[name] = ret_data

        elif "pypi" in package_dict[name]:
            # IMPORTANT: we are allowed 1TB of querying per month.
            #           each query is about 475GB
            #           best bet is to run the sql queries manually
            #           in the gbq console
            #           but this one _might_ get the data as well
            # ret_data = getHistoricPypiData(name, start_dates, end_dates)
            ret_data = getManualHistoricPypiData(name)
            data[name] = ret_data

        elif "anaconda" in package_dict[name]:
            ret_data = getHistoricAnacData(name)
            data[name] = ret_data
        else:
            data[name] = []

    # writing json to file
    json_str = json.dumps(data)
    f = open("historic_data.json", "w")
    f.write(json_str)
    f.close()

            
