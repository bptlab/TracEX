### Preprocessing.SpellingGrammarPunctuation
[{"role": "system", "content": [{
    "text": "You are an expert in language correction, specializing in correcting spelling, grammar, and punctuation errors. Your task is to correct the following patient's journey while preserving the meaning of the original text.\n\nExample:\nOriginal text:\n\"\"\"\nthe patint wuz admited to the hospital with sever pain in his abdomen. he wasnt sure wat caused it but mentioned eating a large meal before.\n\"\"\"\n\nCorrected text:\n\"\"\"\nThe patient was admitted to the hospital with severe pain in his abdomen. He wasn't sure what caused it but mentioned eating a large meal before.\n\"\"\"\n\nNow, correct this text:\n\n",
    "type": "text"}]}, {"role": "user", "content": [{"type": "text",
                                                     "text": "I (30f) started noticing unusual fatigue, and joint pains in early Febuary 2023. I initially brushed it off as overwork since I always had something with my heart, However as the symptons persisted, I desided to see a doctor in Sevenoaks two weeks later. Blood tests were conducted and exactly one month after my initial visit, I was diagnosed with rhumatoid \narthritis. Following the diagnosis my treatment began on April, 13, focusing on managing the symptoms. A significant improvement was noted during a follow-up appoinment three months after the start of the treatment.\n"}]},
 {"role": "assistant", "content": [{
     "text": "I (30F) started noticing unusual fatigue and joint pains in early February 2023. I initially brushed it off as overwork since I always had something with my heart. However, as the symptoms persisted, I decided to see a doctor in Sevenoaks two weeks later. Blood tests were conducted, and exactly one month after my initial visit, I was diagnosed with rheumatoid arthritis. Following the diagnosis, my treatment began on April 13, focusing on managing the symptoms. A significant improvement was noted during a follow-up appointment three months after the start of the treatment.",
     "type": "text"}]}, {"role": "user",
                         "content": "I remeber the day I first learnt about the importnce of spellchek. It was an eye-opener for me."},
 {"role": "assistant",
  "content": "I remember the day I first learned about the importance of spellcheck. It was an eye-opener for me."}]

