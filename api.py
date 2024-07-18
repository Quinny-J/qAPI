"""       
This project provides two endpoints: 
one for GeoIP lookup and another for Name Server lookup. 
It's built using Python and Flask.

----- Note
$: This whole thing is a WIP and may get updated now and then

----- Features
$: API Key Auth: Inorder to make a request the person must have a valid api key
$: GeoIP Lookup: Retrieve location information (city, region, country, latitude, longitude) for a given IP address.
$: Name Server Lookup: Retrieve the name server (NS) records for a given domain name.

----- Author
$: github.com/quinny-j

"""

from flask import Flask, request, jsonify
import requests
import dns.resolver
import re
import logging
from datetime import datetime

app = Flask(__name__)

# Set a api key here
API_KEY = "qAPI-User1"

# Configure logging
logging.basicConfig(filename='api_requests.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def is_valid_ip(ip):
    pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    return pattern.match(ip) is not None

def is_valid_domain(domain):
    pattern = re.compile(r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)$|(?=.{1,253}\.[A-Za-z]{2,63}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)$")
    return all(pattern.match(part) for part in domain.split('.'))

def log_request(ip, country, status_code, response):
    logging.info(f"IP: {ip}, Country: {country}, Status Code: {status_code}, Response: {response}")

def get_country_from_ip(ip):
    response = requests.get(f'https://ipapi.co/{ip}/json/')
    if response.status_code == 200:
        data = response.json()
        return data.get('country', 'Unknown')
    return 'Unknown'

@app.before_request
def require_api_key():
    api_key = request.args.get('api_key')
    if api_key != API_KEY:
        return jsonify({'error': 'Invalid or missing API key'}), 403

# Endpoint for GeoIP lookup
@app.route('/geoip', methods=['GET'])
def geoip_lookup():
    ip = request.args.get('ip')
    if not ip:
        return jsonify({'error': 'IP address is required'}), 400
    if not is_valid_ip(ip):
        return jsonify({'error': 'Invalid IP address'}), 400

    response = requests.get(f'https://ipapi.co/{ip}/json/')
    status_code = response.status_code
    if status_code == 200:
        data = response.json()
        log_request(request.remote_addr, get_country_from_ip(request.remote_addr), status_code, data)
        return jsonify(data)
    else:
        error_message = 'Failed to retrieve GeoIP information'
        log_request(request.remote_addr, get_country_from_ip(request.remote_addr), status_code, error_message)
        return jsonify({'error': error_message}), 500

# Endpoint for Name Server lookup
@app.route('/nslookup', methods=['GET'])
def ns_lookup():
    domain = request.args.get('domain')
    if not domain:
        return jsonify({'error': 'Domain name is required'}), 400
    if not is_valid_domain(domain):
        return jsonify({'error': 'Invalid domain name'}), 400

    try:
        result = dns.resolver.resolve(domain, 'NS')
        ns_records = [str(ns) for ns in result]
        response = {'ns_records': ns_records}
        log_request(request.remote_addr, get_country_from_ip(request.remote_addr), 200, response)
        return jsonify(response)
    except dns.resolver.NXDOMAIN:
        error_message = 'Domain does not exist'
        log_request(request.remote_addr, get_country_from_ip(request.remote_addr), 404, error_message)
        return jsonify({'error': error_message}), 404
    except Exception as e:
        error_message = str(e)
        log_request(request.remote_addr, get_country_from_ip(request.remote_addr), 500, error_message)
        return jsonify({'error': error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)
