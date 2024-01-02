# This Python file uses the following encoding: utf-8
import sys
import traceback
import time

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
setpoint = 0


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


class pid_control:
    def __init__(self, _kp=0.1, _ki=0, _kd=0.0001):
        self.Kp = _kp
        self.Ki = _ki
        self.Kd = _kd

        self.current_value = 0

        self.cycle = 1

        self.error = 0
        self.dt_error = 0

    def set_new_params(self, params):
        self.Kp, self.Ki, self.Kd = params

    def calc_p(self):
        return round(float(self.Kp * self.error), 4)

    def calc_i(self):
        return round(float(self.Ki * self.dt_error), 4)

    def calc_d(self, _error):
        return round(float(self.Kd * _error), 4)

    def pid_calc(self, _target):
        _c = 0
        self.error = _target - self.current_value
        _c += self.calc_p()

        self.dt_error += self.error
        _c += self.calc_i()

        temp = self.dt_error / self.cycle
        _c += self.calc_d(temp)

        self.current_value += _c
        self.cycle += 1

    def get_current_value(self):
        return self.current_value

    def __str__(self):
        return "Current value = {0}, Error = {1}, Cycle = {2}".format(
            int(self.current_value), int(self.error), self.cycle
            )

    def err(self):
        return self.error

    def pv(self):
        return int(self.current_value)


class Serial:
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        '''
        self.connection = serial.Serial(
            port='/dev/ttyS0',
            # port="COM3",
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1,
        )
        '''
        self.pid_controller = pid_control()
        self.threadpool = QThreadPool()
        worker = Worker(self.calc)
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

    def calc(self):
        global setpoint
        global _alive
        while _alive:
            self.pid_controller.pid_calc(setpoint)
            #print(self.pid_controller)
            self.parent.data_connector_pv.cb_append_data_point(self.pid_controller.pv())
            self.parent.data_connector_sp.cb_append_data_point(setpoint)
            time.sleep(.1)


class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        self.data_connector_sp = None
        self.data_connector_pv = None
        self.plot_sp = None
        self.plot_pv = None
        self.live_plot_widget = None
        self.graph_setup()
        self.serial = Serial(self)
        self.message = {'Kp': 0.0, 'Ki': 0.0, 'Kd': 0.0, 'setpoint': 0.0}
        self.ui.Start_btn.clicked.connect(self.send_start)
        self.ui.Pause_btn.clicked.connect(self.send_pause)
        self.ui.Stop_btn.clicked.connect(self.send_stop)
        self.ui.Send_values_btn.clicked.connect(self.send_values)
        self.ui.clear_graph_btn.clicked.connect(self.clear_graph)
        self.ui.P_value_txt.setText('0.1')
        self.ui.I_value_txt.setText('0')
        self.ui.D_value_txt.setText('0.0001')

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

        # The set point line in the graph
        self.plot_sp = LiveLinePlot(pen="red")

        # The process value line in the graph
        self.plot_pv = LiveLinePlot(pen="blue")

        # To add another line create another LiveLinePlot object then add to the self.live_plot_widget below
        self.live_plot_widget.addItem(self.plot_sp)
        self.live_plot_widget.addItem(self.plot_pv)
        # To add data to that line create another DataConnector object max points is how much "history" it keeps
        self.data_connector_sp = DataConnector(self.plot_sp, max_points=150, update_rate=100000)
        self.data_connector_pv = DataConnector(self.plot_pv, max_points=150, update_rate=100000)

        self.ui.gridLayout.addWidget(self.live_plot_widget, 2, 0, 1, 4)




    def send_start(self):
        self.serial.send("start")

    def send_pause(self):
        self.serial.send("pause")

    def send_stop(self):
        self.serial.send("stop")

    def clear_graph(self):
        self.data_connector_pv.clear()
        self.data_connector_sp.clear()

    def send_values(self):
        global setpoint
        # This is for sending data to the pico
        # self.message.update({'Kp': float(self.ui.P_value_txt.text())})
        # self.message.update({'Ki': float(self.ui.I_value_txt.text())})
        # self.message.update({'Kd': float(self.ui.D_value_txt.text())})
        # self.message.update({'setpoint': float(self.ui.SetPoint_value_txt.text())})
        # self.serial.send(self.message)
        params = (float(self.ui.P_value_txt.text()), float(self.ui.I_value_txt.text()), float(self.ui.D_value_txt.text()))
        self.serial.pid_controller.set_new_params(params)
        setpoint = float(self.ui.SetPoint_value_txt.text())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