### Preprocessing.IdentifyMarkTimestamps
[{"role": "system", "content": [{
    "text": "You are an expert in text analysis. Your task is to identify timestamps of events in the given text. Timestamps can include:\n- Specific dates (e.g., \"January 1, 2022\")\n- Months (e.g., \"June 2023\")\n- Years (e.g., \"1999\")\n- Recognized holidays (e.g., \"Christmas\")\n- Relative dates (e.g., \"12 weeks later\" or \"as the week progressed\")\n\n### Examples:\n1. \"On January 1, 2022, the event occurred\" should become \"On $$$January 1, 2022$$$, the event occurred\".\n2. \"The project is due in June 2023\" should become \"The project is due in $$$June 2023$$$\".\n3. \"It happened during Christmas\" should become \"It happened during $$$Christmas$$$\".\n4. \"They met again 12 weeks later\" should become \"They met again $$$12 weeks later$$$\".\n\n### Instructions:\n1. Read the given text carefully.\n2. Identify any timestamps as defined above.\n3. Highlight each identified timestamp by surrounding it with triple dollar signs ($$$).\n\n### Text for Analysis:\n\"\"\"\n{Insert text here}\n\"\"\"\n\n### Output:\nReturn the full text with all timestamps highlighted.\n",
    "type": "text"}]}, {"role": "user", "content": [{
    "text": "I (30f) started noticing unusual fatigue, and joint pain in early February 2023. \u000bI initially brushed it off as overwork since I always had something with my heart, However as the symptoms persisted, I decided to see a doctor in Sevenoaks two weeks later. Blood tests were conducted and exactly one month after my initial visit, I was diagnosed with rheumatoid \narthritis. Following the diagnosis my treatment began on April, 13, focusing on managing the symptoms. A significant improvement was noted during a follow-up appointment three months after the start of the treatment. And on Christmas I was symptom free!\n",
    "type": "text"}]},
 {"role": "assistant", "content": [{
     "text": "\"\"\"\nI (30f) started noticing unusual fatigue, and joint pain in $$$early February 2023$$$. I initially brushed it off as overwork since I always had something with my heart, However as the symptoms persisted, I decided to see a doctor in Sevenoaks $$$two weeks later$$$. Blood tests were conducted and exactly $$$one month after my initial visit$$$, I was diagnosed with rheumatoid arthritis. Following the diagnosis my treatment began on $$$April 13$$$, focusing on managing the symptoms. A significant improvement was noted during a follow-up appointment $$$three months after the start of the treatment$$$. And on $$$Christmas$$$ I was symptom free!\n\"\"\"",
     "type": "text"}]}, {"role": "user", "content": [{
    "text": "I started feeling unusually fatigued right before Thanksgiving 2020. The fatigue worsened over the holiday, and by the following Monday, I had developed a fever. I was tested for Covid-19 two days later and received a positive result on November 30th, 2020.",
    "type": "text"}]},
 {"role": "assistant", "content": [{
     "text": "\"\"\"\nI started feeling unusually fatigued right before $$$Thanksgiving 2020$$$. The fatigue worsened over the holiday, and by $$$the following Monday$$$, I had developed a fever. I was tested for Covid-19 $$$two days later$$$ and received a positive result on $$$November 30th, 2020$$$.\n\"\"\"",
     "type": "text"}]}, {"role": "user",
                         "content": "I started feeling unwell around the middle of March 2021. The symptoms were quite severe by the 20th of March, which is when I decided to get tested. The test results came back positive for Covid-19 on March 22nd, 2021."},
 {"role": "assistant",
  "content": "I started feeling unwell around the $$$middle of March 2021$$$. The symptoms were quite severe by the $$$20th of March$$$, which is when I decided to get tested. The test results came back positive for Covid-19 on $$$March 22nd, 2021$$$."},
 {"role": "user",
  "content": "I started feeling unusually fatigued right before Thanksgiving 2020. The fatigue worsened over the holiday, and by the following Monday, I had developed a fever. I was tested for Covid-19 two days later and received a positive result on November 30th, 2020."},
 {"role": "assistant",
  "content": "I started feeling unusually fatigued right before $$$Thanksgiving 2020$$$. The fatigue worsened over the holiday, and by the $$$following Monday$$$, I had developed a fever. I was tested for Covid-19 $$$two days later$$$ and received a positive result on $$$November 30th, 2020$$$."},
 {"role": "user",
  "content": "Two days after new years eve, I started feeling sick. In the following week my symptoms worsened."},
 {"role": "assistant",
  "content": "$$$Two days after$$$ $$$new years eve$$$, I started feeling sick. $$$In the following week$$$ my symptoms worsened."},
 {"role": "user",
  "content": "I was tested positive for Covid-19 on by birthday, the 12th of June. The day before I already felt light-headed. Two weeks after my birthday, I was admitted to the hospital."},
 {"role": "assistant",
  "content": "I was tested positive for Covid-19 on by birthday, $$$the 12th of June$$$. $$$The day before$$$ I already felt light-headed. $$$Two weeks after my birthday$$$, I was admitted to the hospital."},
 {"role": "user",
  "content": "Over the course of the next few days, my symptoms progressed, and I started experiencing high fever. After two weeks of isolation, I finally started feeling better."},
 {"role": "assistant",
  "content": "$$$Over the course of the next few days$$$, my symptoms progressed, and I started experiencing high fever. $$$After two weeks$$$ of isolation, I finally started feeling better."}]

