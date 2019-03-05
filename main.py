from enum import Enum
import sys

class OPERATOR(Enum):
    INVALID=-1
    NONE=0
    NUM=1
    PLUS=2
    MINUS=3
    MULTIPLY=4
    DIVIDE=5
    POWER=6

class Token():
    type=OPERATOR.NUM
    value=0
    def numeric(self,n):
        self.type=OPERATOR.NUM
        self.value=n
        return self
    def operator(self,o):
        self.type=o
        return self
    def brackets(self,n):
        self.value=n
        return self
    def getPriority(self):
        typePriorities={OPERATOR.PLUS:0,
                        OPERATOR.MINUS:0,
                        OPERATOR.MULTIPLY:1,
                        OPERATOR.DIVIDE:2,
                        OPERATOR.POWER:3}
        return self.value*256+typePriorities[self.type]
    def operatorAsString(self):
        lookup={OPERATOR.INVALID:"invalid",
                OPERATOR.NONE:"none",
                OPERATOR.NUM:"number",
                OPERATOR.PLUS:"+",
                OPERATOR.MINUS:"-",
                OPERATOR.MULTIPLY:"*",
                OPERATOR.DIVIDE:"/",
                OPERATOR.POWER:"^"}
        return lookup[self.type]
    def print(self):
        if self.type==OPERATOR.NUM:
            print("Number: " + str(self.value))
        else:
            print("OP: "+self.operatorAsString())


class StringParser:
    string=""
    pointer=0
    brackets=0
    expectNumeric=True
    error=False
    def __init__(self,string):
        self.string=string
        self.pointer=0
        self.brackets=0
        self.expectNumeric=True
    def NextToken(self):
        if self.error:
            return Token().operator(OPERATOR.INVALID)
        if self.pointer>=len(self.string):
            if self.expectNumeric:
                    self.error="String expected to end in a number."
                    return Token().operator(OPERATOR.INVALID)
            return Token().operator(OPERATOR.NONE)
        ret=Token().operator(OPERATOR.NONE)
        substring=""
        firstCharacter=True
        isFloat=False
        for i in range(self.pointer,len(self.string)):
            C=self.string[i]
            if firstCharacter:
                if C==" ":
                    continue
                if C=="(":
                    self.brackets+=1
                elif C==")":
                    self.brackets-=1
                    if self.brackets<0:
                        self.error="Bracket counting error."
                        return Token().operator(OPERATOR.INVALID)
                elif not self.expectNumeric:
                    lookup={"+":OPERATOR.PLUS,
                            "-":OPERATOR.MINUS,
                            "*":OPERATOR.MULTIPLY,
                            "/":OPERATOR.DIVIDE,
                            "^":OPERATOR.POWER}
                    if not C in lookup:
                        self.error="Invalid operator at character: " + str(i)
                        return Token().operator(OPERATOR.INVALID)
                    ret.operator(lookup[C]).brackets(self.brackets)
                    break
                elif C=="-":
                    if i==len(self.string)-1 or not self.string[i+1] in "1234567890.":
                        self.error="Stray minus sign at character: " + str(i)
                        return Token().operator(OPERATOR.INVALID)
                    substring+=C
                    firstCharacter=False
                    continue
                elif not C in "1234567890.":
                    self.error="Expected number at character: " + str(i)
                    return Token().operator(OPERATOR.INVALID)
                else:
                    firstCharacter=False
            if not firstCharacter:
                if C==".":
                    isFloat=True
                    substring+=C
                elif C in "1234567890":
                    substring+=C
                else:
                    i-=1;
                    break
        self.pointer=i+1;
        if self.expectNumeric:
            self.expectNumeric=False
            try:
                if isFloat:
                    return ret.numeric(float(substring))
                else:
                    return ret.numeric(int(substring))
            except ValueError:
                print(substring)
                self.error="Expected number at character: " + str(i)
                return Token().operator(OPERATOR.INVALID)
        else:
            self.expectNumeric=True
            return ret

class Expression:
    def __init__(self, string):
        RPN=""
        opStack=[]
        evaluationStack=[]
        def evaluate(operator):
            b=evaluationStack.pop()
            a=evaluationStack.pop()
            c=0
            if operator==OPERATOR.PLUS:
               c=a+b
            if operator==OPERATOR.MINUS:
               c=a-b
            if operator==OPERATOR.MULTIPLY:
               c=a*b
            if operator==OPERATOR.DIVIDE:
               c=a/b
            if operator==OPERATOR.POWER:
               c=pow(a,b)
            evaluationStack.append(c)
        s=StringParser(string)
        while True:
            token=s.NextToken()
            if token.type==OPERATOR.INVALID:
                print("String parse error: "+s.error)
                quit()
            elif token.type==OPERATOR.NONE:
                break
            elif token.type==OPERATOR.NUM:
                evaluationStack.append(token.value)
                RPN+=str(token.value)+" "
            else:
                while True:
                    if len(opStack)==0:
                        opStack.append(token)
                        break
                    if token.getPriority()<=opStack[-1].getPriority(): #The interesting part, the "less than" gets the operator order right, the "or equals" results in left associativity.
                        op=opStack.pop()
                        evaluate(op.type)
                        RPN+=op.operatorAsString()+" "
                    else:
                        opStack.append(token)
                        break
        while len(opStack)!=0:            
            op=opStack.pop()
            evaluate(op.type)
            RPN+=op.operatorAsString()+" "
                
        print("RPN: " + RPN)
        print("Result: " + str(evaluationStack[0]))


if len(sys.argv)<2:
    print("Expecting an expression as a command line argument.")
elif len(sys.argv)>2:
    print("Expecting only one command line argument, if providing an expression try enclosing it in quotes.")
else:
    Expression(sys.argv[1])

        
