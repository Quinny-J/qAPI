"""       
This project provides two endpoints: 
one for GeoIP lookup and another for Name Server lookup. 
It's built using Python and Flask.

----- Note
$: This whole thing is a WIP and may get updated now and then
$: DB Intergration in prog

----- Features
$: API Key Auth: Inorder to make a request the person must have a valid api key
$: GeoIP Lookup: Retrieve location information (city, region, country, latitude, longitude) for a given IP address.
$: Name Server Lookup: Retrieve the name server (NS) records for a given domain name.

----- Author
$: github.com/quinny-j

"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import dns.resolver
import re
import json
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_logs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class ApiLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100))
    endpoint = db.Column(db.String(100), nullable=False)
    status_code = db.Column(db.Integer, nullable=False)
    response = db.Column(db.Text, nullable=False)
    api_key = db.Column(db.String(100), nullable=False)

class ApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)

# Initialize database
@app.before_first_request
def create_tables():
    db.create_all()

# Utility functions
def validate_api_key(api_key):
    key = ApiKey.query.filter_by(key=api_key).first()
    return key is not None

def add_api_key(key):
    new_key = ApiKey(key=key)
    db.session.add(new_key)
    db.session.commit()

def log_request(ip, country, endpoint, status_code, response, api_key):
    new_log = ApiLog(ip=ip, country=country, endpoint=endpoint, status_code=status_code, response=json.dumps(response), api_key=api_key)
    db.session.add(new_log)
    db.session.commit()

def is_valid_ip(ip):
    pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    return pattern.match(ip) is not None

def is_valid_domain(domain):
    pattern = re.compile(r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)$|(?=.{1,253}\.[A-Za-z]{2,63}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)$")
    return all(pattern.match(part) for part in domain.split('.'))

# API endpoints
@app.route('/geoip', methods=['GET'])
def geoip_lookup():
    api_key = request.args.get('api_key')
    if not api_key or not validate_api_key(api_key):
        return jsonify({'error': 'Invalid or missing API key'}), 403

    ip = request.args.get('ip')
    if not ip:
        return jsonify({'error': 'IP address is required'}), 400
    if not is_valid_ip(ip):
        return jsonify({'error': 'Invalid IP address'}), 400

    response = requests.get(f'https://ipapi.co/{ip}/json/')
    status_code = response.status_code
    if status_code == 200:
        data = response.json()
        log_request(request.remote_addr, data.get('country', 'Unknown'), '/geoip', status_code, data, api_key)
        return jsonify(data)
    else:
        error_message = 'Failed to retrieve GeoIP information'
        log_request(request.remote_addr, 'Unknown', '/geoip', status_code, {'error': error_message}, api_key)
        return jsonify({'error': error_message}), 500

@app.route('/nslookup', methods=['GET'])
def ns_lookup():
    api_key = request.args.get('api_key')
    if not api_key or not validate_api_key(api_key):
        return jsonify({'error': 'Invalid or missing API key'}), 403

    domain = request.args.get('domain')
    if not domain:
        return jsonify({'error': 'Domain name is required'}), 400
    if not is_valid_domain(domain):
        return jsonify({'error': 'Invalid domain name'}), 400

    try:
        result = dns.resolver.resolve(domain, 'NS')
        ns_records = [str(ns) for ns in result]
        response = {'ns_records': ns_records}
        log_request(request.remote_addr, 'Unknown', '/nslookup', 200, response, api_key)
        return jsonify(response)
    except dns.resolver.NXDOMAIN:
        error_message = 'Domain does not exist'
        log_request(request.remote_addr, 'Unknown', '/nslookup', 404, {'error': error_message}, api_key)
        return jsonify({'error': error_message}), 404
    except Exception as e:
        error_message = str(e)
        log_request(request.remote_addr, 'Unknown', '/nslookup', 500, {'error': error_message}, api_key)
        return jsonify({'error': error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)
    add_api_key("your_static_api_key")
