#Steps:
#1: Key expansion

#2: Add round Key

#3: 9 (128-bit key), 11 (192-bit key), 13 (256-bit key) times:
    #a)Sub Bytes
    #b)Shift Rows
    #c)Mix Columns
    #d)Add Round Key

#4:
    #a)Sub Bytes
    #b)Shift Rows
    #c)Add Round Key
from math import *
from copy import deepcopy
from variables import *

def keyExpansion():
    print("#")

def text_to_bits(text, encoding='utf-8'):
    bits = bin(int.from_bytes(text.encode(encoding), 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))

def text_from_bits(bits, encoding='utf-8'):
    n = int(bits, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode(encoding) or '\0'

def XOR(input1,input2,size):
    input1="".join(str(e) for e in input1)
    input2="".join(str(e) for e in input2)

    output = [0]*size
    for bit in range(size):
        if (int(input1[bit]) + int(input2[bit]) == 0 or int(input1[bit]) + int(input2[bit]) == 2):
            output[bit] = 0
        else:
            output[bit] = 1
    return output

def eightBitShift(input):
    output = [0] * 32
    for bit in range(32):
        output[bit] = input[(bit+8)%32]
    return("".join(str(e) for e in output))

def oneBitShift(input):
    output = [0]*8
    for column in range(7):
        output[column]=input[column+1]
    output="".join(str(e) for e in output)
    return(output)

def rjindaelMultiplication(input):
    bitshift = oneBitShift(input)
    if (input[0] == "1"):
        bitshift = XOR(bitshift,mixColumnsMultiplications,8)

    return("".join(str(e) for e in bitshift))

def subBytes(blockText):
    newBlock = [["" for x in range(4)] for y in range(4)]
    for row in range(4):
        for byte in range(4):
            data = int(blockText[row][byte*8:(byte+1)*8],2)
            newBlock[row][byte]= str(bin(Sbox[data//16][data%16])[2:])
            length = len(newBlock[row][byte])
            newBlock[row][byte]="0"*(8-length)+str(newBlock[row][byte])

    return(newBlock)

def subWord(word):
    newWord = [""]*4
    for eightByte in range(4):
        data = int(word[8*eightByte:8+8*eightByte],2)
        newWord[eightByte] = bin(Sbox[data//16][data%16])[2:]
        length = len(newWord[eightByte])
        newWord[eightByte]="0"*(8-length)+str(newWord[eightByte])
    return("".join(str(e) for e in newWord))

def shiftRows(matrix):
    temporaryMatrix = deepcopy(matrix)
    for row in range(3):
        for column in range(4):
            matrix[row+1][column]=temporaryMatrix[row+1][(column+row+1)%4]
    for row in range(4):
        matrix[row]="".join(str(e) for e in matrix[row])
    return(matrix)

def mixColumns(block):
    newBlock = [""]*4
    for column in range(4):
        sStart = column*8 #stringStart
        sEnd = 8 + column*8 #stringEnd
        newBlock[0] += str(XOR(XOR(XOR(rjindaelMultiplication(str(block[0][sStart:sEnd])),XOR(rjindaelMultiplication(str(block[1][sStart:sEnd])),str(block[1][sStart:sEnd]),8),8),str(block[2][sStart:sEnd]),8),str(block[3][sStart:sEnd]),8))
        newBlock[1] += str(XOR(XOR(XOR(rjindaelMultiplication(str(block[1][sStart:sEnd])),XOR(rjindaelMultiplication(str(block[2][sStart:sEnd])),str(block[2][sStart:sEnd]),8),8),str(block[3][sStart:sEnd]),8),str(block[0][sStart:sEnd]),8))
        newBlock[2] += str(XOR(XOR(XOR(rjindaelMultiplication(str(block[2][sStart:sEnd])),XOR(rjindaelMultiplication(str(block[3][sStart:sEnd])),str(block[3][sStart:sEnd]),8),8),str(block[0][sStart:sEnd]),8),str(block[1][sStart:sEnd]),8))
        newBlock[3] += str(XOR(XOR(XOR(rjindaelMultiplication(str(block[3][sStart:sEnd])),XOR(rjindaelMultiplication(str(block[0][sStart:sEnd])),str(block[0][sStart:sEnd]),8),8),str(block[1][sStart:sEnd]),8),str(block[2][sStart:sEnd]),8))
    for row in range(4):
        for chr in ('[], '):
            newBlock[row] = newBlock[row].replace(chr,'')
    return(newBlock)

def addRoundKey(message,round):
    newMessage = [0]*4

    for row in range(4):
        newRow = "".join(str(e) for e in (XOR(roundKeys[round][row],message[row],32)))
        newMessage[row]=newRow
    return(newMessage)

def columnMajorOrder(message): #Consiste à prendre un message et le mettre dans une matrice par les colonnes, par ex, le message (123456) sera mis dans une matrice 3x2 par #(1,4)#(2,5)#(3,6)

    messageBlock = [[0 for x in range(4)] for y in range(4)]
    for byte in range(16):
        messageBlock[byte%4][byte//4]=message[byte]
    return(messageBlock)

def makeRoundKeys(w0,w1,w2,w3,rcon):
    global roundKeys
    roundKeys = [["" for x in range(4)] for y in range(11)]
    tempRoundKeys = [[0 for x in range(4)] for y in range(11)]
    tempRoundKeys[0][0]=w0
    tempRoundKeys[0][1]=w1
    tempRoundKeys[0][2]=w2
    tempRoundKeys[0][3]=w3
    for round in range(10):
        tempRoundKeys[round+1][0]=XOR(XOR(tempRoundKeys[round][0],subWord(eightBitShift(tempRoundKeys[round][3])),32),rcon[round],32)
        tempRoundKeys[round+1][1]=XOR(tempRoundKeys[round+1][0],tempRoundKeys[round][1],32)
        tempRoundKeys[round+1][2]=XOR(tempRoundKeys[round+1][1],tempRoundKeys[round][2],32)
        tempRoundKeys[round+1][3]=XOR(tempRoundKeys[round+1][2],tempRoundKeys[round][3],32)
    for key in range(11):
        for line in range(4):
            roundKeys[key][0]+="".join(str(e) for e in tempRoundKeys[key][line][:8])
            roundKeys[key][1]+="".join(str(e) for e in tempRoundKeys[key][line][8:16])
            roundKeys[key][2]+="".join(str(e) for e in tempRoundKeys[key][line][16:24])
            roundKeys[key][3]+="".join(str(e) for e in tempRoundKeys[key][line][24:32])

def steps(message):
    block = columnMajorOrder(message)
    step = addRoundKey(block,0)
    for round in range(9):
        temp = subBytes(step)
        temp = shiftRows(temp)
        temp = mixColumns(temp)
        step = addRoundKey(temp,round+1)
        print(hex(int("".join(str(e) for e in step),2)))

    temp = subBytes(step)
    temp = shiftRows(temp)
    step = addRoundKey(temp,10)
    print(hex(int("".join(str(e) for e in step),2)))


makeRoundKeys(masterKey0,masterKey1,masterKey2,masterKey3,rcon)
steps(message)
