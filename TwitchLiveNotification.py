"""
Twitch notifications with python
Uses twitch api to notify if streamer is live faster than twitch's integrated live notifications can

Requries:
Gmail account (two accounts recommended, as the sender needs "Less secure app access")
Twitch api access
"""
import json
import requests
import smtplib
import time

streamers = ["timthetatman", "summit1g", "riotgames"]           #List of streamers to check

client_id = "<client id>"                                       #ID for twitch api
oauth_key = "<oauth_key>"                                       #OAuth key for twitch api
gmail_user = "<gmail_address_sender>"                           #Email to send notification FROM (Less secure app access must be turned ON)
gmail_pwd = "<gmail_password>"                                  #Password for email
send_msg_to = "<gmail_address_receiver>"                        #Email to send notification TO

def check_status(streamers):
        url = "https://api.twitch.tv/helix/streams"
        headers = {"Client-ID": client_id, "Authorization": "Bearer "+oauth_key}
        for i, streamer in enumerate(streamers):                #Creates the api url to check status of all streamers
            if i ==0:
                url = url+"?user_login="+streamer
            else:
                url = url+"&user_login="+streamer
        response = requests.get(url,  headers=headers).json()   #Gets status
        is_live = [False] * len(streamers)                      #Initialise
        if len(response['data']) != 0:                          #If response is not empty a stream is online
            for i in range(len(response['data'])):              #Check which are online
                index = streamers.index(response['data'][i]['user_name'].lower())
                is_live[index] = True
        return is_live

def notification(email_sent, is_live):
    for i, (a,b,c) in enumerate(zip(is_live, email_sent, streamers)):   #Checks if streamer is live, but email has not been sent yet
        if a == False:
            email_sent[i] = False
        elif a == True:                                                 #Send email if live and not already sent
            if b == False:
                send_email(c)
                email_sent[i] = True
    return email_sent

def send_email(streamer):                                      
    FROM = gmail_user
    TO = [send_msg_to]                                          #must be a list
    SUBJECT = streamer + " is now live"
    TEXT = 	"This is a python notification"
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (FROM, ", ".join(TO), SUBJECT, TEXT) #Creates the message
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)            #Setup email server connection
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print('successfully sent notification')
    except:
        print("failed to send mail")
	
if __name__ == "__main__":
    print("Notifications Turned On")
    email_sent = [True] * len(streamers)                        #Ensures that emails are not sent on start-up if already live
    #send_email("test")                                         #if email account settings are correct
    while True:                                                 #Check every 30s if streamers are online, then emails notification if has not already
        is_live = check_status(streamers)
        email_sent = notification(email_sent, is_live)
        #print(email_sent)                                      #Test twitch api is pulling correctly                              
        time.sleep(30)
