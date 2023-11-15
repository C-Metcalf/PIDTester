# This Python file uses the following encoding: utf-8
import sys
import traceback
import serial
import json
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QRunnable, Signal, Slot, QObject, QThreadPool
from pglive.sources.data_connector import DataConnector
from pglive.sources.live_axis_range import LiveAxisRange
from pglive.sources.live_plot import LiveLinePlot
from pglive.sources.live_axis import LiveAxis
from pglive.kwargs import LeadingLine, Crosshair
from pglive.sources.live_plot_widget import LivePlotWidget
import pyqtgraph as pg  # type: ignore

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_Widget

_alive = True


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    """

    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(object)


class Worker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        # self.kwargs["progress_callback"] = self.signals.progress

    @Slot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class Serial:
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.connection = serial.Serial(
            port="/dev/ttyS0",
            # port="COM3",
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1,
        )
        self.threadpool = QThreadPool()
        worker = Worker(self.recv)
        self.threadpool.start(worker)

    def close(self):
        global _alive
        _alive = False
        self.connection.close()

    def recv(self):
        global _alive
        while _alive:
            try:
                msg = self.connection.readline()
                msg = json.loads(msg)
                print(msg)
                self.parent.data_connector.cb_append_data_point(msg["pos_cnt"])
            except Exception as e:
                pass

    def send(self, msg):
        if type(msg) is dict:
            # change this to what ever it needs to be
            msg = json.dumps(msg)
        msg += "\n"
        print(msg)
        self.connection.write(msg.encode())


class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        self.serial = Serial(self)
        self.plot = None
        self.data_connector = None
        self.live_plot_widget = None
        self.graph_setup()
        self.message = {'Kp': 0.0, 'Ki': 0.0, 'Kd': 0.0, 'setpoint': 0.0}
        self.ui.Start_btn.clicked.connect(self.send_start)
        self.ui.Pause_btn.clicked.connect(self.send_pause)
        self.ui.Stop_btn.clicked.connect(self.send_stop)
        self.ui.Send_values_btn.clicked.connect(self.send_values)
        self.ui.clear_graph_btn.clicked.connect(self.clear_graph)

    def closeEvent(self, event):
        self.serial.close()

    def graph_setup(self):
        left_axis = LiveAxis("left", axisPen="red", textPen="red")
        bottom_axis = LiveAxis(
            "bottom",
            axisPen="red",
            textPen="red",
        )
        kwargs = {
            Crosshair.ENABLED: True,
            Crosshair.LINE_PEN: pg.mkPen(color="red", width=1),
            Crosshair.TEXT_KWARGS: {"color": "green"},
        }

        self.live_plot_widget = LivePlotWidget(
            title="PID output",
            axisItems={"bottom": bottom_axis, "left": left_axis},
            x_range_controller=LiveAxisRange(roll_on_tick=150, offset_left=1.5),
            **kwargs,
        )

        self.live_plot_widget.x_range_controller.crop_left_offset_to_data = True
        self.plot = LiveLinePlot(pen="purple")
        self.plot.set_leading_line(
            LeadingLine.VERTICAL, pen=pg.mkPen("green"), text_axis=LeadingLine.AXIS_Y
        )
        self.live_plot_widget.addItem(self.plot)
        self.data_connector = DataConnector(self.plot, max_points=1500, update_rate=100000)
        self.ui.gridLayout.addWidget(self.live_plot_widget, 2, 0, 1, 4)

    def send_start(self):
        self.serial.send("start")

    def send_pause(self):
        self.serial.send("pause")

    def send_stop(self):
        self.serial.send("stop")

    def clear_graph(self):
        self.data_connector.clear()

    def send_values(self):
        self.message.update({'Kp': float(self.ui.P_value_txt.text())})
        self.message.update({'Ki': float(self.ui.I_value_txt.text())})
        self.message.update({'Kd': float(self.ui.D_value_txt.text())})
        self.message.update({'setpoint': float(self.ui.SetPoint_value_txt.text())})
        self.serial.send(self.message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
