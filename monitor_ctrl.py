#!python3
# coding = utf-8

import os
import sys
import logging
import argparse
import vcp

try:
    import tkinter
    from tkinter import ttk
    TK_IMPORTED = True
except ImportError:
    TK_IMPORTED = False


__VERSION__ = '1.0'
__APP_NAME__ = 'monitor_ctrl'

DEFAULT_LOGFILE_PATH = os.path.join(
    os.environ.get('TEMP', './'), __APP_NAME__, 'log.txt')
_LOGGER = logging.getLogger(__name__)


# Win32 _PhysicalMonitorStructure
ALL_MONITORS = []
# vcp.PhyMonitor() instance(s)
ALL_PHY_MONITORS = []


def enum_monitors():
    """
    enumerate all monitor. append to ALL_PHY_MONITORS list
    :return:
    """
    global ALL_PHY_MONITORS
    global ALL_MONITORS
    ALL_MONITORS = vcp.enumerate_monitors()
    for i in ALL_MONITORS:
        try:
            monitor = vcp.PhyMonitor(i)
        except OSError as err:
            _LOGGER.error(err)
            # ignore this monitor
            continue
        _LOGGER.info('Found monitor: ' + monitor.model)
        ALL_PHY_MONITORS.append(monitor)


def start_gui():
    import tkui
    import threading

    app = tkui.TkApp()
    app.title(__APP_NAME__)
    app.geometry('180x300')
    app.status_text_var.set('detecting monitor...')

    def background_task():
        enum_monitors()
        _LOGGER.info('start GUI, ignore command line actions.')
        app.status_text_var.set('')
        app.add_monitors_to_tab(ALL_PHY_MONITORS)

    threading.Thread(target=background_task, daemon=True).start()
    app.mainloop()


if __name__ == '__main__':
    start_gui()
