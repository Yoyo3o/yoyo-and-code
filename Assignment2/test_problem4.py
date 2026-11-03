"""
Unit tests for Problem 4: MeetingRoom

Instructions:
Complete the unit test methods below using Python's unittest framework.
Your test methods must assert MULTIPLE ATTRIBUTES on the MeetingRoom object
(e.g., bookings list, total_hours_booked, free slots, utilization rate)
to verify room state and conflict management.

Running tests:
    python -m unittest test_problem4.py -v
"""
import unittest
from problem4 import MeetingRoom


class TestMeetingRoom(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.room = MeetingRoom("Conference-A", capacity=10)

    def test_initial_state_multi_attributes(self):
        """
        Verify initial state of an empty meeting room.
        """
        self.assertEqual(self.room.room_id, "Conference-A")
        self.assertEqual(self.room.capacity, 10)
        self.assertEqual(self.room.bookings, [])
        self.assertEqual(self.room.total_hours_booked, 0)
        self.assertFalse(self.room.is_maintenance)
        self.assertEqual(self.room.get_free_slots(), [(8, 18)])
        self.assertEqual(self.room.get_utilization_rate(), 0.0)

    def test_single_booking_multi_attributes(self):
        """
        Test making a single valid booking.
        Verify bookings list, total_hours_booked, utilization rate, and free slots.
        """
        self.assertTrue(self.room.book("B01", "Planning", 10, 12, 5))

        self.assertEqual(
            self.room.bookings,
            [{
                "booking_id": "B01",
                "title": "Planning",
                "start_time": 10,
                "end_time": 12,
                "attendees": 5,
            }],
        )
        self.assertEqual(self.room.total_hours_booked, 2)
        self.assertEqual(self.room.get_utilization_rate(), 0.2)
        self.assertEqual(self.room.get_free_slots(), [(8, 10), (12, 18)])
        self.assertFalse(self.room.is_maintenance)

    def test_back_to_back_meetings_allowed(self):
        """
        Test that valid consecutive / back-to-back meetings (e.g. 9-10 and 10-12)
        are permitted without raising conflict errors.
        Verify multi-attribute state after both bookings succeed.
        """
        self.assertTrue(self.room.book("B01", "Standup", 9, 10, 4))
        self.assertTrue(self.room.book("B02", "Review", 10, 12, 6))

        self.assertEqual([b["booking_id"] for b in self.room.bookings], ["B01", "B02"])
        self.assertEqual(self.room.bookings[0]["start_time"], 9)
        self.assertEqual(self.room.bookings[1]["end_time"], 12)
        self.assertEqual(self.room.total_hours_booked, 3)
        self.assertEqual(self.room.get_free_slots(), [(8, 9), (12, 18)])
        self.assertEqual(self.room.get_utilization_rate(), 0.3)

    def test_overlapping_booking_rejected(self):
        """
        Test that overlapping bookings (e.g. 9-11 and 10-12, or completely inside 9-12 and 10-11)
        raise ValueError and leave room state unchanged.
        """
        self.room.book("B01", "Workshop", 9, 12, 8)
        original_bookings = list(self.room.bookings)

        with self.assertRaises(ValueError):
            self.room.book("B02", "Overlap", 10, 13, 3)
        with self.assertRaises(ValueError):
            self.room.book("B03", "Inside", 10, 11, 2)

        self.assertEqual(self.room.bookings, original_bookings)
        self.assertEqual(self.room.total_hours_booked, 3)
        self.assertEqual(self.room.get_free_slots(), [(8, 9), (12, 18)])
        self.assertEqual(self.room.get_utilization_rate(), 0.3)

    def test_cancel_booking_updates_all_attributes(self):
        """
        Test that cancelling a booking correctly removes it from bookings,
        decrements total_hours_booked, and restores free slots.
        """
        self.room.book("B01", "Morning", 9, 11, 4)
        self.room.book("B02", "Afternoon", 13, 16, 7)

        self.assertTrue(self.room.cancel("B01"))
        self.assertEqual([b["booking_id"] for b in self.room.bookings], ["B02"])
        self.assertEqual(self.room.total_hours_booked, 3)
        self.assertEqual(self.room.get_free_slots(), [(8, 13), (16, 18)])
        self.assertEqual(self.room.get_utilization_rate(), 0.3)
        self.assertEqual(self.room.bookings[0]["attendees"], 7)
        self.assertFalse(self.room.is_maintenance)

    def test_capacity_and_validation_exceptions(self):
        """
        Test edge cases and exceptions:
        - Attendees exceeding capacity (ValueError)
        - Start time >= End time (ValueError)
        - Duplicate booking ID (ValueError)
        - Booking when room is under maintenance (RuntimeError)
        - Cancelling non-existent booking (KeyError)
        """
        with self.assertRaises(ValueError):
            self.room.book("B01", "Too large", 9, 10, 11)
        with self.assertRaises(ValueError):
            self.room.book("B02", "Invalid time", 10, 10, 2)
        with self.assertRaises(ValueError):
            self.room.book("B03", "Invalid time", 12, 11, 2)
        with self.assertRaises(ValueError):
            self.room.book("B04", "Invalid start", -1, 10, 2)
        with self.assertRaises(ValueError):
            self.room.book("B05", "Invalid attendees", 9, 10, 0)

        self.room.book("B06", "Valid", 9, 10, 2)
        with self.assertRaises(ValueError):
            self.room.book("B06", "Duplicate", 11, 12, 2)

        self.room.is_maintenance = True
        with self.assertRaises(RuntimeError):
            self.room.book("B07", "Maintenance", 11, 12, 2)
        self.assertEqual(len(self.room.bookings), 1)
        self.assertEqual(self.room.total_hours_booked, 1)
        with self.assertRaises(KeyError):
            self.room.cancel("missing")

        self.assertEqual(self.room.bookings[0]["booking_id"], "B06")
        self.assertEqual(self.room.get_free_slots(), [(8, 9), (10, 18)])
        with self.assertRaises(ValueError):
            self.room.get_free_slots(18, 8)
        with self.assertRaises(ValueError):
            self.room.get_utilization_rate(0)


if __name__ == "__main__":
    unittest.main()
