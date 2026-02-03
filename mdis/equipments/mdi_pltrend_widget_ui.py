# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mdi_pltrend_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QSizePolicy, QVBoxLayout, QWidget)

class Ui_PLTrend(object):
    def setupUi(self, PLTrend):
        if not PLTrend.objectName():
            PLTrend.setObjectName(u"PLTrend")
        PLTrend.resize(503, 353)
        self.verticalLayoutWidget = QWidget(PLTrend)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(100, 90, 201, 131))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.retranslateUi(PLTrend)

        QMetaObject.connectSlotsByName(PLTrend)
    # setupUi

    def retranslateUi(self, PLTrend):
        PLTrend.setWindowTitle(QCoreApplication.translate("PLTrend", u"Form", None))
    # retranslateUi

