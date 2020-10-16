import pandas as pd
from pvmon.logger import local_logger

# TODO: To be refactored to make use of a validation library


def load_data_for_multi_sensor_projects(file):
    cols = [0, 1, 2, 3, 4, 5, 7, 9, 25]
    colnames = [
        "project_id",
        "project_name",
        "sensor_num",
        "sensor_id",
        "location",
        "observation_date",
        "total_prod_kwh",
        "total_sold_kwh",
        "sale_type",
    ]
    df = pd.read_csv(
        filepath_or_buffer=file,
        usecols=cols,
        header=0,
        names=colnames,
        encoding="utf_8",
    )
    return df


def load_data_for_single_sensor_projects(file):
    cols = [0, 1, 2, 3, 4, 5, 7, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 23, 24, 25]
    colnames = [
        "project_id",
        "project_name",
        "sensor_num",
        "sensor_id",
        "location",
        "observation_date",
        "total_prod_kwh",
        "total_sold_kwh",
        "pcs#01_kwh",
        "pcs#02_kwh",
        "pcs#03_kwh",
        "pcs#04_kwh",
        "pcs#05_kwh",
        "pcs#06_kwh",
        "pcs#07_kwh",
        "pcs#08_kwh",
        "pcs#09_kwh",
        "restricted_time",
        "restricted_amount (%)",
        "sale_type",
    ]
    df = pd.read_csv(
        filepath_or_buffer=file,
        usecols=cols,
        header=0,
        names=colnames,
        encoding="utf_8",
    )
    return df


def relabel_data(df, replacements_dict):
    # for key, value in replacements_dict.items():
    #     for subkey, subvalue in value.items():
    #         df[key] = df[key].str.replace(subkey, subvalue)
    return df


def transform_data_for_multi_sensor_projects(df):
    """
    :param df: pandas data frame outputted by load_data()
    :return: data frame correctly pivoted for use with any of the analyse_...() functions
    """
    indexNames = df[df['sensor_num'] == 'EIGセンサー01'].index
    df.drop(indexNames, inplace=True)
    pivot_df = df.pivot_table(
        values="total_prod_kwh",
        index=["project_name", "observation_date"],
        columns="sensor_num",
    )
    pivot_df["aggregate_kwh"] = pivot_df["センサー01"] + pivot_df["センサー02"] + pivot_df["センサー03"]
    pivot_df["S01"] = pivot_df["センサー01"] / pivot_df["aggregate_kwh"]
    pivot_df["S02"] = pivot_df["センサー02"] / pivot_df["aggregate_kwh"]
    pivot_df["S03"] = pivot_df["センサー03"] / pivot_df["aggregate_kwh"]
    return pivot_df


def transform_data_for_single_sensor_projects(df):
    df = df[
        ~df["pcs#01_kwh"].isnull()
    ]
    pivot_df = df.pivot_table(
        values=[
            "total_prod_kwh",
            "pcs#01_kwh",
            "pcs#02_kwh",
            "pcs#03_kwh",
            "pcs#04_kwh",
            "pcs#05_kwh",
            "pcs#06_kwh",
            "pcs#07_kwh",
            "pcs#08_kwh",
            "pcs#09_kwh",
        ],
        index=[
            "project_name",
            "observation_date"
        ],
    )
    pivot_df["S01"] = pivot_df["pcs#01_kwh"] / pivot_df["total_prod_kwh"]
    pivot_df["S02"] = pivot_df["pcs#02_kwh"] / pivot_df["total_prod_kwh"]
    pivot_df["S03"] = pivot_df["pcs#03_kwh"] / pivot_df["total_prod_kwh"]
    pivot_df["S04"] = pivot_df["pcs#04_kwh"] / pivot_df["total_prod_kwh"]
    pivot_df["S05"] = pivot_df["pcs#05_kwh"] / pivot_df["total_prod_kwh"]
    pivot_df["S06"] = pivot_df["pcs#06_kwh"] / pivot_df["total_prod_kwh"]
    pivot_df["S07"] = pivot_df["pcs#07_kwh"] / pivot_df["total_prod_kwh"]
    pivot_df["S08"] = pivot_df["pcs#08_kwh"] / pivot_df["total_prod_kwh"]
    pivot_df["S09"] = pivot_df["pcs#09_kwh"] / pivot_df["total_prod_kwh"]
    return pivot_df


