from liblogger.legacy import local_logger
import pandas as pd
import pytest


@pytest.fixture(scope='function')
def example_fixture():
    local_logger.info("Setting Up Example Fixture...")
    yield
    local_logger.info("Tearing Down Example Fixture...")




dataframe = pd.DataFrame(
    columns=['project_id', 'project_name', 'sensor_num', 'sensor_id', 'location', 'observation_date', 'total_prod_kwh', 'total_sold_kwh', 'sale_type'],
)