### Preprocessing.TranslateTimestamps
[{"role": "system",
  "content": "\"\"\"\nTask: Transform all timestamps and the word \"holidays\" marked with $$$ to a YYYY/MM/DD format.\n\nInstructions:\n1. Identify all timestamps and the word \"holidays\" in the text that are marked with $$$.\n2. Convert each timestamp to the format YYYY/MM/DD.\n3. Replace the original timestamp and the word \"holidays\" with the new format.\n4. If a timestamp is invalid or unrecognizable, leave it unchanged.\n5. Replace \"holidays\" with the current date in YYYY/MM/DD format.\n\nExamples:\nInput: \"The event will be held on $$$2023-06-12 and $$$holidays.\"\nOutput: \"The event will be held on 2023/06/12 and 2024/06/13.\"  # Assuming today's date is June 13, 2024\n\nInput: \"Check the dates: $$$2023/12/31, $$$holidays.\"\nOutput: \"Check the dates: 2023/12/31, 2024/06/13.\"\n\nInput: \"Invalid dates should remain: $$$13-13-2023, $$$holidays.\"\nOutput: \"Invalid dates should remain: $$$13-13-2023, 2024/06/13.\"\n\"\"\"Specifically, convert 'early [month]' to the 1st of the month, 'mid [month]' to the 15th of the month, and 'end of [month]' to the last day of the month (use 30 for April, June, September, and November; 31 for January, March, May, July, August, October, and December; and 28 or 29 for February, depending on leap years). If the year is not mentioned, assume the current year. Return the full text, with the transformed timestamps."},
 {"role": "user",
  "content": "$$$In early January$$$, I noticed a persistent cough. By $$$mid January$$$, the cough had worsened, leading me to seek medical advice. A specialist finally saw me $$$at the end of January$$$, diagnosing me with a chronic condition."},
 {"role": "assistant",
  "content": "In 2020/01/01, I noticed a persistent cough. By 2020/01/15, the cough had worsened, leading me to seek medical advice. A specialist finally saw me at 2020/01/31, diagnosing me with a chronic condition."},
 {"role": "user",
  "content": "In the $$$middle of 2023$$$ I got a stroke. By the $$$end of the year$$$ I had recovered. But in $$$early 2024$$$ I had a relapse."},
 {"role": "assistant",
  "content": "On 2023/06/01, I got a stroke. By 2023/12/01, I had recovered. On 2024/01/01, I had a relapse."},
 {"role": "user",
  "content": "I plan to start my new fitness routine in $$$early February 2024$$$. By $$$mid February$$$, I hope to see some initial results. By the $$$end of February$$$, I want to have a consistent habit."},
 {"role": "assistant",
  "content": "I plan to start my new fitness routine on 2024/02/01. By 2024/02/15, I hope to see some initial results. By 2024/02/29, I want to have a consistent habit."},
 {"role": "user",
  "content": "I usually experience seasonal allergies in $$$early April$$$. By $$$mid April$$$, they become severe, and by the $$$end of May$$$, I need to take stronger medication."},
 {"role": "assistant",
  "content": "I usually experience seasonal allergies on 2024/04/01. By 2024/04/15, they become severe, and by 2024/05/31, I need to take stronger medication."},
 {"role": "user",
  "content": "I started feeling unwell around the $$$middle of March 2021$$$. The symptoms were quite severe by the $$$20th of March$$$, which is when I decided to get tested. The test results came back positive for Covid-19 on $$$March 22nd, 2021$$$."},
 {"role": "assistant",
  "content": "I started feeling unwell around the 2021/03/15. The symptoms were quite severe by the 2021/03/20, which is when I decided to get tested. The test results came back positive for Covid-19 on 2021/03/22."}]

### Preprocessing.Interpretation

[{"role": "system", "content": [{
    "text": "\"\"\"\nTask: Interpret vague timestamps and convert holidays into specific dates.\n\nDefinitions:\n- 'Early' in the month: 1st\n- 'Mid' in the month: 14th\n- 'End' in the month: 28th\n\nExamples:\n\n1. Interpret vague timestamps:\nInput: \"I visited the doctor in early February 2024.\"\nOutput: \"I visited the doctor on 2024/02/01.\"\n\nInput: \"The meeting is scheduled for mid-March 2021.\"\nOutput: \"The meeting is scheduled for 2021/03/14.\"\n\nInput: \"The project is due at the end of April 1999.\"\nOutput: \"The project is due on 1999/04/28.\"\n\n2. Convert holidays to specific dates:\nInput: \"Today is Christmas 1994\"\nOutput: \"Today is 1994/12/25\"\n\nInput: \"New Year's Day 1999 I got pregnant\"\nOutput: \"1999/01/01 I got pregnant\"\n\nInstructions:\n1. When interpreting a vague timestamp, replace 'early' with the 1st, 'mid' with the 14th, and 'end' with the 28th of the mentioned month.\n2. When converting holidays, provide the specific date for well-known holidays. For less familiar holidays, include more context or examples if needed.\n\nPlease interpret the following timestamps and convert the holidays:\n",
    "type": "text"}]},
 {"role": "user", "content": [{"type": "text", "text": "My birthday is in early May."}]},
 {"role": "assistant", "content": [{"type": "text", "text": "My birthday is on 2024/05/01."}]},
 {"role": "user", "content": [
     {"type": "text", "text": "I met my girlfriend on the 24.12.1994 and on the 27th of december we got together. "}]},
 {"role": "assistant",
  "content": [{"type": "text", "text": "I met my girlfriend on 1994/12/24 and on 1994/12/27 we got together."}]},
 {"role": "user", "content": [{"type": "text", "text": "We scheduled the appointment to early April this Year"}]},
 {"role": "assistant", "content": [{"type": "text", "text": "We scheduled the appointment for 2023/04/01."}]},
 {"role": "user", "content": [{"type": "text", "text": "My Bachelorthesis is due to the 30th June 2024"}]},
 {"role": "assistant", "content": [{"type": "text", "text": "My Bachelor thesis is due on 2024/06/30."}]}]

### preprocessing.calculatingRelativesDates

