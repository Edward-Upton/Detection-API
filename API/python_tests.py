import requests
headers = {"key":"8ee516adb0c216f432ae6d9d0f0101b8"}
brickData = requests.get("https://rebrickable.com/api/v3/lego/parts/3001/", params=headers)
print(brickData.json())
print(type(brickData.json()))