from google.cloud import bigquery

client = bigquery.Client()

query_job = client.query("""
    SELECT
	  COUNT(*) AS num_downloads,
	  SUBSTR(_TABLE_SUFFIX, 1, 6) AS `month`
	FROM `the-psf.pypi.downloads*`
	WHERE
	  file.project =""" + 
      "'%s'" % ("pytest") + 
      """
	  AND _TABLE_SUFFIX
	    BETWEEN FORMAT_DATE(
	      '%Y%m01', DATE("2018-04-01 00:00:00"))
	    AND FORMAT_DATE('%Y%m%d', DATE("2018-04-30 23:59:59"))
	GROUP BY `month`


""")

results = query_job.result()  # Waits for job to complete.
for row in results:
    print("{} downloads".format(row.num_downloads))

    