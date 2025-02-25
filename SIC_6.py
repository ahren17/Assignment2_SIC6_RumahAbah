import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Menggunakan variabel lingkungan untuk keamanan, atau gunakan connection string default
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://ahrenmustafa44:GSR4ilc78UtBArL7@cluster0.eltgc.mongodb.net/MyDatabase?retryWrites=true&w=majority&appName=Cluster0"
)

# Konfigurasi MongoDB
DATABASE_NAME = "MyDatabase"
COLLECTION_NAME = "SensorData"

# Membuat koneksi ke MongoDB menggunakan server API v1
try:
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
    # Kirim perintah ping untuk memastikan koneksi berhasil
    client.admin.command('ping')
    print("✅ Pinged your deployment. You successfully connected to MongoDB!")
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
except Exception as e:
    print(f"❌ Gagal terhubung ke MongoDB: {e}")

# Inisialisasi Flask dan aktifkan CORS
app = Flask(__name__)
CORS(app)

# Route untuk menerima data dari ESP32
@app.route('/sensor', methods=['POST'])
def receive_data():
    try:
        data = request.json  # Ambil data JSON dari ESP32
        if not data:
            return jsonify({"message": "No data received"}), 400

        # Validasi apakah data memiliki semua field yang dibutuhkan
        required_fields = {"temperature", "humidity", "motion"}
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Simpan data ke MongoDB
        collection.insert_one(data)
        return jsonify({"message": "Data stored successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route untuk mengambil data dari database
@app.route('/get_data', methods=['GET'])
def get_data():
    try:
        all_data = list(collection.find({}, {"_id": 0}))  # Ambil semua data tanpa field "_id"
        return jsonify(all_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Menjalankan Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
