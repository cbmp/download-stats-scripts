import csv
import requests
import os
import datetime
import calendar
import operator
import json
import pypistats
from condastats.cli import overall, pkg_platform, pkg_version, pkg_python, data_source
from google.cloud import bigquery

# IMPORTANT: get updated software and webapp csvs from paul
# BEFORE YOU RUN/WHEN SWITCHING VENVS:
# make sure dlStats.json has the most up-to-date data
# 
# > pip install requests 
# > pip install --upgrade google-cloud-bigquery
# > pip install pypistats <- or python -m pip install pypistats
# > pip install google-cloud-bigquery
# IF WINDOWS: > choco install miniconda3 
#               switch to miniconda venv in VSCode
#             > conda install -c conda-forge condastats
#               install the rest of the packages with pip
# IF MAC:   install anaconda
#         > conda install -c conda-forge condastats
#
# If that doesn't work, switch to conda environment and only run anaconda stuff (comment out other code)
# Switch back to python environment and run everything other than conda
#
# FOR PYPI: If you need another GBQ credentials file, follow this guide for GBQ: https://github.com/ofek/pypinfo
## up until step 10 (moving credential JSON file)
# IMPORTANT:
# Follow this guide to set up the credentials in your PATH/env variable. Example: 
## https://cloud.google.com/bigquery/docs/reference/libraries
# $env:GOOGLE_APPLICATION_CREDENTIALS="C:\Users\chant\Documents\GitHub\download-stats-scripts\pypiv3-1b463de8d1b0.json"
# export GOOGLE_APPLICATION_CREDENTIALS="/Users/chantalho/Documents/GitHub/download-stats-scripts/pypiv3-1b463de8d1b0.json"
#
# Change the file path name based on OS
### if Windows: \\software.csv, \\dlStats.json
### if Mac/Linux: /software.csv, /dlStats.json
#

### UTILS ###
# reads the software csv into a usable dict
def readDownloadLinks():
    path = "" + str(os.getcwd()) + "/software.csv"
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

# make all str
def makeAllStr(data):
    for item in data:
        for statItem in item["stats"]:
            statItem["downloads"] = str(statItem["downloads"])
    
    return data
### END UTILS ###

# get bioconductor download stats for the package name
def getBiocData(name, year, month):
    # changing month from num to str
    month = calendar.month_abbr[month]
    url = "https://bioconductor.org/packages/stats/bioc/%s/%s_%s_stats.tab" % (name, name, year)
    response = requests.get(url).text

    ### FORMAT DATA ###
    # separating into arrays
    lines = response.split('\n') 
    res_data = [x.split('\t') for x in lines]

    # header is Year / Month / Nb_of_distinct_IPs / Nb_of_downloads
    # cut the header out
    res_data.pop(0)

    # iterate and put into array
    for row in res_data:
        if row[0] == str(year) and row[1] == month:
            return {
                "year": str(row[0]),
                "month": row[1], 
                "downloads": str(row[3]),
            }

# get  cran download stats for the package name
def getCranData(name, year, month):
    date = str(year) + "-" + "%02d" % month
    end_date = str(year) + "-" + "%02d" % month + "-" + str(calendar.monthrange(int(year), int(month))[1])
    # iterate over every month from start_year
    url = "https://cranlogs.r-pkg.org/downloads/total/%s-01:%s/%s" % (date, end_date, name)
    data = requests.get(url).json()[0]

    ### format data ###
    # get year, month from "start" value
    data["year"] = str(year)
    data["month"] = calendar.month_abbr[month]

    # parse downloads to str for consistency
    data["downloads"] = str(data["downloads"])

    # remove start, end, package
    del data["start"]
    del data["end"]
    del data["package"]

    return data

# get pypi download stats for the package name
def getPypiData(name, year, month):
    client = bigquery.Client()

    # get the number of downloads per month
    query_job = client.query("""
        SELECT
        COUNT(*) AS num_downloads,
        SUBSTR(_TABLE_SUFFIX, 1, 6) AS `month`
        FROM `the-psf.pypi.downloads*`
        WHERE
        file.project =""" + 
        "'%s'" % (name.lower()) + 
        """
        AND _TABLE_SUFFIX
            BETWEEN FORMAT_DATE(
            '%Y%m01', DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH))
            AND FORMAT_DATE('%Y%m%d', CURRENT_DATE())
        GROUP BY `month`
        """
    )

    results = query_job.result() 
    for row in results:
        if row["month"][:4] == str(year) and row["month"][4:] == "%02d" % month:
            return {
                "month": calendar.month_abbr[month],
                "downloads": str(row["num_downloads"]),
                "year": str(year)
            }

# get anaconda download stats for the package name
def getAnacData(name, year, month):
    date = "%d-%02d" % (year, month-1)
    
    # returns a series - transform to data frame
    df = overall(name.lower(), month=date).to_frame()

    return {
        "year": str(year),
        "month": calendar.month_abbr[month],
        "downloads":str(df.iloc[0].counts),
    }

if __name__ == "__main__":
    package_dict = readDownloadLinks()
    year = datetime.datetime.today().year # 2020
    month = datetime.datetime.today().month-1 # 6

    data = None
   
    # get json from data file
    path = "" + str(os.getcwd()) + "/dlStats.json"
    with open(path) as f:
        data = json.load(f)

    for item in data:
        name = item["name"]
        print(name)
        ret_data = None
        if "bioconductor" in package_dict[name]:
            print("bioc")
            ret_data = getBiocData(name, year, month)

        if "cran" in package_dict[name]:
            print("cran")
            ret_data = getCranData(name, year, month)

        if "pypi" in package_dict[name]:
            print("pypi")
            ret_data = getPypiData(name, year, month)

        # WARNING: anaconda data for last month isn't updated until a few days after
        #          the first day of the month. Might give an error.
        if "anaconda" in package_dict[name]:
            print("anac")
            ret_data = getAnacData(name, year, month)

        print(ret_data)

    	# add data to json
        if ret_data != None:
            item["stats"].append(ret_data)

    json_str = json.dumps(data)
    f = open("new_data_temp2.json", "w")
    f.write(json_str)
    f.close()
    


        


   

            
