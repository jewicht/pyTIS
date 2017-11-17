import sys
try:
    from queue import Queue
except:
    from Queue import Queue

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from pyTIS.cpu import CPU


class TISWidget(QWidget):
    def __init__(self, h=3, w=3):
        super(TISWidget, self).__init__()
        self.initUI()  

    def initUI(self):
        grid = QGridLayout()

        
class CPUWidget(QWidget):
    def __init__(self, cpu=None):
        super(CPUWidget, self).__init__()
        if cpu is None:
            self.cpu = CPU()
        else:
            self.cpu = cpu
        self.initUI()
            
    def initUI(self):
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        #self.te = QTextEdit()
        self.te = QPlainTextEdit()
        #self.te.setFixedHeight(14 * self.te.fontMetrics().lineSpacing())
        
        vbox.addWidget(self.te)
        
        grid = QGridLayout()
        #self.setLayout(grid)


        accLabel = QLabel('ACC')
        self.accEdit = QLineEdit()
        self.accEdit.setReadOnly(True)
        self.accEdit.setMaxLength(3)
        self.accEdit.setText("0")
        self.cpu.accEdit = self.accEdit
        
        bakLabel = QLabel('BAK')
        self.bakEdit = QLineEdit()
        self.bakEdit.setReadOnly(True)
        self.bakEdit.setMaxLength(3)
        self.bakEdit.setText("0")
        self.cpu.bakEdit = self.bakEdit
        
        grid.addWidget(accLabel, 0, 0) 
        grid.addWidget(self.accEdit, 0, 1)

        grid.addWidget(bakLabel, 1, 0)
        grid.addWidget(self.bakEdit, 1, 1)
        
        vbox.addLayout(grid)
        
        self.show()

    def run(self):
        program = []
        for string in self.te.toPlainText().split('\n'):
            program.append(str(string))
        self.cpu.setprogram(program)
        self.cpu.start()

    def stop(self):
        self.cpu.stop()
        self.cpu.join()

class TISWidget(QWidget):
    def __init__(self, h=3, w=3):
        super(TISWidget, self).__init__()
        self._h, self._w = h, w

        self._ud_queue = [[Queue(1) for x in range(self._w)] for y in range(self._h+1)]
        self._lr_queue = [[Queue(1) for x in range(self._w+1)] for y in range(self._h)]
        
        self._cpus = [[CPU(self._lr_queue[y][x], self._lr_queue[y][x+1], self._ud_queue[y][x], self._ud_queue[y+1][x]) for x in range(self._w)] for y in range(self._h)]
        self._cpuwidgets = [[0 for x in range(self._w)] for y in range(self._h)]
        
        self.initUI()  

    def initUI(self):
        grid = QGridLayout()

        for x in range(self._w):
            for y in range(self._h):
                onecpu = CPUWidget(self._cpus[y][x])
                grid.addWidget(onecpu, y, x)
                self._cpuwidgets[y][x] = onecpu
                
        self.setLayout(grid)

        runbutton = QPushButton("Run")
        runbutton.clicked.connect(self.run)
        stopbutton = QPushButton("Stop")
        stopbutton.clicked.connect(self.stop)
        
        grid.addWidget(runbutton,  self._h, 0)
        grid.addWidget(stopbutton, self._h, 1)
        
        self.show()

    def run(self):
        for x in range(self._w):
            for y in range(self._h):
                self._cpuwidgets[y][x].run() 

    def stop(self):
        for x in range(self._w):
            for y in range(self._h):
                self._cpuwidgets[y][x].stop() 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = TISWidget(3, 3)
    sys.exit(app.exec_())
