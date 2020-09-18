from pvmon.analyse import (
    analyse_data_consecutive_days_multi_sensor,
    analyse_data_consecutive_days_single_sensor,
    load_data_for_multi_sensor_projects,
    load_data_for_single_sensor_projects,
    transform_data_for_multi_sensor_projects,
    transform_data_for_single_sensor_projects,
)

from .context import pvmon

data = '/home/alexclaydon/dev/projects/pvmon/tests/resources/test_data.csv'


def test_load_data_for_multi_sensor_projects():
    df = load_data_for_multi_sensor_projects(data)
    columns = [
        'project_id', 'project_name', 'sensor_num',
        'sensor_id', 'location', 'observation_date',
        'total_prod_kwh', 'total_sold_kwh', 'sale_type'
    ]
    for column in columns:
        assert column in df.columns


def test_load_data_for_single_sensor_projects():
    df = load_data_for_single_sensor_projects(data)
    columns = [
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
    for column in columns:
        assert column in df.columns


def test_analyse_data_consecutive_days_multi_sensor():
    df = transform_data_for_multi_sensor_projects(
        load_data_for_multi_sensor_projects(data)
    )
    result = analyse_data_consecutive_days_multi_sensor(df, 3)
    assert "ＳＡＮＣＯＮ１ / S01" in result[0]
    assert ('ＳＡＮＣＯＮ１', '2020/08/14') in result[0]["ＳＡＮＣＯＮ１ / S01"]
    assert ('ＳＡＮＣＯＮ１', '2020/08/15') in result[0]["ＳＡＮＣＯＮ１ / S01"]
    assert ('ＳＡＮＣＯＮ１', '2020/08/16') in result[0]["ＳＡＮＣＯＮ１ / S01"]


def test_analyse_data_consecutive_days_single_sensor():
    df = transform_data_for_single_sensor_projects(
        load_data_for_single_sensor_projects(data)
    )
    result = analyse_data_consecutive_days_single_sensor(df, 3)
    assert "ＣＡＳａｗａｊｉ / S01" in result[0]
    assert ('ＣＡＳａｗａｊｉ', '2020/08/14') in result[0]["ＣＡＳａｗａｊｉ / S01"]
    assert ('ＣＡＳａｗａｊｉ', '2020/08/15') in result[0]["ＣＡＳａｗａｊｉ / S01"]
    assert ('ＣＡＳａｗａｊｉ', '2020/08/15') in result[0]["ＣＡＳａｗａｊｉ / S01"]
