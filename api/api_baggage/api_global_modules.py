from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.http import JsonResponse
import requests
from enhance.settings import SERVER_URL
from fcm.utils import get_device_model
from .models import CustomerBag
import datetime
from base_app.models import PushMessage
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.get_or_create(user=instance)


def transaction_update_create(parent_obj=None,child_obj=None,store_id=None,transaction=None,location1=None,location2=None,zone=None,status=None):
	print ("transaction_update_create",parent_obj)
	now = datetime.datetime.now()
	customer_requested = None
	customer_requested_time = None
	customer_requested_place = None

	if child_obj:
		for child in child_obj:
			print ("child-=================", child.id)
			if child.status == 0:
				child.status = 1
				child.save()

				if child.customer_requested and child.customer_requested == 1:
					print ("customer is requested")
					customer_requested = 1
					customer_requested_time = child.customer_requested_time
					customer_requested_place = child.customer_requested_place
				else:
					print ("else transaction_update_create")
					pass
			else:
				pass
	else:
		print ("no child found")
	obj = CustomerBag.objects.create()
	obj.pick_up_time=now
	
	obj.parent_id=parent_obj
	obj.transaction=transaction

	if status == None:
		obj.status=0
	else:
		obj.status=status
		parent_obj.status = 1
		parent_obj.save()

	if location1 != None:
		obj.location1=location1
	if location2 != None:
		obj.location2=location2
		if transaction == 11:
			obj.shelf=location2
	if store_id != None:
		obj.stored_location_id=store_id
	if zone != None:
		obj.zone=zone
	if customer_requested != None:
		obj.customer_requested=customer_requested
	if customer_requested_time != None:
		obj.customer_requested_time=customer_requested_time
	if customer_requested_place != None:
		obj.customer_requested_place=customer_requested_place
	if parent_obj != None and transaction != None: 
		obj.save()

def device_register(request):
	try:
		reg_id = request.GET.get('reg_id', None)
		device_id = request.GET.get('device_id', None)
		name = request.GET.get('name', None)
		url = SERVER_URL + '/fcm/v1/devices/'
		print ("url==============", url)
		try:
			Device = get_device_model()
			device_object = Device.objects.filter(dev_id=device_id)
			for dev in device_object:
				print ("deleting old data")
				dev.delete()
		except Exception as e:
			print (e)
			pass
		r = requests.post(url, dict(
			dev_id=device_id,
			reg_id=reg_id,
			name=name))
		print ("device registerd", r)
	except Exception as e:
		print ("Exception while registering device", e)
		pass
	return JsonResponse({'message':'Done'})



def send_message1(request):
	key = request.GET('key')
	try:
		Device = get_device_model()
		device_object = Device.objects.get(dev_id='cxm7vfc2VEw:APA91bEPCxpLA4UDEzZ_5hGaGSFBQQz9hBLQuspl_j7xLMxOIUgpPp-kkdZoLouJ1MjLteEqBbkha44b_GINE-g-6kwvKF9gYN0EUpfiDp4fRZrtwW1_BmjnQgK6nT2ngzCn4DBmn_st')
		response = device_object.send_message({'text':'my test message'}, collapse_key='CUSTOMER_DELIVERY_REQ')
		print ("send_message response===", response)


	except Exception as e:
		print ("Exception while sending message ", e)
		pass
	return JsonResponse({'message':'Done'})


def send_message(mobile_number=None,location1=None,location2=None,key=None):
	if mobile_number != None:
		try:
			Device = get_device_model()
			device_objects = Device.objects.filter(name=mobile_number)
			print ("device_object===", device_objects)
			for device_object in device_objects:
				result = {}
				result["mobile_number"] = str(device_object.name)
				result["device_id"] = str(device_object.dev_id)
				result["message"] = " "
				if key == 1:
					result["message"] = location1 + ' made a delivery request'
				elif key == 2:
					result["message"] = location1 + ' transferred bag to ' + location2
				elif key == 3:
					result["message"] = location1 + ' received bag from ' + location2
				elif key == 4:
					result["message"] = location2 + ' transferred bag to ' + location1
				elif key == 5:
					result["message"] = location2 + ' received bag from ' + location1
				elif key == 6:
					result["message"] = location2 + ' received bag from ' + location1
				else:
					print ("no action")

				print ("device_object mobile number", device_object.name)
				response = device_object.send_message({"message":result}, collapse_key='key')
				print ("send_message response===", response)
				success = 1
				for data in response:
					if 'success' in data:
						print ("sucess data check")
						success = data['success']
						print (success)
				PushMessage.objects.create(dev_id=str(device_object.dev_id),receiver=device_object.name, message_content=result['message'],status=success)
		except Exception as e:
			print ("Exception while sending message ", e)
			return JsonResponse({'message':'Failed'})
			pass
	return JsonResponse({'message':'Done'})