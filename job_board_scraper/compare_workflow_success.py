import os
import sys
import logging
import boto3
import psycopg2
from scrapy.crawler import CrawlerProcess
from job_board_scraper.utils.postgres_wrapper import PostgresWrapper
from scrapy.utils.project import get_project_settings

logger = logging.getLogger("ComparisonLogger")
logger.setLevel(logging.INFO)
process = CrawlerProcess(get_project_settings())
connection = psycopg2.connect(host=os.environ.get("PG_HOST"), user=os.environ.get("PG_USER"), password=os.environ.get("PG_PASSWORD"), dbname=os.environ.get("PG_DATABASE"))
time_to_check = sys.argv[1]
cursor = connection.cursor()
# Check all companies who had a posting since yesterday
cursor.execute(os.environ.get("COMPARISON_QUERY_EXPECTED"))
num_expected = cursor.fetchall()[0][0]
# Check all companies who were just scraped by scrapy
cursor.execute(os.environ.get("COMPARISON_QUERY_ACTUAL"), tuple([time_to_check, time_to_check]))
num_actual = cursor.fetchall()[0][0]
logger.info(f"Num Expected to Scrape: {num_expected}")
logger.info(f"Num Actually Scraped: {num_actual}")

if num_expected != num_actual:
    cursor.execute(os.environ.get("MISMATCHED_URL_QUERY"), tuple([time_to_check, time_to_check]))
    logger.warning(f"Mismatched URLs: {cursor.fetchall()}")
cursor.close()
connection.close()
assert num_expected == num_actual