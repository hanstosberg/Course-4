text = """
5 PRINT TAB(24);"TICKERTAPE"
6 PRINT TAB(20);"CREATIVE COMPUTING"
7 PRINT TAB(18);"MORRISTOWN, NEW JERSEY"
9 PRINT:PRINT:PRINT
10 INPUT A$:GOSUB 80
20 FOR N=1 TO LEN(A$)
25 B=ASC(MID$(A$,N,1))
30 IF B>90 THEN 47
33 IF B<65 THEN 40
35 B=B-64
37 GOTO 50
40 IF B>57 OR B<48 THEN 47
43 B=B-20
45 GOTO 50
47 B=27
50 FOR S=0 TO (B-1)*5:READ A:NEXT S
60 FOR S=1 TO 5:READ A:GOSUB 1000:NEXT S
65 A=0:GOSUB 1000:RESTORE
70 NEXT N
75 GOSUB 80:END
80 FOR N=1 TO 30:A=0:GOSUB 1000:NEXT N
90 RETURN
110 DATA 0,254,9,9,9,254,255,137,137,137,118,126,129,129,129,129
120 DATA 255,129,129,129,126,255,137,137,137,137,255,9,9,9,1
130 DATA 126,129,129,145,243,255,8,8,8,255,129,129,255,129,129
140 DATA 96,128,129,127,1,255,8,20,34,193,255,128,128,128,128
150 DATA 255,2,12,2,255,255,2,60,64,255,126,129,129,129,126
160 DATA 255,9,9,9,6,126,129,161,65,190
170 DATA 255,25,41,73,134,134,137,137,137,113,1,1,255,1,1
180 DATA 127,128,128,128,127,63,96,192,96,63,127,128,112,128,127
215 DATA 195,36,24,36,195,3,4,248,4,3,193,161,145,137,135
220 DATA 0,0,0,0,0,126,161,137,133,126,132,130,255,128,128,194,161,145
230 DATA 137,134,66,137,137,137,118,12,10,137,255,136,199,137,137,137
240 DATA 248,126,137,137,137,114,1,1,249,5,2,118,137,137,137,118
250 DATA 70,137,137,137,126
1000 FOR I = 1 TO 8
1010 IF A < 128 THEN PRINT " ";:GOTO 1030
1020 PRINT "*";:A=A-128
1030 A = A * 2
1040 NEXT I
1050 PRINT
1060 RETURN
"""

import re

class DataTable:
    data = []
    code = []
    read_index = 0
    vars = {}

code_data = DataTable()

def ASC(a):
    return ord(a)

def LEN(a):
    a = code_data.vars[a]
    return len(a)

def MID(s, a, b):

    global code_data;
    if not a.isdigit():
       a = code_data.vars[a]
    if not b.isdigit():
       b = code_data.vars[b]

    a -= 1
    s = code_data.vars[s]

    return s[int(a):int(a)+int(b)]

def apply_function(expression):
    if re.match("[A-Za-z$]+\(.*\)", expression):
        func = expression.split("(")[0]

        body = apply_function("(".join(expression.split("(")[1:])[:-1])

        if func == 'ASC':
            return ASC(body)
        elif func == 'MID$':
            return MID(*body)
        elif func == 'LEN':
            return LEN(body)

    else:
        if "," in expression:
            return expression.split(",")
        else:
            return calculate(to_rpn(expression))



def is_operator(char):
    return char in ['+', '-', '*', '/', '>', '<', "OR"]

def to_rpn(expression):

    symbols = ['+', '-', '*', '/', '>', '<', "(", ")", "OR"]

    for i in symbols:
        expression = expression.replace(i, f" {i} ")

    stack = []
    output = []
    precedence = {'+': 2, '-': 2, '*': 3, '/': 2, '>' : 1, '<' : 1, "OR" : 0}

    for char in expression.split():
        if is_operator(char):
            while stack and is_operator(stack[-1]) and precedence[char] <= precedence[stack[-1]]:
                output.append(stack.pop())
            stack.append(char)
        elif char == '(':
            stack.append(char)
        elif char == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()

        else:
            output.append(char)

    while stack:
        output.append(stack.pop())

    return ' '.join(output)

