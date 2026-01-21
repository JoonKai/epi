# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mdi_pltrend_widgettggEpr.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLayout, QListWidget, QListWidgetItem,
    QPushButton, QSizePolicy, QSpinBox, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_SUSMaker(object):
    def setupUi(self, SUSMaker):
        if not SUSMaker.objectName():
            SUSMaker.setObjectName(u"SUSMaker")
        SUSMaker.resize(515, 639)
        self.gridLayout_2 = QGridLayout(SUSMaker)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.tabWidget = QTabWidget(SUSMaker)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayout = QGridLayout(self.tab)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.groupBox = QGroupBox(self.tab)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_4 = QGridLayout(self.groupBox)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.listWidget = QListWidget(self.groupBox)
        self.listWidget.setObjectName(u"listWidget")

        self.horizontalLayout_3.addWidget(self.listWidget)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.pushButton_3 = QPushButton(self.groupBox)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.verticalLayout_3.addWidget(self.pushButton_3)

        self.pushButton_4 = QPushButton(self.groupBox)
        self.pushButton_4.setObjectName(u"pushButton_4")

        self.verticalLayout_3.addWidget(self.pushButton_4)

        self.pushButton_6 = QPushButton(self.groupBox)
        self.pushButton_6.setObjectName(u"pushButton_6")

        self.verticalLayout_3.addWidget(self.pushButton_6)

        self.pushButton_7 = QPushButton(self.groupBox)
        self.pushButton_7.setObjectName(u"pushButton_7")

        self.verticalLayout_3.addWidget(self.pushButton_7)

        self.pushButton_5 = QPushButton(self.groupBox)
        self.pushButton_5.setObjectName(u"pushButton_5")

        self.verticalLayout_3.addWidget(self.pushButton_5)


        self.horizontalLayout_3.addLayout(self.verticalLayout_3)

        self.horizontalLayout_3.setStretch(1, 3)

        self.gridLayout_4.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(self.tab)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_5 = QGridLayout(self.groupBox_2)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName(u"label")

        self.horizontalLayout_4.addWidget(self.label)

        self.doubleSpinBox_3 = QDoubleSpinBox(self.groupBox_2)
        self.doubleSpinBox_3.setObjectName(u"doubleSpinBox_3")

        self.horizontalLayout_4.addWidget(self.doubleSpinBox_3)

        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_4.addWidget(self.label_2)

        self.horizontalLayout_4.setStretch(0, 8)
        self.horizontalLayout_4.setStretch(1, 2)
        self.horizontalLayout_4.setStretch(2, 3)

        self.verticalLayout_4.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_6.addWidget(self.label_3)

        self.doubleSpinBox_4 = QDoubleSpinBox(self.groupBox_2)
        self.doubleSpinBox_4.setObjectName(u"doubleSpinBox_4")

        self.horizontalLayout_6.addWidget(self.doubleSpinBox_4)

        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_6.addWidget(self.label_4)

        self.horizontalLayout_6.setStretch(0, 8)
        self.horizontalLayout_6.setStretch(1, 2)
        self.horizontalLayout_6.setStretch(2, 3)

        self.verticalLayout_4.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.checkBox = QCheckBox(self.groupBox_2)
        self.checkBox.setObjectName(u"checkBox")

        self.horizontalLayout_5.addWidget(self.checkBox)


        self.verticalLayout_4.addLayout(self.horizontalLayout_5)


        self.gridLayout_5.addLayout(self.verticalLayout_4, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.groupBox_3 = QGroupBox(self.tab)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.gridLayout_6 = QGridLayout(self.groupBox_3)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_5 = QLabel(self.groupBox_3)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_7.addWidget(self.label_5)

        self.spinBox_3 = QSpinBox(self.groupBox_3)
        self.spinBox_3.setObjectName(u"spinBox_3")

        self.horizontalLayout_7.addWidget(self.spinBox_3)


        self.verticalLayout_5.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_6 = QLabel(self.groupBox_3)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_11.addWidget(self.label_6)

        self.doubleSpinBox = QDoubleSpinBox(self.groupBox_3)
        self.doubleSpinBox.setObjectName(u"doubleSpinBox")

        self.horizontalLayout_11.addWidget(self.doubleSpinBox)


        self.verticalLayout_5.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.label_7 = QLabel(self.groupBox_3)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_10.addWidget(self.label_7)

        self.comboBox = QComboBox(self.groupBox_3)
        self.comboBox.setObjectName(u"comboBox")

        self.horizontalLayout_10.addWidget(self.comboBox)


        self.verticalLayout_5.addLayout(self.horizontalLayout_10)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_8 = QLabel(self.groupBox_3)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_9.addWidget(self.label_8)

        self.doubleSpinBox_2 = QDoubleSpinBox(self.groupBox_3)
        self.doubleSpinBox_2.setObjectName(u"doubleSpinBox_2")

        self.horizontalLayout_9.addWidget(self.doubleSpinBox_2)


        self.verticalLayout_5.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_9 = QLabel(self.groupBox_3)
        self.label_9.setObjectName(u"label_9")

        self.horizontalLayout_8.addWidget(self.label_9)

        self.comboBox_2 = QComboBox(self.groupBox_3)
        self.comboBox_2.setObjectName(u"comboBox_2")

        self.horizontalLayout_8.addWidget(self.comboBox_2)


        self.verticalLayout_5.addLayout(self.horizontalLayout_8)


        self.gridLayout_6.addLayout(self.verticalLayout_5, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.groupBox_3)

        self.frame = QFrame(self.tab)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_3 = QGridLayout(self.frame)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButton = QPushButton(self.frame)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout_2.addWidget(self.pushButton)

        self.pushButton_2 = QPushButton(self.frame)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.horizontalLayout_2.addWidget(self.pushButton_2)


        self.gridLayout_3.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.frame)

        self.verticalLayout.setStretch(0, 2)
        self.verticalLayout.setStretch(1, 2)
        self.verticalLayout.setStretch(2, 2)
        self.verticalLayout.setStretch(3, 3)

        self.horizontalLayout.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSpacing(12)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.susceptor_widget = QWidget(self.tab)
        self.susceptor_widget.setObjectName(u"susceptor_widget")

        self.verticalLayout_6.addWidget(self.susceptor_widget)


        self.verticalLayout_2.addLayout(self.verticalLayout_6)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.horizontalLayout.setStretch(0, 3)
        self.horizontalLayout.setStretch(1, 7)

        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.tabWidget.addTab(self.tab_2, "")

        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)


        self.retranslateUi(SUSMaker)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(SUSMaker)
    # setupUi

    def retranslateUi(self, SUSMaker):
        SUSMaker.setWindowTitle(QCoreApplication.translate("SUSMaker", u"Suceptor Maker", None))
        self.groupBox.setTitle(QCoreApplication.translate("SUSMaker", u"Susceptor Configuration", None))
        self.pushButton_3.setText(QCoreApplication.translate("SUSMaker", u"\u2191", None))
        self.pushButton_4.setText(QCoreApplication.translate("SUSMaker", u"\u2193", None))
        self.pushButton_6.setText(QCoreApplication.translate("SUSMaker", u"ADD Ring", None))
        self.pushButton_7.setText(QCoreApplication.translate("SUSMaker", u"DEL Ring", None))
        self.pushButton_5.setText(QCoreApplication.translate("SUSMaker", u"Clear All", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("SUSMaker", u"Global Spec", None))
        self.label.setText(QCoreApplication.translate("SUSMaker", u"Wafer Diameter", None))
        self.label_2.setText(QCoreApplication.translate("SUSMaker", u"inch", None))
        self.label_3.setText(QCoreApplication.translate("SUSMaker", u"Susceptor Diameter", None))
        self.label_4.setText(QCoreApplication.translate("SUSMaker", u"inch", None))
        self.checkBox.setText(QCoreApplication.translate("SUSMaker", u"Start number from zero (0)", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("SUSMaker", u"GroupBox", None))
        self.label_5.setText(QCoreApplication.translate("SUSMaker", u"Count", None))
        self.label_6.setText(QCoreApplication.translate("SUSMaker", u"Radius (in)", None))
        self.label_7.setText(QCoreApplication.translate("SUSMaker", u"Flat", None))
        self.label_8.setText(QCoreApplication.translate("SUSMaker", u"Init Angle", None))
        self.label_9.setText(QCoreApplication.translate("SUSMaker", u"Rotate Dir", None))
        self.pushButton.setText(QCoreApplication.translate("SUSMaker", u"Open", None))
        self.pushButton_2.setText(QCoreApplication.translate("SUSMaker", u"Save", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("SUSMaker", u"MultiRIng (Circle)", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("SUSMaker", u"Free (Rectangle)", None))
    # retranslateUi

