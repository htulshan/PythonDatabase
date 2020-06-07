#!/bin/python3

"""
    Flask application to create an inventory file and maintain it.
"""

from flask import Flask, render_template, request, redirect, url_for, abort
from sqlalchemy import exc
from ipaddress import ip_address
import csv

from database import DataBase

app = Flask(__name__)
db = DataBase("mysql://root:mysql@db/inventory_db")


class InvalidIPError(Exception):
    pass


def create_csv(data):
    with open('static/report.csv', 'w') as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(data[0].keys()),
            quoting=csv.QUOTE_NONNUMERIC,
        )
        writer.writeheader()
        for d in data:
            writer.writerow(d)


def ip_validator(ip):
    try:
        ip_address(ip)
        return True
    except:
        raise InvalidIPError


@app.errorhandler(409)
def error_409(e):
    return render_template('409.html'), 409


@app.before_request
def connect():
    db.connect()


@app.after_request
def disconnect(response):
    db.disconnect()
    return response


@app.route('/inventory')
def inventory_home():
    return render_template('welcome.html')


@app.route('/inventory/showalldevices')
def show_all_devices():
    data = [dict(foo) for foo in db.select_all()]
    if data:
        create_csv(data)
        return render_template('device.html', data=data)
    else:
        return render_template('empty.html')


@app.route('/inventory/showdevice', methods=['GET', 'POST'])
def show_device():
    try:
        if request.method == 'POST':
            ip_validator(request.form['address'])
            return redirect(url_for('device', address=request.form['address']))
        else:
            return render_template('show_device.html')
    except InvalidIPError:
        abort(422)


@app.route('/inventory/adddevice', methods=['GET', 'POST'])
def add_device():
    if request.method == 'POST':
        try:
            ip_validator(request.form['address'])
            data = {
                'address': request.form['address'],
                'name': request.form['name'],
                'device_type': request.form['device_type'],
                'group': request.form['group']
            }
            db.insert(data)

            return redirect(url_for('device', address=data['address']))
        except InvalidIPError:
            abort(422)
        except exc.IntegrityError:
            abort(409)
    else:
        return render_template('add_device.html')


@app.route('/inventory/deletedevice/<address>', methods=['GET', 'POST'])
def del_device(address):
    if request.method == 'POST':
        db.delete(address)
        return redirect(url_for('inventory_home'))
    else:
        return render_template('delete.html', data=dict(db.select_one(address)))


@app.route('/inventory/device/<address>')
def device(address):
    result = db.select_one(address)
    if result:
        data = dict(result)
        return render_template('device_detail.html', data=data)
    else:
        abort(404)


@app.route('/inventory/update/<address>', methods=['GET', 'POST'])
def update_device(address):
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'device_type': request.form['device_type'],
            'group': request.form['group']
        }
        db.update(address, data)
        return redirect(url_for('device', address=address))
    else:
        return render_template('update.html', data=dict(db.select_one(address)))
