import sys
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

from Test1.korean_holiday_calendar import KoreanHolidayCalendar


class HolidayCalendarWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Korean Holiday Calendar")

        self.calendar = KoreanHolidayCalendar()

        self.info_label = QLabel()
        self.info_label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.calendar)
        layout.addWidget(self.info_label)

        self.calendar.currentPageChanged.connect(self.on_page_changed)
        self.calendar.selectionChanged.connect(self.on_selection_changed)

        self.on_page_changed(self.calendar.yearShown(), self.calendar.monthShown())

    def update_holiday_list(self, year, month):
        try:
            items = []
            holiday_map = self.calendar.load_holidays_for_year(year)
            for holiday_date, name in sorted(holiday_map.items()):
                if holiday_date.month == month:
                    items.append(f"{holiday_date.isoformat()} - {name}")
        except Exception as exc:
            self.info_label.setText(f"Failed to load holidays: {exc}")
            return

        if items:
            self.info_label.setText("Holidays this month:\n" + "\n".join(items))
        else:
            self.info_label.setText("No holidays in this month.")

    def on_page_changed(self, year, month):
        self.update_holiday_list(year, month)

    def on_selection_changed(self):
        qdate = self.calendar.selectedDate()
        self.update_holiday_list(qdate.year(), qdate.month())


def main():
    app = QApplication(sys.argv)
    widget = HolidayCalendarWindow()
    widget.resize(520, 520)
    widget.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
