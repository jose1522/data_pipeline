from typing import Optional

import pandas as pd
from sqlalchemy.engine import Engine

from db.models import engine as default_engine


def quarterly_hires(year: int, engine: Optional[Engine] = None) -> pd.DataFrame:
    """Returns a dataframe of quarterly hires for a given year."""
    query = f"""
    SELECT
        d.department as department_name,
        j.job as job_title,
        concat('Q',EXTRACT(QUARTER FROM datetime)) AS quarter,
        COUNT(*) AS employee_count
    FROM
        public.user u
        inner join public.department d on u.department_id = d.id
        inner join public.job j on u.job_id = j.id
    WHERE
        EXTRACT(YEAR FROM datetime) = {year}
    GROUP BY
        department_name, job_title, EXTRACT(QUARTER FROM datetime)
    ORDER BY
        department_name, job_title, EXTRACT(QUARTER FROM datetime)  
    """
    engine = engine or default_engine
    data = pd.read_sql_query(query, engine)
    df_pivot = data.pivot(
        index=["department_name", "job_title"],
        columns="quarter",
        values="employee_count",
    ).reset_index()

    # Fill NaNs with 0 if needed
    df_pivot.fillna(0, inplace=True)
    return df_pivot


def department_hires(year: int, engine: Optional[Engine] = None) -> pd.DataFrame:
    """Returns a dataframe of departmental hires above the global mean for a given year.
    Args:
        year: The year to filter on.
        engine: The database engine to use. Defaults to the default engine.
    Returns:
        A dataframe of quarterly hires for a given year.
    """
    query = f"""
    SELECT d.id as id, d.department as department, COUNT(*) as hired
    FROM public.user u inner join public.department d on d.id = u.department_id
    WHERE EXTRACT(YEAR FROM u.datetime) = {year}
    GROUP BY d.id, d.department;
    """
    engine = engine or default_engine
    data = pd.read_sql_query(query, engine)

    mean_hires = data["hired"].mean()

    # Filter departments that hired more than the mean
    result_df = data[data["hired"] > mean_hires]

    # Sort by number of employees hired in descending order
    result_df = result_df.sort_values("hired", ascending=False)
    return result_df
