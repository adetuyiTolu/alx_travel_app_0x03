# Airbnb bookings

This project implements a basic Airbnb-style structure with Listings, Bookings, and Reviews. It also includes serializers and a custom seed command for populating the database with sample data.

---

## ✅ Models – `listings/models.py`

### 1. **Listing**
- Fields: `id`, `host (User)`, `name`, `description`, `location`, `price_per_night`, `created_at`, `updated_at`
- A listing is created by a host and represents a rentable property.

### 2. **Booking**
- Fields: `id`, `listing`, `user`, `start_date`, `end_date`, `total_price`, `status`, `created_at`
- Connects a user to a listing with a time frame and status.
- Booking statuses include: `pending`, `confirmed`, `canceled`.

### 3. **Review**
- Fields: `id`, `listing`, `user`, `rating`, `comment`, `created_at`
- Ratings must be between 1 and 5.
- Used for post-booking feedback.

---
