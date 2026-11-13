from drafter import *
from dataclasses import dataclass
from bakery import assert_equal


# -----------------------------------------
# WEBSITE INFORMATION
# -----------------------------------------

set_site_information(
    author="chasbd@udel.edu",
    description="A construction site timesheet tracker that "
                "records worker hours and summarizes labor.",
    sources="Drafter documentation and CS1 course materials.",
    planning= "CBD - CS1 Final Project - Design.docx" "CBD - CS1 Final Project - Pick a Problem.docx",
    links=["https://github.com/chasbd-ud/construction-timesheet-tracker"]
)

hide_debug_information()
set_website_title("Construction Site Timesheet Tracker")
set_website_framed(False)


# -----------------------------------------
# CONSTANTS
# -----------------------------------------

TRADES = [
    "Carpenter",
    "Electrician",
    "Laborer",
    "Operator"
]


# -----------------------------------------
# DATA CLASSES
# -----------------------------------------

@dataclass
class TimesheetEntry:
    """
    Stores the recorded hours for one construction worker.
    """
    worker_name: str
    trade: str
    hours_per_day: float
    days_worked: int
    total_hours: float


@dataclass
class State:
    """
    Stores all information for the active construction timesheet.

    Attributes:
        entries: List of worker timesheet entries.
        site_name: Name of the construction project.
        pay_period: Current timesheet period.
        error_message: Feedback displayed to the user.
    """
    entries: list[TimesheetEntry]
    site_name: str
    pay_period: str
    error_message: str


# -----------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------

def calculate_total_hours(
    hours_per_day: float,
    days_worked: int
) -> float:
    """
    Calculates the total hours worked by one employee.
    """
    return hours_per_day * days_worked


def calculate_site_hours(
    entries: list[TimesheetEntry]
) -> float:
    """
    Calculates the combined hours for the entire construction site.
    """
    total = 0.0

    for entry in entries:
        total += entry.total_hours

    return total


def calculate_trade_hours(
    entries: list[TimesheetEntry],
    selected_trade: str
) -> float:
    """
    Calculates the total hours recorded for one construction trade.
    """
    total = 0.0

    for entry in entries:
        if entry.trade == selected_trade:
            total += entry.total_hours

    return total


def is_valid_hours(value: str) -> bool:
    """
    Checks whether hours are a positive number no greater than 24.

    Allows whole numbers and decimal values.
    """
    if not value:
        return False

    if value.count(".") > 1:
        return False

    parts = value.split(".")

    for part in parts:
        if part and not part.isdigit():
            return False

    if not parts[0]:
        return False

    hours = float(value)

    if hours <= 0 or hours > 24:
        return False

    return True


def make_entry(
    worker_name: str,
    trade: str,
    hours: float,
    days: int
) -> TimesheetEntry:
    """
    Creates a timesheet entry and calculates its total hours.
    """
    total = calculate_total_hours(hours, days)

    return TimesheetEntry(
        worker_name,
        trade,
        hours,
        days,
        total
    )


# -----------------------------------------
# HOME DASHBOARD
# -----------------------------------------

@route
def index(state: State) -> Page:
    """
    Displays the main construction timesheet dashboard.
    """
    total_workers = len(state.entries)
    total_hours = calculate_site_hours(state.entries)

    return Page(
        state,
        [
            Header("Construction Site Timesheet Tracker"),
            "Welcome to your construction workforce dashboard!",
            HorizontalRule(),

            Header("Project Information", 2),
            "Construction Site: " + state.site_name,
            "Timesheet Period: " + state.pay_period,

            Header("Workforce Overview", 2),
            "Worker Entries: " + str(total_workers),
            "Total Labor Hours: " + str(total_hours),

            HorizontalRule(),

            Header("Navigation", 2),
            Button("Project Setup", "setup_route"),
            Button("Add Worker Entry", "add_entry_route"),
            Button("View Timesheets", "view_entries_route"),
            Button("Trade Summary", "trade_summary_route"),
            Button("Help & Instructions", "help_route"),
        ]
    )


# -----------------------------------------
# PROJECT SETUP
# -----------------------------------------

