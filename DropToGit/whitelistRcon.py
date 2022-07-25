import mcrcon_new,time
import os,sys
import secrets
import asyncio
import discord
import psutil
from sys import platform
from datetime import datetime
import Config

tokenDiscord = Config.tokenDiscord
authority = Config.authority
rconIP = Config.rconIP
rconPassword = Config.rconPassword
rconPort = Config.rconPort
tokensFile = Config.tokensFile
whitelistFile = Config.whitelistFile

rconTag = "gamemodeproperty GameModeTagName"
startTag = "<WList>Start"
tokenTag = "<WListReturn>"
resultTag = "<WListResult>"

users = "1234567;9923456;"
tokens = ["Token123","TokenTest"]
badserver = []
plat = platform.lower()

mcr = mcrcon_new.MCRcon(rconIP,rconPassword,rconPort)
try:
    mcr.connect()
except:
    print("Couldn't connect, will retry later...")
puid = os.getpid()
lastResult = ""
def generateTokens(count = 1):
    if(count < 1): return ""
    global users
    global tokens
    f = open(tokensFile, 'a')
    back = "\n"
    for i in range(0,count):
        key = secrets.token_urlsafe(22).replace(",","*")
        tokens.append(key)
        line = "\n"+key
        f.write(line)
        back+="`"+key+"`\n"
    return back
def removeTokens(tokenR):
    if(len(tokenR) < 1): return
    global tokens
    with open(tokensFile,"w+") as f:
        for line in f:
            for word in tokenR:
                line = line.replace(word, "")
    for i in tokenR:
        tokens.remove(i)
    f.close()
    return
def addUsers(userIDs):
    if(len(userIDs) < 1): return ""
    global users
    global tokens
    f = open(whitelistFile, 'a')
    back = "\n"
    for i in userIDs:
        users.append(i)
        line = "\n"+i
        f.write(line)
        back+="`"+i+"`\n"
    return back

try:
    users = []
    for n in open(whitelistFile,encoding='utf-8').readlines():
        if(n != "" and n !="\n"):
           n.strip()
           users.append(n)
except:
    print("Can't Read File! ("+whitelistFile+"), creating new one")
    f = open(whitelistFile, 'w')
    f.close()

try:
    tokens = []
    for n in open(tokensFile,encoding='utf-8').readlines():
        if(n != "" and n !="\n"): 
            n = n.strip()
            tokens.append(n)
except:
    print("Can't Read File! ("+tokensFile+")")
    f = open(tokensFile, 'w')
    f.close()
class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        await (runServers())
    async def on_message(self, message):
        if((message.author.id in authority)):
            if('!whitelist' == message.content):
                strN = ""
                maxCount = 30
                for i in users:
                    if(maxCount <=0): break
                    strN+="`"+i+"`\n"
                    maxCount -=1
                strN+="\nOverall: "+str(len(users))+" Whitelisted Users"
                await message.channel.send(strN)
            elif('!tokens' == message.content):
                strN = ""
                maxCount = 30
                for i in tokens:
                    strN+="`"+i+"`\n"
                    if(maxCount <=0): break
                strN+="\nOverall: "+str(len(tokens))+" Tokens Stored"
                await message.channel.send(strN)
            elif('!addtokens' in message.content):
                count = int(message.content.split(" ")[1])
                cResult = generateTokens(count)
                strN = "Added: "+cResult
                await message.channel.send(strN)
            elif('!addUsers' in message.content):
                count = int(message.content.split(" ")).remove("!addUsers")
                cResult = addUsers(count)
                strN = "Added: "+cResult
                await message.channel.send(strN)
async def runServers(): 
  global mcr
  while(1):
    if 'win' not in plat:
        time.sleep(0.1) #Config.maxTSeconds
        time.sleep(0.1)
        cpuP = psutil.Process(puid).cpu_percent()
        if cpuP > 8.0:
            time.sleep(0.2)
    try:
        await runMain()
    except:
        ss = sys.exc_info()[0]
        print(ss)
        print("Error:"+"    "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+"     On "+mcr.host+":"+str(mcr.port))        
        await asyncio.sleep(5)
        mcr.disconnect()
        try:
            print("Trying to re-Connect....")
            mcr.connect()
            print("Connected!!")+"  |  "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+"  |"
        except:
            print("Couldn't connect to server:(" +"  |  "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+"  |")
            ss = sys.exc_info()[0]
            print(ss)

async def runMain():
        global mcr
        global lastResult
        global users
        global tokens    
        await asyncio.sleep(1)
        result = mcr.command(rconTag)
        if(lastResult != result):
            lastResult = result
            if(startTag in result):
                sendBack = ""
                if(len(users) > 0): 
                    for i in users:
                        sendBack +=i+";"
                else:
                    sendBack = "NONE;"
                mcr.command(rconTag+" "+sendBack)
            elif(tokenTag in result):
                res = result.split("\"")[1].replace(tokenTag,"")
                ret = ""
                spl = res.split(";")
                addU = []
                tokensR = []
                for i in spl: #76561198059902896,TOKEN123;
                    if(i != ""):
                        splitN = i.split(",")
                        if(len(splitN) > 1):
                            tok = splitN[1]
                            idSteam = splitN[0]
                            resOk = ""
                            if(tok in tokens): 
                                resOk = "OK"
                                addU.append(idSteam)
                                tokensR.append(tok)
                            else:
                                resOk = "OFF"
                            ret += idSteam+"-"+resOk+";"
                mcrBack = rconTag+" "+resultTag+ret
                mcr.command(mcrBack)
                addUsers(addU)  
                removeTokens(tokensR)
client = MyClient()
client.run(tokenDiscord)
