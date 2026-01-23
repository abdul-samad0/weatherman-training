import argparse
import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Optional


@dataclass
class WeatherReading:
    """
    Stores weather data for a single day.
    """

    date: date
    max_temp: Optional[int]
    min_temp: Optional[int]
    max_humidity: Optional[int]
    mean_humidity: Optional[int]


@dataclass
class DailyReport:
    """
    Stores daily temperature data for reporting.
    """

    day: int
    max_temp: Optional[int]
    min_temp: Optional[int]


def safe_int(value):
    """
    Convert value to integer safely.
    """
    if not value:
        return None
    try:
        value = value.strip()
        number = int(value)
        return number
    except (ValueError, AttributeError):
        return None


class WeatherFileParser:
    """
    Reads weather files and creates WeatherReading objects.
    """

    def find_weather_files(self, directory: Path, year: int):
        """
        Find all weather files for a given year in the directory.
        """
        return list[Path](directory.glob("*" + str(year) + "*.txt"))

    def parse_file(self, file_path: Path):
        """
        Parse a single weather file and return a list of WeatherReading objects.
        """
        readings = []

        with open(file_path, "r", encoding="utf-8", errors="ignore", newline="") as file_handle:
            file_reader = csv.reader(file_handle)

            is_header = True

            for row in file_reader:
                # skip header
                if is_header:
                    is_header = False
                    continue

                # skip empty or broken rows
                if len(row) < 9:
                    continue

                if not row[0]:
                    continue

                try:
                    reading_date = datetime.strptime(row[0].strip(), "%Y-%m-%d").date()
                except ValueError:
                    continue

                max_temp = safe_int(row[1])
                min_temp = safe_int(row[3])
                max_humidity = safe_int(row[7])
                mean_humidity = safe_int(row[8])

                reading = WeatherReading(
                    reading_date, max_temp, min_temp, max_humidity, mean_humidity
                )

                readings.append(reading)

        return readings

    def parse_files(self, directory, year):
        """
        Find and parse all weather files for a given year.
        """
        readings = []
        weather_files = self.find_weather_files(directory, year)

        for file in weather_files:
            file_readings = self.parse_file(file)
            readings.extend(file_readings)

        return readings


class WeatherCalculator:
    """
    Calculates yearly and monthly weather statistics.
    """

    def calculate_yearly(self, yearly_readings):
        highest_temp = None
        highest_temp_date = None

        lowest_temp = None
        lowest_temp_date = None

        highest_humidity = None
        highest_humidity_date = None

        for report in yearly_readings:
            if report.max_temp is not None:
                if highest_temp is None or report.max_temp > highest_temp:
                    highest_temp = report.max_temp
                    highest_temp_date = report.date
            if report.min_temp is not None:
                if lowest_temp is None or report.min_temp < lowest_temp:
                    lowest_temp = report.min_temp
                    lowest_temp_date = report.date
            if report.max_humidity is not None:
                if highest_humidity is None or report.max_humidity > highest_humidity:
                    highest_humidity = report.max_humidity
                    highest_humidity_date = report.date

        result = {}
        result["highest_temp"] = (highest_temp, highest_temp_date)
        result["lowest_temp"] = (lowest_temp, lowest_temp_date)
        result["highest_humidity"] = (highest_humidity, highest_humidity_date)

        return result

    def calculate_monthly_averages(self, reports, year, month):
        """
        Calculates monthly averages for a given year and month.
        """
        total_max = 0
        total_min = 0
        total_humidity = 0

        count_max = 0
        count_min = 0
        count_humidity = 0

        for report in reports:
            if report.date.year != year or report.date.month != month:
                continue

            if report.max_temp is not None:
                total_max += report.max_temp
                count_max += 1

            if report.min_temp is not None:
                total_min += report.min_temp
                count_min += 1

            if report.mean_humidity is not None:
                total_humidity += report.mean_humidity
                count_humidity += 1

        if count_max > 0:
            average_max = total_max / count_max
        else:
            average_max = None

        if count_min > 0:
            average_min = total_min / count_min
        else:
            average_min = None

        if count_humidity > 0:
            average_humidity = total_humidity / count_humidity
        else:
            average_humidity = None

        return average_max, average_min, average_humidity

    def calculate_daily_reports(self, monthly_each_day_reports, year, month):
        """
        Calculates daily reports for a given year and month.
        """
        daily_reports = []
        for report in monthly_each_day_reports:
            if report.date.year != year or report.date.month != month:
                continue

            daily_reports.append(
                DailyReport(report.date.day, report.max_temp, report.min_temp)
            )

        daily_reports.sort(key=lambda x: x.day)
        return daily_reports


