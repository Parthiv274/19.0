import xmlrpc.client
import sys



BASE_URL = "http://localhost:8045"
DATABASE = "partner_credit_limit_v19_1"
USERNAME = "admin"
PASSWORD = "admin"


try:
    common = xmlrpc.client.ServerProxy(f'{BASE_URL}/xmlrpc/common')
    uid = common.authenticate(DATABASE,USERNAME,PASSWORD, {})

    if not uid:
        print("Login Failed")
        sys.exit()


    print("Login Successfull")

    models = xmlrpc.client.ServerProxy(f"{BASE_URL}/xmlrpc/object")
    partners = models.execute_kw(DATABASE,uid,PASSWORD,'res.partner', 'search_read',
            [[]],
            {
                'fields': ['name', 'credit_limit'],
                'context': {'lang': 'en_US'}
            }
    )
    print(f"\nFound {len(partners)} partners:\n")

    for partner in partners:
        name = partner.get('name', 'N/A')
        credit_limit = partner.get('credit_limit', 0)
        print(f"Name:{name}, Credit_limit:{credit_limit}")


except xmlrpc.client as e:
    print(f"XML-RPC Fault: {e.faultCode} - {e.faultString}")
    sys.exit()
except Exception as e:
    print(f"Error: {e}")
    sys.exit()
    