@route
def setup_route(state: State) -> Page:
    """
    Displays the form for entering project information.
    """
    return Page(
        state,
        [
            Header("Project Setup"),
            "Enter the information for your construction project.",

            "Construction Site Name:",
            TextBox("site_name", state.site_name),

            "Timesheet Period:",
            TextBox("pay_period", state.pay_period),

            Button("Save Project Information", "save_setup"),
            Button("Back to Dashboard", "index")
        ]
    )


@route
def save_setup(
    state: State,
    site_name: str,
    pay_period: str
) -> Page:
    """
    Saves the construction site and timesheet period.
    """
    if not site_name.strip():
        state.error_message = "Please enter a construction site name."

    elif not pay_period.strip():
        state.error_message = "Please enter a timesheet period."

    else:
        state.site_name = site_name.strip()
        state.pay_period = pay_period.strip()
        state.error_message = ""

    return Page(
        state,
        [
            Header("Project Setup"),
            state.error_message,
            Button("Return to Dashboard", "index"),
            Button("Edit Project Information", "setup_route")
        ]
    )


# -----------------------------------------
# ADD WORKER ENTRY
# -----------------------------------------

@route
def add_entry_route(state: State) -> Page:
    """
    Displays the form for recording a worker's hours.
    """
    return Page(
        state,
        [
            Header("Add Worker Timesheet Entry"),
            "Enter the worker's information below.",

            "Worker Name:",
            TextBox("worker_name", ""),

            "Construction Trade:",
            SelectBox("trade", TRADES, TRADES[0]),

            "Hours Worked Per Day:",
            TextBox("hours_per_day", "8"),

            "Number of Days Worked:",
            TextBox("days_worked", "5"),

            Button("Submit Timesheet", "submit_entry"),
            Button("Back to Dashboard", "index")
        ]
    )


@route
def submit_entry(
    state: State,
    worker_name: str,
    trade: str,
    hours_per_day: str,
    days_worked: str
) -> Page:
    """
    Validates worker information and adds a timesheet entry.
    """
    worker_name = worker_name.strip()

    if not worker_name:
        state.error_message = "Please enter the worker's name."

    elif trade not in TRADES:
        state.error_message = "Please select a valid construction trade."

    elif not is_valid_hours(hours_per_day):
        state.error_message = "Hours must be greater than 0 and no more than 24."

    elif not days_worked.isdigit() or int(days_worked) <= 0:
        state.error_message = "Days worked must be a positive whole number."

    else:
        hours = float(hours_per_day)
        days = int(days_worked)

        new_entry = make_entry(
            worker_name,
            trade,
            hours,
            days
        )

        state.entries.append(new_entry)
        state.error_message = "Timesheet entry successfully added!"

    return Page(
        state,
        [
            Header("Timesheet Submission"),
            state.error_message,
            Button("Add Another Worker", "add_entry_route"),
            Button("View All Entries", "view_entries_route"),
            Button("Return Home", "index")
        ]
    )


# -----------------------------------------
# VIEW TIMESHEET ENTRIES
# -----------------------------------------

@route
def view_entries_route(state: State) -> Page:
    """
    Displays all recorded worker timesheet entries.
    """
    content = [
        Header("Recorded Timesheet Entries"),
        "Construction Site: " + state.site_name,
        "Timesheet Period: " + state.pay_period,
        HorizontalRule()
    ]

    if not state.entries:
        content.append("No worker entries have been recorded yet.")

    else:
        table_data = []

        for index, entry in enumerate(state.entries):
            table_data.append([
                entry.worker_name,
                entry.trade,
                str(entry.hours_per_day),
                str(entry.days_worked),
                str(entry.total_hours),
                Button(
                    "Delete",
                    "delete_entry",
                    Argument("index", index)
                )
            ])

        content.append(
            Table([
                [
                    "Worker",
                    "Trade",
                    "Hours/Day",
                    "Days",
                    "Total Hours",
                    "Action"
                ]
            ] + table_data)
        )

        content.append(
            "Total Site Hours: " +
            str(calculate_site_hours(state.entries))
        )

    content.append(Button("Add Worker", "add_entry_route"))
    content.append(Button("Back to Dashboard", "index"))

    return Page(state, content)


# -----------------------------------------
# DELETE TIMESHEET ENTRY
# -----------------------------------------

