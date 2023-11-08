import inputInquiry as ii
import inputHandling as ih
import outputHandling as oh

ii.greeting()
inp = ii.getInput()
xesfile = ih.convertInpToXES(inp)
oh.getOutput(xesfile)
oh.farewell()
