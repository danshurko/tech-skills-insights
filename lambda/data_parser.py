from datetime import date, datetime, timedelta

import boto3
import emoji
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests
import s3fs
from bs4 import BeautifulSoup

BASE_URL = "https://djinni.co/api/jobs/"
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('DatesTable')


def fetch_all_jobs(categories, start_date, end_date):
    all_jobs = []
    for category in categories:
        all_jobs.extend(fetch_jobs_by_category(category, start_date, end_date))
    return all_jobs


def fetch_jobs_by_category(category, start_date, end_date):
    all_jobs = []
    parameters = {"offset": 0, "category": category}

    while True:
        response = requests.get(BASE_URL, params=parameters)
        if response.status_code != 200:
            break
        data = response.json()
        limit = data.get("limit", 10)
        parameters["offset"] += limit
        jobs = data.get("results", [])

        for job in jobs:
            published_date = datetime.fromisoformat(job["published"]).date()
            if published_date < start_date:
                return all_jobs
            elif published_date <= end_date:
                result = {
                    "id": job["id"],
                    "title": job["title"],
                    "slug": job["slug"],
                    "company": job["company_name"],
                    "description": clean_text(job["long_description"]),
                    "category": category,
                    "location": job["location"],
                    "experience": job["experience"],
                    "english": job["english"]["name"],
                    "domain": job["domain"],
                    "date": published_date,
                    "dou_link": job["dou_link"],
                    "public_salary_min": job["public_salary_min"],
                    "public_salary_max": job["public_salary_max"],
                    "is_parttime": job["is_parttime"],
                    "has_test": job["has_test"],
                    "is_ukraine_only": job["is_ukraine_only"]
                }
                all_jobs.append(result)

    return all_jobs


def clean_text(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    text = soup.get_text(separator=" ").strip()
    clean_text = emoji.replace_emoji(text, "")
    return clean_text


def save_jobs_to_s3(df, bucket_name, prefix='djinni'):
    table = pa.Table.from_pandas(df)
    s3 = s3fs.S3FileSystem()

    pq.write_to_dataset(
        table,
        root_path=f"s3://{bucket_name}/{prefix}/",
        partition_cols=["date"],
        filesystem=s3
    )


def get_last_date():
    response = table.get_item(Key={'Name': 'last_file_date'})
    last_date = response.get('Item', {}).get('Date', None)

    if last_date is None:
        return date(1970, 1, 1)

    return date.fromisoformat(last_date)


def lambda_handler(event, context):
    bucket = "jobtrends-data"

    start = get_last_date()
    end = date.today() - timedelta(days=1)

    table.put_item(Item={
        'Name': 'last_file_date',
        'Date': date.today().isoformat()
    })

    categories = event.get("categories")
    all_jobs = fetch_all_jobs(categories, start, end)

    if all_jobs:
        df = pd.DataFrame(all_jobs)
        save_jobs_to_s3(df, bucket)

    return {'statusCode': 200}
