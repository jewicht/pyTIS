import re
import sys
import threading
try:
    from queue import Queue
except:
    from Queue import Queue
from time import sleep

def sanitize(instruction):
    return ' '.join(instruction.split()).upper()

def intchecker(val):
    try:
        tmp = int(val)
        if abs(tmp)>999:
            raise Exception("Value too large")
    except:
        raise Exception("Integer not understood")
        

class CPU(threading.Thread):
    def __init__(self, left=None, right=None, up=None, down=None):
        super(CPU, self).__init__()
        self._acc = 0
        self._bak = 0
        self._program = []
        self._labels = {}

        self._queues = {
            'LEFT': left,
            'RIGHT': right,
            'UP': up,
            'DOWN': down
        }

        self.bakEdit = None
        self.accEdit = None

    def updateaccbak(self):
        if self.bakEdit is not None:
            self.bakEdit.setText(str(self._bak))
        if self.accEdit is not None:
            self.accEdit.setText(str(self._acc))
        
    def findlabel(self, label):
        if not label in self._labels:
            raise Exception("Label not found")
        return self._labels[label]

    def validate(self, i):
        instruction = self._program[i]
        if instruction == '':
            return
        
        operands = instruction.split(' ')

        
        if operands[0] == "MOV":
            if len(operands) != 3:
                raise Exception("MOV: too many arguments")
            src = operands[1]
            if src in ['UP', 'DOWN', 'LEFT', 'RIGHT', 'ACC']:
                pass
            else:
                intchecker(src)

            dst = operands[2]
            if dst in ['UP', 'DOWN', 'LEFT', 'RIGHT', 'ACC']:
                pass
            else:
                raise Exception("MOV destination not understood")
            return

        #math
        if operands[0] in ["ADD", "SUB"]:
            if len(operands) != 2:
                raise Exception(operands[0] + ": too many operands")
            if operands[1] in ['UP', 'DOWN', 'LEFT', 'RIGHT', 'ACC']:
                pass
            else:
                intchecker(operands[1])
            return

        if operands[0] in ["SWP", "SAV"]:
            if len(operands) != 1:
                raise Exception(operands[0] + ": too many operands")
            return

        if operands[0] in ["JNZ", "JEZ", "JGZ", "JLZ", "JMP"]:
            if len(operands) != 2:
                raise Exception(operands[0] + ": too many operands")
            self.findlabel(operands[1])
            return
        
        if operands[0] == "JRO":
            if len(operands) != 2:
                raise Exception("JRO: too many operands")
            if operands[1] == "ACC":
                return
            intchecker(operands[i])
            return

        if instruction.endswith(':'):
            return
        
        raise Exception("instruction not understood " + instruction)
   
    
                
    def process(self, i):
        instruction = self._program[i]
        operands = instruction.split(' ')
        
        if operands[0] == "MOV":
            src = operands[1]
            if src in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
                tmp = self._queues[src].get(block=True, timeout=5)
            elif src == 'ACC':
                tmp = self._acc
            else:
                tmp = int(src)

            dst = operands[2]
            if dst in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
                self._queues[dst].put(tmp, block=True, timeout=5)
            else:
                self._acc = tmp
                self.updateaccbak()
            return i+1

        #math
        if operands[0] == "SUB":
            if operands[1] in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
                self._acc -= self._queues[operands[1]].get(block=True, timeout=5)
            elif operands[1] == "ACC":
                self._acc -= self._acc
            else:
                self._acc -= int(operands[1])
            if self._acc > 999:
                self._acc = 999
            if self._acc < -999:
                self._acc = -999
            self.updateaccbak()
            return i+1

        if operands[0] == "ADD":
            if operands[1] in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
                self._acc += self._queues[operands[1]].get(block=True, timeout=5)
            elif operands[1] == "ACC":
                self._acc += self._acc
            else:
                self._acc += int(operands[1])
            if self._acc > 999:
                self._acc = 999
            if self._acc < -999:
                self._acc = -999
            self.updateaccbak()
            return i+1

        if operands[0] == "SWP":
            self._acc, self._bak = self._bak, self._acc
            self.updateaccbak()
            return i+1

        if operands[0] == "SAV":
            self._bak = self._acc
            self.updateaccbak()
            return i+1
        
        if operands[0] == "JNZ":
            if (self._acc != 0):
                return self.findlabel(operands[1])
            return i+1
        
        if operands[0] == "JEZ":
            if (self._acc == 0):
                return self.findlabel(operands[1])
            return i+1
        
        if operands[0] == "JGZ":
            if (self._acc > 0):
                return self.findlabel(operands[1])
            return i+1
        
        if operands[0] == "JLZ":
            if (self._acc < 0):
                return self.findlabel(operands[1])
            return i+1
        
        if operands[0] == "JMP":
            return self.findlabel(operands[1])
        
        if operands[0] == "JRO":
            if operands[1] == "ACC":
                return i + self._acc
            return i + int(operands[1])

        return i+1


    def setprogram(self, instructions):
        self._labels = {}
        self._program = []
        for instruction in instructions:

            if ':' in instruction:
                s1, s2 = instruction.split(':')
                s1 = sanitize(s1) + ':'
                s2 = sanitize(s2)
                self._program.append(s1)
                self._program.append(s2)
            else:
                self._program.append(sanitize(instruction))

        #find labels:
        for cnt, instruction in enumerate(self._program):
            m = re.match('(.*):(.*)', instruction)
            if m:
                self._labels[m.group(1)] = cnt
        
        #validate
        for cnt, instruction in enumerate(self._program):
            self.validate(cnt)
        
    def run(self):
        if len(self._program) == 0:
            return
        if len(self._program) == 1 and self._program[0] == "":
            return
        print(len(self._program))
        lineno = 0
        iter = 0
        self.kill = False
        while not self.kill:
            lineno = self.process(lineno)
            sleep(0.1)
            self.printstate()
            if lineno >= len(self._program):
                lineno = 0

    def stop(self):
        self.kill = True
        for n, q in self._queues.items():
            if q.qsize() == 0:
                q.put(1)
            sleep(0.01)
            if q.qsize() == 1:
                q.get(False)
            sleep(0.01)

    def printstate(self):
        print("ACC = {} BAK = {}".format(self._acc, self._bak))
            

class Broken:
    def __init__(self):
        pass

class Stack:
    def __init(self):
        pass

        

class TIS:
    def __init__(self):
        h, w = 3, 3

        ud_queue = [[Queue(1) for x in range(w)] for y in range(h+1)]
        lr_queue = [[Queue(1) for x in range(w+1)] for y in range(h)]
        
        cpus = [[CPU(lr_queue[y][x], lr_queue[y][x+1], ud_queue[y][x], ud_queue[y+1][x]) for x in range(w)] for y in range(h)]
    

