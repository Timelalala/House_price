# -----------------------------
# 🔹 Import Python libraries
# -----------------------------
from flask import Flask, request, jsonify         # สำหรับสร้าง web API
from flask_cors import CORS                       # เพื่อเปิด CORS ให้สามารถเรียกจาก front-end ได้
from pydantic import BaseModel, Field, ValidationError  # สำหรับ validate ข้อมูล input
from werkzeug.exceptions import BadRequest        # สำหรับจัดการข้อผิดพลาดของ request
import joblib                                     # สำหรับโหลดโมเดลที่ train ไว้
import numpy as np                                # สำหรับจัดการข้อมูลในรูปแบบ array

# -----------------------------
# 🔹 Configuration
# -----------------------------
app = Flask(__name__) # สร้าง Flask app เพื่อใช้สร้าง API
CORS(app)  # เปิดใช้งาน CORS เพื่อให้ front-end เรียก API ได้
MODEL_PATH = "house_price_model.pkl" # ที่เก็บโมเดลที่ train ไว้

# -----------------------------
# 🔹 Load ML model at startup
# -----------------------------
try:
    model = joblib.load(MODEL_PATH)   # โหลดโมเดลที่ train ไว้แล้ว
except Exception as e:
    raise RuntimeError(f"Failed to load model: {e}")  # ถ้าโหลดไม่สำเร็จ ให้หยุดโปรแกรมพร้อมข้อความ

# -----------------------------
# 🔹 Define input schema to validate inputs 
# -----------------------------
class HouseFeatures(BaseModel):
    age: int = Field(..., ge=0, le=120)          # อายุบ้าน (0-120 ปี)
    distance: int = Field(..., ge=0, le=10000)    # ระยะทางถึง MRT (เมตร)
    minimart: int = Field(..., ge=0, le=20)       # จำนวนร้านสะดวกซื้อใกล้เคียง

# -----------------------------
# 🔹 Hello World API
# -----------------------------
@app.route("/api/hello", methods=["GET"])
def hello_world():
    return jsonify({"message": "hello world"}) 

# -----------------------------
# 🔹 Hourse Price Prediction API
# -----------------------------
@app.route("/api/house", methods=["POST"])
def predict_house_price():
    try:
        # รับข้อมูล JSON จาก client
        data = request.get_json()

        # ตรวจสอบและแปลงข้อมูลด้วย Pydantic
        features = HouseFeatures(**data)

        # จัดรูปข้อมูลให้อยู่ในรูป numpy array เพื่อส่งเข้าโมเดล
        x = np.array([[features.age, features.distance, features.minimart]])

        # ทำนายราคาด้วยโมเดลที่โหลดมา
        prediction = model.predict(x)

        # ส่งผลลัพธ์กลับในรูป JSON
        return jsonify({
            "status": True,
            "price": np.round(float(prediction[0]*1000), 2),  # คูณ 1000 เป็น บาท
            "currency": "บาท/ตร.ม."
        })

    except ValidationError as ve:
        # จัดการข้อผิดพลาดกรณี input ไม่ถูกต้อง (เช่น อายุเป็น -1)
        errors = {}
        print(ve.errors())
        for error in ve.errors():
            field = error['loc'][0]
            msg = error['msg']                        
            errors.setdefault(field, []).append(msg) #errors[field] = msg
        return jsonify({"status": False, "detail": errors}), 400
    except BadRequest as e: 
        # จัดการข้อผิดพลาดกรณี input ไม่ถูกต้อง (เช่น อายุเป็น a)
        return jsonify({
            "status": False,
            "error": "Invalid JSON format",
            "detail": str(e)
        }), 400
    except Exception as e:
        # จัดการข้อผิดพลาดอื่น ๆ (มิติของข้อมูลในตัวแปร x ไม่ตรงกับโมเดล)
        return jsonify({"status": False, "error": str(e)}), 500

# -----------------------------
# 🔹 Run API server
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

