# Appointment Scheduling Service

A small Flask + MongoDB microservice for booking appointments and sending confirmation emails.

---

## Overview

This service lets a client:

- View available time slots for a resource
- Book an appointment (with a simple double-booking check)
- Send a confirmation email via the Email Microservice
- Look up an existing appointment by ID

MongoDB is used for persistence, and the Email Microservice is called over HTTP.

---

## API Endpoints

### Health Check

**GET** `/health`  
Returns basic status.

```json
{
  "message": "Appointment Scheduling Microservice Online"
}
```

---

### Get Available Slots

**GET** `/api/slots/available?resource_id={resource_id}`  

Returns available time slots for a given resource.

- `resource_id` (optional): if omitted, returns all slots.

Example response:

```json
{
  "message": "Available slots endpoint",
  "resource_id": "test_resource",
  "available_slots": [
    {
      "_id": "slot_id",
      "resource_id": "test_resource",
      "date": "2025-01-10",
      "time": "14:00",
      "available": true
    }
  ]
}
```

---

### Book Appointment

**POST** `/api/appointments`  

Request body:

```json
{
  "customer_id": "user123",
  "resource_id": "test_resource",
  "date": "2025-01-10",
  "time": "14:00",
  "customer_email": "test@example.com"
}
```

Success (201):

```json
{
  "message": "Appointment booked successfully",
  "appointment_id": "...</mongo id...>",
  "customer_id": "user123",
  "resource_id": "test_resource",
  "date": "2025-01-10",
  "time": "14:00",
  "status": "confirmed"
}
```

If the same resource/date/time is already booked:

```json
{
  "error": "Slot already booked"
}
```

Status code: **409 Conflict**

---

### Confirm Appointment (Email)

**POST** `/api/appointments/confirm`  

Request body:

```json
{
  "appointment_id": "...</mongo id...>"
}
```

Example response:

```json
{
  "message": "Confirmation processed",
  "appointment_id": "...</mongo id...>",
  "notification_status": "sent"
}
```

- `notification_status` is `"sent"` when the Email Microservice returns 2xx.
- Otherwise it is `"failed"` (network error or non-2xx response).

---

### Get Appointment Details

**GET** `/api/appointments/{appointment_id}`  

Example response:

```json
{
  "message": "Appointment details",
  "appointment_id": "...</mongo id...>",
  "appointment": {
    "_id": "...</mongo id...>",
    "customer_id": "user123",
    "resource_id": "test_resource",
    "date": "2025-01-10",
    "time": "14:00",
    "customer_email": "test@example.com",
    "status": "confirmed",
    "created_at": "2025-11-23T05:04:37.252650"
  }
}
```

---

## Setup

### 1. Start MongoDB

Example (Windows, MongoDB installed in Program Files):

```powershell
mkdir C:\Users\acos2\CS361\Project\data\mongo-appointments

"C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe" `
  --port 28018 `
  --dbpath "C:\Users\acos2\CS361\Project\data\mongo-appointments"
```

Make sure MongoDB is running on `mongodb://localhost:28018/`.

---

### 2. Install Dependencies

From the project root:

```bash
cd Appointment-Scheduling-Service
pip install -r requirements.txt
```

---

### 3. Environment Variables

Create a `.env` file in the project root (or use `.env.example` as a template):

```env
MONGO_URI=mongodb://localhost:28018/
PORT=5006
CORS_ORIGINS=http://localhost:5173,http://localhost:5000
EMAIL_MICROSERVICE_URL=http://127.0.0.1:5002/send-email
```

- `EMAIL_MICROSERVICE_URL` must point to a running instance of the Email Microservice.

---

### 4. Run the Service

```bash
python app.py
```

Service URL: `http://localhost:5006`

Check:

```bash
curl http://localhost:5006/health
```

---

## Helper Scripts

### `test.py`

- Sends a health check request
- Books a test appointment
- Calls the Email Microservice to send a confirmation
- Fetches the appointment by ID
- Verifies double-booking returns **409**

Run:

```bash
python test.py
```

---

### `clear_appointments.py`

Clears all documents from the `appointments` collection in `appointment_scheduling_db`.  
Useful when resetting test data.

Run:

```bash
python clear_appointments.py
```

---

## Team

- **Lev** – Original implementation (service skeleton and endpoints)
- **Olivia** – MongoDB integration, Email Microservice integration, CORS configuration, `test.py`, `clear_appointments.py`, and README updates.
- 
