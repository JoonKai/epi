from PySide6.QtCore import QDate
from PySide6.QtGui import QBrush, QColor, QFont, QTextCharFormat
from PySide6.QtWidgets import QCalendarWidget

try:
    from holidayskr.core import get_holidays
    HOLIDAYS_IMPORT_ERROR = None
except Exception as exc:
    get_holidays = None
    HOLIDAYS_IMPORT_ERROR = exc


class KoreaCalendar(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGridVisible(True)

        self._holiday_format = QTextCharFormat()
        self._holiday_format.setForeground(QBrush(QColor("#b00020")))
        self._holiday_format.setBackground(QBrush(QColor("#fde8e8")))
        font = QFont()
        font.setBold(True)
        self._holiday_format.setFont(font)

        self._formatted_dates = []
        self._holiday_cache = {}

        self.currentPageChanged.connect(self.on_page_changed)
        self.on_page_changed(self.yearShown(), self.monthShown())

    def load_holidays_for_year(self, year):
        if year in self._holiday_cache:
            return self._holiday_cache[year]
        if get_holidays is None:
            raise RuntimeError(f"holidayskr import failed: {HOLIDAYS_IMPORT_ERROR}")
        holidays = get_holidays(year)
        holiday_map = {holiday_date: name for holiday_date, name in holidays}
        self._holiday_cache[year] = holiday_map
        return holiday_map

    def clear_formats(self):
        for qdate in self._formatted_dates:
            self.setDateTextFormat(qdate, QTextCharFormat())
        self._formatted_dates = []

    def apply_holiday_formats(self, year):
        self.clear_formats()
        holiday_map = self.load_holidays_for_year(year)
        for holiday_date in holiday_map:
            qdate = QDate(holiday_date.year, holiday_date.month, holiday_date.day)
            self.setDateTextFormat(qdate, self._holiday_format)
            self._formatted_dates.append(qdate)

    def on_page_changed(self, year, month):
        self.apply_holiday_formats(year)

    def holiday_name(self, qdate):
        holiday_map = self.load_holidays_for_year(qdate.year())
        key = qdate.toPython()
        return holiday_map.get(key)
