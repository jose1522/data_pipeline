from unittest import mock

import pandas
import pandas as pd

from reports.user import quarterly_hires, department_hires

mock_quarterly_data = pd.DataFrame(
    {
        "department_name": ["HR", "Engineering"],
        "job_title": ["Manager", "Developer"],
        "quarter": ["Q1", "Q2"],
        "employee_count": [5, 10],
    }
)

mock_department_data = pd.DataFrame(
    {"id": [1, 2], "department": ["HR", "Engineering"], "hired": [5, 10]}
)


@mock.patch.object(pandas, "read_sql_query", return_value=mock_quarterly_data)
def test_quarterly_hires(mock_read_sql_query):
    df = quarterly_hires(year=2021)
    assert "department_name" in df.columns
    assert "job_title" in df.columns
    assert df.shape == (2, 4)  # 2 rows, 4 columns
    assert mock_read_sql_query.called


@mock.patch.object(pandas, "read_sql_query", return_value=mock_department_data)
def test_department_hires(mock_read_sql_query):
    df = department_hires(year=2021)
    assert "id" in df.columns
    assert "department" in df.columns
    assert "hired" in df.columns
    assert df.shape == (1, 3)  # 1 row, 3 columns (only Engineering is above the mean)
    assert mock_read_sql_query.called