def analyse_data_single_days(df, days: int):
    # TODO: Fix the mean() calculation at 30 days rather than, if given, using a larger number of samples
    """
    :param df: pandas data frame outputted by transform_data()
    :param days: the number of days in the window ending at today's date to check for the occurrence of the trigger condition (i.e. within which the trigger must occur), which condition is itself determined by the logic embodied in the result variable
    :return: tuple consisting of (i) a dict at element[0] containing the relevant records meeting the trigger condition and (ii) a float at element[1] being the mean() for the data embodied in the sensor variable; this tuple is then fed directly into notify()
    """
    records = {}
    for project in df.index.get_level_values(0).unique():
        select = df.loc[df.index.get_level_values(0).isin([project])]
        if days > len(select.index):
            local_logger.warning(
                f"days parameter passed (days={days}) was greater than number of records available ({len(select.index)}); reducing days parameter accordingly"
            )
            days = len(select.index)
        cols = ["S01", "S02", "S03"]
        for col in cols:
            sensor = select[col]
            key = (abs(sensor - sensor.mean())) > (sensor.mean() * 0.20)
            result = round(sensor.tail(days)[key.tail(days)] * 100, ndigits=2)
            if result.any():
                records[project + " / " + col] = result.to_dict()
                records[project + " / " + col]["mean"] = round(
                    sensor.mean() * 100, ndigits=2
                )
    local_logger.info("Downloaded data successfully analysed")
    return records, days


def analyse_data_consecutive_days_multi_sensor(df, days: int):
    # TODO: Fix the mean() calculation at 30 days rather than, if given, using a larger number of samples
    """
    Calculation method taken from https://stackoverflow.com/questions/59836303/select-rows-where-3-consecutive-values-match-condition-python-pandas
    :param df: pandas data frame outputted by transform_data()
    :param days: the number of days in the window ending at today's date to check for the occurrence of the trigger condition (i.e. within which the trigger must occur), which condition is itself determined by the logic embodied in the result variable
    :return: tuple consisting of (i) a dict at element[0] containing the relevant records meeting the trigger condition and (ii) a float at element[1] being the mean() for the data embodied in the sensor variable; this tuple is then fed directly into notify()
    """
    records = {}
    for project in df.index.get_level_values(0).unique():
        select = df.loc[df.index.get_level_values(0).isin([project])]
        if days > len(select.index):
            local_logger.warning(
                f"days parameter passed (days={days}) was greater than number of records available ({len(select.index)}); reducing days parameter accordingly"
            )
            days = len(select.index)
        cols = ["S01", "S02", "S03"]
        for col in cols:
            sensor = select[col]
            key = sensor.gt((abs(sensor - sensor.mean())) < (sensor.mean() * 0.20))
            intermed = (~key).cumsum()[key]
            result = sensor.tail(days)[
                intermed.map(intermed.value_counts())
                .ge(2)
                .reindex(sensor.index, fill_value=False)
            ]
            # NB if you remove the .tail(days) from sensor, it will return the whole series instead of just the window period; good to remember for debugging
            if result.any():
                records[project + " / " + col] = result.to_dict()
                records[project + " / " + col]["mean"] = round(
                    sensor.mean() * 100, ndigits=2
                )
    local_logger.info("Downloaded data successfully analysed")
    return records, days


def analyse_data_consecutive_days_single_sensor(df, days: int):
    records = {}
    for project in df.index.get_level_values(0).unique():
        select = df.loc[df.index.get_level_values(0).isin([project])]
        if days > len(select.index):
            local_logger.warning(
                f"days parameter passed (days={days}) was greater than number of records available ({len(select.index)}); reducing days parameter accordingly"
            )
            days = len(select.index)
        cols = [
            "S01", "S02", "S03",
            "S04", "S05", "S06",
            "S07", "S08", "S09",
        ]
        for col in cols:
            sensor = select[col]
            key = sensor.gt((abs(sensor - sensor.mean())) < (sensor.mean() * 0.20))
            intermed = (~key).cumsum()[key]
            result = sensor.tail(days)[
                intermed.map(intermed.value_counts())
                    .ge(2)
                    .reindex(sensor.index, fill_value=False)
            ]
            # NB if you remove the .tail(days) from sensor, it will return the whole series instead of just the window period; good to remember for debugging
            if result.any():
                records[project + " / " + col] = result.to_dict()
                records[project + " / " + col]["mean"] = round(
                    sensor.mean() * 100, ndigits=2
                )
    local_logger.info("Downloaded data successfully analysed")
    return records, days


# NB: In connection with the above function, the following are the settings for pivoting the downloaded production data in LibreCalc:
# Row fields: project name and observation date
# Column fields: data (pre-existing) and sensor number
# Data fields: sum - energy produced
