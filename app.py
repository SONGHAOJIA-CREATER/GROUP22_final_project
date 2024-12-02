from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token
from pymongo import MongoClient
import datetime
from flask_cors import CORS
from dotenv import load_dotenv
import os
from flask_pymongo import PyMongo
from flask_mail import Mail, Message
app = Flask(__name__)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
import secrets
from bson.json_util import dumps
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


CORS(app)  # 允许所有域名的跨域请求

uri = "mongodb+srv://shj040503:Shj20040503@xiange.osv5yac.mongodb.net/?retryWrites=true&w=majority&appName=xiange"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
db = client.luggage_management # 使用或创建一个数据库
users_collection = db['users']  # 使用或创建一个用户集合
flights_collection = db['flights']  # 使用或创建一个航班集合
luggage_collection = db['luggage']  # 使用或创建一个行李集合
orders_collection = db["orders"]


def init_db():
    if users_collection.count_documents({}) == 0:
        users_collection.insert_one({
            'email': 'test@example.com',
            'password': bcrypt.generate_password_hash('password123').decode('utf-8')
        })
    
    basic_flights = [
        {
            "flight_number": "FL1001",
            "origin": "New York",
            "destination": "Los Angeles",
            "departure_time": "2023-10-01T10:00:00",
            "arrival_time": "2023-10-01T13:00:00",
            "price": 299.99
        },
        {
            "flight_number": "FL1002",
            "origin": "San Francisco",
            "destination": "Chicago",
            "departure_time": "2023-10-01T08:30:00",
            "arrival_time": "2023-10-01T14:00:00",
            "price": 199.99
        },
        {
            "flight_number": "FL1003",
            "origin": "Miami",
            "destination": "New York",
            "departure_time": "2023-10-01T09:00:00",
            "arrival_time": "2023-10-01T12:00:00",
            "price": 249.99
        },
        {
            "flight_number": "FL1004",
            "origin": "Boston",
            "destination": "Seattle",
            "departure_time": "2023-10-02T07:00:00",
            "arrival_time": "2023-10-02T10:30:00",
            "price": 329.99
        },
        {
            "flight_number": "FL1005",
            "origin": "Dallas",
            "destination": "San Francisco",
            "departure_time": "2023-10-03T14:00:00",
            "arrival_time": "2023-10-03T16:30:00",
            "price": 199.99
        },
        {
            "flight_number": "FL1006",
            "origin": "Orlando",
            "destination": "Atlanta",
            "departure_time": "2023-10-04T12:00:00",
            "arrival_time": "2023-10-04T13:15:00",
            "price": 89.99
        },
        {
            "flight_number": "FL1007",
            "origin": "Los Angeles",
            "destination": "Las Vegas",
            "departure_time": "2023-10-05T15:00:00",
            "arrival_time": "2023-10-05T16:15:00",
            "price": 79.99
        },
        {
            "flight_number": "FL1008",
            "origin": "Chicago",
            "destination": "Miami",
            "departure_time": "2023-10-06T18:30:00",
            "arrival_time": "2023-10-06T21:00:00",
            "price": 199.99
        },
        {
            "flight_number": "FL1009",
            "origin": "Seattle",
            "destination": "New York",
            "departure_time": "2023-10-07T09:00:00",
            "arrival_time": "2023-10-07T15:00:00",
            "price": 349.99
        },
        {
            "flight_number": "FL1010",
            "origin": "Atlanta",
            "destination": "Washington D.C.",
            "departure_time": "2023-10-08T11:30:00",
            "arrival_time": "2023-10-08T13:00:00",
            "price": 129.99
        }
    ]

    # 进行初次插入
    if flights_collection.count_documents({}) == 0:
        flights_collection.insert_many(basic_flights)

    if luggage_collection.count_documents({}) == 0:
        luggage_collection.insert_many([
            {"id": "L001", "flight_number": "FL1001", "status": "在托运中"},
            {"id": "L002", "flight_number": "FL1001", "status": "已到达"},
            {"id": "L003", "flight_number": "FL1002", "status": "丢失"},
            {"id": "L004", "flight_number": "FL1003", "status": "在海关检查"},
            {"id": "L005", "flight_number": "FL1004", "status": "在托运中"},
            {"id": "L006", "flight_number": "FL1005", "status": "已到达"},
            {"id": "L007", "flight_number": "FL1006", "status": "丢失"},
            {"id": "L008", "flight_number": "FL1007", "status": "在海关检查"},
            {"id": "L009", "flight_number": "FL1008", "status": "已到达"},
            {"id": "L010", "flight_number": "FL1009", "status": "在托运中"},
            {"id": "L011", "flight_number": "FL1010", "status": "丢失"}
        ])

