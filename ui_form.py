# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLineEdit, QPushButton,
    QSizePolicy, QWidget)

class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.resize(1010, 600)
        self.gridLayout = QGridLayout(Widget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.Pause_btn = QPushButton(Widget)
        self.Pause_btn.setObjectName(u"Pause_btn")

        self.gridLayout.addWidget(self.Pause_btn, 1, 1, 1, 1)

        self.D_value_txt = QLineEdit(Widget)
        self.D_value_txt.setObjectName(u"D_value_txt")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.D_value_txt.sizePolicy().hasHeightForWidth())
        self.D_value_txt.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.D_value_txt, 3, 2, 1, 1, Qt.AlignmentFlag.AlignCenter)

        self.P_value_txt = QLineEdit(Widget)
        self.P_value_txt.setObjectName(u"P_value_txt")
        sizePolicy.setHeightForWidth(self.P_value_txt.sizePolicy().hasHeightForWidth())
        self.P_value_txt.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.P_value_txt, 3, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)

        self.Start_btn = QPushButton(Widget)
        self.Start_btn.setObjectName(u"Start_btn")

        self.gridLayout.addWidget(self.Start_btn, 1, 0, 1, 1)

        self.Stop_btn = QPushButton(Widget)
        self.Stop_btn.setObjectName(u"Stop_btn")

        self.gridLayout.addWidget(self.Stop_btn, 1, 2, 1, 1)

        self.SetPoint_value_txt = QLineEdit(Widget)
        self.SetPoint_value_txt.setObjectName(u"SetPoint_value_txt")
        sizePolicy.setHeightForWidth(self.SetPoint_value_txt.sizePolicy().hasHeightForWidth())
        self.SetPoint_value_txt.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.SetPoint_value_txt, 3, 3, 1, 1, Qt.AlignmentFlag.AlignCenter)

        self.I_value_txt = QLineEdit(Widget)
        self.I_value_txt.setObjectName(u"I_value_txt")
        sizePolicy.setHeightForWidth(self.I_value_txt.sizePolicy().hasHeightForWidth())
        self.I_value_txt.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.I_value_txt, 3, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)

        self.Send_values_btn = QPushButton(Widget)
        self.Send_values_btn.setObjectName(u"Send_values_btn")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.Send_values_btn.sizePolicy().hasHeightForWidth())
        self.Send_values_btn.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.Send_values_btn, 1, 3, 1, 1)

        self.clear_graph_btn = QPushButton(Widget)
        self.clear_graph_btn.setObjectName(u"clear_graph_btn")

        self.gridLayout.addWidget(self.clear_graph_btn, 0, 3, 1, 1)


        self.retranslateUi(Widget)

        QMetaObject.connectSlotsByName(Widget)
    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"Widget", None))
        self.Pause_btn.setText(QCoreApplication.translate("Widget", u"Pause", None))
        self.Start_btn.setText(QCoreApplication.translate("Widget", u"Start", None))
        self.Stop_btn.setText(QCoreApplication.translate("Widget", u"Stop", None))
        self.Send_values_btn.setText(QCoreApplication.translate("Widget", u"Send Values", None))
        self.clear_graph_btn.setText(QCoreApplication.translate("Widget", u"Clear Graph", None))
    # retranslateUi

