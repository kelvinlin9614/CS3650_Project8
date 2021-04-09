import sys
import glob
import os
import re


class write_code:
    def __init__(self, file_name):
        self.file_name = file_name
        self.labelNo = 0
        self.label_prefix = ''

    def set_filename(self, file_name):
        self.prefix = os.path.splitext(os.path.basename(file_name))[0] + '.'

    def next_label(self):
        self.labelNo += 1
        return self.label_prefix + 'LABEL' + str(self.labelNo)

    def function_label(self, func):
        return func

    def write(self, line):
        self.file_name.write(line + '\n')

    def write_comment(self, text):
        self.write('// ' + text)

    def push(self):
        self.write('@SP')
        self.write('M=M+1')
        self.write('A=M-1')
        self.write('M=D')

    def push_const(self, value):
        self.write('@' + str(value))
        self.write('D=A')
        self.push()

    def push_register(self, register):
        self.write('@' + register)
        self.write('D=M')
        self.push()

    def push_segment(self, segmentRegister, address):
        self.write('@' + segmentRegister)
        self.write('D=M')
        self.write('@' + address)
        self.write('A=D+A')
        self.write('D=M')
        self.push()

    def push_segment_address(self, segment):
        self.write('@' + segment)
        self.write('D=M')
        self.push()

    def pop(self):
        self.write('@SP')
        self.write('AM=M-1')
        self.write('D=M')

    def pop_register(self, register):
        self.pop()
        self.write('@' + register)
        self.write('M=D')

    def pop_segment(self, segmentRegister, address):
        self.write('@' + segmentRegister)
        self.write('D=M')
        self.write('@' + address)
        self.write('D=D+A')
        self.write('@R13')
        self.write('M=D')
        self.pop()
        self.write('@R13')
        self.write('A=M')
        self.write('M=D')

    def write_push(self, segment, address):
        if segment == 'constant':
            self.push_const(address)
        elif segment == 'pointer':
            self.push_register('R' + str(3 + int(address)))
        elif segment == 'temp':
            self.push_register('R' + str(5 + int(address)))
        elif segment == 'static':
            self.push_register(self.prefix + address)
        elif segment == 'local':
            self.push_segment('LCL', address)
        elif segment == 'argument':
            self.push_segment('ARG', address)
        elif segment == 'this':
            self.push_segment('THIS', address)
        elif segment == 'that':
            self.push_segment('THAT', address)
        else:
            raise Exception('Unknown push segment ' + segment)

    def write_pop(self, segment, address):
        if segment == 'pointer':
            self.pop_register('R' + str(3 + int(address)))
        elif segment == 'temp':
            self.pop_register('R' + str(5 + int(address)))
        elif segment == 'static':
            self.pop_register(self.prefix + address)
        elif segment == 'local':
            self.pop_segment('LCL', address)
        elif segment == 'argument':
            self.pop_segment('ARG', address)
        elif segment == 'this':
            self.pop_segment('THIS', address)
        elif segment == 'that':
            self.pop_segment('THAT', address)
        else:
            raise Exception('Unknown pop segment ' + segment)

    def write_neg(self):
        self.write('@SP')
        self.write('A=M-1')
        self.write('M=-M')

    def write_not(self):
        self.write('@SP')
        self.write('A=M-1')
        self.write('M=!M')

    def write_and(self):
        self.write('@SP')
        self.write('AM=M-1')
        self.write('D=M')
        self.write('A=A-1')
        self.write('M=D&M')

    def write_or(self):
        self.write('@SP')
        self.write('AM=M-1')
        self.write('D=!M')
        self.write('A=A-1')
        self.write('M=!M')
        self.write('M=D&M')
        self.write('M=!M')

    def write_add(self):
        self.write('@SP')
        self.write('AM=M-1')
        self.write('D=M')
        self.write('A=A-1')
        self.write('M=D+M')

    def write_sub(self):
        self.write('@SP')
        self.write('AM=M-1')
        self.write('D=M')
        self.write('A=A-1')
        self.write('M=M-D')

    def write_eq(self):
        label1 = self.next_label()
        label2 = self.next_label()
        self.write('@SP')
        self.write('AM=M-1')
        self.write('D=M')
        self.write('A=A-1')
        self.write('D=M-D')
        self.write('@' + label1)
        self.write('D;JEQ')
        self.write('@SP')
        self.write('A=M-1')
        self.write('M=0')
        self.write_goto(label2)
        self.write_label(label1)
        self.write('@SP')
        self.write('A=M-1')
        self.write('M=-1')
        self.write_label(label2)

    def write_lt(self):
        label1 = self.next_label()
        label2 = self.next_label()
        self.write('@SP')
        self.write('M=M-1')
        self.write('A=M')
        self.write('D=M')
        self.write('A=A-1')
        self.write('D=M-D')
        self.write('@' + label1)
        self.write('D;JLT')
        self.write('@SP')
        self.write('A=M-1')
        self.write('M=0')
        self.write_goto(label2)
        self.write_label(label1)
        self.write('@SP')
        self.write('A=M-1')
        self.write('M=-1')
        self.write_label(label2)

    def write_gt(self):
        label1 = self.next_label()
        label2 = self.next_label()
        self.write('@SP')
        self.write('M=M-1')
        self.write('A=M')
        self.write('D=M')
        self.write('A=A-1')
        self.write('D=M-D')
        self.write('@' + label1)
        self.write('D;JGT')
        self.write('@SP')
        self.write('A=M-1')
        self.write('M=0')
        self.write_goto(label2)
        self.write_label(label1)
        self.write('@SP')
        self.write('A=M-1')
        self.write('M=-1')
        self.write_label(label2)

    def write_label(self, label):
        self.write('(' + label + ')')

    def write_goto(self, label):
        self.write('@' + label)
        self.write('0;JMP')

    def write_if(self, label):
        self.pop()
        self.write('@' + label)
        self.write('D;JNE')

    def write_call(self, function, arg_count):
        return_addr = self.next_label()
        self.write('@' + return_addr)
        self.write('D=A')
        self.push()
        self.push_segment_address('LCL')
        self.push_segment_address('ARG')
        self.push_segment_address('THIS')
        self.push_segment_address('THAT')
        self.write('@SP')
        self.write('D=M')
        self.write('@' + str(arg_count + 5))
        self.write('D=D-A')
        self.write('@ARG')
        self.write('M=D')
        self.write('@SP')
        self.write('D=M')
        self.write('@LCL')
        self.write('M=D')
        self.write_goto(self.function_label(function))
        self.write_label(return_addr)

    def write_function(self, function, local_count):
        self.label_prefix = function + '$'
        self.write_label(self.function_label(function))
        self.write('D=0')
        for i in range(local_count):
            self.push()

    def write_return(self):
        self.write('@LCL')
        self.write('D=M')
        self.write('@R13')
        self.write('M=D')
        self.write('@5')
        self.write('A=D-A')
        self.write('D=M')
        self.write('@R14')
        self.write('M=D')
        self.pop()
        self.write('@ARG')
        self.write('A=M')
        self.write('M=D')
        self.write('@ARG')
        self.write('D=M+1')
        self.write('@SP')
        self.write('M=D')
        self.write('@R13')
        self.write('AM=M-1')
        self.write('D=M')
        self.write('@THAT')
        self.write('M=D')
        self.write('@R13')
        self.write('AM=M-1')
        self.write('D=M')
        self.write('@THIS')
        self.write('M=D')
        self.write('@R13')
        self.write('AM=M-1')
        self.write('D=M')
        self.write('@ARG')
        self.write('M=D')
        self.write('@R13')
        self.write('AM=M-1')
        self.write('D=M')
        self.write('@LCL')
        self.write('M=D')
        self.write('@R14')
        self.write('A=M')
        self.write('0;JMP')
        self.label_prefix = ''

    def write_init(self):
        self.write('@256')
        self.write('D=A')
        self.write('@SP')
        self.write('M=D')
        self.write_comment('call Sys.init')
        self.write_call('Sys.init', 0)


