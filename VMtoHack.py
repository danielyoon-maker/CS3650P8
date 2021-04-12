commandDict ={    
                "add" : "a1",
                "sub" : "a1",
                "and" : "a1",
                "or" : "a1",
                "eq" : "a2",
                "gt" : "a2",
                "lt" : "a2",
                "neg" : "neg",
                "not" : "not",
                "push" : "push",
                "pop" : "pop",
                "label" : "label",
                "goto" : "goto",
                "if-goto" : "if",
                "function" : "function",
                "call" : "call",
                "return" : "return"
            }

basePush = ("@SP\n" +
                "A=M\n" +
                "M=D\n" +
                "@SP\n" +
                "M=M+1\n") 

basePop = ("@R13\n" +
                "M=D\n" +
                "@SP\n" +
                "AM=M-1\n" +
                "D=M\n" +
                "@R13\n" +
                "A=M\n" +
                "M=D\n") 

class Parser():

    def __init__(self, file_name):
        self.file_name = file_name
        self.f = open(file_name + ".vm", "r")
        self.writer = open(file_name + ".asm", "w")
        self.currentCommand = None
        self.jumpFlag = 0
        self.labelCounter = 0

    def startParsing(self):
        self.writer.write(self.writeInit())
        for x in self.f:
            x = x.strip()
            x = self.stripComments(x)
            if(self.skipOrStay(x) == False):
                continue
            c = CodeWriter(x)
            self.writer.write(c.startWriting())
        self.writer.close()

    def skipOrStay(self, line): #checks to see if line is a comment or blank line
        if len(line.strip()) ==0 :
            #return "empty"
            return False
        if "//" in line:
            #return "comment"
            return False
        #return "proceed"
        return True

    def instructionType(self, line):
        return "working"

    def stripComments(self, line):
        if line.find("//") > 2:
            return line.split("//")[0]
        return line

    def writeInit(self):
        tracked = "RETURN_LABEL" + str(self.labelCounter)
        self.labelCounter += 1
        return ("@256\n" +
                         "D=A\n" +
                         "@SP\n" +
                         "M=D\n" "@" + str(tracked) + "\n" + "D=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"+
                        "@LCL\n" + "D=M\n" + basePush +
                        "@ARG\n" + "D=M\n" + basePush +
                        "@THIS\n" + "D=M\n" + basePush +
                        "@THAT\n" + "D=M\n" + basePush + 
                        "@SP\n" +
                        "D=M\n" +
                        "@5\n" +
                        "D=D-A\n" +
                        "@0" + "\n" +
                        "D=D-A\n" +
                        "@ARG\n" +
                        "M=D\n" +
                        "@SP\n" +
                        "D=M\n" +
                        "@LCL\n" +
                        "M=D\n" +
                        "@Sys.init\n" +
                        "0;JMP\n" +
                        "(" + tracked + ")\n"
                        )

