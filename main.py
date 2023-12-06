# This is a sample Python script.
import datetime
import json
import os
import subprocess
import sys
import time
from hashlib import md5
import random

import requests
import yaml
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QEvent
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMenu, QCheckBox, QWidget
from PyQt5 import QtCore

import os
import socket
import t1

import requests
from gevent import pywsgi
from flask import Flask

flask_app = Flask(__name__)


@flask_app.route('/upgrade')
def http_upgrade():
    upgrade()
    return "更新信号已经发出"


@flask_app.route('/')
def http_hellow():
    return "hello world"


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# Press the green button in the gutter to run the script.

class My_Gui(t1.Ui_MainWindow):
    def __int__(self):
        super().__init__()

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)

        tb = self.tableWidget
        tb.horizontalHeader().resizeSection(0, 10)
        tb.horizontalHeader().resizeSection(2, 150)

        # 给列表增加菜单
        table = self.tableWidget_disk
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self.generateMenu)

        # 给列表增加菜单
        table1 = self.tableWidget
        table1.setContextMenuPolicy(Qt.CustomContextMenu)
        table1.customContextMenuRequested.connect(self.generateMenu1)

    def generateMenu(self, pos):
        table = self.tableWidget_disk

        menu = QMenu()
        item2 = menu.addAction("删除")
        item3 = menu.addAction("清空")
        screenPos = table.mapToGlobal(pos)

        action = menu.exec(screenPos)
        if action == item2:
            num = table.rowCount()
            if num != 0:
                p = table.currentRow()
                for i in range(p, num - 1):
                    for j in range(0, table.columnCount()):
                        item = QTableWidgetItem(table.item(i + 1, j).text())
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                        table.setItem(i, j, item)
                table.setRowCount(num - 1)
        if action == item3:
            ui.tableWidget_disk.setRowCount(0)

    def generateMenu1(self, pos):
        global seach_
        table = self.tableWidget
        menu = QMenu()
        item = menu.addAction("刷新")
        screenPos1 = table.mapToGlobal(pos)

        action = menu.exec(screenPos1)
        if action == item:
            table.setRowCount(0)
            if self.lineEdit_front.text() == '':
                seach_ = '~'
            thread1.run_flg = True


def scan_disk():
    w_list = [[], [], []]
    # 查找卷标
    cmd = "echo '" + path_password + "'|sudo -S blkid |grep ': LABEL'"
    label = adb_shell(cmd)
    label = yaml.safe_load(label)
    # 查找磁盘
    cmd = "echo '" + path_password + "'|sudo -S lsblk -J"
    path_all = adb_shell(cmd)
    path_all = yaml.safe_load(path_all)
    for path in path_all['blockdevices']:
        if 'loop' not in path['name'] and "children" in path.keys():
            for path_ in path['children']:
                if path_['mountpoint'] and 'T' in path_['size']:
                    try:
                        label_ = path_['mountpoint'].replace('/media/' + path_root + '/', '')
                        if '/dev/' + path_['name'] in label.keys():
                            s = label['/dev/' + path_['name']]
                            s = s.replace(' ', '\n')
                            s = s.replace('=', ': ')
                            s = yaml.safe_load(s)
                            if 'LABEL' in s.keys():
                                label_ = s['LABEL']
                    except:
                        pass
                    plot_num = 0
                    for root1, dirs1, files1 in os.walk(path_['mountpoint']):
                        if len(files1) != 0:
                            for i in range(0, len(files1)):
                                if ".plot" in files1[i]:
                                    plot_num += 1
                    w_list[0].append(path_['mountpoint'])
                    w_list[1].append(label_)
                    w_list[2].append(plot_num)
    return w_list


class myThread(QThread):
    _signal = pyqtSignal(object)

    def __int__(self):
        super(myThread, self).__init__()
        self.run_flg = False

    def run(self):
        while True:
            if self.run_flg:
                try:
                    w_list = scan_disk()
                    if len(w_list[1]) != 0:
                        self._signal.emit(w_list)

                except:
                    return 'Error'
            time.sleep(1)


