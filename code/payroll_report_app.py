"""
payroll_report_app.py — the quarter at a glance, for someone who never opens a terminal.

Every Friday since September the office manager at Salt City Coffee has downloaded
a payroll export from the Assignment 04 app; before that she typed the same file
by hand. The owner now wants to know where the hours went this quarter, the
accountant wants pay by month and department, and the manager wants to see who
has been missing shifts. This page answers all three from the pile of exports.

Same shape as Assignment 04: the page *assembles* the pipeline — one call to
`build_history` does the cleaning — and then shows the reports, filtered by the
department and dates the user picks.

Run it:  Run and Debug -> "Streamlit Run: Current File"
Test it: pytest tests/test_pipeline.py -k app
"""
import streamlit as st
 
from payroll import (
    build_history,
    hours_grid,
    load_employees,
    load_export,
    missed_weeks,
    pay_by_month,
    summarize_employees,
)
 
st.title("Salt City Coffee — Quarterly Payroll Report")
st.write("Upload the weekly payroll exports to see hours, pay and missed shifts.")
 
roster = load_employees()
uploads = st.file_uploader(
    "Weekly payroll exports", type="csv", accept_multiple_files=True, key="exports"
)
 
if uploads:
    history = build_history([load_export(upload) for upload in uploads], roster)
 
    unmatched = history[history["department"].isna()]
    if not unmatched.empty:
        bad_ids = sorted(unmatched["employeeid"].str.strip().unique())
        st.warning(
            "These employeeids are not on the roster and are left out of the "
            f"reports: {', '.join(bad_ids)}"
        )
    history = history[history["department"].notna()]
 
    if history.empty:
        st.info("None of the uploaded rows match the roster.")
        st.stop()
 
    departments = ["All"] + sorted(history["department"].unique())
    department = st.selectbox("Department", departments, key="department")
 
    pay_days = history["pay_date"].dt.date
    first_day, last_day = pay_days.min(), pay_days.max()
    chosen = st.date_input(
        "Pay dates",
        value=(first_day, last_day),
        min_value=first_day,
        max_value=last_day,
        key="dates",
    )
    if len(chosen) != 2:
        st.info("Pick both a start and an end date.")
        st.stop()
    start, end = chosen
 
    keep = (history["pay_date"].dt.date >= start) & (history["pay_date"].dt.date <= end)
    if department != "All":
        keep = keep & (history["department"] == department)
    selected = history[keep]
 
    st.subheader(f"{department}: {start} to {end}")
    if selected.empty:
        st.info("No payroll rows for that selection.")
        st.stop()
 
    columns = st.columns(4)
    columns[0].metric("Weeks", f"{selected['week_ending'].nunique()}")
    columns[1].metric("Employees", f"{selected['employee_id'].nunique()}")
    columns[2].metric("Total hours", f"{selected['hours_worked'].sum():,.2f}")
    columns[3].metric("Total gross pay", f"${selected['gross_pay'].sum():,.2f}")
 
    monthly = pay_by_month(selected)
    st.bar_chart(monthly, x="month")
 
    st.dataframe(summarize_employees(selected))
    grid = hours_grid(selected)
    st.dataframe(grid)
    st.dataframe(missed_weeks(grid))
 
    st.download_button(
        "Download pay by month (CSV)",
        data=monthly.to_csv(index=False),
        file_name="pay_by_month.csv",
        mime="text/csv",
        key="download",
    )
