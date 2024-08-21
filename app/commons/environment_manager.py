from dotenv import load_dotenv
from app.commons.logger import logger
import os

def load_env() :
    load_dotenv()
    env = os.getenv("ENV")
    if (env == "dev") : 
        logger.info("Running on dev environment")
        load_dotenv("dev.env")
    elif (env == "prod") :
        logger.info("Running on prod environment")
        load_dotenv("prod.env")