from flask import Flask, jsonify, request
from flask_cors import CORS
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

# Temporary in-memory storage (Lev will replace with database)
appointments = []
available_slots = []

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
    # Placeholder - Lev will implement full logic
    return jsonify({
        "message": "Available slots endpoint",
        "resource_id": resource_id,
        "available_slots": available_slots
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
    
    # Placeholder - Lev will implement:
    # - Optimistic locking mechanism
    # - Database transaction
    # - Conflict detection
    
    return jsonify({
        "message": "Appointment booked successfully",
        "appointment_id": "placeholder_id",
        "customer_id": customer_id,
        "resource_id": resource_id,
        "date": date,
        "time": time,
        "status": "confirmed"
    }), 201

@app.route("/api/appointments/confirm", methods=["POST"])
def confirm_appointment():
    """
    User Story 2: Receive Appointment Confirmation
    Publishes confirmation message to notification queue
    Ensures at-least-once delivery for reliability
    """
    data = request.get_json()
    appointment_id = data.get("appointment_id")
    
    # Placeholder - Lev will implement:
    # - Message queue integration
    # - At-least-once delivery guarantee
    # - Notification service communication
    
    return jsonify({
        "message": "Confirmation sent to notification service",
        "appointment_id": appointment_id,
        "notification_status": "queued"
    }), 200

@app.route("/api/appointments/<appointment_id>", methods=["GET"])
def get_appointment(appointment_id):
    """
    Retrieves appointment details
    """
    # Placeholder - Lev will implement database lookup
    return jsonify({
        "message": "Appointment details",
        "appointment_id": appointment_id
    }), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5006"))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
