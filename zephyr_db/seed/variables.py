from zephyr_db import zephyr_db_session
from zephyr_db.models import Variable
from .utils import seed_table



VARIABLES = [{'name':'wind speed','unit':'wind speed'}]

def seed_variables(**VARIABLES) -> None :
    seed_table(Variable, VARIABLES)

