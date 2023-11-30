#!python3
# coding = utf-8

import tkinter as tk
from tkinter import ttk
import logging
import os

_LOGGER = logging.getLogger(__name__)


def _get_attr(object_, property_name):
    try:
        return getattr(object_, property_name)
    except AttributeError as err:
        _LOGGER.error(err)
        return None


def _set_attr(object_, property_name, value):
    try:
        setattr(object_, property_name, value)
    except AttributeError as err:
        _LOGGER.error(err)


class ButtonListWidget(ttk.Frame):
    def __init__(self, parent, phy_monitor, property_name: str, options_list: list, **kwargs):
        super(ButtonListWidget, self).__init__(parent, **kwargs)

        self.phy_monitor = phy_monitor
        self.property_name = property_name
        self.options_list = options_list

        for idx, option in enumerate(self.options_list):
            btn = ttk.Button(self, text=option,
                             command=lambda opt=option: self.__set_value(opt))
            btn.grid(row=idx, column=0, sticky='ew', padx=5, pady=5)

    def __set_value(self, value):
        old_value = _get_attr(self.phy_monitor, self.property_name)
        if old_value == value:
            logging.info('ignored: update setting: ' + value)
            return
        _set_attr(self.phy_monitor, self.property_name, value)


class MonitorTab(ttk.Frame):
    """
    一个显示器实例的Tab
    """

    def __init__(self, parent, phy_monitor, **kwargs):
        super(MonitorTab, self).__init__(parent, **kwargs)
        self.phy_monitor = phy_monitor

        self.__init_widgets()
        self.__init_ui()

    def __init_widgets(self):
        """
        initialize UI elements.
        :return:
        """
        self.model_name = self.phy_monitor.model
        self.input_select_option = ButtonListWidget(self, self.phy_monitor,
                                                    'input_src', self.phy_monitor.input_src_list)

    def __init_ui(self):
        self.input_select_option.grid(row=6, column=1, sticky='W')


class TkApp(tk.Tk):
    """
    APP
    """

    def __init__(self, *args, **kwargs):
        super(TkApp, self).__init__(*args, **kwargs)
        self.status_text_var = tk.StringVar()
        self.status_text_bar = ttk.Label(
            self, textvariable=self.status_text_var)
        self.notebook = ttk.Notebook(self)

        self.__init_ui()

    def __init_ui(self):
        self.notebook.grid(row=0, column=0, sticky='NESW')
        self.status_text_bar.grid(row=1, column=0, sticky='SW')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.geometry('300x400')

    def add_monitors_to_tab(self, phy_monitor_list: list):
        """
        将PhyMonitor对象添加到NoteBook widget
        :param phy_monitor_list:
        :return:
        """
        for pm in phy_monitor_list:
            widget = MonitorTab(self.notebook, pm)
            self.notebook.add(widget, text=widget.model_name)
        self.status_text_var.set(
            '{} monitor(s) found.'.format(len(phy_monitor_list)))


if __name__ == '__main__':
    # Test Code
    import vcp
    import threading

    logging.basicConfig(level=logging.DEBUG)

    app = TkApp()
    app.title('DDC/CI APP')
    app.status_text_var.set('Detecting Monitor...')

    def background_task():
        monitors = []
        for i in vcp.enumerate_monitors():
            try:
                monitors.append(vcp.PhyMonitor(i))
            except OSError:
                pass
        app.status_text_var.set(' ')
        app.add_monitors_to_tab(monitors)

    threading.Thread(target=background_task, daemon=True).start()
    app.mainloop()