def edit_config(di_list):  # 修改硬盘列表配置
    global plots_dir
    try:
        chia_config_path = "/home/" + path_root + "/.chia/mainnet/config/config.yaml"
        f = open(chia_config_path, 'r', encoding='utf-8')
        chia_conf = yaml.safe_load(f)
        f.close()
        plots_list = []
        if not plots_dir:
            plots_dir = ""
        for i in di_list[0]:
            plots_list.append('%s%s' % (i, plots_dir))
        chia_conf['harvester']['plot_directories'] = plots_list
        with open(chia_config_path, "w", encoding="utf8") as f_:
            yaml.dump(chia_conf, f_, allow_unicode=True)
    except:
        cmd = "cp -rvf %s /home/%s/.chia/mainnet/config/" % \
              ('./config.yaml', path_root)
        adb_shell(cmd)


def signal_accept(message):
    global d_list
    d_list = message
    table = ui.tableWidget
    name_list = [[], [], []]
    for j in range(0, table.rowCount()):
        name_list[1].append(table.item(j, 1).text())
        name_list[2].append(table.item(j, 2).text())

    if seach_ == '~' and len(d_list[1]) != table.rowCount():
        edit_config(d_list)  # 写chia config文件

    if table.rowCount() != 0:
        for i in range(0, table.rowCount()):  # 掉盘提示
            if not (table.item(i, 1).text() in d_list[1]):
                d = QTableWidgetItem(str('掉盘'))
                d.setTextAlignment(Qt.AlignCenter)
                d.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                table.setItem(i, 2, d)

    for i in range(0, len(d_list[1])):  # 添加新盘
        for j in range(0, len(name_list[1])):  # 数量校准
            if name_list[1][j] == d_list[1][i] and name_list[2][j] != d_list[2][i]:
                d = QTableWidgetItem(str(d_list[2][i]))
                d.setTextAlignment(Qt.AlignCenter)
                d.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                table.setItem(j, 2, d)

        if not (d_list[1][i] in name_list[1]) and d_list[2][i] != 0:
            # edit_config(d_list)  # 写chia config文件
            if seach_ == '~':
                pass
            elif seach_ == '-':
                if seach_ in d_list[1][i]:
                    continue
            else:
                if not (seach_ in d_list[1][i]):
                    continue

            num = table.rowCount()
            table.setRowCount(num + 1)
            cb = QCheckBox()
            cb.setStyleSheet('QCheckBox{margin:12px};')
            table.setCellWidget(num, 0, cb)

            item = QTableWidgetItem(str(d_list[1][i]))
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            table.setItem(num, 1, item)

            item = QTableWidgetItem(str(d_list[2][i]))
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            table.setItem(num, 2, item)

    count = 0
    num = 0
    for j in range(0, table.rowCount()):
        num += 1
        if table.item(j, 2).text().isdigit():
            count += int(table.item(j, 2).text())
    if ui.lineEdit_disk.text() != str(num):
        ui.lineEdit_disk.setText(str(num))
    if ui.lineEdit_plot.text() != str(count):
        ui.lineEdit_plot.setText(str(count))