# 调用数据库初始化函数

init_db()


# 登录路由
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data:
        # 处理没有数据的情况
        return jsonify({'message': 'No input data provided'}), 400

    email = data.get('email')
    password = data.get('password')

    global user_found
    user_found = users_collection.find_one({'email': email},{'_id': 0})

    # 检查是否找到用户
    if user_found is None:
        response = jsonify({'message': 'Invalid email or password'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # 比较密码
    if password != user_found['password']:
        response = jsonify({'message': 'Invalid email or password'}) 
        response.status_code = 401  # 设置未授权状态码
        return response
        #response = jsonify({'message': 'Invalid email or password'})
    else:
        # 假设验证成功
        response = jsonify({'message': 'Login successful', 'user': {'email': user_found['email']}})

    # 添加 CORS 头
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    
    return response

load_dotenv()

#client = MongoClient('localhost', 27017)  # Connect to MongoDB on localhost
#mongo = PyMongo(app, uri='mongodb://localhost:27017/mydatabase')  # Replace 'mydatabase' with your database name


# Registration endpoint
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    full_name = data.get('full_name')
    phone_number = data.get('phone_number')  # 获取电话号码
    email = data.get('email')
    password = data.get('password')

    # 检查是否存在相同的用户
    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        return jsonify({"message": "User with this email already exists."}), 400

    # 创建新的用户
    new_user = {
        "full_name": full_name,
        "phone": phone_number,  # 添加电话号码字段
        "email": email,
        "password": password,  # 生产环境中，记得对密码进行哈希处理
    }
    users_collection.insert_one(new_user)

    return jsonify({"message": "User registered successfully."}), 201

# Password reset endpoint
'''
@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    
    user = users_collection.find_one({"email": data["email"]})

    if not user:
        return jsonify({"message": "User not found."}), 404

    # Generate a unique token for password reset
    token = secrets.token_urlsafe(16)
    
    # Usually, you would save the token in the database with expiration time
    # Here, we're just sending it via email for demonstration

    # Send email with password reset link
    msg = Message('Password Reset Request', recipients=[data['email']])
    msg.body = f'Click here to reset your password: http://localhost:5000/reset-password/{token}'
    
    try:
        mail.send(msg)
        return jsonify({"message": "Password reset link sent to your email."}), 200
    except Exception as e:
        return jsonify({"message": "Error sending reset link."}), 500
    '''

    

# 获取航班信息的路由
@app.route('/api/flights', methods=['GET'])
def get_flights():
    flights = list(flights_collection.find({}, {'_id': False}))  # 获取所有航班，排除 _id 字段
    return jsonify(flights)

@app.route('/api/bookings', methods=['POST'])
def book_flight():
    booking_data = request.json
    global flight_number_ordered
    flight_number_ordered = booking_data.get('flight_number')
    #global user_found

    if flight_number_ordered:
        # 假设您有一个 bookings_collection 用于存储订购记录
        #orders_collection.insert_one({'flight_number': flight_number_ordered})
        return jsonify({'message': 'The flight was ordered!'}), 201
    return jsonify({'error': 'The flight number cannot be empty!'}), 400
# API 路由：创建订单
@app.route('/api/orders', methods=['POST'])  # 使用 POST 方法
def create_order():
    data = request.json
    
    # 从请求中获取订单信息
    global flight_number_ordered
    customer_name = data.get('customerName')
    global customer_email
    customer_email = data.get('customerEmail')
    # 确保座位和航班号被正确定义和赋值
    seat = data.get('seat')  # 假设这些信息从请求体中获取
    flight_id = flight_number_ordered
    
    # 创建订单
    order = {
        "flightId": flight_id,
        "seat": seat,
        "customerName": customer_name,
        "customerEmail": customer_email,
        "createdAt": datetime.datetime.now()
    }

    try:
        result = orders_collection.insert_one(order)
        order["_id"] = str(result.inserted_id)  # 将 ObjectId 转换为字符串
        
        # 添加 CORS 头
        response = jsonify(order)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        
        return response, 201
    except Exception as e:
        return jsonify({"message": "Server error", "error": str(e)}), 500
    
@app.route('/api/orders_get', methods=['GET']) 
def get_order():
    global user_found
    global customer_email
    email = user_found['email']
    order_found = orders_collection.find_one({"customerEmail": customer_email},{'_id': 0})
    return jsonify(order_found)
    
@app.route('/api/seat-selection', methods=['POST'])
def select_seat():
    seat_data = request.json
    global seat_number
    seat_number = seat_data.get('seat_number')

    if seat_number:
        # 假设您有一个 seat_selection_collection 用于存储座位选择记录
        #seat_selection_collection.insert_one({'seat_number': seat_number})
        return jsonify({'message': 'Seat selection successful!'}), 201
    return jsonify({'error': 'The seat number cannot be empty!'}), 400
# 获取所有行李记录
@app.route('/api/luggage', methods=['GET'])
def get_luggage():
    luggage = list(luggage_collection.find({}, {'_id': False}))  # 获取所有行李
    return jsonify(luggage)


# 查询行李状态
@app.route('/api/luggage/query', methods=['GET'])
def query_luggage():
    flight_number = request.args.get('flightId')  # 获取航班号
    luggage_id = request.args.get('id')  # 获取行李 ID

    # 在数据库中查找行李记录
    luggage = luggage_collection.find_one({'flight_number': flight_number, 'id': luggage_id}, {'_id': False})

    if luggage:
        return jsonify(luggage), 200
    return jsonify({'error': 'No baggage records found'}), 404

# 更新行李状态
@app.route('/api/luggage/<string:luggage_id>', methods=['PUT'])
def update_luggage(luggage_id):
    updated_data = request.json
    result = luggage_collection.update_one({'id': luggage_id}, {'$set': updated_data})  # 根据 ID 更新状态

    if result.matched_count > 0:
        return jsonify({'message': 'The status of the baggage has been updated successfully'}), 200
    else:
        return jsonify({'error': 'The baggage record was not found'}), 404

# 删除行李记录
@app.route('/api/luggage/<string:luggage_id>', methods=['DELETE'])
def delete_luggage(luggage_id):
    result = luggage_collection.delete_one({'id': luggage_id})  # 根据 ID 删除行李记录

    if result.deleted_count > 0:
        return jsonify({'message': 'The status of the baggage has been DELETE successfully'}), 200
    else:
        return jsonify({'error': 'The baggage record was not found'}), 404


emergency_requests_collection = db['emergency_requests']  # 紧急请求集合
medical_info_collection = db['medical_info']  # 医疗信息集合
staff_availability_collection = db['staff_availability']  # 人员可用性集合
staff_availability_collection.insert_many([
    { 'name': "Doctor1", 'available': 'true' },
    { 'name': "Doctor2", 'available': 'false' },
    { 'name': "Doctor3", 'available': 'true' }
])
@app.route('/api/emergency_request', methods=['POST'])
def emergency_request():
    data = request.get_json()
    location = data.get('location')
    description = data.get('description')

    # 存储请求到 MongoDB
    emergency_request_doc = {
        'location': location,
        'description': description,
        'timestamp': datetime.datetime.now()
    }
    emergency_requests_collection.insert_one(emergency_request_doc)

    return jsonify({'message': 'Emergency request received successfully.'}), 201

@app.route('/api/medical_info', methods=['POST'])
def save_medical_info():
    data = request.get_json()
    passenger_id = data.get('passengerId')
    medical_history = data.get('medicalHistory')
    medications = data.get('medications')

    # 存储医疗信息到 MongoDB
    medical_info_doc = {
        'passengerId': passenger_id,
        'medicalHistory': medical_history,
        'medications': medications
    }
    medical_info_collection.insert_one(medical_info_doc)

    return jsonify({'message': 'Medical information saved successfully.'}), 201

@app.route('/api/check_availability', methods=['GET'])
def check_availability():
    # 假设有人可用的信息存储在MongoDB中
    available_staff = staff_availability_collection.find_one({'available': 'true'})

    if available_staff:
        availability_message = "Available staff: " + available_staff['name']
    else:
        availability_message = "No staff available at the moment."
    
    return jsonify({'message': availability_message}), 200

@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    """获取用户个人信息"""
    global user_found
    return jsonify(user_found)  
    #return jsonify({"message": "No user data found"}), 404



# 启动 Flask 应用
if __name__ == '__main__':
    app.run(debug=True, port=5000)
