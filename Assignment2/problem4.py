"""
Problem 4: Meeting Room Scheduler (Developed by AI)

This module implements a MeetingRoom class with multi-attribute scheduling,
conflict detection, utilization tracking, and free slot calculation.
"""
from typing import List, Dict, Any, Tuple


class MeetingRoom:
    """
    A meeting room reservation manager tracking bookings, capacity,
    total hours booked, utilization rate, and available time slots.

    Attributes:
        room_id (str): Unique room name/number.
        capacity (int): Maximum number of allowed attendees.
        bookings (List[Dict[str, Any]]): Chronologically sorted list of bookings.
        total_hours_booked (int): Total number of booked hours.
        is_maintenance (bool): Whether the room is closed for maintenance.
    """

    def __init__(self, room_id: str, capacity: int):
        if capacity <= 0:
            raise ValueError("Room capacity must be a positive integer")

        self.room_id = room_id
        self.capacity = int(capacity)
        self.bookings: List[Dict[str, Any]] = []
        self.total_hours_booked = 0
        self.is_maintenance = False

    def book(self, booking_id: str, title: str, start_time: int, end_time: int, attendees: int) -> bool:
        """
        Book the meeting room for a specified time interval [start_time, end_time].
        Time is represented as integer hours (e.g., 9 for 9:00 AM, 17 for 5:00 PM).

        Rules:
        1. start_time >= 0 and end_time > start_time.
        2. attendees must be > 0 and <= capacity.
        3. Room cannot be booked if under maintenance.
        4. Booking IDs must be unique.
        5. Cannot overlap with existing bookings. Back-to-back meetings (e.g. 9-10 and 10-11)
           do NOT conflict and are allowed.
        """
        if self.is_maintenance:
            raise RuntimeError("Cannot book a room that is under maintenance")
        if start_time < 0:
            raise ValueError("Start time cannot be negative")
        if end_time <= start_time:
            raise ValueError("End time must be strictly greater than start time")
        if attendees <= 0:
            raise ValueError("Attendees must be positive")
        if attendees > self.capacity:
            raise ValueError(f"Attendees ({attendees}) exceeds room capacity ({self.capacity})")
        if any(b["booking_id"] == booking_id for b in self.bookings):
            raise ValueError(f"Duplicate booking ID: {booking_id}")

        # Check for time conflicts with existing bookings
        for b in self.bookings:
            if not (end_time <= b["start_time"] or start_time >= b["end_time"]):
                raise ValueError(f"Time slot [{start_time}, {end_time}] conflicts with booking '{b['booking_id']}' [{b['start_time']}, {b['end_time']}]")

        new_booking = {
            "booking_id": booking_id,
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "attendees": attendees
        }

        self.bookings.append(new_booking)
        self.bookings.sort(key=lambda x: x["start_time"])
        self.total_hours_booked += (end_time - start_time)
        return True

    def cancel(self, booking_id: str) -> bool:
        """Cancel an existing booking by booking_id."""
        for i, b in enumerate(self.bookings):
            if b["booking_id"] == booking_id:
                duration = b["end_time"] - b["start_time"]
                self.total_hours_booked -= duration
                del self.bookings[i]
                return True
        raise KeyError(f"Booking ID '{booking_id}' not found")

    def get_free_slots(self, day_start: int = 8, day_end: int = 18) -> List[Tuple[int, int]]:
        """
        Return a list of available free time intervals (start, end) between day_start and day_end.
        """
        if day_start >= day_end:
            raise ValueError("day_start must be less than day_end")

        free_slots = []
        current_time = day_start

        for b in self.bookings:
            if b["end_time"] <= day_start:
                continue
            if b["start_time"] >= day_end:
                break

            b_start = max(day_start, b["start_time"])
            if b_start > current_time:
                free_slots.append((current_time, b_start))
            current_time = max(current_time, b["end_time"])

        if current_time < day_end:
            free_slots.append((current_time, day_end))

        return free_slots

    def get_utilization_rate(self, total_available_hours: int = 10) -> float:
        """
        Calculate room utilization rate (total_hours_booked / total_available_hours).
        """
        if total_available_hours <= 0:
            raise ValueError("Total available hours must be positive")
        return round(self.total_hours_booked / total_available_hours, 2)