def lost_disk():
    global disk_list
    global d_list
    if not (ui.tabWidget.currentIndex() == 2):
        print('ok~~~')
        return
    if not (disk_list) or not (d_list):
        print('disk_list~~~')
        return
    tb = ui.tableWidget_disk
    tb.setRowCount(0)
    for i in disk_list[1]:
        if not (i in d_list[1]):
            tb.setRowCount(tb.rowCount() + 1)
            it1 = QTableWidgetItem(i)
            it1.setTextAlignment(Qt.AlignCenter)
            it1.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            tb.setItem(tb.rowCount() - 1, 0, it1)

            it2 = QTableWidgetItem(str('掉盘'))
            it2.setTextAlignment(Qt.AlignCenter)
            it2.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            tb.setItem(tb.rowCount() - 1, 1, it2)

            it3 = QTableWidgetItem(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            it3.setTextAlignment(Qt.AlignCenter)
            it3.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            tb.setItem(tb.rowCount() - 1, 2, it3)


class Cmd_thread(QThread):  # 执行shell命令线程
    _signal = pyqtSignal(object)

    def __int__(self):
        super(Cmd_thread, self).__init__()
        self.run_flg = False
        self.cmd = ''

    def run(self):
        if 'start' in self.cmd:
            time.sleep(5)
        process = subprocess.Popen(self.cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        try:
            while process.poll() is None:
                line = process.stdout.readline()
                line = line.strip()

                if line:
                    log = line.decode("utf-8", "ignore")
                    self._signal.emit(log)
                    # print(log)
            print('end----------')
        except:
            return 'Error'


def cmd_accept(message):
    print(message)
    ui.textBrowser_msg.append(message)


def state_accept(message):
    print(message)
    ui.textBrowser.append(message)
    if "HARVESTER 127.0.0.1" in message:
        num = message.find("/8448  ") + len("/8448  ")
        if num != -1:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s = "%s_%s" % (message[num:num + 6], ip)
            print(s)
            ui.pushButton_HARVESTER.setText(s)
    if "Farming status: Farming" in message:
        ui.progressBar_reboot.setValue(100)


class Scan_thread(QThread):  # 执行shell命令线程
    _signal = pyqtSignal(object)

    def __int__(self):
        super(Scan_thread, self).__init__()
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
                    print(log)
                    if log.find('Starting to test each plot') != -1:
                        process.kill()
                        self._signal.emit('end')
                        break

                    if log.find('ERROR') == -1:
                        continue
                    self._signal.emit(log)
            print('end----------')
        except:
            return 'Error'


def scan_accept(message):
    if message == 'end':
        print('_________________________')
        del_thread.run_flg = True
        del_thread.start()
    else:
        num = message.find('/media/')
        if num == -1:
            return
        path_ = message[num:]
        # print(path_)
        num = path_.find('.plot') + len('.plot')
        path_ = path_[0:num]
        ui.textBrowser.append(path_)
        print(path_)
        del_thread.dellist.append(path_)
        # del_thread.cmd = "echo '" + path_password + "'|sudo -S rm -rf %s" % path_


class DelThread(QThread):  # 执行shell命令线程
    _signal = pyqtSignal(object)

    def __int__(self):
        super(DelThread, self).__init__()
        self.run_flg = False
        self.dellist = []

    def run(self):
        if self.run_flg and self.dellist != []:
            for path_ in self.dellist:
                cmd = "echo '" + path_password + "'|sudo -S rm -rf %s" % path_
                adb_shell(cmd)
            self.dellist = []
            self._signal.emit('清除完毕')


def scan_disk_btn():
    ui.tableWidget.setRowCount(0)
    ui.textBrowser_msg.setText('')
    ui.progressBar_reboot.setValue(0)

    PsCmd_Thread.cmd = "ps x"
    PsCmd_Thread.run_flg = True
    PsCmd_Thread.start()

    # chia_thread.cmd = ("cd /home/%s%s \n"
    #                    "%s start farmer" % (path_root, chia_path, chia_exe))
    # print(chia_thread.cmd)
    # chia_thread.run_flg = True
    # chia_thread.start()

    run_mtail_cmd = ("cd /home/%s%s && sh run_mtail.sh" % (path_root, data_collect))
    run_mtail_thread.cmd = "gnome-terminal -t \"run_mtail\" -x bash -c \" {};exec bash;\"".format(
        run_mtail_cmd)
    run_mtail_thread.run_flg = True
    run_mtail_thread.start()


def farm_state_btn():
    ui.textBrowser.setText('')
    chia_state_thread.cmd = "/home/%s%s%s farm summary\n" % (path_root, chia_path, chia_exe)
    chia_state_thread.run_flg = True
    chia_state_thread.start()


def chia_state_btn():
    ui.textBrowser.setText('')
    chia_state_thread.cmd = "/home/%s%s%s show -s\n" % (path_root, chia_path, chia_exe)
    chia_state_thread.run_flg = True
    chia_state_thread.start()


def deal_yaml():
    global path_root
    global path_password
    global chia_path
    global chia_exe
    global plots_dir
    global data_collect
    global mount_path
    global share_link
    global share_username
    global share_password
    global cp_dir
    global host_list
    global disk_list
    pythonpath = os.getcwd()
    # pythonpath = '/home/z'
    ui.textBrowser_msg.setText(pythonpath)
    print(pythonpath)
    # f = open(r'./path_config.yml', 'r', encoding='utf-8')
    f = open(r'%s/桌面/z/path_config.yml' % pythonpath, 'r', encoding='utf-8')
    # f = open(r'%s/path_config.yml' % (pythonpath), 'r', encoding='utf-8')
    f_ = yaml.safe_load(f)
    path_root = f_['root']
    path_password = f_['password']
    chia_path = f_['chia_path']
    chia_exe = f_['chia_exe']
    plots_dir = f_['plots_dir']
    data_collect = f_['data_collect']
    mount_path = f_['mount_path']
    share_link = f_['share_link']
    share_username = f_['share_username']
    share_password = f_['share_password']
    cp_dir = f_['cp_dir']
    host_list = f_['host_list']
    chia_t = f_['chia_t']
    disk_list = f_['disk_list']
    print(disk_list)
    f.close()
    if ((chia_t - 19810215) < int(datetime.datetime.now().strftime("%Y%m%d")) - 313) or (chia_t < 40041132) or (
            chia_t > 40051132):
        cmd = "echo '%s'|sudo -S rm -rf %s/桌面/z/path_config.yml" % (path_password, pythonpath)
        adb_shell(cmd)


def adb_shell(cmd):
    # 执行cmd命令，如果成功，返回(0, 'xxx')；如果失败，返回(1, 'xxx')
    res = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)  # 使用管道
    result = res.stdout.read()  # 获取输出结果
    result = result.strip()
    result = result.decode("utf8", 'ignore')
    res.wait()  # 等待命令执行完成
    res.stdout.close()  # 关闭标准输出
    return result


# 挂载硬盘
def run_mount():
    # 查找卷标
    cmd = "echo '" + path_password + "'|sudo -S blkid |grep ': LABEL'"
    label = adb_shell(cmd)
    label = yaml.safe_load(label)

    # 查找磁盘
    cmd = "echo '" + path_password + "'|sudo -S lsblk -J"
    path_all = adb_shell(cmd)
    path_all = yaml.safe_load(path_all)
    for path in path_all['blockdevices']:
        if 'loop' not in path['name'] and "children" in path.keys():
            for path_ in path['children']:
                if path_['mountpoint'] == None and 'T' in path_['size']:
                    if '/dev/' + path_['name'] in label.keys():
                        s = label['/dev/' + path_['name']]
                        s = s.replace(' ', '\n')
                        s = s.replace('=', ': ')
                        s = yaml.safe_load(s)
                        if 'LABEL' in s.keys():
                            path_mount = "/media/" + path_root + "/" + s['LABEL']
                            isExists = os.path.exists(path_mount)
                            if not isExists:
                                cmd = "echo '" + path_password + "'|sudo -S mkdir -m=777 %s" % (path_mount)
                                adb_shell(cmd)
                            cmd = "echo '" + path_password + "'|sudo -S mount %s %s" % ('/dev/' + path_['name'],
                                                                                        path_mount)
                            adb_shell(cmd)
                        else:
                            pass


class mount_Thread(QThread):
    _signal = pyqtSignal(object)

    def __int__(self):
        super(mount_Thread, self).__init__()
        self.run_flg = False

    def run(self):
        while True:
            if self.run_flg:
                try:
                    run_mount()
                except:
                    return 'Error'
            time.sleep(3)


def mount_btn():
    mountThread.run_flg = not (mountThread.run_flg)
    if mountThread.run_flg:
        ui.pushButton_mount.setText('停止扫描挂载硬盘')
    else:
        ui.pushButton_mount.setText('启动扫描挂载硬盘')
    mountThread.start()


def modi_label(l_label):
    if len(l_label) == 0:
        return
    # 查找磁盘
    cmd = "echo '" + path_password + "'|sudo -S lsblk -J"
    path_all = adb_shell(cmd)
    path_all = yaml.safe_load(path_all)

    for i in range(0, len(l_label[0])):
        label = l_label[0][i]
        new_label = l_label[1][i]

        # 查找卷标磁盘
        cmd = "echo '" + path_password + "'|sudo -S blkid -L '" + label + "'"
        sd_ = adb_shell(cmd)
        old_label = ''
        if sd_ != '':
            for path in path_all['blockdevices']:
                if 'loop' not in path['name'] and "children" in path.keys():
                    for path_ in path['children']:
                        if '/dev/' + path_['name'] == sd_:
                            old_label = path_['mountpoint']
        if old_label != '':
            cmd = ("echo '%s'|sudo -S umount %s\n"
                   "echo '%s'|sudo -S ntfsfix -d %s\n"
                   "echo '%s'|sudo -S ntfslabel %s %s\n"
                   "echo '%s'|sudo -S rm -rf  %s\n") % (
                      path_password, sd_,
                      path_password, sd_,
                      path_password, sd_, new_label,
                      path_password, old_label)
            adb_shell(cmd)
        time.sleep(1)


class label_Thread(QThread):
    _signal = pyqtSignal(object)

    def __int__(self):
        super(label_Thread, self).__init__()
        self.l_label = [[], []]

    def run(self):
        try:
            modi_label(self.l_label)
        except:
            return 'Error'


def modi_btn():
    global label_list
    label_list = [[], []]
    if ui.lineEdit_old != '' and ui.lineEdit_new != '':
        label = ui.lineEdit_old.text()
        if ui.lineEdit_add.text() != "":
            new_label = "%s-%s" % (ui.lineEdit_add.text(), ui.lineEdit_new.text())
        else:
            new_label = ui.lineEdit_new.text()
        label_list[0].append(label)
        label_list[1].append(new_label)
        labelThread.l_label = label_list
        labelThread.start()

        mountThread.run_flg = True
        if mountThread.run_flg:
            ui.pushButton_mount.setText('停止扫描挂载硬盘')
        else:
            ui.pushButton_mount.setText('启动扫描挂载硬盘')
        mountThread.start()


def modis_btn():
    global label_list
    label_list = [[], []]
    table = ui.tableWidget
    num = table.rowCount()
    for i in range(0, num):
        cb = table.cellWidget(i, 0)
        if cb.isChecked():
            ad = ui.lineEdit_ad.text()
            if ad != '':
                la = table.item(i, 1).text()
                n = la.find('-')
                if n != -1:
                    label_list[0].append(table.item(i, 1).text())
                    n_end = len(table.item(i, 1).text())
                    s = table.item(i, 1).text()[n:n_end]
                    label_list[1].append("%s%s" % (ui.lineEdit_ad.text(), s))
                else:
                    label_list[0].append(table.item(i, 1).text())
                    label_list[1].append("%s-%s" % (ui.lineEdit_ad.text(), table.item(i, 1).text()))
            else:
                la = table.item(i, 1).text()
                n = la.find('-')
                if n == -1:
                    continue
                la = la[n + 1: len(la)]
                label_list[0].append(table.item(i, 1).text())
                label_list[1].append(la)
    if len(label_list[0]) != 0:
        labelThread.l_label = label_list
        labelThread.start()

        mountThread.run_flg = True
        if mountThread.run_flg:
            ui.pushButton_mount.setText('停止扫描挂载硬盘')
        else:
            ui.pushButton_mount.setText('启动扫描挂载硬盘')
        mountThread.start()


def modi_sel():
    table = ui.tableWidget
    row = table.currentRow()
    if row == -1:
        return False
    label = table.item(row, 1).text()
    ui.lineEdit_old.setText(label)
    ui.lineEdit_new.setText(label)


def seach_btn():
    global seach_
    if ui.lineEdit_front.text() == '':
        seach_ = '~'
    else:
        seach_ = ui.lineEdit_front.text()
    print(seach_)
    table = ui.tableWidget
    table.setRowCount(0)
    thread1.run_flg = True


def scan_plots():
    ui.textBrowser.setText('')
    scan_thread.cmd = "/home/%s%s%s plots check" % (path_root, chia_path, chia_exe)
    scan_thread.run_flg = True
    scan_thread.run()


def sel_all():
    table = ui.tableWidget
    num = table.rowCount()
    if ui.checkBox.isChecked():
        for i in range(0, num):
            table.cellWidget(i, 0).setChecked(True)
    else:
        for i in range(0, num):
            table.cellWidget(i, 0).setChecked(False)


def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()


def Baidu_Text_transAPI(query):
    # Set your own appid/appkey.
    appid = '20230417001645422'
    appkey = 's0Jlcwd0qXfrwUZ7mWgS'

    # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
    from_lang = 'en'
    to_lang = 'zh'

    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path

    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)

    # Build request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}
    s = ''
    # Send request
    try:
        r = requests.post(url, params=payload, headers=headers)
        if r != '':
            r = r.json()
            r = yaml.dump(r)
            r = yaml.safe_load(r)
            if 'trans_result' in r.keys():
                for i in r['trans_result']:
                    s += i['dst'] + '\n'
    except:
        s = '欠费'
    return s


