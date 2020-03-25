import csv
import requests
import os

# BEFORE YOU RUN:
# > pip install requests 
# Change the file path name based on OS
### if Windows: \\software.csv
### if Mac/Linux: /software.csv

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

def getBiocData(package_dict, name):
    url = "https://bioconductor.org/packages/stats/bioc/%s/%s_stats.tab" % (name, name)
    response = requests.get(url)
    return response.text

def getCranData(package_dict, name):
    url = "https://cranlogs.r-pkg.org/downloads/total/last-month/%s" % (name)
    response = requests.get(url)
    print(response.text)
    return response.text

def getPypiData(package_dict, name):
    return 

def getAnacData(package_dict, name):
    return


if __name__ == "__main__":
    package_dict = readDownloadLinks()
    for name in package_dict:
        data = []
        if "bioconductor" in package_dict[name]:
            # get data
            data = getBiocData(package_dict, name)

            # TODO: format data
        elif "cran" in package_dict[name]:
            data = getCranData(package_dict, name)
        elif "pypi" in package_dict[name]:
            data = getPypiData(package_dict, name)
        elif "anaconda" in package_dict[name]:
            data = getAnacData(package_dict, name)
        else:
            data = "none"

            