[{"role": "system", "content": [{
    "text": "You are an expert in medical scheduling with extensive knowledge of date calculations and patient management. Transform all relative dates in a patient's journey into absolute dates in the YYYY/MM/DD format. The output should only be the entire patient journey with the transformed dates.\n\nFollow the steps below carefully to ensure accuracy.\n\nSteps:\n1. Identify each event and its reference date in the journey.\n2. Extract the relative time period for each event (e.g., \"2 weeks after\").\n3. Calculate the absolute date by adding or subtracting the relative time period from the reference date.\n4. Convert the calculated date into the YYYY/MM/DD format.\n5. Replace the relative dates in the patient's journey with the absolute dates.\n\nExamples:\n1. Input: \"Patient will have a follow-up appointment 2 weeks after Christmas 2024.\"\n   - Reference event: Christmas 2024\n   - Date of Christmas 2024: 2024/12/25\n   - Relative time period: 2 weeks after\n   - Calculation: 2024/12/25 + 2 weeks = 2025/01/08\n   - Output: \"Patient will have a follow-up appointment on 2025/01/08.\"\n\n2. Input: \"The next visit is scheduled 10 days before New Year 2025.\"\n   - Reference event: New Year 2025\n   - Date of New Year 2025: 2025/01/01\n   - Relative time period: 10 days before\n   - Calculation: 2025/01/01 - 10 days = 2024/12/22\n   - Output: \"The next visit is scheduled on 2024/12/22.\"\n\n3. Input: \"Start the new medication 1 month after July 4th, 2023.\"\n   - Reference event: July 4th, 2023\n   - Date of July 4th, 2023: 2023/07/04\n   - Relative time period: 1 month after\n   - Calculation: 2023/07/04 + 1 month = 2023/08/04\n   - Output: \"Start the new medication on 2023/08/04.\"\n\nInstructions:\nPlease provide the patient's journey details with all relative dates. The expert will follow the steps outlined above to calculate and convert the dates, and then output the entire journey with the transformed dates.\n\nPatient Journey:\n",
    "type": "text"}]}, {"role": "user", "content": [{
    "text": "I (30f) started noticing unusual fatigue, and joint pain on 2023/02/01. I initially brushed it off as overwork since I always had something with my heart. However, as the symptoms persisted, I decided to see a doctor in Sevenoaks $two weeks later$. Blood tests were conducted and $exactly one month after my initial visit$, I was diagnosed with rheumatoid arthritis. Following the diagnosis my treatment began on 2023/04/13, focusing on managing the symptoms. A significant improvement was noted during a follow-up appointment $three months after the start$ of the treatment.\n",
    "type": "text"}]},
 {"role": "assistant", "content": [{
     "text": "I (30f) started noticing unusual fatigue, and joint pain on 2023/02/01. I initially brushed it off as overwork since I always had something with my heart. However, as the symptoms persisted, I decided to see a doctor in Sevenoaks on 2023/02/15. Blood tests were conducted and on 2023/03/15 (exactly one month after my initial visit), I was diagnosed with rheumatoid arthritis. Following the diagnosis my treatment began on 2023/04/13, focusing on managing the symptoms. A significant improvement was noted during a follow-up appointment on 2023/07/13.",
     "type": "text"}]}, {"role": "user", "content": [{
    "text": "3 weeks after Easter I got Covid 19. 2 days later I went to the doctor and got the first dose of the vaccine.",
    "type": "text"}]},
 {"role": "assistant", "content": [{
     "text": "3 weeks after April 9, 2023, I got Covid-19 on 2023/04/30. 2023/05/02, I went to the doctor and got the first dose of the vaccine.",
     "type": "text"}]}, {"role": "user", "content": [
    {"text": "In midsummer 2021, I was diagnosed with cancer and celebrated my birthday 47 days later.",
     "type": "text"}]}, {"role": "assistant", "content": [
    {"text": "In June 21, 2021, I was diagnosed with cancer and celebrated my birthday on 2021/08/07.",
     "type": "text"}]}, {"role": "user", "content": [{
    "text": "Finally, 9 days after New Year's Eve, I had my first kiss. And two weeks before, I thought it would never happen.",
    "type": "text"}]}, {"role": "assistant", "content": [
    {"text": "Finally, on 2023/01/09, I had my first kiss. And on 2022/12/18, I thought it would never happen.",
     "type": "text"}]}]

### Cohort Extraction

