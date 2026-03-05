import pandas as pd
from .facts import add_facts

def assemble(df: pd.DataFrame) -> pd.DataFrame:
    return add_facts(df)
