# 🕹️ qAPI (Simple Python/Flask powered api)

## Overview
This project provides two endpoints: one for GeoIP lookup and another for Name Server lookup. It's built using Python and Flask.

## 📕 Features
- **API Key Auth**: Inorder to make a request the person must have a valid api key
- **GeoIP Lookup**: Retrieve location information (city, region, country, latitude, longitude) for a given IP address.
- **Name Server Lookup**: Retrieve the name server (NS) records for a given domain name.

## ⚡ Installation
1. Clone the repository:

```
git clone https://github.com/Quinny-J/qAPI.git
cd qAPI
```

2. Install dependencies:
```
pip install -r requirements.txt
```

## Usage
1. Start the bot:
```
python api.py
```

## Example

>$ curl -X GET "http://127.0.0.1:5000/nslookup?domain=example.com&api_key=YOUR-API-KEYHERE"

{
  "ns_records": [
    "ns1.example.com.",
    "ns2.example.com."
  ]
}

## 📋Error Handling
If the API key is missing or invalid, you will receive a 403 Forbidden response.
Invalid requests (e.g., missing parameters) will result in a 400 Bad Request response.
Server errors (e.g., DNS resolution issues) will result in a 500 Internal Server Error response.

## 📜 Logging
All API requests are logged to api_requests.log, including IP address, country, timestamp, status code, and response details.

## Disclaimer
This project is for educational purposes only. Misuse of this software for malicious purposes is strictly prohibited.

## License
This project is licensed under the MIT License - see the LICENSE file for details.