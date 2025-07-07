import ast
import json
import os
from datetime import date, timedelta

import boto3
import pandas as pd
import s3fs
from openai import OpenAI

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('DatesTable')
s3 = boto3.client("s3")

api_key = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)


def extract_keywords(job_description):
    """
    Uses OpenAI API to extract key skills and technologies from a job description.
    Returns a list of keywords exactly as they appear in the text.
    """
    prompt = f"""
    Extract only the most relevant technical skills, technologies, and programming-related terms from the following job description.
    Ignore general soft skills, company details, and non-technical terms.

    Only include specific programming languages, frameworks, libraries, databases, cloud platforms, and tools commonly used in software development.

    - Keep the names exactly as they appear in the text, without corrections or formatting changes.
    - Remove duplicates.
    - Provide only the list of keywords in a valid Python list format.

    Job description:
    {job_description}

    Response format: a Python list containing only the keywords.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3  # Low temperature ensures structured and relevant output
    )

    # Get the response content
    keywords_text = response.choices[0].message.content.strip()

    # Remove possible code block markers
    start = keywords_text.index('[')
    end = keywords_text.index(']') + 1
    keywords_text = keywords_text[start:end]

    try:
        keywords = ast.literal_eval(keywords_text.strip())  # Safely parse Python list
        if isinstance(keywords, list):
            return keywords
        else:
            return []
    except Exception as e:
        print(f"Error parsing response: {e}")
        return []


def get_last_date():
    response = table.get_item(Key={'Name': 'last_key_date'})
    last_date = response.get('Item', {}).get('Date', None)

    if last_date is None:
        return date(1970, 1, 1)

    return date.fromisoformat(last_date)


def process_all_files(start_date, end_date):
    bucket_name = "jobtrends-data"
    folder_prefix = "djinni/"

    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix, Delimiter="/")
    folders = [prefix["Prefix"] for prefix in response.get("CommonPrefixes", [])]

    for folder in folders:
        folder_date = date.fromisoformat(folder.split("=")[1][:-1])
        if start_date <= folder_date <= end_date:
            response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder)
            file_name = response["Contents"][0]["Key"]

            df = get_dataframe_from_file(file_name)
            save_keywords(df, folder)


def get_dataframe_from_file(file_name):
    bucket_name = "jobtrends-data"
    s3_path = f"s3://{bucket_name}/{file_name}"

    fs = s3fs.S3FileSystem()
    df = pd.read_parquet(s3_path, filesystem=fs)

    return df


def save_keywords(df, folder):
    bucket_name = "jobtrends-data"
    file_name = "keywords.json"

    data = {}
    for index, row in df.iterrows():
        job_description = row['description']
        job_id = row['id']
        keywords = extract_keywords(job_description)
        data[job_id] = keywords

    json_data = json.dumps(data)
    s3_key = folder + file_name

    s3.put_object(Bucket=bucket_name, Key=s3_key, Body=json_data)


def lambda_handler(event, context):
    start = get_last_date()
    end = date.today() - timedelta(days=1)

    table.put_item(Item={
        'Name': 'last_key_date',
        'Date': date.today().isoformat()
    })

    process_all_files(start, end)

    return {"statusCode": 200}
