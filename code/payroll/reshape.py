"""
reshape.py — Step 3 of the pipeline: the same numbers, turned sideways.
 
Long to wide with `pivot_table`, wide back to long with `melt`.
"""
 
import pandas as pd
 
 
def hours_grid(history: pd.DataFrame) -> pd.DataFrame:
    """Employees down the side, weeks across the top, hours in the cells."""
    grid = history.pivot_table(
        index=["employee_id", "display_name"],
        columns="week_ending",
        values="hours_worked",
        aggfunc="sum",
        fill_value=0,
    )
    return grid.reset_index().rename_axis(columns=None)
 
 
def missed_weeks(grid: pd.DataFrame) -> pd.DataFrame:
    """Every (employee, week) with zero hours in the grid — the weeks people missed."""
    long = grid.melt(
        id_vars=["employee_id", "display_name"],
        var_name="week_ending",
        value_name="hours_worked",
    )
    missed = long[long["hours_worked"] == 0]
    return missed.sort_values(["employee_id", "week_ending"]).reset_index(drop=True)
 
 
def pay_by_month(history: pd.DataFrame) -> pd.DataFrame:
    """Total gross pay by month (rows) and department (columns), to the cent."""
    table = history.pivot_table(
        index="month",
        columns="department",
        values="gross_pay",
        aggfunc="sum",
        fill_value=0.0,
    )
    return table.round(2).reset_index().rename_axis(columns=None)
 