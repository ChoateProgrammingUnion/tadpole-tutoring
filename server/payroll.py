from config import EXTERNAL_TUTOR_RATE, STRIPE_API_KEY
from pymongo import MongoClient
from utils.log import log_info
import datetime
import stripe
import notify


class payroll:

    def __init__(self):
     try:
        self.client = MongoClient("localhost",27017)
        self.db = self.client.prod_database
        stripe.api_key=STRIPE_API_KEY
     except:
        log_info("can't connect to db")
        return False
    def add_external_tutor(self,id:int):
        col = self.db.teachers # select the teacher collection
        if col.find_one({'$and':[{'id':id},{'is_external':True}]}) == None: # do not over write existing fields
            result = col.update_one({'id':id},{'$set':{'balance':0.0}}) # set the starting balance 
            if result.acknowledged and result.matched_count ==1: # make sure the write was acknowledged
                pass
            else:
                log_info("invalid assign card operation")
                return False
            col.update_one({'id':id},{'$set':{'is_external':True}}) #set the flag for external tutor
            result = stripe.Account.create(type='custom',
            requested_capabilities=[
                "card_payments",
                "transfers",
            ],business_type='individual')
            col.update_one({'id':id},{'$set':{"stripe_account":result['id']}})
            url = stripe.AccountLink.create(
                account=result['id'],
                failure_url= 'https://www.google.com',
                success_url='https://tadpoletutoring.org/?stripe_accoount='+col.find_one({'id':id})['stripe_account'],
                type='custom_account_verification',
                collect='eventually_due'
            )
            notify.Email().send(col.find_one({'id':id})['email'], "Tadpole Tutoring Onboarding"
            , "Hi "+col.find_one({'id':id})['first_name']+',\n\nPlease use the following link to onboard with us\n'
            +url['url']+'\n\nThanks!\nTadpole Tutoring') 
        else:
            log_info("attempted to add to an existing external tutor for id: " + str(id))
    def insert_external_account(self,account:str,card:str):
        col = self.db.teachers # select the teacher collection
        if col.find_one({'$and':[{'stripe_account':account},{'is_external':True}]}) != None:
            stripe.Account.create_external_account(
                account,
                external_account=card
            )
            col.update_one({'stripe_account':account},{'$set':{'card_number':card}})
            return True
        else:
            log_info("attempted to update card for a tutor that is not external or doesn't exist")
            return False
    def credit_sessions(self,id:int,hours: float):
        col = self.db.teachers # select the teacher collection
        if col.find_one({'$and':[{'id':id},{'is_external':True}]}) != None: # verfiy that this is an external tutor
            money = col.find_one({'id':id})['balance']
            money += (hours*EXTERNAL_TUTOR_RATE)
            col.update_one({'id':id},{'$set':{'balance':money}})
            trans = self.db.transactions # select the transctions collection
            trans.insert_one({'amount':money, "tutor_id":id,'timestamp':datetime.datetime.utcnow()}) # write this down for double entry
        else:
            log_info("attempted to credit sessions for a tutor that is not external or doesn't exist id:"+ str(id))
    def pay_out(self,id:int):
        col = self.db.teachers
        payout = col.find_one({'id':id})['balance']
        payout *= 100
        print(payout)
        stripe_account = col.find_one({'id':id})['stripe_account']
        print(stripe_account)
        try:
            stripe.Transfer.create(amount=int(payout),currency='usd',destination=stripe_account)
        except:
            log_info('unable to transfer money to connect stripe')
            return False 
        col.update_one({'id':id},{'$set':{'balance':0.0}})
        trans = self.db.transactions
        trans.insert_one({'amount':round((payout*-0.01),2), "tutor_id":id,'timestamp':datetime.datetime.utcnow()}) # write this down for double entry
        try:
            stripe.Payout.create(amount=int(payout),method='instant',currency='usd',stripe_account=stripe_account)
        except:
            try:
                stripe.Payout.create(amount=int(payout),currency='usd',stripe_account=stripe_account)
            except:
                log_info('stripe payment error')

    
        


pay=payroll()
pay.pay_out(4)   
# bank: btok_1Gupwe2eZvKYlo2CtBdtQiC2
#card: tok_mastercard_debit