class WeatherReport:
    """
    Prints weather reports.
    """

    def __init__(self):
        self.RED = "\033[31m"
        self.BLUE = "\033[34m"
        self.RESET = "\033[0m"

    def print_yearly_report(self, stats):
        high_temp, high_date = stats["highest_temp"]
        low_temp, low_date = stats["lowest_temp"]
        humidity, humidity_date = stats["highest_humidity"]

        if high_temp is not None and high_date is not None:
            print("Highest:", str(high_temp) + "C on", high_date.strftime("%B %d"))
        else:
            print("Highest: No data available")

        if low_temp is not None and low_date is not None:
            print("Lowest:", str(low_temp) + "C on", low_date.strftime("%B %d"))
        else:
            print("Lowest: No data available")

        if humidity is not None and humidity_date is not None:
            print("Humidity:", str(humidity) + "% on", humidity_date.strftime("%B %d"))
        else:
            print("Humidity: No data available")

    def print_monthly_report(self, average_max, average_min, average_humidity):
        print("Highest Average:", str(average_max) + "C")
        print("Lowest Average:", str(average_min) + "C")
        print("Average Mean Humidity:", str(average_humidity) + "%")

    def print_daily_report(self, daily_reports, year, month):
        month_name = datetime(year, month, 1).strftime("%B")
        print(f"Monthly Report for {month_name} {year}")
        for daily_report in daily_reports:
            if daily_report.max_temp is not None:
                max_bar = "*" * abs(daily_report.max_temp)
                print(daily_report.day, self.RED + max_bar + self.RESET, str(daily_report.max_temp) + "C")

            if daily_report.min_temp is not None:
                min_bar = "*" * abs(daily_report.min_temp)
                print(daily_report.day, self.BLUE + min_bar + self.RESET, str(daily_report.min_temp) + "C")

    def print_bonus_bar_chart(self, daily_reports, year, month):
        """
        Prints a bonus bar chart for a given year and month.
        """

        month_name = datetime(year, month, 1).strftime("%B")
        print(month_name, year)

        for daily_report in daily_reports:
            day_str = str(daily_report.day).zfill(2)

            max_bar = ""
            min_bar = ""

            if daily_report.max_temp is not None:
                max_bar = "+" * abs(daily_report.max_temp)

            if daily_report.min_temp is not None:
                min_bar = "+" * abs(daily_report.min_temp)

            print(
                day_str,
                self.RED + max_bar + self.RESET,
                self.BLUE + min_bar + self.RESET,
                str(daily_report.min_temp) + "C - " + str(daily_report.max_temp) + "C",
            )


def main():
    parser = argparse.ArgumentParser(description="Weather Man")
    parser.add_argument("path", help="Path to weather files directory")
    parser.add_argument(
        "-e", "--year", dest="target_year", type=int, help="Year for yearly report (e.g., 2021)"
    )
    parser.add_argument(
        "-a", "--average", dest="year_month_for_average", 
        help="Year/Month for monthly averages (e.g., 2021/3)"
    )
    parser.add_argument(
        "-c", "--monthly-report", dest="year_month_for_monthly_report",
        help="Year/Month for monthly daily report (e.g., 2021/3)"
    )
    parser.add_argument(
        "-b", "--bonus", dest="year_month_for_bonus",
        help="Year/Month for bonus bar chart (e.g., 2021/3)"
    )

    args = parser.parse_args()

    directory = Path(args.path)

    file_parser = WeatherFileParser()
    calculator = WeatherCalculator()
    reporter = WeatherReport()

    if args.target_year is not None:
        yearly_reports: list[WeatherReading] = file_parser.parse_files(directory, args.target_year)

        if len(yearly_reports) == 0:
            print("No data found for yearly report.")
        else:
            stats = calculator.calculate_yearly(yearly_reports)
            reporter.print_yearly_report(stats)

    if args.year_month_for_average is not None:
        year_month = args.year_month_for_average.split("/")
        year = int(year_month[0])
        month = int(year_month[1])

        monthly_reports: list[WeatherReading] = file_parser.parse_files(directory, year)

        if len(monthly_reports) == 0:
            print("No data found for monthly averages.")
        else:
            avg_max, avg_min, avg_humidity = calculator.calculate_monthly_averages(
                monthly_reports, year, month
            )
            reporter.print_monthly_report(avg_max, avg_min, avg_humidity)

    if args.year_month_for_monthly_report is not None:
        year_month = args.year_month_for_monthly_report.split("/")
        year = int(year_month[0])
        month = int(year_month[1])

        monthly_each_day_reports: list[WeatherReading] = file_parser.parse_files(directory, year)

        if len(monthly_each_day_reports) == 0:
            print("No data found for daily report.")
        else:
            daily_reports: list[DailyReport] = calculator.calculate_daily_reports(
                monthly_each_day_reports, year, month
            )
            reporter.print_daily_report(daily_reports, year, month)

    if args.year_month_for_bonus is not None:
        year_month = args.year_month_for_bonus.split("/")
        year = int(year_month[0])
        month = int(year_month[1])

        monthly_reports: list[WeatherReading] = file_parser.parse_files(directory, year)

        if len(monthly_reports) == 0:
            print("No data found for bonus report.")
        else:
            daily_reports: list[DailyReport] = calculator.calculate_daily_reports(
                monthly_reports, year, month
            )
            reporter.print_bonus_bar_chart(daily_reports, year, month)


if __name__ == "__main__":
    main()
