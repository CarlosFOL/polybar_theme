from datetime import datetime, time
from db.wdb_DAO import WeatherDB


def run():
    """
    Get the weather data for my current date and time.
    """
    # 1) Get my current datetime.
    now = datetime.now()
    date_part = now.date().strftime("%Y-%m-%d")
    time_part = time(now.hour, 0, 0).strftime("%H:%M:%S")

    # 2) Use them to retrieve the weather data.
    db = WeatherDB()
    wdata = db.execute_query(sql_keys=("WObservation", "Get"), parameters=(date_part, time_part), read=True)

if __name__ == "__main__":
    run()