[["condition", {"role": "system",
                "content": "You are an expert in text understanding, and your task is to identify the illness mentioned in a given text. Return only the illness name using a maximum of two words. Here are some examples:\n\nText: \"In July I got infected with Covid-19 which resulted in similar symptoms like a heavy flu.\"\nOutput: Covid-19\n\nText: \"I had a heavy flu in July.\"\nOutput: Flu\n\nText: \"Last year I was feeling really well, when all of a sudden I had severe breathtaking problems and high fever. I thought it was a flu, but it turned out to be Covid-19.\"\nOutput: Covid-19\n\nNow, please extract the illness from the following text:"},
  {"role": "user",
   "content": "In July I got infected with Covid-19 which resulted in similar symptoms like a heavy flu."},
  {"role": "assistant", "content": "Covid-19"}, {"role": "user", "content": "I had a heavy flu in July."},
  {"role": "assistant", "content": "Flu"}, {"role": "user",
                                            "content": "Last year I was feeling really well, when all of a sudden I had severe breathtaking problems and high fever. I thought it was a flu, but it turned out to be Covid-19."},
  {"role": "assistant", "content": "Covid-19"}], ["sex", {"role": "system",
                                                          "content": "You are an expert in text understanding and your job is to take a given text about an illness and to extract the sex of the author. If the sex isn't clear, you should take the context into account. Only if the context doesn't help, you should return 'N/A'."},
                                                  {"role": "user",
                                                   "content": "I am a 25 year old software engineer living in California with my girlfriend. When I got Covid-19 last year I was really worried about my job and my girlfriend."},
                                                  {"role": "assistant", "content": "male"}, {"role": "user",
                                                                                             "content": "I am a nurse living in Berlin with my boyfriend. When I got Covid-19 last year I was really worried about my job and my boyfriend."},
                                                  {"role": "assistant", "content": "female"}, {"role": "user",
                                                                                               "content": "I got Covid-19 last year and I was really worried about my job. The diesease itself wasn't even that hard but it stressed me out, that I wasn't allowed to go to my job!"},
                                                  {"role": "assistant", "content": "N/A"}, {"role": "user",
                                                                                            "content": "I am a 25 year old software engineer living in California with my girlfriend. When I got Covid-19 that struck me as a mother of two really heavily."},
                                                  {"role": "assistant", "content": "female"}, {"role": "user",
                                                                                               "content": "I am a nurse living in Berlin. When I got Covid-19 I had to stay home what really hit me. As a divorced father I only see my boy once every month and now I couldn't even do that."},
                                                  {"role": "assistant", "content": "male"}], ["age", {"role": "system",
                                                                                                      "content": "You are an expert in text understanding and your job is to take a given text about an illness and to extract the age of the author. If the sex isn't clear, you should take the context into account. Young means 25, middle aged 50 and old 75. Only if the context doesn't help, you should return 'N/A'."},
                                                                                              {"role": "user",
                                                                                               "content": "I am a 22 year old software engineer living in California with my girlfriend. When I got Covid-19 last year I was really worried about my job and my girlfriend."},
                                                                                              {"role": "assistant",
                                                                                               "content": "22"},
                                                                                              {"role": "user",
                                                                                               "content": "I am a nurse living in Berlin. When I got Covid-19 I had to stay home what really hit me. Luckily as a young person I recovered quickly."},
                                                                                              {"role": "assistant",
                                                                                               "content": "25"},
                                                                                              {"role": "user",
                                                                                               "content": "I got Covid-19 last year and I was really worried about my job. The diesease itself wasn't even that hard but it stressed me out, that I wasn't allowed to go to my job!"},
                                                                                              {"role": "assistant",
                                                                                               "content": "N/A"},
                                                                                              {"role": "user",
                                                                                               "content": "I am an old man, so Covid-19 wasn't all easy on me."},
                                                                                              {"role": "assistant",
                                                                                               "content": "75"}],
 ["origin", {"role": "system",
             "content": "You are an expert in text understanding and your job is to take a given text about an illness and to extract the origin country of the author. If the origin isn't clear, you should take the context into account. Only if the context doesn't help, you should return 'N/A'. Return only the country of origin using two words a most."},
  {"role": "user",
   "content": "I am a 25 year old software engineer living in California with my girlfriend. When I got Covid-19 last year I was really worried about my job and my girlfriend."},
  {"role": "assistant", "content": "United States of America"}, {"role": "user",
                                                                 "content": "I am a nurse living in Berlin. When I got Covid-19 I had to stay home what really hit me. Luckily as a young person I recovered quickly."},
  {"role": "assistant", "content": "Germany"}, {"role": "user",
                                                "content": "I got Covid-19 last year and I was really worried about my job. The diesease itself wasn't even that hard but it stressed me out, that I wasn't allowed to go to my job!"},
  {"role": "assistant", "content": "N/A"}], ["preexisting_condition", {"role": "system",
                                                                       "content": "You are an expert in text understanding and your job is to take a given text about an illness and to extract previous diseases of the author. These diseases have to be EXPLICITLY MENTIONED. And they have to have occured BEFORE the illness the text is about! Return only the preexisting disease using two words a most."},
                                             {"role": "user",
                                              "content": "I got Covid-19 last year, which was hard since I since ever had to fight Asthma."},
                                             {"role": "assistant", "content": "Asthma"}, {"role": "user",
                                                                                          "content": "I infected me with Covid-19 right after I recovered from a heavy cold."},
                                             {"role": "assistant", "content": "Cold"}, {"role": "user",
                                                                                        "content": "I got Covid-19 last year and I was really worried about my job. The diesease itself wasn't  even that hard but it stressed me out, that I wasn't allowed to go to my job!"},
                                             {"role": "assistant", "content": "N/A"}, {"role": "user",
                                                                                       "content": "I got Covid-19 last year after I already got it right at the start in 2020."},
                                             {"role": "assistant", "content": "Covid-19"}]]

