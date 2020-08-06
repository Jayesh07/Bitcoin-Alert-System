import requests,json,time,datetime,math, statistics
from boltiot import  Bolt,Email
import csv
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt
import seaborn as sns
api_key="your bolt api key" #the api key and device id, you will find these things in your bolt account
device_id="your bolt device id"
telegram_chat_id = "@Jayesh_Rane"          # This is the channel ID of the created Telegram channel. Paste after @
telegram_bot_id = "bot742452212:AAGeaaI6bijVIlsi1hLjoZ4ohyUn_FGz2B8"         # This is the bot ID of the created Telegram Bot. Paste after bot
MAILGUN_API_KEY = 'c2e0d4e256d86aad1668a9fce9aed008-87cdd773-6243333f' 
SANDBOX_URL= 'sandbox143bff2cb9a74f06a86c4bb28d6ddc29.mailgun.org' 
SENDER_EMAIL = 'test-@sandbox143bff2cb9a74f06a86c4bb28d6ddc29.mailgun.org'
RECIPIENT_EMAIL = 'your email id'
FRAME_SIZE = 10
MUL_FACTOR = 6
mailer = Email(MAILGUN_API_KEY, SANDBOX_URL, SENDER_EMAIL, RECIPIENT_EMAIL)
mybolt=Bolt(api_key,device_id)
selling_price=100000
count=1
now=datetime.datetime.now()
date=now.date()
time1=now.time()

def compute_bounds(history_data,frame_size,factor):
    if len(history_data)<frame_size :
        return None

    if len(history_data)>frame_size :
        del history_data[0:len(history_data)-frame_size]
    Mn=statistics.mean(history_data)
    Variance=0
    for data in history_data :
        Variance += math.pow((data-Mn),2)
    Zn = factor * math.sqrt(Variance / frame_size)
    High_bound = history_data[frame_size-1]+Zn
    Low_bound = history_data[frame_size-1]-Zn
    return [High_bound,Low_bound]


history_data=[]
startTime = time.time()    # get the first lap's start time
lastTime = startTime
lapNum = 1

def send_telegram_message(message):
    """Sends message via Telegram"""
    url = "https://api.telegram.org/" + telegram_bot_id + "/sendMessage"
    data = {
        "chat_id": telegram_chat_id,
        "text": message
    }
    try:
        response = requests.request(
            "GET",
            url,
            params=data
        )
        print("This is the Telegram response")
        print(response.text)
        telegram_data = json.loads(response.text)
        return telegram_data["ok"]
    except Exception as e:
        print("An error occurred in sending the alert message via Telegram")
        print(e)
        return False


while (count<2):
    URL="https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD,JPY,EUR" # REPLACE WITH CORRECT URL
    response = requests.request("GET", URL)
    response = json.loads(response.text)
    current_price = response["USD"]
	#print(current_price)
    count=count+1
    if current_price>selling_price:
           print("The Current Price is",current_price)
           print("The Selling Price is",selling_price)
           print("Current Price is greater than the Selling Price")
           response = mybolt.digitalWrite('0', 'HIGH')
           print(response)
           print("LED is ON")
           time.sleep(5)
       	   response = mybolt.digitalWrite('0', 'LOW')
           print("LED is OFF")
           time.sleep(5)
           message = "The Bitcoin price is greater than " + str(selling_price) + \
                  ". The current value is " +str(current_price)
           telegram_status = send_telegram_message(message)
           response = mailer.send_email("ALERT","The Bitcoin price is greater than " + str(selling_price) + \
                  ". The current value is " +str(current_price))
           print ("Mailgun response is " + response.text)

    else:
           print("The Current Price is",current_price)
           print("The Selling Price is",selling_price)
           print("Current Price is less than the Selling Price")
           response = mybolt.digitalWrite('1', 'HIGH')
           print(response)
           print("LED is ON")
           time.sleep(5)
           response = mybolt.digitalWrite('1', 'LOW')
           print(response)
           print("LED is OFF")
           time.sleep(5)
           message = "The Bitcoin price is less than " + str(selling_price) + \
                  ". The current value is " +str(current_price)
           telegram_status = send_telegram_message(message)
           response = mailer.send_email("ALERT","The Bitcoin price is less than " + str(selling_price) + \
                  ". The current value is " +str(current_price))
           print ("Mailgun response is " + response.text)
    



    
    diff = current_price - selling_price 
    
    def get_length(file_path):
        with open(file_path) as csvfile:
            reader=csv.reader(csvfile)
            reader_list=list(reader)
            return len(reader_list)
        return 1

    def append_data(file_path,date,time,current_price,selling_price,diff):
        fieldnames=['date','time','current_price','selling_price','diff'] 
        next_id=get_length(file_path)
        with open(file_path,"a",newline='') as csvfile:
            writer=csv.DictWriter(csvfile,fieldnames=fieldnames)
            writer.writerow({"date":date,"time":time,"current_price":current_price,"selling_price":selling_price,"diff":diff})       
    append_data("C:\\Users\\Jayesh\\Desktop\\Database",date,time1,current_price,selling_price,diff)
   
    


data = pd.read_csv("C:\\Users\\Jayesh\\Desktop\\Database")   
plt.figure(figsize=(20,10))
sns.lineplot(y='Current_Price',x='Time',data=data,ci=None)
plt.title("Time vs Current Price")
plt.show()        

minimum_limit =current_price
maximum_limit =selling_price
count1=1
while (True):
    print ("This is the value "+str(current_price))
    bound = compute_bounds(history_data,FRAME_SIZE,MUL_FACTOR)
    if not bound:    
                required_data_count=FRAME_SIZE-len(history_data)
                print ("This is the value "+str(current_price))
                print("Not enough data to compute Z-score. Need ",required_data_count," more data points")
                history_data.append(int(current_price))
                time.sleep(2)
                continue
  

    try:
        if current_price > bound[0] :
                # print ("The temperature level increased suddenly. Sending an SMS.")
            message = "The Bitcoin's price increased suddenly than " + str(maximum_limit) + \
            ". The current value is " +str(current_price)
            telegram_status = send_telegram_message(message)
            print("This is the Telegram status:", telegram_status)
            break
	   # response = sms.send_sms("Someone has opened the fridge")
           # print("This is the response ",response)
        elif current_price < bound[1]:
           # print ("The temperature level decreased suddenly. Sending an SMS.")
                 message = "The Bitcoin's price decreased suddenly than " + str(minimum_limit) + \
                 ". The current value is " +str(current_price)
                 telegram_status = send_telegram_message(message)
                 print("This is the Telegram status:", telegram_status)
                 break
   # history_data.append(current_value)
    except Exception as e:
        print ("Error",e)
        time.sleep(5)






