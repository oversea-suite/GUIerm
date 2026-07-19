import sys
from PyQt6 import QtWidgets, QtCore
import mainwindow
import os
import shlex
import subprocess
import importlib

# config stuff
EXAMPLE_CONFIG="""#!/bin/false
# Example configuration.
# To use GERM, please edit this file.

# The following line disables GERM to tell you to edit this file:
GERM_DISABLED=True

# Options
COMMANDS={
  "local":"/var/lib/probed/getinfo.sh",
  "remote":"bash -c 'exec 3<>/dev/tcp/example.com/555; cat <&3'" # for use with PROBEd
  }
"""

os.makedirs(os.path.expanduser('~/.config/'), exist_ok=True)
if not os.path.isfile(os.path.expanduser('~/.config/germ.conf.py')):
  with open(os.path.expanduser('~/.config/germ.conf.py'), 'w') as f:
    f.write(EXAMPLE_CONFIG)
spec = importlib.util.spec_from_file_location("config", os.path.expanduser('~/.config/germ.conf.py'))
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)
if config.GERM_DISABLED:
  QMessageBox.critical(None, "Config Error", "Please edit ~/.config/germ.conf.py and retry.")
  sys.exit(1)

def parse(output):
  d = {}
  for line in output.strip().splitlines():
    key, _, val = line.partition(':')
    d[key] = val
  return d

class MainWindow(QtWidgets.QMainWindow):
  name=None
  def __init__(self):
    super(MainWindow, self).__init__()
    self.ui = mainwindow.Ui_MainWindow()
    self.ui.setupUi(self)
    for i in config.COMMANDS.keys():
      action = self.ui.menuSwitch_Target.addAction(i)
      action.triggered.connect(lambda checked, name=i: self.switch(name))
    self.ui.actionReload.triggered.connect(self.reload)
    self.reloadTimer = QtCore.QTimer(self)
    self.reloadTimer.timeout.connect(self.reload)
    self.ui.actionAuto_Reload_2.toggled.connect(self.toggleAutoReload)
    if "local" in config.COMMANDS:
      self.switch("local")
      self.ui.actionAuto_Reload_2.setChecked(True)

  def switch(self, name):
    self.name=name
    self.setWindowTitle(f"GUIerm - loading...")
    self.reload()
    self.setWindowTitle(f"GUIerm - {name}")

  def toggleAutoReload(self, checked):
    if checked:
        self.reloadTimer.start(5000)
    else:
        self.reloadTimer.stop()

  def reload(self):
    if self.name==None:
      return
    args = shlex.split(config.COMMANDS[self.name])
    r    = subprocess.run(args, capture_output=True, text=True, check=True, timeout=10)
    out=parse(r.stdout)
    seconds = float(out["uptime_s"].strip())
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    self.ui.label_CONTAIN_UPTIME.setText(f"{h:02d}:{m:02d}:{s:02d} up")
    self.ui.label_CONTAIN_LOAD_AVG.setText(out["load_avg"])
    self.ui.label_CONTAIN_CPU_TEMP_C.setText(f"{out['cpu_temp_c']}°C")
    self.ui.label_CONTAIN_CPU_PCT.setText(f"{out['cpu_pct']}%")

    self.ui.label_CONTAIN_RAM_TOTAL_GB.setText(f"{float(out['ram_total_kb']) / 1048576:.1f}".rstrip('0').rstrip('.')+"G")
    self.ui.label_CONTAIN_SWAP_TOTAL_GB.setText(f"{float(out['swap_total_kb']) / 1048576:.1f}".rstrip('0').rstrip('.')+"G")
    self.ui.label_CONTAIN_RAM_USED_GB.setText(f"{float(out['ram_used_kb']) / 1048576:.1f}".rstrip('0').rstrip('.')+"G")
    self.ui.label_CONTAIN_SWAP_USED_GB.setText(f"{float(out['swap_used_kb']) / 1048576:.1f}".rstrip('0').rstrip('.')+"G")

    self.ui.label_CONTAIN_DISK_TOTAL_GB.setText(f"{float(out['disk_total_kb']) / 1048576:.1f}".rstrip('0').rstrip('.')+"G")
    self.ui.label_CONTAIN_DISK_USED_GB.setText(f"{float(out['disk_used_kb']) / 1048576:.1f}".rstrip('z0').rstrip('.')+"G")
    self.ui.label_CONTAIN_DISK_READ_MB_S.setText(f"{float(out['disk_read_kb_s']) / 1024:.1f}".rstrip('0').rstrip('.')+"M/s")
    self.ui.label_CONTAIN_DISK_WRITE_MB_S.setText(f"{float(out['disk_write_kb_s']) / 1024:.1f}".rstrip('0').rstrip('.')+"M/s")

    self.ui.label_CONTAIN_NET_RX_MB_S.setText(f"{float(out['net_rx_kb_s']) / 1024:.1f}".rstrip('0').rstrip('.')+"M/s")
    self.ui.label_CONTAIN_NET_TX_MB_S.setText(f"{float(out['net_tx_kb_s']) / 1024:.1f}".rstrip('0').rstrip('.')+"M/s")

    self.ui.label_PROC_CPU_1.setText(out['proc_cpu_1'].partition(':')[0])
    self.ui.label_PROC_CPU_2.setText(out['proc_cpu_2'].partition(':')[0])
    self.ui.label_PROC_CPU_3.setText(out['proc_cpu_3'].partition(':')[0])
    self.ui.label_PROC_CPU_4.setText(out['proc_cpu_4'].partition(':')[0])
    self.ui.label_PROC_CPU_5.setText(out['proc_cpu_5'].partition(':')[0])

    self.ui.label_CONTAIN_PROC_CPU_1.setText(out['proc_cpu_1'].partition(':')[2]+"%")
    self.ui.label_CONTAIN_PROC_CPU_2.setText(out['proc_cpu_2'].partition(':')[2]+"%")
    self.ui.label_CONTAIN_PROC_CPU_3.setText(out['proc_cpu_3'].partition(':')[2]+"%")
    self.ui.label_CONTAIN_PROC_CPU_4.setText(out['proc_cpu_4'].partition(':')[2]+"%")
    self.ui.label_CONTAIN_PROC_CPU_5.setText(out['proc_cpu_5'].partition(':')[2]+"%")

    self.ui.label_PROC_RAM_1.setText(out['proc_ram_1'].partition(':')[0])
    self.ui.label_PROC_RAM_2.setText(out['proc_ram_2'].partition(':')[0])
    self.ui.label_PROC_RAM_3.setText(out['proc_ram_3'].partition(':')[0])
    self.ui.label_PROC_RAM_4.setText(out['proc_ram_4'].partition(':')[0])
    self.ui.label_PROC_RAM_5.setText(out['proc_ram_5'].partition(':')[0])

    self.ui.label_CONTAIN_PROC_RAM_1.setText(out['proc_ram_1'].partition(':')[2]+"%")
    self.ui.label_CONTAIN_PROC_RAM_2.setText(out['proc_ram_2'].partition(':')[2]+"%")
    self.ui.label_CONTAIN_PROC_RAM_3.setText(out['proc_ram_3'].partition(':')[2]+"%")
    self.ui.label_CONTAIN_PROC_RAM_4.setText(out['proc_ram_4'].partition(':')[2]+"%")
    self.ui.label_CONTAIN_PROC_RAM_5.setText(out['proc_ram_5'].partition(':')[2]+"%")



app = QtWidgets.QApplication(sys.argv)

my_mainWindow = MainWindow()
my_mainWindow.show()

sys.exit(app.exec())
