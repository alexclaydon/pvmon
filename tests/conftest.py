import random

import pandas as pd
import pytest
from liblogger.legacy import local_logger

source_ecomegane_test_data = {
    'project_id': random.sample(range(10, 30), 10),
    'project_name': ['proj'] * 10,
    'sensor_num': random.sample(range(10, 30), 10),
    'sensor_id': random.sample(range(10, 30), 10),
    'location': random.sample(range(10, 30), 10),
    'observation_date': random.sample(range(10, 30), 10),
    'total_prod_kwh': random.sample(range(10, 30), 10),
    'total_sold_kwh': random.sample(range(10, 30), 10),
    'sale_type': random.sample(range(10, 30), 10),
}


@pytest.fixture(scope='function')
def ecomegane_test_data():
    return pd.DataFrame(
        data=source_ecomegane_test_data,
    )
