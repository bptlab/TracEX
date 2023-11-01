import inputInquiry as ii
import inputHandling as ih 

#Put OpenAI-key as environment variable "OPENAI_API_KEY" in your system

inp = ii.getInput()
ih.convertInpToCSV(inp)