class Parse:
    def __init__(self, code_writer):
        self.writer = code_writer

    def strip(self, line):
        line = re.sub('//.*', '', line)
        line = re.sub('(^\s|\s*$)', '', line)
        return line

    def parse_file(self, filename):
        self.writer.set_filename(filename)
        with open(filename) as file:
            for line in file.readlines():
                line = self.strip(line)
                if len(line):
                    self.parse_line(line)

    def parse_line(self, line):
        self.writer.write_comment(line)
        word = line.split()
        command = word[0]
        args = word[1:]
        if command == 'push':
            self.writer.write_push(args[0], args[1])
        elif command == 'pop':
            self.writer.write_pop(args[0], args[1])
        elif command == 'add':
            self.writer.write_add()
        elif command == 'sub':
            self.writer.write_sub()
        elif command == 'eq':
            self.writer.write_eq()
        elif command == 'lt':
            self.writer.write_lt()
        elif command == 'gt':
            self.writer.write_gt()
        elif command == 'neg':
            self.writer.write_neg()
        elif command == 'and':
            self.writer.write_and()
        elif command == 'or':
            self.writer.write_or()
        elif command == 'not':
            self.writer.write_not()
        elif command == 'label':
            self.writer.write_label(args[0])
        elif command == 'goto':
            self.writer.write_goto(args[0])
        elif command == 'if-goto':
            self.writer.write_if(args[0])
        elif command == 'call':
            self.writer.write_call(args[0], int(args[1]))
        elif command == 'function':
            self.writer.write_function(args[0], int(args[1]))
        elif command == 'return':
            self.writer.write_return()
        else:
            raise Exception('Unknown command ' + command)


def translator_file(file):
    asm_filename = os.path.splitext(file)[0] + ".asm"
    with open(asm_filename, "w") as asm_file:
        writer = write_code(asm_file)
        parser = Parse(writer)
        parser.parse_file(file)


def translator_dir(dir):
    asm_filename = dir + '/' + os.path.basename(dir) + '.asm'
    with open(asm_filename, "w") as asm_file:
        writer = write_code(asm_file)
        writer.write_init()
        parser = Parse(writer)
        for file in glob.glob(dir + "/*.vm"):
            writer.write_comment('file ' + file)
            parser.parse_file(file)


def main(argv):
    if os.path.isdir(argv[0]) and len(argv) == 1:
        translator_dir(argv[0])
    elif os.path.splitext(argv[0])[1] == ".vm" and len(argv) == 1:
        translator_file(argv[0])
    else:
        print("invalid")
        print()


main(sys.argv[1:])