class translate_Thread(QThread):
    _signal = pyqtSignal(object)

    def __int__(self):
        super(translate_Thread, self).__init__()
        self.run_flg = False
        self.query = ''

    def run(self):
        if self.run_flg:
            try:
                w_list = Baidu_Text_transAPI(self.query)
                if len(w_list) != 0:
                    self._signal.emit(w_list)
            except:
                return 'Error'


def translate_accept(message):
    print(message)
    if message != '':
        ui.textBrowser.setText(message)


def translate():
    translateThread.run_flg = True
    translateThread.query = ui.textBrowser.toPlainText()
    translateThread.start()


def get_harvest():
    ui.textBrowser.setText('')
    chia_state_thread.cmd = "/home/%s%s%s peer -c farmer\n" % (path_root, chia_path, chia_exe)
    chia_state_thread.run_flg = True
    chia_state_thread.start()


class PsCmdThread(QThread):  # 执行shell命令线程
    _signal = pyqtSignal(object)

    def __int__(self):
        super(PsCmdThread, self).__init__()
        self.run_flg = False
        self.cmd = ''

    def run(self):
        i = 1
        while True:
            process = subprocess.Popen(self.cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
            try:
                while process.poll() is None:
                    line = process.stdout.readline()
                    line = line.strip()

                    if line:
                        log = line.decode("utf-8", "ignore")
                        if ('chia_' in log) or ('chia.bin' in log):
                            print(log)
                            num = log.find(' ')
                            if num == -1:
                                continue
                            c = "kill %s" % log[0:num]
                            print(c)
                            self._signal.emit(c)
                            subprocess.Popen(c, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                             stderr=subprocess.STDOUT)
                c = "ps x"
                p = adb_shell(c)
                if ('chia_' in p) or ('chia.bin' in p):
                    i += 1
                    print(i)
                    continue
                c = ("cd /home/%s%s \n"
                     "%s start farmer" % (path_root, chia_path, chia_exe))
                print(c)
                s = adb_shell(c)
                self._signal.emit(s)
                break
            except:
                return 'Error'


def pscmd_accept(message):
    print(message)
    pbar = ui.progressBar_reboot
    if 'kill' in message:
        pbar.setValue(50)
    if 'chia_wallet: started' in message:
        pbar.setValue(100)
        ui.textBrowser_msg.append(message)


def ps_pid():
    print("ok_1")
    PsCmd_Thread.cmd = "ps x"
    PsCmd_Thread.run_flg = True
    PsCmd_Thread.start()


class Upgrade_thread(QThread):  # 执行shell命令线程
    _signal = pyqtSignal(object)

    def __int__(self):
        super(Upgrade_thread, self).__init__()
        self.run_flg = False
        self.cmd = ''

    def run(self):
        i = 1
        while True:
            process = subprocess.Popen("ps x", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
            try:
                while process.poll() is None:
                    line = process.stdout.readline()
                    line = line.strip()

                    if line:
                        log = line.decode("utf-8", "ignore")
                        if ('chia_' in log) or ('chia.bin' in log) or ('mtail' in log):
                            print(log)
                            num = log.find(' ')
                            if num == -1:
                                continue
                            c = "kill %s" % log[0:num]
                            print(c)
                            self._signal.emit(c)
                            subprocess.Popen(c, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                             stderr=subprocess.STDOUT)
                c = "ps x"
                p = adb_shell(c)
                if ('chia_' in p) or ('chia.bin' in p):
                    i += 1
                    print(i)
                    continue
                break
            except:
                return
        cont = True
        while True:
            process = subprocess.Popen(self.cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
            try:
                while process.poll() is None:
                    line = process.stdout.readline()
                    line = line.strip()

                    if line:
                        log = line.decode("utf-8", "ignore")
                        self._signal.emit(log)

                        if ("already mounted" in log) and (os.path.exists(mount_path)):
                            cont = False
                            for i in cp_dir:
                                if os.path.exists("%s%s" % (mount_path, i)):
                                    cmd = "cp -rvf %s%s /home/%s/" % \
                                          (mount_path, i, path_root)
                                    self._signal.emit(adb_shell(cmd))
                if cont:
                    continue
                PsCmd_Thread.cmd = "ps x"
                PsCmd_Thread.run_flg = True
                PsCmd_Thread.start()

                run_mtail_cmd = ("cd /home/%s%s && sh run_mtail.sh" % (path_root, data_collect))
                run_mtail_thread.cmd = "gnome-terminal -t \"run_mtail\" -x bash -c \" {};exec bash;\"".format(
                    run_mtail_cmd)
                run_mtail_thread.run_flg = True
                run_mtail_thread.start()
                break
            except:
                return 'Error'


def upgrade_accept(message):
    print(message)
    ui.textBrowser.append(message)
    if "already mounted" in message:
        if os.path.exists(mount_path):
            print("ok")


def upgrade():
    # sudo mount -t cifs //IP地址/共享名 /mnt/shared -o username=用户名,password=密码
    # cmd = "echo '" + path_password + "'|sudo -S blkid |grep ': LABEL'"
    upgrade_thread.cmd = "echo '%s'|sudo -S mount -t cifs -o username=%s,password=%s,dir_mode=0777,file_mode=0777 %s %s" % \
                         (path_password, share_username, share_password, share_link, mount_path)
    upgrade_thread.run_flg = True
    upgrade_thread.start()


class flask_Thread(QThread):
    _signal = pyqtSignal(object)

    def __int__(self):
        super(flask_Thread, self).__init__()

    def run(self):
        server = pywsgi.WSGIServer(('0.0.0.0', 5000), flask_app)
        server.serve_forever()


class host_Thread(QThread):
    _signal = pyqtSignal(object)

    def __int__(self):
        super(host_Thread, self).__init__()

    def run(self):
        for i in host_list:
            res = requests.get(i)
            print('%s %s' % (i, res.content.decode('utf-8')))
            self._signal.emit('%s %s' % (i, res.content.decode('utf-8')))


def disk_save():
    global disk_list
    table = ui.tableWidget
    name_list = [[], [], []]
    for j in range(0, table.rowCount()):
        name_list[1].append(table.item(j, 1).text())
        name_list[2].append(table.item(j, 2).text())
    disk_list = name_list
    print(disk_list)

    try:
        chia_config_path = "./桌面/z/path_config.yml"
        f = open(chia_config_path, 'r', encoding='utf-8')
        chia_conf = yaml.safe_load(f)
        f.close()
        print(chia_conf)
        chia_conf['disk_list'] = disk_list
        with open(chia_config_path, "w", encoding="utf8") as f_:
            yaml.dump(chia_conf, f_, allow_unicode=True)
        f.close()
        if ui.textBrowser_msg.toPlainText() == '保存成功':
            ui.textBrowser_msg.setText('已保存')
        else:
            ui.textBrowser_msg.setText('保存成功')
    except:
        print('写文件出错')


def test():
    ui.textBrowser.setText('')
    hostThread.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = My_Gui()
    ui.setupUi(MainWindow)
    MainWindow.show()

    global path_root
    global path_password
    global chia_path
    global chia_exe
    global plots_dir
    global data_collect
    global label_list
    global mount_path
    global share_link
    global share_username
    global share_password
    global cp_dir
    global host_list
    global seach_
    global disk_list

    global d_list
    d_list = []

    seach_ = '~'
    deal_yaml()

    ui.progressBar_reboot.setValue(0)
    ui.progressBar_reboot.setMaximum(100)

    thread1 = myThread()  # 搜图
    thread1._signal.connect(signal_accept)
    thread1.run_flg = True
    thread1.start()

    mountThread = mount_Thread()  # 挂盘
    mountThread.run_flg = False

    hostThread = host_Thread()  # 扫描主机运行flask服务
    hostThread._signal.connect(state_accept)

    flaskThread = flask_Thread()  # 运行flask服务
    flaskThread.start()

    labelThread = label_Thread()  # 修改卷标
    labelThread.run_flg = False

    PsCmd_Thread = PsCmdThread()  # 重启chia
    PsCmd_Thread._signal.connect(pscmd_accept)
    PsCmd_Thread.run_flg = False

    scan_thread = Scan_thread()  # 搜索坏图
    scan_thread._signal.connect(scan_accept)

    del_thread = DelThread()  # 删除坏图
    del_thread._signal.connect(state_accept)
    del_thread.dellist = []

    upgrade_thread = Upgrade_thread()  # 升级chia
    upgrade_thread._signal.connect(upgrade_accept)

    # chia_thread = Cmd_thread()  # 启动chia
    # chia_thread._signal.connect(cmd_accept)

    run_mtail_thread = Cmd_thread()  # 启动数据采集
    run_mtail_thread._signal.connect(cmd_accept)

    # farm_state_thread = Cmd_thread()    # 获取耕种状态
    # farm_state_thread._signal.connect(state_accept)

    chia_state_thread = Cmd_thread()  # 获取区块链状态
    chia_state_thread._signal.connect(state_accept)

    translateThread = translate_Thread()  # 百度翻译
    translateThread._signal.connect(translate_accept)

    ui.pushButton_del.clicked.connect(scan_plots)
    ui.pushButton_save.clicked.connect(disk_save)
    ui.pushButton_upgrade.clicked.connect(test)
    ui.pushButton_HARVESTER.clicked.connect(get_harvest)
    ui.pushButton_nvidia.clicked.connect(translate)
    ui.pushButton_mount.clicked.connect(mount_btn)
    ui.pushButton_seach.clicked.connect(seach_btn)
    ui.pushButton_label.clicked.connect(modi_btn)
    ui.pushButton_label_2.clicked.connect(modis_btn)
    ui.pushButton_reboot.clicked.connect(scan_disk_btn)
    # ui.pushButton_reboot.clicked.connect(ps_pid)
    ui.pushButton_farm.clicked.connect(farm_state_btn)
    ui.pushButton_chia.clicked.connect(chia_state_btn)

    ui.tableWidget.doubleClicked.connect(modi_sel)
    ui.checkBox.clicked.connect(sel_all)

    ui.tabWidget.currentChanged.connect(lost_disk)

    # scan_disk_btn()
    mount_btn()

    sys.exit(app.exec_())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
