"""
Definition of basic components of PIC18F simulator

DataMemory: memory for storing General Purpose Registers and Specific Purpose Registers
ProgramMemory: memory for storing operation objects corresponding to opcodes
Stack: stack memory
PC: program counter structure
MCU: main class describing core of PIC18F
"""
from op import NOP
from register import *

class DataMemory:
    """ Data memory of PIC """
    def __init__(self, trace):
        self.trace = trace
        self.memory = {
                WREG: ByteRegister(WREG, trace),
                BSR: ByteRegister(BSR, trace),
                STATUS: Status(trace),
                STKPTR: ByteRegister(STKPTR, trace)
                }
    def __getitem__(self, addr):
        return self.memory.setdefault(addr, ByteRegister(addr, self.trace))

class ProgramMemory:
    """ Program memory of PICmicro """
    SIZE = 0x200000
    def __init__(self):
        self.memory = [NOP()] * (self.SIZE >> 1)
    def __getitem__(self, addr):
        return self.memory[addr >> 1]
    def __setitem__(self, addr, op):
        self.memory[addr >> 1] = op

class Stack:
    """ Stack memory """
    SIZE = 31
    STKFUL, STKUNF = 7, 6
    def __init__(self, stkptr_reg, trace):
        self.ws = self.statuss = self.bsrs = 0
        self.memory = [0] * self.SIZE
        self.stkptr_reg = stkptr_reg
        self.trace = trace
    def push(self, data):
        assert 0 <= data < ProgramMemory.SIZE
        stkptr = self.stkptr_reg.get()
        if (stkptr & 0x1f) == 0x1f:
            self.stkptr_reg[self.STKFUL] = 1
            trace.add_event(('stack_is_full',))
            return
        self.memory[stkptr & 0x1f] = data
        self.stkptr_reg.put(stkptr + 1)
        self.trace.add_event(('stack_push', data))
    def pop(self):
        stkptr = self.stkptr_reg.get()
        if (stkptr & 0x1f) == 0:
            self.stkptr_reg[self.STKUNF] = 1
            trace.add_event(('stack_is_unfull',))
            return
        self.stkptr_reg.put(stkptr - 1)
        data = self.memory[(stkptr - 1) & 0x1f]
        self.trace.add_event(('stack_pop', data))
        return data

class PC: 
    """ Program counter """
    MAX_VALUE = ProgramMemory.SIZE
    def __init__(self):
        self.value = 0
    def inc(self, delta):
        self.value = (self.value + delta) % self.MAX_VALUE

class TraceBuf:
    """ Buffer for saving of trace logs """
    SIZE = 128
    def __init__(self):
        self.buf = [None] * self.SIZE
        self.index = 0
        self.iter_index = 0
    def add_event(self, event):
        self.buf[self.index] = event
        self.index = (self.index + 1) % self.SIZE
        if self.index == self.iter_index:
            self.iter_index = (self.iter_index + 1) % self.SIZE
    def __iter__(self):
        return self
    def next(self):
        if self.iter_index == self.index:
            raise StopIteration()
        item = self.buf[self.iter_index]
        self.iter_index = (self.iter_index + 1) % self.SIZE
        return item

class MCU(object): 
    """ PIC18F microprocessor core unit """
    def __init__(self):
        self.trace = TraceBuf()
        self.pc = PC()
        self.data = DataMemory(self.trace)
        self.program = ProgramMemory()
        self.stack = Stack(self.data[STKPTR], self.trace)



















#class Stack:
    #"""Stack memory of PIcarry-lookahead adderC18F"""
    #SIZE = 31
    #def __init__(self):
        #"""Initialize stack and fast registries of stack"""
        #self.storage = [0] * self.SIZE
        #self.stkptr = 0
        #self.wregs = self.statuss = self.bsrs = 0
    #def push(self, value):
        #"""Push value on top of stack"""
        #assert 0 <= value < self.PC_SUP
        #if self.stkptr > self.SIZE:
            #return
        #self.storage[self.stkptr] = value
        #self.stkptr += 1
    #def pop(self):
        #"""Pop value from top of stack"""
        #if self.stkptr == 0:
            #return 0
        #self.stkptr -= 1
        #return self.storage[self.stkptr]
    #@property
    #def top(self):
        #if self.stkptr == 0:
            #return 0
        #return self.storage[self.stkptr - 1]
    #@top.setter
    #def top(self, value):
        #assert 0 <= value < PC_SUP
        #if self.stkptr == 0:
            #return
        #self.storage[self.stkptr - 1] = value