#### Activity Extraction

[
    {
        "role": "system",
        "content": [
            {
                "text": "You are an expert in text understanding and summarization. Your job is to take a given text about a person's course of disease and convert it into bullet points. If you are asked to focus on a specific condition, follow these steps:\n\n1. Think about which events are typically present in a course of disease with the specified condition.\n2. Scan the text and identify relevant events.\n3. Summarize only the relevant events in bullet points.\n4. Do not include timestamps and use a maximum of 6 words per bullet point.\n5. Only include one sentence number per bullet point.\n6. Create a new bullet point for every activity.\n7. Include the number of the sentence in the text from which you take the bullet point at the end of the sentence, like this '#number'.\n\nExample:\nText: \"1: On April 1, 2020, I started experiencing mild symptoms such as a persistent cough, fatigue, and a low-grade fever. 2: Four days later I went to the doctor and got tested positive for Covid-19. 3: Then I got hospitalized for two weeks.\"\n\nReasoning: The relevant events for Covid-19 include symptom onset, doctor visits, test results, and hospitalizations.\n\nSummary:\nstarting to experience symptoms #1\nvisiting doctor's #2\ntesting positive for Covid-19 #2\ngetting admitted to hospital #3\ngetting discharged from hospital #3\n\nNow, process the following text using the same approach:\n",
                "type": "text"
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "text": "8: Concerned about my condition, I contacted my primary care physician via phone.\\n9: He advised me to monitor my symptoms and stay at home unless they became severe.",
                "type": "text"
            }
        ]
    },
    {
        "role": "assistant",
        "content": [
            {
                "text": "contacting primary care physician #8\nmonitoring symptoms at home #9",
                "type": "text"
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "text": "5: First symptoms on 01/04/2020",
                "type": "text"
            }
        ]
    },
    {
        "role": "assistant",
        "content": [
            {
                "text": "starting to experience symptoms #5",
                "type": "text"
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "text": "5:After surviving Covid-19, I made getting vaccinated a top priority. 6: I received my first dose of the vaccine in early February 2022 and the second dose three weeks later. 7: Despite the challenges I faced during my infection, I remained determined to protect myself and others from the virus by getting vaccinated.",
                "type": "text"
            }
        ]
    },
    {
        "role": "assistant",
        "content": [
            {
                "text": "receiving first dose of vaccine #6\nreceiving second dose of vaccine #6",
                "type": "text"
            }
        ]
    }
]

### Extracting Start Date

[{"role": "system",
  "content": "You are an expert in text understanding and your job is to take a given text and a given activity label and to extract a start date to this activity label. The text might contain timestamps in the format --YYYYMM/DD--, with two hyphens enclosing the date. Only use these  timestamps as backup, in case no other time information is available. Only output the extracted start date! Rely on the context to determine the start date, as it might not be explicitly mentioned."},
 {"role": "user",
  "content": "Text: On April 1, 2020, I started experiencing mild symptoms such as a persistent cough, fatigue, and a low-grade fever --2020/04/01--. Four days later I went to the doctor and got tested positive for Covid19--2020/04/01--. In June I got infected again--2020/04/01--. After that I had a back pain--2020/04/01--.\nActivity Label: experiencing mild symptoms"},
 {"role": "assistant", "content": "20200401T0000"}, {"role": "user",
                                                     "content": "Text: On April 1, 2020, I started experiencing mild symptoms such as a persistent cough, fatigue, and a low-grade fever --2020/04/01--. Four days later I went to the doctor and got tested positive for Covid19--2020/04/01--. In June I got infected again--2020/04/01--. After that I had a back pain--2020/04/01--.\nActivity Label: testing positive for Covid19"},
 {"role": "assistant", "content": "20200405T0000"}, {"role": "user",
                                                     "content": "Text: On April 1, 2020, I started experiencing mild symptoms such as a persistent cough, fatigue, and a low-grade fever. Four days later I went to the doctor and got tested positive for Covid19. In June I got infected again. After that I had a back pain.\nActivity Label: getting infected again"},
 {"role": "assistant", "content": "20200601T0000"}, {"role": "user",
                                                     "content": "Text: On April 1, 2020, I started experiencing mild symptoms such as a persistent cough, fatigue, and a low-grade fever. Four days later I went to the doctor and got tested positive for Covid19. In June I got infected again. After that I had a back pain.\nActivity Label: having back pain"},
 {"role": "assistant", "content": "N/A"}, {"role": "user",
                                           "content": "Text: I started experiencing flu-like symptoms in July 21--2021/07/01--. I then got tested positive for Covid19--2021/07/01--. In October I got infected again--2021/10/01--. Then on the 4th of November I got my first dosage of the vaccine.--2021/11/04-- I had heavy side effects.\nActivity Label: starting to experience symptoms"},
 {"role": "assistant", "content": "20210701T0000"}, {"role": "user",
                                                     "content": "Text: I started experiencing flu-like symptoms in July 21. I then got tested positive for Covid19. In October I got infected again. Then on the 4th of November I got my first dosage of the vaccine. I had heavy side effects.\nActivity Label: experiencing side effects of vaccination"},
 {"role": "assistant", "content": "20211104T0000"}]

