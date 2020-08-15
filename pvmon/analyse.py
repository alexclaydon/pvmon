from liblogger.legacy import local_logger
import pandas as pd


# TODO: To be refactored to make use of a validation library


def load_data(file):
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


def relabel_data(df, replacements_dict):
    # for key, value in replacements_dict.items():
    #     for subkey, subvalue in value.items():
    #         df[key] = df[key].str.replace(subkey, subvalue)
    return df


def transform_data(df):
    """
    :param df: pandas data frame outputted by load_data()
    :return: data frame correctly pivoted for use with any of the analyse_...() functions
    """
    pivot_df = df.pivot_table(
        values="total_prod_kwh",
        index=["project_name", "observation_date"],
        columns="sensor_num",
    )
    pivot_df = pivot_df[
        ~pivot_df["センサー02"].isnull()
    ]  # Removes all rows where there is no sensor data for sensor 02 (being, at least on the basis of all the data I've seen to date, those projects which do not break out individual sensor data)
    pivot_df["aggregate_kwh"] = pivot_df["センサー01"] + pivot_df["センサー02"] + pivot_df["センサー03"]
    pivot_df["S01"] = pivot_df["センサー01"] / pivot_df["aggregate_kwh"]
    pivot_df["S02"] = pivot_df["センサー02"] / pivot_df["aggregate_kwh"]
    pivot_df["S03"] = pivot_df["センサー03"] / pivot_df["aggregate_kwh"]
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


def analyse_data_consecutive_days(df, days: int):
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


# NB: In connection with the above function, the following are the settings for pivoting the downloaded production data in LibreCalc:
# Row fields: project name and observation date
# Column fields: data (pre-existing) and sensor number
# Data fields: sum - energy produced
