# Appointment Scheduling Service

A microservice for booking appointments and managing appointment time slot reservations with MongoDB integration.

## Overview

This microservice provides functionality for customers to view available time slots, book appointments, and receive confirmation notifications by integrating with the Email Microservice. It uses MongoDB for persistent storage and includes an optimistic check to prevent double-booking.


## Features

### User Story 1: Book Resource Time Slot
As a customer, I want to view available dates/times and schedule a specific appointment for a required resource so that I can select a reservation that fits my schedule.

**Key Capabilities:**
- View available time slots for specific resources
- Book appointments with immediate reservation
- Prevent double-booking with optimistic check
- Persist appointment details in MongoDB  

### User Story 2: Receive Appointment Confirmation
**As a customer**, I want to receive an email confirming my scheduled appointment so that I have a verified record.

**Key Capabilities**
- Automatic email confirmation  
- Integration with the Email Microservice (`/send-email`)  
- Error handling and delivery status reporting  

## API Endpoints

### Health Check
```
GET /health
```
Returns service health status.

**Response:**
```json
{
  "message": "Appointment Scheduling Microservice Online"
}
```

### Get Available Slots
```
GET /api/slots/available?resource_id={resource_id}
```
Retrieves available time slots for a specific resource from MongoDB.

**Query Parameters:**
- `resource_id` (string, optional): The ID of the resource (if not provided, returns all slots)

**Response:**
```json
{
  "message": "Available slots endpoint",
  "resource_id": "resource123",
  "available_slots": [
    {
      "_id": "slot_id",
      "resource_id": "resource123",
      "date": "2024-12-15",
      "time": "14:00",
      "available": true
    }
  ]
}
```

### Book Appointment
```
POST /api/appointments
```
Books a new appointment for a customer with optimistic locking to prevent conflicts.

**Request Body:**
```json
{
  "customer_id": "customer123",
  "resource_id": "resource456",
  "date": "2024-12-15",
  "time": "14:00",
  "customer_email": "customer@example.com"
}
```

**Response (Success):**
```json
{
  "message": "Appointment booked successfully",
  "appointment_id": "674a1b2c3d4e5f6g7h8i9j0k",
  "customer_id": "customer123",
  "resource_id": "resource456",
  "date": "2024-12-15",
  "time": "14:00",
  "status": "confirmed"
}
```

**Response (Conflict):**
```json
{
  "error": "Slot already booked"
}
```

### Confirm Appointment
```
POST /api/appointments/confirm
```
Sends appointment confirmation email via the Email Microservice.

**Request Body:**
```json
{
  "appointment_id": "674a1b2c3d4e5f6g7h8i9j0k"
}
```

**Response:**
```json
{
  "message": "Confirmation processed",
  "appointment_id": "674a1b2c3d4e5f6g7h8i9j0k",
  "notification_status": "sent"
}
```

**Error Responses:**
- `400 Bad Request`: Missing or invalid appointment_id
- `404 Not Found`: Appointment not found
- `notification_status: "failed"`: Email service unavailable

### Get Appointment Details
```
GET /api/appointments/{appointment_id}
```
Retrieves details of a specific appointment by ID.

**Response:**
```json
{
  "message": "Appointment details",
  "appointment_id": "674a1b2c3d4e5f6g7h8i9j0k",
  "appointment": {
    "_id": "674a1b2c3d4e5f6g7h8i9j0k",
    "customer_id": "customer123",
    "resource_id": "resource456",
    "date": "2024-12-15",
    "time": "14:00",
    "customer_email": "customer@example.com",
    "status": "confirmed",
    "created_at": "2024-12-01T10:30:00"
  }
}
```

## Setup and Installation

### Prerequisites
- Python 3.9 or higher
- MongoDB (running locally or remote instance)
- pip

### Local Development

1. **Clone the repository:**
```bash
git clone 
cd Appointment-Scheduling-Service
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables (optional):**
Create a `.env` file in the root directory:
```
MONGO_URI=mongodb://localhost:28018/
PORT=5006
CORS_ORIGINS=http://localhost:5173,http://localhost:5000
EMAIL_MICROSERVICE_URL=http://127.0.0.1:5002/send-email
```

4. **Run the service:**
```bash
python app.py
```

The service will start on `http://localhost:5006`

### Docker Deployment

1. **Build the Docker image:**
```bash
docker build -t appointment-scheduling-service .
```

2. **Run the container:**
```bash
docker run -p 5006:5006 \
  -e MONGO_URI=mongodb://host.docker.internal:28018/ \
  -e EMAIL_MICROSERVICE_URL=http://host.docker.internal:5002/send-email \
  appointment-scheduling-service
```

3. **Verify the service is running:**
```bash
curl http://localhost:5006/health
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Port number for the service | `5006` |
| `CORS_ORIGINS` | Comma-separated list of allowed CORS origins | `http://localhost:5173,http://localhost:5000` |
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:28018/` |
| `EMAIL_MICROSERVICE_URL` | URL for the Email Microservice | `http://127.0.0.1:5002/send-email` |

## MongoDB Collections

The service uses the following MongoDB collections:

### Database: `appointment_scheduling_db`

**Collection: `appointments`**
- Stores booked appointments
- Fields: `customer_id`, `resource_id`, `date`, `time`, `customer_email`, `status`, `created_at`

**Collection: `available_slots`**
- Stores available time slots for resources
- Fields: `resource_id`, `date`, `time`, `available`

## Architecture

### Quality Attributes

**Integrity:**
- Implements optimistic locking mechanism to prevent double-booking
- Validates appointment existence before processing confirmations
- Ensures data correctness with MongoDB transactions

**Reliability:**
- Error handling for Email Microservice integration
- Timeout protection (5-second timeout) for external service calls
- Graceful degradation when email service is unavailable

**Scalability:**
- Stateless design allows horizontal scaling
- MongoDB provides flexible data storage
- CORS configuration supports multiple frontend origins

## Technology Stack

- **Framework:** Flask 3.0.0
- **Database:** MongoDB with PyMongo
- **CORS Support:** Flask-Cors 4.0.0
- **HTTP Client:** Requests library
- **Environment Management:** python-dotenv 1.0.0
- **Containerization:** Docker

## Team

- **Lev:** Main Implementation
- **Olivia:** Collaborator

## Known Issues & Limitations

1. **Bug in `get_available_slots`:** Line 35 references undefined variable `slots_cursor` (should be `cursor`)
2. **Syntax Error:** Line 48 has duplicate colon in error response
3. No transaction support for atomic operations across collections
4. Email confirmation is synchronous (could benefit from async/queue implementation)

## Future Enhancements

- Add cancellation and rescheduling endpoints
- Implement slot availability updates after booking
- Add authentication and authorization
- Implement message queue for email notifications
- Add comprehensive error logging
- Unit and integration tests

## License

Educational project for CS361 at Oregon State University.
