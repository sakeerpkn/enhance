
####### SMS GATEWAY start here ########

###kapsystem 

# SMS_GATEWAY_URL = 'http://193.105.74.159/api/v3/sendsms/plain?'
# SMS_GATEWAY_USER = 'kapsystem'
# SMS_GATEWAY_PASS = 'j5SkaRdY'
# SMS_GATEWAY_SENDER_ID = 'KAPNFO'
# SMS_GATEWAY_TYPE = 'longsms'



# #### http://107.20.199.106/api/v3/sendsms/plain?user=anishjain&password=anishjain123&sender=NHANCE&SMSText=TestinglongSMS&GSM=91XXXXXXXXXX&type=longsms

# """  sample success response
# -------------------------
# <results>
# <result>
# <status>0</status>
# <messageid>178032110025268455</messageid>
# <destination>918089660929</destination>
# </result>
# </results>
# -------------------------

# """


SMS_GATEWAY_URL = 'http://107.20.199.106/api/v3/sendsms/plain?'
SMS_GATEWAY_USER = 'anishjain'
SMS_GATEWAY_PASS = 'anishjain123'
SMS_GATEWAY_SENDER_ID = 'NHANCE'
SMS_GATEWAY_TYPE = 'longsms'
SMS_CUSTOMER_ACCEPT_MSG = "Start your Hands Free Shopping Experience using the OTP {}. Your bags will be safely stored with us. To initiate a Pick Up, just come and ask our baggage service assistants or find your closest Pick Up Zone. Contact us at +919962340702 for any assistance."
SMS_CUSTOMER_HANDOVER_MSG = "Thank you for using the Hands Free Shopping Experience. Your OTP is {}. Please provide this to your Baggage Handler. If you enjoyed our service please leave a comment on our Facebook page NhanceGo. See you soon."

####### SMS GATEWAY end here ########

CUSTOMER_REQ = 1
HANDLER_TRANSFER = 2
HANDLER_RECIEVER = 3
ZONE_TRANSFER = 4
ZONE_RECIEVER = 5
CUSTOMER_RECEIVE = 6

