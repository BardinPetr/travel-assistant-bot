from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv(), verbose=True)


def get_tg_token():
    return os.getenv("TG_TOKEN")


def get_apiai_token():
    return os.getenv("APIAI_TOKEN")
