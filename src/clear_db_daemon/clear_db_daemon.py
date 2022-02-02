import logging
import os
import sys
from datetime import datetime, timedelta
from time import sleep

import pytz
from dotenv import dotenv_values
from pymongo import MongoClient

if __name__ == "__main__":
    config = dotenv_values(".env")
    logger = logging.getLogger("CLEAR_DB_DAEMON")
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

    db_name: str = config["MONGO_INITDB_DATABASE"]
    collection_name: str = "claim-data"
    delay_sec_raw: str = os.environ.get("DELAY_SEC")
    delay_sec: int = 60 * 60 * 2 \
        if (delay_sec_raw is None) or (delay_sec_raw.isdigit() is False)\
        else int(delay_sec_raw)
    logger.info(f"Delay seconds: {delay_sec}")

    data_lifetime_h_raw: str = os.environ.get("DATA_LIFETIME_H")
    data_lifetime_h: int = 2 \
        if (data_lifetime_h_raw is None) or (data_lifetime_h_raw.isdigit() is False) \
        else int(data_lifetime_h_raw)
    logger.info(f"Data lifetime: {data_lifetime_h}")

    mongo_config: dict = {
        "host": config["MONGO_HOST"],
        "port": int(config["MONGO_PORT"]),
        "username": config["MONGO_INITDB_USERNAME"],
        "password": config["MONGO_INITDB_PASSWORD"],
        "authSource": db_name,
        "authMechanism": "SCRAM-SHA-256"
    }

    while True:
        logger.info("Start processing expired claim data.")
        date_threshold: datetime = datetime.utcnow().replace(tzinfo=pytz.UTC) - timedelta(hours=data_lifetime_h)
        logger.info(f"Date threshold: {date_threshold}.")

        with MongoClient(**mongo_config) as mongo_client:
            expired_records = list(mongo_client[db_name][collection_name] \
                                   .find({"created": {'$lt': date_threshold}}))

            logger.info(f"Found {len(expired_records)} expired records.")
            for record in expired_records:
                mongo_client[db_name][collection_name].delete_one({"_id": record["_id"]})

        logger.info(f"Sleep for {delay_sec} seconds until next iteration.")
        sleep(delay_sec)
