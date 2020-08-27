# download-stats-scripts
For scraping the download stats for packages from Bioconductor, CRAN, PyPI, Anaconda.

Painfully documented and written by Chantal, so if you have any questions, please ask her.

## Structure
```
 |- credentials
 |---- credentials files for Google Analytics/Google Cloud Big Query
 |- data
 |---- data from the spreadsheets 
 |- misc
 |---- misc scripts and files (kept just in case)
 |- results
 |---- result data - copy all to CBMP's src/data folder
 |- scripts
 |---- run all scripts in here
```
## Script descriptions, instructions, and FAQ
**PLEASE READ BEFORE RUNNING ANYTHING.**
- **Links to spreadsheets with data:**
    - [Datasets](https://docs.google.com/spreadsheets/d/1Rjtpwff_ilJZOekWPzRPmBAqSlik-Mq0X7ggsT5XWCA/edit?usp=sharing)
    - [Software/Webapps](https://docs.google.com/spreadsheets/d/14-I6LTDXQ7Qtg3tkheZ2gLbbprkuuwc_KseldLROBoA/edit?usp=sharing)
- **New software package?**
    - Replace `/data/software.csv` with new data from the spreadsheet. Also replace it in CBMP's data folder `cbmp/src/data/`.
    - **Wait until the next month** to do the following:
        - Add the following code into the array in `/results/dlStats.json`:
        ```
        {
            "name": "<PACKAGE_NAME>",
            "stats": [],
            "lab": "<LAB_NAME>"
        }
        ```
        - Run `/scripts/lastMonthDataCollection.py` to replace the monthly download stats
            - You could also try making it work with `/misc/historicDataCollection.py` to get data from previous months but it might be too messy :)
        - Run `/scripts/gsCitedBy.py` to replace the cited-by data with the correct file name (`software.csv` and `/results/gsSoftwareStats.json`)      
- **New webapp?**
    - Replace `/data/webapps.csv` with new data from the spreadsheet. Also replace it in CBMP's data folder `cbmp/src/data/`.
    - Add the web app's name, view id from Google Analytics, and start date (when to start recording analytics data) to the arrays in the `/scripts/gaWebapps.py` script.
    - Run `/scripts/gaWebapps.py` to replace the monthly usage stats 
    - Run `/scripts/gsCitedBy.py` to replace the cited-by data with the correct file name (`/data/webapps.csv` and `/results/gsWebappStats.json`)    
- **New dataset?**
    - No need to run anything, just replace the data in CBMP's data folder `cbmp/src/data/`.
- **What do I do after I've run all the scripts?**
    - Take everything in `/results/`, and copy/replace the data in CBMP's data folder `cbmp/src/data/`.
- **When do I run all these scripts?**
    - First week of every month is when I typically run it. As long as you run it before the month ends.
    - Don't run it in the first few days - in `/scripts/lastMonthDataCollection.py`, there is a function to collect Anaconda data that uses a package called condastats. Condastats doesn't update their data until basically after the first week in my experience.
- **What the hell is going on / I don't understand what you're doing in this section of code / What does this error mean / Why is this so broken / Huh??**
    - Just message Chantal on slack
*** 

### lastMonthDataCollection
Collects a list of package names and their platforms from `/data/software.csv`, and then collects the number of downloads for the previous month and appends it to a master JSON file (`/results/dlStats.json`) of all downloads per month.

**Output:** `/results/dlStats.json`
#### Instructions
Try installing everything on an **anaconda venv**.
```bash
pip install requests 
pip install --upgrade google-cloud-bigquery
pip install pypistats
pip install google-cloud-bigquery
conda install -c conda-forge condastats
```

Before running the file, run:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="<YOUR_CURRENT_WORKING_DIRECTORY_PATH_HERE>/credentials/pypiv3-1b463de8d1b0.json"
```

Right now, the script is set up so that the new data is written to `/misc/new_data.json`. This is to quickly look over all the new data and make sure it's correct.

After you've ensured that it looks fine, replace `/results/dlStats.json` with the JSON from `new_data.json`.
*** 

### gaWebapps
Collects Google Analytics stats for all webapps.
**Output:** `/results/gaWebappsStats.json`
#### Instructions
No specific instructions other than to just run the script.

*** 

### gsCitedBy
Collects Google Scholar cited by stats for all packages that have a citation.
**Output:** `/results/gaWebappsStats.json`
#### Instructions
Depending on if you're running it for software or web apps, you might need to replace the file names in the script. More instructions under **New webapp/software?** above.

After a while, Google Scholar will block your IP because it doesn't allow scraping. More specifically, the package will start to produce an error saying `Exception: Cannot fetch the page from Google Scholar` which is a mighty helpful except that tells you absolutely nothing!

[Here is a link](https://github.com/scholarly-python-package/scholarly/issues/154) to a Github Issue thread about the error, and possibly setting up a proxy, and you can read how user Nicholas-Lewis-USDA basically skims over my comments and assumes a totally wrong understanding of what I was saying. My last comment links to threads to setting up a proxy.

*** 

### collabs
Collects publication lists for each PI in the list. Data is formatted into intersections in CBMP's scripts.
**Output:** `/results/collabStats.json`
#### Instructions
No specific instructions other than to just run the script.
