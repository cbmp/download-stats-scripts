import csv
import os
import scholarly
import json

# BEFORE YOU RUN/WHEN SWITCHING VENVS:
#
# 
#
# Change the file path name based on OS
### if Windows: \\software.csv
### if Mac/Linux: /software.csv

# RUN for both software and webapps

### UTILS ###
# reads the software csv into a usable dict
def readNames():
    path = '' + str(os.getcwd()) + '\\software.csv'
    with open(path, encoding='utf8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0

        # making a dict, formatL {name: url}
        package_dict = {}
        for row in csv_reader:
            # header
            if line_count == 0: 
                line_count += 1

            # body
            package_dict[row['name']] = {
                'scholar_link': row['scholar_link'],
                'citation': row['citation']
            }
                                        
        return package_dict

### END UTILS ###

# get cited by, and title to make sure it's the right publication
def getCitedBy(pdict):
    cited_by = {}
    for key in pdict:
        # if there is no google scholar link (then no cited by)
        if pdict[key]['scholar_link'] == '' or pdict[key]['citation'] == '':
            cited_by[key] = {
                'title': '',
                'cited': 0,
            }
            print(key, "has no google scholar link/citation.")
        else:
            item = scholarly.search_pubs_query(pdict[key]['citation'])
            
            try:
                # go to the first item in the iteration
                item = next(item) 
               
                # if there's a citedby               
                if hasattr(item, 'citedby'):
                    cited_by[key] = {
                        'title': item.bib['title'],
                        'cited': item.citedby
                    }
                    print('Iteration done of', key, '-', item.bib['title'])
                else:
                    cited_by[key] = {
                        'title': '',
                        'cited': 0,
                    }
                    print('Iteration done of', key, ': has no citations')
            # if there is nothing that matches the result
            except StopIteration:
                cited_by[key] = {
                    'title': '',
                    'cited': 0,
                }
                print(key, "has no findings.")
    return cited_by


if __name__ == '__main__':
    package_dict = readNames()
    cited_dict = getCitedBy(package_dict)

    # changing format of data to [{name: CREAM, cited: 0} , ...]
    new_data = []
    for key in cited_dict:
        new_data.append({
            'name': key,
            'cited': str(cited_dict[key]['cited'])
        })

     # writing to file
    json_str = json.dumps(new_data)
    f = open("gs_software_stats.json", "w") 
    f.write(json_str)
    f.close()
    
   
    

            