@route
def delete_entry(state: State, index: int) -> Page:
    """
    Removes a selected timesheet entry from the list.
    """
    if index >= 0 and index < len(state.entries):
        removed_worker = state.entries[index].worker_name
        state.entries.pop(index)

        state.error_message = (
            removed_worker + "'s entry was successfully removed."
        )

    else:
        state.error_message = "That timesheet entry could not be found."

    return Page(
        state,
        [
            Header("Manage Timesheet Entries"),
            state.error_message,
            Button("View Remaining Entries", "view_entries_route"),
            Button("Return Home", "index")
        ]
    )


# -----------------------------------------
# TRADE SUMMARY
# -----------------------------------------

@route
def trade_summary_route(state: State) -> Page:
    """
    Calculates and displays labor hour totals for each trade.
    """
    content = [
        Header("Construction Trade Summary"),
        "Labor hours organized by construction trade.",
        HorizontalRule()
    ]

    if not state.entries:
        content.append("There are currently no timesheet entries.")

    else:
        summary_data = []

        for trade in TRADES:
            trade_hours = calculate_trade_hours(
                state.entries,
                trade
            )

            summary_data.append([
                trade,
                str(trade_hours)
            ])

        content.append(
            Table([
                ["Construction Trade", "Total Hours"]
            ] + summary_data)
        )

        content.append(HorizontalRule())

        content.append(
            Header(
                "Total Site Labor Hours: " +
                str(calculate_site_hours(state.entries)),
                2
            )
        )

        content.append(
            "Total Worker Entries: " + str(len(state.entries))
        )

    content.append(Button("View All Workers", "view_entries_route"))
    content.append(Button("Back to Dashboard", "index"))

    return Page(state, content)


# -----------------------------------------
# HELP PAGE
# -----------------------------------------

@route
def help_route(state: State) -> Page:
    """
    Explains how to use the construction timesheet tracker.
    """
    return Page(
        state,
        [
            Header("Help & Instructions"),

            Header("1. Set Up Your Project", 2),
            "Enter your construction site name and timesheet period.",

            Header("2. Add Worker Information", 2),
            "Enter the worker's name, construction trade, "
            "hours worked per day, and number of days worked.",

            Header("3. Review Timesheets", 2),
            "View all recorded worker entries and their "
            "calculated total hours.",

            Header("4. Review Trade Summaries", 2),
            "See the combined labor hours for Carpenters, "
            "Electricians, Laborers, and Operators.",

            Header("5. Correct Mistakes", 2),
            "Use the Delete button to remove an incorrect entry.",

            HorizontalRule(),

            Header("Important Information", 2),
            "This website records manually entered labor hours. "
            "It does not calculate official payroll, taxes, "
            "benefits, or overtime.",

            Button("Return to Dashboard", "index")
        ]
    )


# -----------------------------------------
# UNIT TESTS
# -----------------------------------------

# Test the total hours calculation.

assert_equal(calculate_total_hours(8.0, 5), 40.0)
assert_equal(calculate_total_hours(10.0, 4), 40.0)
assert_equal(calculate_total_hours(6.5, 3), 19.5)


# Test the site-wide hours calculation.

test_entries = [
    TimesheetEntry("John", "Carpenter", 8.0, 5, 40.0),
    TimesheetEntry("Sarah", "Electrician", 8.0, 4, 32.0),
    TimesheetEntry("Mike", "Carpenter", 6.0, 5, 30.0)
]

assert_equal(calculate_site_hours(test_entries), 102.0)


# Test the trade summary calculation.

assert_equal(
    calculate_trade_hours(test_entries, "Carpenter"),
    70.0
)

assert_equal(
    calculate_trade_hours(test_entries, "Electrician"),
    32.0
)

assert_equal(
    calculate_trade_hours(test_entries, "Operator"),
    0.0
)


# Test input validation.

assert_equal(is_valid_hours("8"), True)
assert_equal(is_valid_hours("7.5"), True)
assert_equal(is_valid_hours("0"), False)
assert_equal(is_valid_hours("-5"), False)
assert_equal(is_valid_hours("25"), False)
assert_equal(is_valid_hours("abc"), False)


# -----------------------------------------
# START WEBSITE
# -----------------------------------------

initial_state = State(
    entries=[],
    site_name="Construction Timesheet Tracker",
    pay_period="Current Pay Period",
    error_message=""
)

start_server(initial_state)