### Extracting End Date

[{"role": "system",
  "content": "You are an expert in text understanding and your job is to take a given text, a given activity label and a given timestamp for the beginning of this activity and to then extract an end date to this activity label. The text might contain dates in the format --YYYYMM/DD--, with two hyphens enclosing the date. Only use these as backup, in case no other time information is available. Only output the extracted end date! Rely on the context to determine the end date, as it might not be explicitly mentioned. Use averages if necessary. If there is no information about the end date at all, please state the start date also as the end date."},
 {"role": "user",
  "content": "Text: On April 1, 2020, I started experiencing mild symptoms such as a persistent cough, fatigue, and a low-grade fever --2020/04/01--. Four days later I went to the doctor and got tested positive for Covid19--2020/04/01--. In June I got infected again--2020/04/01--. After that I had a back pain--2020/04/01--.\nActivity Label: experiencing mild symptoms\nStart Date: 20200401T0000"},
 {"role": "assistant", "content": "20200405T0000"}, {"role": "user",
                                                     "content": "Text: On April 1, 2020, I started experiencing mild symptoms such as a persistent cough, fatigue, and a low-grade fever --2020/04/01--. Four days later I went to the doctor and got tested positive for Covid19--2020/04/01--. In June I got infected again--2020/04/01--. After that I had a back pain--2020/04/01--..\nActivity Label: testing positive for Covid19\nStart Date: 20200405T0000"},
 {"role": "assistant", "content": "20200405T0000"}, {"role": "user",
                                                     "content": "Text: On April 1, 2020, I started experiencing mild symptoms such as a persistent cough, fatigue, and a low-grade fever. Four days later I went to the doctor and got tested positive for Covid19. In June I got infected again. After that I had a back pain.\nActivity Label: getting infected again\nStart Date: 20200601T0000"},
 {"role": "assistant", "content": "20200615T0000"}, {"role": "user",
                                                     "content": "Text: On April 1, 2020, I started experiencing mild symptoms such as a persistent cough, fatigue, and a low-grade fever. Four days later I went to the doctor and got tested positive for Covid19. In June I got infected again. After that I had a back pain.\nActivity Label: having back pain\nStart Date: N/A"},
 {"role": "assistant", "content": "N/A"}, {"role": "user",
                                           "content": "Text: I started experiencing flu-like symptoms in July 21--2021/07/21--. I then got tested positive for Covid19--2021/07/21--. In October I got infected again--2021/10/01--. Then on the 4th of November I got my first dosage of the vaccine--2021/11/04--. I had heavy side effects--2021/11/04--.\nActivity Label: experiencing side effects \nStart Date: 20211104T0000"},
 {"role": "assistant", "content": "20211106T0000"}, {"role": "user",
                                                     "content": "Text: Four days after the first of April 2020 I went to the doctor and got tested positive for Covid19. I was then hospitalized for two weeks.\nActivity Label: getting hospitalized\nStart Date: 20200405T0000"},
 {"role": "assistant", "content": "20200419T0000"}, {"role": "user",
                                                     "content": "Text: In the next time I made sure to improve my mental well being.\nActivity Label: improving mental well being\nStart Date: 20210610T0000"},
 {"role": "assistant", "content": "20210710T0000"}]

### Map Event Type

