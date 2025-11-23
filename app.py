from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import requests
from bson import ObjectId
import os
from datetime import datetime

app = Flask(__name__)
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:5000").split(",")
CORS(app, resources={
    r"/*": {
        "origins": [o.strip() for o in allowed_origins if o.strip()],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:28018/")
client = MongoClient(MONGO_URI)
db = client["appointment_scheduling_db"]
appointments_col = db["appointments"]
slots_col = db["available_slots"]

@app.route("/health")
def health():
    return jsonify({"message": "Appointment Scheduling Microservice Online"}), 200

@app.route("/api/slots/available", methods=["GET"])
def get_available_slots():
    """
    User Story 1: Book Resource Time Slot
    Returns available date/time slots for a resource
    """
    resource_id = request.args.get("resource_id")
    # Fetch available slots from MongoDB
    query = {"resource_id": resource_id} if resource_id else {}
    cursor = slots_col.find(query)

    slots = []
    for slot in cursor:
        slot["_id"] = str(slot["_id"])
        slots.append(slot)

    return jsonify({
        "message": "Available slots endpoint",
        "resource_id": resource_id,
        "available_slots": slots
    }), 200

@app.route("/api/appointments", methods=["POST"])
def book_appointment():
    """
    User Story 1: Book Resource Time Slot
    Books a specific time slot for a customer
    Implements optimistic locking for integrity
    """
    data = request.get_json()
    customer_id = data.get("customer_id")
    resource_id = data.get("resource_id")
    date = data.get("date")
    time = data.get("time")
    customer_email = data.get("customer_email")

    # Basic validation
    if not all([customer_id, resource_id, date, time]):
        return jsonify({"error": "Missing required fields (customer_id, resource_id, date, time)"}), 400

    # Optimistic locking: check if slot is already booked
    existing = appointments_col.find_one({
        "resource_id": resource_id,
        "date": date,
        "time": time
    })
    if existing:
        return jsonify({"error": "Slot already booked"}), 409

    # Insert new appointment
    doc = {
        "customer_id": customer_id,
        "resource_id": resource_id,
        "date": date,
        "time": time,
        "customer_email": customer_email,
        "status": "confirmed",
        "created_at": datetime.utcnow().isoformat()
    }

    result = appointments_col.insert_one(doc)

    return jsonify({
        "message": "Appointment booked successfully",
        "appointment_id": str(result.inserted_id),
        "customer_id": customer_id,
        "resource_id": resource_id,
        "date": date,
        "time": time,
        "status": "confirmed"
    }), 201

# Email Microservice Integration
# This function sends a confirmation email by making a POST request to the /send-email endpoint
# of the Email Microservice. It retrieves the appointment details from MongoDB, extracts the customer's email,
# and sends the confirmation message. The result of the email operation is returned in the response.
@app.route("/api/appointments/confirm", methods=["POST"])
def confirm_appointment():

    """
    User Story 2: Receive Appointment Confirmation
    Sends a confirmation notification via the Email Microservice.
    """
    data = request.get_json() or {}
    appointment_id = data.get("appointment_id")

    if not appointment_id:
        return jsonify({"error": "appointment_id is required"}), 400

    # Fetch appointment details from MongoDB
    try:
        oid = ObjectId(appointment_id)
    except Exception:
        return jsonify({"error": "Invalid appointment ID format"}), 400
    appointment = appointments_col.find_one({"_id": oid})
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404

    customer_email = appointment.get("customer_email")
    if not customer_email:
        return jsonify({"error": "Customer email not found in appointment"}), 400

    # Prepare email payload
    email_payload = {
        "recipients": [customer_email],
        "subject_line": "Your appointment is confirmed!",
        "body": f"Your appointment (ID: {appointment_id}) has been confirmed.",
        "is_html": False
    }

    # Send request to email microservice
    email_service_url = os.getenv(
        "EMAIL_MICROSERVICE_URL",
        "http://127.0.0.1:5002/send-email"
    )

    try:
        response = requests.post(email_service_url, json=email_payload, timeout=5)
        response.raise_for_status()
        notification_status = "sent"
    except Exception:
        notification_status = "failed"

    return jsonify({
        "message": "Confirmation processed",
        "appointment_id": appointment_id,
        "notification_status": notification_status
    }), 200

@app.route("/api/appointments/<appointment_id>", methods=["GET"])
def get_appointment(appointment_id):
    """
    Retrieves appointment details by ID.
    """
    try:
        oid = ObjectId(appointment_id)
    except Exception:
        return jsonify({"error": "Invalid appointment ID format"}), 400

    appointment = appointments_col.find_one({"_id": oid})
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404

    appointment["_id"] = str(appointment["_id"])

    return jsonify({
        "message": "Appointment details",
        "appointment_id": appointment_id,
        "appointment": appointment
    }), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5006"))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)


