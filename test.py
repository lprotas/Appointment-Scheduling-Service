import requests
import json

BASE = "http://127.0.0.1:5006"

def pretty(res):
    try:
        return json.dumps(res.json(), indent=2, ensure_ascii=False)
    except:
        return res.text


# Health Check
def test_health():
    print("\n[1] HEALTH CHECK")
    r = requests.get(f"{BASE}/health")
    print(pretty(r))


# Get Available Slots
def test_get_slots():
    print("\n[2] GET AVAILABLE SLOTS")
    r = requests.get(f"{BASE}/api/slots/available", params={"resource_id": "test_resource"})
    print(pretty(r))


# Book Appointment
def test_book_appt():
    print("\n[3] BOOK APPOINTMENT")
    payload = {
        "customer_id": "user123",
        "resource_id": "test_resource",
        "date": "2025-01-10",
        "time": "14:00",
        "customer_email": "test@example.com"
    }
    r = requests.post(f"{BASE}/api/appointments", json=payload)
    print(pretty(r))

    if r.status_code == 201:
        return r.json()["appointment_id"]
    return None


# Confirm Appointment (Email Microservice Test)
def test_confirm_appt(appointment_id):
    print("\n[4] CONFIRM APPOINTMENT (EMAIL)")
    payload = {"appointment_id": appointment_id}
    r = requests.post(f"{BASE}/api/appointments/confirm", json=payload)
    print(pretty(r))


# Get Appointment Details
def test_get_appt(appointment_id):
    print("\n[5] GET APPOINTMENT DETAILS")
    r = requests.get(f"{BASE}/api/appointments/" + appointment_id)
    print(pretty(r))


# Double-booking Test
def test_double_booking():
    print("\n[6] DOUBLE-BOOKING TEST")
    payload = {
        "customer_id": "user123",
        "resource_id": "test_resource",
        "date": "2025-01-10",
        "time": "14:00",
        "customer_email": "test@example.com"
    }
    r = requests.post(f"{BASE}/api/appointments", json=payload)
    print(pretty(r))
    print("Status Code:", r.status_code, "(should be 409 if working correctly)")


if __name__ == "__main__":
    test_health()
    test_get_slots()
    appt_id = test_book_appt()

    if appt_id:
        test_confirm_appt(appt_id)
        test_get_appt(appt_id)

    test_double_booking()

    print("\nAll tests finished.")