
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import calendar
import json

# pip install --upgrade google-api-python-client 
# pip install --upgrade oauth2client

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = 'ga-key-file.json'

def initialize_analyticsreporting():
  """Initializes an Analytics Reporting API V4 service object.

  Returns:
    An authorized Analytics Reporting API V4 service object.
  """
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      KEY_FILE_LOCATION, SCOPES)

  # Build the service object.
  analytics = build('analyticsreporting', 'v4', credentials=credentials)

  return analytics


def get_report(analytics, view_id, start_date):
  """Queries the Analytics Reporting API V4.

  Args:
    analytics: An authorized Analytics Reporting API V4 service object.
  Returns:
    The Analytics Reporting API V4 response.
  """
  return analytics.reports().batchGet(
    body={
      'reportRequests': [
        {
            'viewId': view_id,
            'dateRanges': [{'startDate': start_date, 'endDate': 'today'}],
            'metrics': [{'expression': 'ga:users'},{'expression': 'ga:pageviews'}],
            'dimensions': [{'name': 'ga:month'}, {'name': 'ga:nthMonth'}, {'name': 'ga:year'}],
            'orderBys': [{'fieldName': 'ga:year'}, {'fieldName': 'ga:month'}, {'fieldName': 'ga:nthMonth'}]
        }
      ]
    }
  ).execute()


def format_data(response, name):
    ret = {
        'name': name,
        'stats': []
    }
    data = response['reports'][0]['data']['rows']
    for item in data:
        ret['stats'].append({
            'pageviews': item['metrics'][0]['values'][1],
            'users': item['metrics'][0]['values'][0],
            'year': item['dimensions'][2],
            'month': calendar.month_abbr[int(item['dimensions'][0])],
        })
    return ret


if __name__ == "__main__":
    view_names = ['PharmacoDB', 'SYNERGxDB', 'ToxicoDB', 'XevaDB', 'Orcestra']
    view_ids = ['154809134', '217887541', '217861980', '217840729', '217856753']
    start_dates = ['2017-07-01', '2020-05-01', '2020-05-01', '2020-05-01', '2020-05-01']
    analytics = initialize_analyticsreporting()
    data = []
    for i in range(0,len(view_ids)):
        response = get_report(analytics, view_ids[i], start_dates[i])
        data.append(format_data(response, view_names[i])) 

    json_str = json.dumps(data)
    f = open("gaWebappsStats.json", "w") 
    f.write(json_str)
    f.close()