-- First, select the database you want to work with
USE ola_project;

-- Query 1: Retrieve all successful bookings
SELECT * FROM ride_details WHERE Booking_Status = 'Success';

-- Query 2: Find the average ride distance for each vehicle type
SELECT Vehicle_Type, AVG(Ride_Distance) AS average_ride_distance_km
FROM ride_details
GROUP BY Vehicle_Type
ORDER BY average_ride_distance_km DESC;

-- Query 3: Get the total number of cancelled rides by customers
SELECT COUNT(*) AS total_rides_cancelled_by_customer
FROM ride_details
WHERE Booking_Status = 'Canceled by Customer';

-- Query 4: List the top 5 customers who booked the highest number of rides
SELECT Customer_ID, COUNT(*) AS number_of_rides
FROM ride_details
GROUP BY Customer_ID
ORDER BY number_of_rides DESC
LIMIT 5;

-- Query 5: Get the number of rides cancelled by drivers due to personal and car-related issues
SELECT COUNT(*) AS cancellations_for_personal_car_issues
FROM ride_details
WHERE Driver_Cancel_Reason = 'Personal & Car related issue';

-- Query 6: Find the maximum and minimum driver ratings for Prime Sedan bookings
SELECT MAX(Driver_Ratings) AS max_prime_sedan_rating, MIN(Driver_Ratings) AS min_prime_sedan_rating
FROM ride_details
WHERE Vehicle_Type = 'Prime Sedan';

-- Query 7: Retrieve all rides where payment was made using UPI
SELECT * FROM ride_details
WHERE Payment_Method = 'UPI';

-- Query 8: Find the average customer rating per vehicle type
SELECT Vehicle_Type, AVG(Customer_Rating) AS average_customer_rating
FROM ride_details
GROUP BY Vehicle_Type
ORDER BY average_customer_rating DESC;

-- Query 9: Calculate the total booking value of rides completed successfully
SELECT SUM(Booking_Value) AS total_revenue_from_successful_rides
FROM ride_details
WHERE Booking_Status = 'Success';

-- Query 10: List all incomplete rides along with the reason
SELECT Booking_ID, Vehicle_Type, Incomplete_Rides_Reason
FROM ride_details
WHERE Incomplete_Rides = 'Yes';