class CodeWriter():

    def __init__(self, x):
        self.command = x
        self.commandPartition = self.command.split(" ")
        self.cType = commandDict.get(self.commandPartition[0])
        self.assemblyCode = ""

    def startWriting(self):
        if(self.cType == "a1"):
            return(self.writeA1())
        if(self.cType == "a2"):
            return(self.writeA2())
        if(self.cType == "not"):
            return(self.writeNot())
        if(self.cType == "neg"):
            return(self.writeNeg())
        if(self.cType == "push"):
            return(self.writePush())
        if(self.cType == "pop"):
            return(self.writePop())
        if(self.cType == "label"):
            return(self.writeLabel())
        if(self.cType == "goto"):
            return(self.writeGoto())
        if(self.cType == "if"):
            return(self.writeIf())
        if(self.cType == "call"):
            return(self.writeCall())
        if(self.cType == "function"):
            return(self.writeFunction())
        if(self.cType == "return"):
            return(self.writeReturn())
    def writeA1(self):
        self.assemblyCode = "@SP\n" + "AM=M-1\n" + "D=M\n" + "A=A-1\n"
        a1Dict = {
            "add" : "M=M+D\n",
            "sub" : "M=M-D\n",
            "and" : "M=M&D\n",
            "or"  : "M=M|D\n"
        }
        return (self.assemblyCode + a1Dict.get(self.commandPartition[0]))
    
    def writeA2(self):
        a2Dict = {
            "gt" : "JLE",
            "lt" : "JGE",
            "eq" : "JNE",
        }
        self.assemblyCode = ("@SP\n" + "AM=M-1\n" + "D=M\n" + "A=A-1\n" + "D=M-D\n" + "@FALSE" + str(p.jumpFlag) + "\n" "D;" + a2Dict.get(self.commandPartition[0]) + "\n" 
                + "@SP\n" +
                "A=M-1\n" +
                "M=-1\n" +
                "@CONTINUE" + str(p.jumpFlag) + "\n" +
                "0;JMP\n" +
                "(FALSE" + str(p.jumpFlag) + ")\n" +
                "@SP\n" +
                "A=M-1\n" +
                "M=0\n" +
                "(CONTINUE" + str(p.jumpFlag) + ")\n")
        p.jumpFlag += 1
        return(self.assemblyCode)    

    def writeNot(self):
        return "@SP\nA=M-1\nM=!M\n"

    def writeNeg(self):
        return "D=0\n@SP\nA=M-1\nM=D-M\n"

    def writePush(self):
        index = self.commandPartition[2]
        if(self.commandPartition[1] == "constant"):
            return("@" + index + "\n" + "D=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        if(self.commandPartition[1] == "local"):
            return ("@LCL\n" + "D=M\n" + "@" + index + "\n" + "A=D+A\nD=M\n" + basePush)
        if(self.commandPartition[1] == "argument"):
            return ("@ARG\n" + "D=M\n" + "@" + index + "\n" + "A=D+A\nD=M\n" + basePush)
        if(self.commandPartition[1] == "this"):
            return ("@THIS\n" + "D=M\n" + "@" + index + "\n" + "A=D+A\nD=M\n" + basePush)
        if(self.commandPartition[1] == "that"):
            return ("@THAT\n" + "D=M\n" + "@" + index + "\n" + "A=D+A\nD=M\n" + basePush)
        if(self.commandPartition[1] == "temp"):
            return ("@R5\n" + "D=M\n" + "@" + str(int(index) + 5) + "\n" + "A=D+A\nD=M\n" + basePush)
        if(self.commandPartition[1] == "pointer"):
            if(int(index) == 0):
                return ("@THIS\n" + "D=M\n" + basePush)
            if(int(index) == 1):
                return ("@THAT\n" + "D=M\n" + basePush)
        if(self.commandPartition[1] == "static"):
            return ("@" + str(int(index) + 16) + "\n" + "D=M\n" + basePush)
    
    def writePop(self):
        index = self.commandPartition[2]
        basePop = ("@R13\n" +
                "M=D\n" +
                "@SP\n" +
                "AM=M-1\n" +
                "D=M\n" +
                "@R13\n" +
                "A=M\n" +
                "M=D\n") 
        if(self.commandPartition[1] == "local"):
            return ("@LCL\n" + "D=M\n@" + index + "\nD=D+A\n" + basePop)
        if(self.commandPartition[1] == "argument"):
            return ("@ARG\n" + "D=M\n@" + index + "\nD=D+A\n" + basePop)
        if(self.commandPartition[1] == "this"):
            return ("@THIS\n" + "D=M\n@" + index + "\nD=D+A\n" + basePop)
        if(self.commandPartition[1] == "that"):
            return ("@THAT\n" + "D=M\n@" + index + "\nD=D+A\n" + basePop)
        if(self.commandPartition[1] == "temp"):
            return ("@R5\n" + "D=M\n@" + str(int(index) + 5) + "\nD=D+A\n" + basePop)
        if(self.commandPartition[1] == "pointer"):
            if(int(index) == 0):
                return ("@THIS\n" + "D=A\n" + basePop)
            if(int(index) == 1):
                return ("@THAT\n" + "D=A\n" + basePop)
        if(self.commandPartition[1] == "static"):
            return ("@" + str(int(index) + 16) + "\n" + "D=A\n" + basePop)
    
    def writeLabel(self):
        return ("(" + self.commandPartition[1] +")\n")

    def writeGoto(self):
        return ("@" + self.commandPartition[1] +"\n0;JMP\n")

    def writeIf(self):
        return ("@SP\n" +
                "AM=M-1\n" +
                "D=M\n" +
                "A=A-1\n""@" + self.commandPartition[1] +"\nD;JNE\n")
    
    def writeCall(self):
        tracked = "RETURN_LABEL" + str(p.labelCounter)
        p.labelCounter += 1
        return ("@" + str(tracked) + "\n" + "D=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"+
                        "@LCL\n" + "D=M\n" + basePush +
                        "@ARG\n" + "D=M\n" + basePush +
                        "@THIS\n" + "D=M\n" + basePush +
                        "@THAT\n" + "D=M\n" + basePush + 
                        "@SP\n" +
                        "D=M\n" +
                        "@5\n" +
                        "D=D-A\n" +
                        "@0" + "\n" +
                        "D=D-A\n" +
                        "@ARG\n" +
                        "M=D\n" +
                        "@SP\n" +
                        "D=M\n" +
                        "@LCL\n" +
                        "M=D\n" +
                        "@Sys.init\n" +
                        "0;JMP\n" +
                        "(" + tracked + ")\n"
                        )

    def writeReturn(self):
        return ("@LCL\n" +
                "D=M\n" +
                "@R11\n" +
                "M=D\n" +
                "@5\n" +
                "A=D-A\n" +
                "D=M\n" +
                "@R12\n" +
                "M=D\n" +
                "@ARG\n" + "D=M\n@0" + "\nD=D+A\n" + basePop +
                "@ARG\n" +
                "D=M\n" +
                "@SP\n" +
                "M=D+1\n" +
                "@R11\n" +
                "D=M-1\n" +
                "AM=D\n" +
                "D=M\n" +
                "@THAT" + "\n" +
                "M=D\n" +
                "@R11\n" +
                "D=M-1\n" +
                "AM=D\n" +
                "D=M\n" +
                "@THIS" + "\n" +
                "M=D\n" +
                "@R11\n" +
                "D=M-1\n" +
                "AM=D\n" +
                "D=M\n" +
                "@ARG" + "\n" +
                "M=D\n" +
                "@R11\n" +
                "D=M-1\n" +
                "AM=D\n" +
                "D=M\n" +
                "@LCL" + "\n" +
                "M=D\n"+
                "@R12\n" +
                "A=M\n" +
                "0;JMP\n")
        
    def writeFunction(self):
        pushConstantN = ""
        i = 0
        while(i < int(self.commandPartition[2])):
            pushConstantN = pushConstantN + "@0" + "\n" + "D=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
            i += 1
        return ("(" + self.commandPartition[1] +")\n" + pushConstantN)

filetoRead = input("Please enter name of the file(no file extension): \n")
p = Parser(filetoRead)
p.startParsing()