def calculate(expression):
    global code_data

    stack = []
    operators = {'+', '-', '*', '/', '>', '<', "OR"}

    for element in expression.split():
        if element not in operators:
            stack.append(element)
        else:
            operand2 = stack.pop()
            operand1 = stack.pop()

            if not type(operand2) in (float, bool):
                if not operand2.isdigit():
                    operand2 = code_data.vars[operand2]
                else:
                    operand2 = float(operand2)

            if not type(operand1) in (float, bool):
                if not operand1.isdigit():
                    operand1 = code_data.vars[operand1]
                else:
                    operand1 = float(operand1)

            if element == '+':
                result = operand1 + operand2
            elif element == '-':
                result = operand1 - operand2
            elif element == '*':
                result = operand1 * operand2
            elif element == '/':
                result = operand1 / operand2
            elif element == '>':
                result = operand1 > operand2
            elif element == '<':
                result = operand1 < operand2
            elif element == 'OR':
                result = operand1 or operand2

            stack.append(result)

    return stack[0]

def parse_code(code):
    global code_data

    code = code.replace(":", "\n0 ")
    code = code.replace("THEN", "THEN\n0 ")

    result = []

    for line in code.split("\n"):
        line = line.strip()
        if len(line) == 0: continue;

        splited_line = line.split()

        idx = int(splited_line[0])
        s = " ".join(splited_line[1:])

        if re.match("^DATA.*", s):
            data = list([int(i) for i in s.strip("DATA").split(",")])
            code_data.data += data
        else:
            splited_line = line.split()
            result.append([idx, s])

    for i in range(len(result)):
        if result[i][1].isdigit():
            result[i][1] = f"GOTO {result[i][1]}"

    code_data.code = result

def eval_str(current_line):
    current_line = current_line.strip()

    if re.match("^PRINT.*", current_line):
        body = re.search("(?<=PRINT ).*", current_line)

        if body != None:

            body = body.group(0).split(";")

            for i in body:
                if re.match("^TAB()", i):
                    print()
                    count = int(re.search("\((.*?)\)", current_line).group(0).strip("(").strip(")"))
                    for i in range(count):
                        print(" ", end="")
                elif re.match('\"*\"', i):
                    b = re.search('\"(.*?)\"', current_line).group(0).strip("\"")
                    print(b, end="")
        else:
            print()
    elif re.match("^RESTORE.*", current_line):
        code_data.read_index = 0
    elif re.match("^GOSUB.*", current_line):
        body = int(current_line.split()[1])
        eval_code(body)
    elif re.match("^READ.*", current_line):
        body = current_line.split()[1]
        code_data.vars[body] = code_data.data[code_data.read_index]
        code_data.read_index += 1
    elif "=" in current_line: #re.match("([A-Za-z]+\s*=*)", current_line):
        left = re.search('^(.*?)=', current_line).group(0)[:-1].strip()
        right = re.search('(?<==)(.*)$', current_line).group(0)
        code_data.vars[left] = float(apply_function(right))

        return left
    else:
        return float(apply_function(current_line))


def eval_code(idx = None, true_idx = 0, before_zero = False):
    global code_data

    if idx != None:
        for i in range(len(code_data.code)):
            if code_data.code[i][0] == idx:
                true_idx = i

    current_line = code_data.code[true_idx][1]

    if before_zero and code_data.code[true_idx][0] != 0: return true_idx


    if re.match("^INPUT.*", current_line):
        body = current_line.split()[1]
        code_data.vars[body] = str(input("? "))
    elif re.match("^RETURN.*", current_line):
        return
    elif re.match("^END.*", current_line):
        return
    elif re.match("^NEXT.*", current_line):
        return true_idx
    elif re.match("^GOTO.*", current_line):
        body = int(current_line.split()[1])
        for i in range(len(code_data.code)):
            if code_data.code[i][0] == body:
                true_idx = i - 1

    elif re.match("^IF.*", current_line):
        fr = re.search('IF.*.THEN', current_line).group(0).strip("IF").strip("THEN")
        exp = bool(eval_str(fr))
        b = False
        if(exp):
            pass
        else:
            for i in range(true_idx + 1, len(code_data.code)):
                if code_data.code[i][0] != 0:
                    true_idx = i - 1
                    break
    elif re.match("^FOR.*", current_line):
        fr = re.search('FOR.*.TO', current_line).group(0).strip("FOR").strip("TO")
        eval_str(fr.strip())
        to = current_line.split("TO")[-1]
        var = fr.split("=")[0].strip()

        next_idx = true_idx
        for i in range(true_idx + 1, len(code_data.code)):
            if re.match(f"^NEXT {var}", code_data.code[i][1]):
                next_idx = i
                break

        while(int(code_data.vars[var]) < int(eval_str(to)) + 1):
            eval_code(None, true_idx + 1, False)
            code_data.vars[var] += 1

        true_idx = next_idx

    else:
        eval_str(current_line)

    if(len(code_data.code) > true_idx + 1):
        eval_code(None, true_idx + 1)

parse_code(text)
eval_code()
