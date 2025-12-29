import argparse
import csv
from datetime import datetime
from pathlib import Path


class WeatherReading:
    """
    Stores weather data for a single day.
    """

    def __init__(self, date, max_temp, min_temp, max_humidity, mean_humidity):
        self.date = date
        self.max_temp = max_temp
        self.min_temp = min_temp
        self.max_humidity = max_humidity
        self.mean_humidity = mean_humidity


def safe_int(value):
    """
    Convert value to integer safely.
    """
    try:
        value = value.strip()
        number = int(value)
        return number
    except:
        return None


class WeatherFileParser:
    """
    Reads weather files and creates WeatherReading objects.
    """

    def parse_files(self, directory, year):
        readings = []

        weather_files = directory.glob("*" + str(year) + "*.txt")

        for file in weather_files:
            print("Processing file:", file)

            file_handle = open(file, "r", encoding="utf-8", errors="ignore")
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

                try:
                    reading_date = datetime.strptime(row[0].strip(), "%Y-%m-%d").date()
                except:
                    continue

                max_temp = safe_int(row[1])
                min_temp = safe_int(row[3])
                max_humidity = safe_int(row[7])
                mean_humidity = safe_int(row[8])

                reading = WeatherReading(
                    reading_date, max_temp, min_temp, max_humidity, mean_humidity
                )

                readings.append(reading)

            file_handle.close()

        return readings


class WeatherCalculator:
    """
    Calculates yearly and monthly weather statistics.
    """

    def calculate_yearly(self, yearly_weather_report):
        highest_temp = None
        highest_temp_date = None

        lowest_temp = None
        lowest_temp_date = None

        highest_humidity = None
        highest_humidity_date = None

        for report in yearly_weather_report:
            print(
                "Checking:",
                report.date,
                report.max_temp,
                report.min_temp,
                report.max_humidity,
            )
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
            print(
                "Checking:",
                report.date,
                report.max_temp,
                report.min_temp,
                report.mean_humidity,
            )

            if report.date.year == year and report.date.month == month:
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
            if report.date.year == year and report.date.month == month:
                daily_reports.append(
                    (report.date.day, report.max_temp, report.min_temp)
                )

        daily_reports.sort(key=lambda x: x[0])
        return daily_reports


class WeatherReport:
    """
    Prints weather reports.
    """

    def print_yearly_report(self, stats):
        high_temp, high_date = stats["highest_temp"]
        low_temp, low_date = stats["lowest_temp"]
        humidity, humidity_date = stats["highest_humidity"]

        print("Highest:", str(high_temp) + "C on", high_date.strftime("%B %d"))
        print("Lowest:", str(low_temp).zfill(2) + "C on", low_date.strftime("%B %d"))
        print("Humidity:", str(humidity) + "% on", humidity_date.strftime("%B %d"))

    def print_monthly_report(self, average_max, average_min, average_humidity):
        print("Highest Average:", str(average_max) + "C")
        print("Lowest Average:", str(average_min) + "C")
        print("Average Mean Humidity:", str(average_humidity) + "%")

    def print_daily_report(self, daily_reports, year, month):
        RED = "\033[31m"
        BLUE = "\033[34m"
        month_name = datetime(year, month, 1).strftime("%B")
        print(f"Monthly Report for {month_name} {year}")
        for day, max_temp, min_temp in daily_reports:
            if max_temp is not None:
                max_bar = "*" * max_temp
                print(day, RED + max_bar, str(max_temp) + "C")

            if min_temp is not None:
                min_bar = "*" * min_temp
                print(day, BLUE + min_bar, str(min_temp) + "C")


def main():
    parser = argparse.ArgumentParser(description="Weather Man")
    parser.add_argument("path", help="Path to weather files directory")
    parser.add_argument("-e", "--year", type=int)
    parser.add_argument("-a", "--average")
    parser.add_argument("-c", "--monthly-report")

    args = parser.parse_args()

    directory = Path(args.path)

    file_parser = WeatherFileParser()
    calculator = WeatherCalculator()
    reporter = WeatherReport()

    if args.year:
        yearly_reports = file_parser.parse_files(directory, args.year)

        if len(yearly_reports) == 0:
            print("No data found.")
            return

        stats = calculator.calculate_yearly(yearly_reports)
        reporter.print_yearly_report(stats)

    elif args.average:
        year_month = args.average.split("/")
        year = int(year_month[0])
        month = int(year_month[1])

        monthly_reports = file_parser.parse_files(directory, year)

        if len(monthly_reports) == 0:
            print("No data found.")
            return

        avg_max, avg_min, avg_humidity = calculator.calculate_monthly_averages(
            monthly_reports, year, month
        )

        reporter.print_monthly_report(avg_max, avg_min, avg_humidity)

    elif args.monthly_report:
        monthly_report_each_day = args.monthly_report.split("/")
        year = int(monthly_report_each_day[0])
        month = int(monthly_report_each_day[1])

        monthly_each_day_reports = file_parser.parse_files(directory, year)

        if len(monthly_each_day_reports) == 0:
            print("No data found")
            return

        daily_reports = calculator.calculate_daily_reports(
            monthly_each_day_reports, year, month
        )
        reporter.print_daily_report(daily_reports, year, month)


if __name__ == "__main__":
    main()