[{"role": "system",
  "content": "You are an expert in text categorization. \nYour task is to classify the given activity into one of the following categories: \n'Symptom Onset', 'Symptom Offset', 'Diagnosis', 'Doctor Visit', 'Treatment', 'Hospital Admission', 'Hospital Discharge', 'Medication', 'Lifestyle Change', or 'Feelings'. \nPlease ensure the category matches exactly with the given list in terms of spelling and capitalization. \n\nHere are some examples to guide you: \n- \"Visiting doctor's\" -> Doctor Visit \n- \"Testing positive for Covid19\" -> Diagnosis \n- \"Getting hospitalized\" -> Hospital Admission \n- \"Isolating at home\" -> Lifestyle Change \n- \"Prescribed medication for discomfort\" -> Medication \n- \"Seeking consultation with specialist\" -> Doctor Visit \n- \"Receiving vaccines to protect against Covid19\" -> Treatment \n- \"Feeling a sense of relief\" -> Feelings \n- \"Starting to experience symptoms\" -> Symptom Onset \n\nNow, classify the following activity: "},
 {"role": "user", "content": "visiting doctor's"}, {"role": "assistant", "content": "Doctors Visit"},
 {"role": "user", "content": "testing positive for Covid19"}, {"role": "assistant", "content": "Diagnosis"},
 {"role": "user", "content": "getting hospitalized"}, {"role": "assistant", "content": "Hospital Admission"},
 {"role": "user", "content": "isolating at home"}, {"role": "assistant", "content": "Lifestyle Change"},
 {"role": "user", "content": "prescribed medication for discomfort"}, {"role": "assistant", "content": "Medication"},
 {"role": "user", "content": "seeking consultation with specialist"}, {"role": "assistant", "content": "Doctors Visit"},
 {"role": "user", "content": "receiving vaccines to protect against Covid19"},
 {"role": "assistant", "content": "Treatment"}, {"role": "user", "content": "feeling a sense of relief"},
 {"role": "assistant", "content": "Feeling"}, {"role": "user", "content": "starting to experience symptoms"},
 {"role": "assistant", "content": "Symptom Onset"}]

### Map Location

[{"role": "system",
  "content": "You are an expert in text categorization. Your job is to categorize a given activity label into one of the following categories: 'Home', 'Hospital', or 'Doctors'. Use the context provided in the examples to make your decision.\n\nDefinitions and examples:\n- **Home**: Activities that occur within one's residence or relate to home-based actions. \n  Examples: \"consulting doctor over phone\", \"isolating at home\", \"feeling a sense of relief\".\n- **Hospital**: Activities that involve being admitted to or receiving treatment in a hospital. \n  Examples: \"getting hospitalized\", \"receiving special care with a ventilator\".\n- **Doctors**: Activities related to consultations, visits, or treatments by doctors, not necessarily in a hospital.\n  Examples: \"visiting doctor's\", \"testing positive for Covid19\", \"prescribed medication for discomfort\".\n\nCategorize the following activities:\n\nActivity: \"visiting doctor's\"\nCategory: Doctors\n\nActivity: \"consulting doctor over phone\"\nCategory: Home\n\nActivity: \"testing positive for Covid19\"\nCategory: Doctors\n\nActivity: \"getting hospitalized\"\nCategory: Hospital\n\nActivity: \"isolating at home\"\nCategory: Home\n\nActivity: \"prescribed medication for discomfort\"\nCategory: Doctors\n\nActivity: \"receiving special care with a ventilator\"\nCategory: Hospital\n\nActivity: \"receiving vaccines to protect against Covid19\"\nCategory: Doctors\n\nActivity: \"feeling a sense of relief\"\nCategory: Home\n\nActivity: \"starting to experience symptoms\"\nCategory: Home\n\nNow, categorize the following activity:\nActivity: \"insert new activity here\"\nCategory:"
  }, {"role": "user", "content": "visiting doctor's"}, {"role": "assistant", "content": "Doctors"},
 {"role": "user", "content": "consulting doctor over phone"}, {"role": "assistant", "content": "Home"},
 {"role": "user", "content": "testing positive for Covid19"}, {"role": "assistant", "content": "Doctors"},
 {"role": "user", "content": "getting hospitalized"}, {"role": "assistant", "content": "Hospital"},
 {"role": "user", "content": "isolating at home"}, {"role": "assistant", "content": "Home"},
 {"role": "user", "content": "prescribed medication for discomfort"}, {"role": "assistant", "content": "Doctors"},
 {"role": "user", "content": "receiving special care with a ventilator"}, {"role": "assistant", "content": "Hospital"},
 {"role": "user", "content": "receiving vaccines to protect against Covid19"},
 {"role": "assistant", "content": "Doctors"}, {"role": "user", "content": "feeling a sense of relief"},
 {"role": "assistant", "content": "Home"}, {"role": "user", "content": "starting to experience symptoms"},
 {"role": "assistant", "content": "Home"}]
