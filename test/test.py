import requests 

url='https://google.com'
# headers1={"Authorization": f'Bearer {token}'}
res=requests.get(url)
print(res.text)

