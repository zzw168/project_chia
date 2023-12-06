# This is a sample Python script.
import os
import subprocess
import sys
import threading
import time

import yaml
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem

import t1


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# Press the green button in the gutter to run the script.
class My_Gui(t1.Ui_MainWindow):
    def __int__(self):
        super().__init__()

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)


def scan_disk():
    print("______________检测线程______________")
    path = "/media/z"
    # chia_config_path = "/home/z/.chia/mainnet/config/config.yaml"
    # f = open(chia_config_path, 'r', encoding='utf-8')
    # chia_conf = yaml.safe_load(f)
    w_list = [[], [], []]
    # count = 0
    for root, dirs, files in os.walk(path):
        for d in dirs:
            path = "%s/%s" % (root, d)
            for root1, dirs1, files1 in os.walk(path):
                # print(files1)
                if len(files1) != 0:
                    if ".plot" in files1[0]:
                        plot_num = 0
                        for i in range(0, len(files1)):
                            if ".plot" in files1[i]:
                                plot_num += 1

                        print("路径：%s----数量:%d" % (d, plot_num))
                        # count += plot_num
                        w_list[0].append(root1)
                        w_list[1].append(d)
                        w_list[2].append(plot_num)
                break
        break
    print("______________检测线程完成______________")

    return w_list


class myThread(QThread):
    _signal = pyqtSignal(object)

    def __int__(self):
        super(myThread, self).__init__()
        self.run_flg = False

    def run(self):
        while True:
            time.sleep(3)
            print(self.run_flg)
            if self.run_flg:
                try:
                    w_list = scan_disk()
                    # print(w_list)
                    self._signal.emit(w_list)

                except:
                    return 'Error'


def edit_config(d_list):
    chia_config_path = "/home/z/.chia/mainnet/config/config.yaml"
    f = open(chia_config_path, 'r', encoding='utf-8')
    chia_conf = yaml.safe_load(f)
    chia_conf['harvester']['plot_directories'] = d_list[0]
    with open(chia_config_path, "w", encoding="utf8") as f:
        yaml.dump(chia_conf, f, allow_unicode=True)
        f.close()


def signal_accept(message):
    # print(message)
    d_list = message
    table = ui.tableWidget
    if table.rowCount() < len(d_list[1]):
        edit_config(d_list)
        count = 0
        for i in range(0, len(d_list[1])):
            count += d_list[2][i]
            table.setRowCount(i + 1)
            # print(d_list[1][i])
            item = QTableWidgetItem(str(d_list[1][i]))
            item.setTextAlignment(Qt.AlignCenter)
            table.setItem(i, 0, item)

            d = QTableWidgetItem(str(d_list[2][i]))
            d.setTextAlignment(Qt.AlignCenter)
            table.setItem(i, 1, d)
        if ui.lineEdit_disk.text() != str(len(d_list[1])):
            ui.lineEdit_disk.setText(str(len(d_list[1])))
        if ui.lineEdit_plot.text() != str(count):
            ui.lineEdit_plot.setText(str(count))

    elif table.rowCount() > len(d_list[1]):
        for i in range(0, table.rowCount()):
            if not (table.item(i, 0).text() in d_list[1]):
                d = QTableWidgetItem(str('掉盘'))
                d.setTextAlignment(Qt.AlignCenter)
                table.setItem(i, 1, d)
        count = 0
        for j in range(0, len(d_list[1])):
            count += d_list[2][j]
        if ui.lineEdit_disk.text() != str(len(d_list[1])):
            ui.lineEdit_disk.setText(str(len(d_list[1])))
        if ui.lineEdit_plot.text() != str(count):
            ui.lineEdit_plot.setText(str(count))

    else:
        for i in range(0, table.rowCount()):
            if table.item(i, 0).text() == d_list[1][i]:
                if table.item(i, 1).text() != str(d_list[2][i]):
                    d = QTableWidgetItem(str(d_list[2][i]))
                    d.setTextAlignment(Qt.AlignCenter)
                    table.setItem(i, 1, d)
                    # edit_config(d_list)
            else:
                item = QTableWidgetItem(str(d_list[1][i]))
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(i, 0, item)

                d = QTableWidgetItem(str(d_list[2][i]))
                d.setTextAlignment(Qt.AlignCenter)
                table.setItem(i, 1, d)
                edit_config(d_list)
        count = 0
        for j in range(0, len(d_list[1])):
            count += d_list[2][j]
        if ui.lineEdit_disk.text() != str(len(d_list[1])):
            ui.lineEdit_disk.setText(str(len(d_list[1])))
        if ui.lineEdit_plot.text() != str(count):
            ui.lineEdit_plot.setText(str(count))




class Cmd_thread(QThread):
    _signal = pyqtSignal(object)

    def __int__(self):
        super(myThread, self).__init__()
        self.run_flg = False
        self.cmd = ''

    def run(self):
        process = subprocess.Popen(self.cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        try:
            while process.poll() is None:
                line = process.stdout.readline()
                line = line.strip()

                if line:
                    log = line.decode("utf-8", "ignore")
                    self._signal.emit(log)
                    print(log)
            print('end----------')
        except:
            return 'Error'

def cmd_accept(message):
    print(message)
    ui.listWidget.addItem(message)

def scan_disk_btn():
    ui.tableWidget.setRowCount(0)

    thread1.run_flg = True

    chia_thread.cmd = "/home/z/chia-gigahorse-farmer/chia.bin start farmer -r"
    chia_thread.run_flg = True
    chia_thread.start()

    run_mtail_cmd = "cd /home/z/chia-gigahorse-farmer/data_collect/ && sh run_mtail.sh"
    run_mtail_thread.cmd = "gnome-terminal -t \"run_mtail\" -x bash -c \" {};exec bash;\"".format(run_mtail_cmd)
    run_mtail_thread.run_flg = True
    run_mtail_thread.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = My_Gui()
    ui.setupUi(MainWindow)
    MainWindow.show()

    thread1 = myThread()
    thread1._signal.connect(signal_accept)

    thread1.run_flg = False
    thread1.start()

    chia_thread = Cmd_thread()
    chia_thread._signal.connect(cmd_accept)

    run_mtail_thread = Cmd_thread()
    run_mtail_thread._signal.connect(cmd_accept)

    ui.pushButton_reboot.clicked.connect(scan_disk_btn)

    scan_disk_btn

    sys.exit(app.exec_())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
