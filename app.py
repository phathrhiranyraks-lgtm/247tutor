from flask import Flask, render_template, request, jsonify
import os
import requests

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_tutor():
    # รับข้อมูลทั้งหมดจาก Frontend
    level = request.form.get('level')
    mode = request.form.get('mode')
    message = request.form.get('message', '')
    image = request.files.get('image')
    
    # 1. สร้าง Dynamic Prompt ตามตัวเลือกของนักเรียน
    mode_instructions = {
        "Soft": "ใบ้คำตอบทีละสเต็ปอย่างช้าๆ ให้กำลังใจเยอะๆ อย่าบอกสมการตรงๆ ให้ถามนำเพื่อให้นักเรียนคิด",
        "Medium": "อธิบายระดับปานกลาง บอกสมการที่ต้องใช้ และไกด์ทิศทางแรงหรือการตั้งแกนให้",
        "Expert": "อธิบายแบบรวบรัด ชี้จุดหลอกหรือจุดผิดพลาดที่พบบ่อย (Common mistakes) ทันที"
    }
    
    system_prompt = f"""
    คุณคือพี่นัท ติวเตอร์ฟิสิกส์ นักศึกษาวิศวกรรมระบบควบคุม มจธ.
    - นักเรียนคนนี้กำลังเรียนอยู่ระดับ: {level}
    - สไตล์การสอนที่คุณต้องใช้ตอบข้อนี้คือ: {mode_instructions.get(mode, "Medium")}
    - ถ้าเป็นไปได้ ให้เชื่อมโยงฟิสิกส์กับระบบวิศวกรรมควบคุม หรืออุปกรณ์ฮาร์ดแวร์ เพื่อให้เห็นภาพ
    """
    
    # 2. จำลองการวิเคราะห์ภาพโจทย์ (ในระบบจริงตรงนี้คือการส่งภาพให้ OCR/Vision Model)
    image_info = "แนบรูปภาพโจทย์มาด้วย" if image else "ไม่มีรูปภาพ"
    
    # 3. ส่งข้อมูลให้ Local LLM (Ollama)
    full_prompt = f"{system_prompt}\n\nสถานะรูปภาพ: {image_info}\nคำถามนักเรียน: {message}\nตอบ:"
    
    try:
        response = requests.post('http://localhost:11434/api/generate', json={
            "model": "llama3", # หรือโมเดลที่คุณใช้
            "prompt": full_prompt,
            "stream": False
        })
        ai_reply = response.json()['response']
    except Exception as e:
        ai_reply = "พี่กำลังปรับปรุงระบบอยู่นะครับ (เชื่อมต่อ Local AI ไม่สำเร็จ)"

    return jsonify({"reply": ai_reply})

if __name__ == '__main__':
    app.run(debug=True, port=5000)