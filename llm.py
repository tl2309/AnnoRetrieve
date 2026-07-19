# llm.py
import openai
import time
from config import Config

def init_chatgpt(api_key):
    openai.api_key = api_key

def ask_completion_with_retry(messages, model, max_tokens=1000, n=1, stop=None, temperature=0, retries=3, delay=5):
    if Config.USE_MOCK_LLM:
        # Mock response for testing
        return "mock_value"
    attempt = 0
    while attempt < retries:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                n=n,
                stop=stop,
                temperature=temperature
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            print(f"LLM error: {e}. Retrying in {delay}s...")
            attempt += 1
            time.sleep(delay)
    raise Exception(f"Failed after {retries} retries.")

def ask_sample_file(sql_query, sql_query_description, text):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"""
        Given the SQL query and its description, extract all attributes from the text.
        If an attribute is not found, leave it empty.
        Return each attribute and its value in the format:
        [attribute1]: [value1]
        [attribute2]: [value2]
        ...
        SQL: {sql_query}
        Description: {sql_query_description}
        Text: {text[:3000]}
        """}
    ]
    return ask_completion_with_retry(messages, model="gpt-4o", max_tokens=1000)

def ask_extract_attribute(attribute, text):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"""
        Extract the value of '{attribute}' from the following text.
        Return only the value, nothing else.
        Text: {text[:2000]}
        """}
    ]
    return ask_completion_with_retry(messages, model="gpt-4o", max_tokens=50, temperature=0)