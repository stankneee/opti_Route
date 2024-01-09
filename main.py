
import datetime
import csv
import datetime
import re


class HashTable:
    def __init__(self, initial_capacity=40):
        # Initialize the hash table with a specific capacity.
        self.table = [[] for _ in range(initial_capacity)]
        self.num_items = 0

    def insert(self, key, item):
        # Resize the table if the load factor is too high.
        self.check_and_resize()

        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]

        for key_value in bucket_list:
            if key_value[0] == key:
                key_value[1] = item
                return
        bucket_list.append([key, item])
        self.num_items += 1

    def check_and_resize(self):
        load_factor = self.num_items / len(self.table)
        if load_factor > 0.7:
            self._resize(2 * len(self.table))

    def _resize(self, new_capacity):
        old_table = self.table
        self.table = [[] for _ in range(new_capacity)]
        self.num_items = 0

        for bucket in old_table:
            for key, value in bucket:
                self.insert(key, value)

    def search(self, key):
        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]

        for key_value in bucket_list:
            if key_value[0] == key:
                return key_value[1]
        return None

    def remove(self, key):
        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]

        for i, key_value in enumerate(bucket_list):
            if key_value[0] == key:
                del bucket_list[i]
                self.num_items -= 1
                return True
        return False

    def __iter__(self):
        for bucket in self.table:
            for key_value in bucket:
                yield key_value

    def display(self):
        for i, bucket in enumerate(self.table):
            print(f"Bucket {i}: {bucket}")

    def size(self):
        return self.num_items


class Package:
    def __init__(self, id, street, city, state, zipcode, deadline, weight, status, departure_time, delivery_time):
        # Constructor for the Package class. Initializes the package with various attributes.
        self.id = id  # Unique identifier for the package.
        self.street = street  # Street address for delivery.
        self.city = city  # City for delivery.
        self.state = state  # State for delivery.
        self.zipcode = zipcode  # Zipcode for delivery.
        self.deadline = deadline  # Deadline for the delivery.
        self.weight = weight  # Weight of the package.
        self.status = status  # Current status of the package (e.g., 'At Hub', 'En Route').
        self.departure_time = departure_time  # Time when the package left the hub.
        self.delivery_time = delivery_time  # Expected time of delivery.

    def __str__(self):
        package_details = f"Package ID: {self.id}, Address for Delivery: {self.street}, " \
                          f"City: {self.city}, State: {self.state}, Postal Code: {self.zipcode}, " \
                          f"Delivery Deadline: {self.deadline}, Weight: {self.weight} lbs, " \
                          f"Current Status: {self.status}"
        return package_details

    def status_update(self, time_check):
        # Method to update the package's delivery status based on the current time
        updated_status = self.status

        if self.delivery_time < time_check:
            # Delivery time has passed
            pass  # Keeping the status as is
        elif self.departure_time > time_check:
            # Package is still at the hub
            updated_status = "at the Hub"
        else:
            # Package is in transit
            updated_status = "en route"

        print(f"Package ID: {self.id}, Delivery Address: {self.street}, City: {self.city}, " \
              f"Zipcode: {self.zipcode}, Weight: {self.weight} lbs, Status: {updated_status}")
class Truck:
    def __init__(self, packages, location, time, size=16, speed=18, mileage=0.0):
        # Constructor for the Truck class.
        self.packages = packages  # List of packages to be delivered by this truck.
        self.location = location  # Current location of the truck.
        self.depart_time = time  # Departure time of the truck from the hub.
        self.size = size  # Maximum number of packages the truck can carry (default is 16).
        self.speed = speed  # Average speed of the truck (default is 18).
        self.time = time  # Current time or the time at which the status is being checked.
        self.mileage = mileage  # Total distance covered by the truck (default is 0.0).

    def __str__(self):
        truck_info = (
            f"Truck Information --",
            f"Size: {self.size},",
            f"Travel Speed: {self.speed} mph,",
            f"Current Location: {self.location},",
            f"Total Mileage: {self.mileage} miles,",
            f"Time on Road: {self.time}"
        )
        return ' | '.join(truck_info)

def load_package(hash_table):
    # Open the CSV file containing package data
    with open("CSV/package.csv", mode='r') as csv_file:
        # Initializing a CSV reader
        csv_reader = csv.reader(csv_file, delimiter=',')

        for row in csv_reader:
            # Unpacking each field from the row into separate variables
            package_id = int(row[0])  # Convert Package ID to integer
            address = row[1]  # Street address for the package
            delivery_city = row[2]  # Destination city
            delivery_state = row[3]  # Destination state
            postal_code = row[4]  # Zipcode for delivery
            delivery_deadline = row[5]  # Deadline for delivery
            package_weight = row[6]  # Weight of the package

            # Setting up default attributes for a new package
            initial_status = "pending"  # Initial status of the package
            time_of_departure = None  # Departure time is initially undefined
            expected_delivery_time = None  # Delivery time is initially undefined

            # Constructing a new Package instance
            new_package = Package(package_id, address, delivery_city, delivery_state, postal_code,
                                  delivery_deadline, package_weight, initial_status,
                                  time_of_departure, expected_delivery_time)

            # Adding the new package to the hash table
            hash_table.insert(package_id, new_package)

def load_distance(distance_data):
    # Open the file containing distance data
    with open(distance_data) as file:
        # Read the file using csv.reader and convert it to a list
        return list(csv.reader(file))


def load_address(address_data):
    # Open the file containing address data
    with open(address_data) as file:
        # Read the file using csv.reader and convert it to a list
        return list(csv.reader(file))


def distance_between(address1_index, address2_index):
    # Retrieve distance matrix from CSV
    distance_matrix = load_distance("CSV/distance.csv")

    # Accessing the distance between two specified addresses
    distance = distance_matrix[address1_index][address2_index]

    # Check and correct for empty entries in the matrix
    if not distance:
        # Fetch distance by interchanging the indices if initially not found
        distance = distance_matrix[address2_index][address1_index]

    # Convert and return the distance as a float type
    return float(distance)

def min_distance_from(from_address, truck_packages, hash_table):
    # Get the index number for the given 'from_address'
    index_of_from_address = get_address_index(from_address)

    # Set initial minimum distance to the highest possible value
    smallest_distance = float("inf")
    closest_package_id = -1

    # Loop through each package on the truck to find the closest one
    for pkg_id in truck_packages:
        # Fetch the package details from the hash table
        current_package = hash_table.search(pkg_id)

        # Get the index for the current package's address
        address_index_of_package = get_address_index(current_package.street)

        # Compute the distance to this package from 'from_address'
        calculated_distance = distance_between(index_of_from_address, address_index_of_package)

        # Update the smallest distance and package ID if a closer package is found
        if calculated_distance < smallest_distance:
            smallest_distance = calculated_distance
            closest_package_id = pkg_id

    # Return the package ID that is closest to the 'from_address'
    return closest_package_id




def get_address_index(street):
    # Retrieve a list of addresses from the specified CSV file
    addresses = load_address("CSV/address.csv")

    # Loop through the list of addresses
    for address in addresses:
        # If the given street is part of the current address entry
        if street in address[2]:
            # Return the index position of this address, ensuring it's an integer
            return int(address[0])



def truck_load_packages(hash_table):
    # Assigning predefined package IDs to the first truck
    initial_truck1_packages = [1, 4, 7, 13, 14, 15, 16, 19, 20, 21, 29, 34, 37, 39, 40]
    truck1 = Truck(initial_truck1_packages, "4001 South 700 East", datetime.timedelta(hours=8))

    # Creating groups of package IDs for the second and third trucks
    packages_for_truck2 = [3, 5, 9, 18, 36, 38]
    packages_for_truck3 = [6, 8, 25, 26, 28, 30, 31, 32]

    # Identifying packages that are yet to be assigned to a truck
    remaining_packages = [2, 10, 11, 12, 17, 22, 23, 24, 27, 33, 35]

    # Optimally loading the remaining packages onto the second and third trucks
    load_package_set(packages_for_truck2, remaining_packages, 9, hash_table)
    load_package_set(packages_for_truck3, remaining_packages, 16, hash_table)

    # Setting up the second and third trucks with their packages and departure times
    truck2 = Truck(packages_for_truck2, "4001 South 700 East", datetime.timedelta(hours=10, minutes=20))
    truck3 = Truck(packages_for_truck3, "4001 South 700 East", datetime.timedelta(hours=9, minutes=5))

    # Sending out the prepared trucks
    return truck1, truck2, truck3


def load_package_set(package_set, packages_not_loaded, limit, hash_table):
    # Initialize with the first package's address as the starting point
    current_address = hash_table.search(package_set[0]).street

    # Continuously load packages until reaching the specified limit
    while len(package_set) < limit:
        # Determine the closest package not yet loaded
        closest_package_id = min_distance_from(current_address, packages_not_loaded, hash_table)

        # Fetch the details of the closest package
        closest_package = hash_table.search(closest_package_id)

        # Include this package in the truck's load
        package_set.append(closest_package_id)

        # Update the reference address to that of the newly added package
        current_address = closest_package.street

        # Remove the added package from the pool of unloaded packages
        packages_not_loaded.remove(closest_package_id)


def truck_deliver_packages(truck, hash_table):
    # List to track packages on the truck that need to be delivered
    undelivered_packages = []

    # Loop through the package IDs assigned to the truck
    for package_id in truck.packages:
        # Access each package using its ID from the hash table
        current_package = hash_table.search(package_id)

        # Set each package's departure time to match the truck's departure
        current_package.departure_time = truck.time

        # Add the package ID to the list of undelivered packages
        undelivered_packages.append(package_id)

    # Reset the truck's package list to prepare for delivery
    truck.packages = []

    # Continuously deliver packages until all are delivered
    while undelivered_packages:
        # Identify the next closest package for delivery
        next_closest_package_id = min_distance_from(truck.location, undelivered_packages, hash_table)
        next_package = hash_table.search(next_closest_package_id)

        # Measure the distance to the next delivery address
        next_distance = distance_between(get_address_index(truck.location), get_address_index(next_package.street))

        # Add this package to the truck's delivery list
        truck.packages.append(next_closest_package_id)

        # Remove this package from the list of undelivered packages
        undelivered_packages.remove(next_closest_package_id)

        # Update the truck's mileage to reflect this delivery
        truck.mileage += next_distance

        # Adjust the truck's current location and time post-delivery
        truck.location = next_package.street
        truck.time += datetime.timedelta(hours=next_distance / 18.0)

        # Record the delivery time and update the package's status
        next_package.delivery_time = truck.time
        next_package.status = f"Delivered at {truck.time}"


def return_to_hub(truck):
    # Define the hub's address
    hub = "4001 South 700 East"
    # Calculate the distance from the truck's current location to the hub
    distance = distance_between(get_address_index(truck.location), get_address_index(hub))
    # Update the truck's mileage for the return trip
    truck.mileage += distance
    # Update the truck's time based on the return trip distance
    truck.time += datetime.timedelta(hours=distance / 18.0)



def print_menu():
    # Display the menu options to the user
    print()
    print("Menu:")
    print("1. Print All Package Status & Mileage")
    print("2. Get a Single Package Status")
    print("3. Get All Package Status & a Time ")
    print("4. Exit ")


def print_all_package_status_and_total_mileage(hash_table, truck1, truck2, truck3):
    # Loop through each package ID in the range and print its current status
    for i in range(1, 41):
        current_package_status = hash_table.search(i)
        print(current_package_status)

    # Calculate the combined mileage of all three trucks and display the result
    combined_mileage = truck1.mileage + truck2.mileage + truck3.mileage
    print(f"Total mileage for the three trucks is {combined_mileage}")


def get_single_package_status_with_time(hash_table):
    # Convert the time entered by the user
    user_time = convert_user_time()

    # Loop to prompt for a package ID and show its current status
    while True:
        try:
            package_id = int(input("Enter package ID number (#1-40): "))
            selected_package = hash_table.search(package_id)
            selected_package.status_update(user_time)
            break
        except ValueError:
            print("Invalid input. Please enter a valid package ID.")



def get_all_package_status_with_time(hash_table):
    # Changing user input into a time format
    user_time = convert_user_time()

    # Iterating through each package to update and display its status at the user-defined time
    for package_id in range(1, 41):
        current_package = hash_table.search(package_id)
        current_package.status_update(user_time)



def convert_user_time():
    # Define a regular expression pattern for time input validation
    pattern = r"([01][0-9]|2[0-3]):[0-5][0-9]:([0-5][0-9]){1}$"
    user_time = input("Enter time in the following format: HH:MM:SS - ")

    # Validate and convert user input time
    while True:
        if re.match(pattern, user_time):
            (hours, minutes, seconds) = user_time.split(":")
            convert_timedelta = datetime.timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds))
            return convert_timedelta
        else:
            user_time = input("Invalid. Enter time in the following format: HH:MM:SS - ")

# Main program execution starts here
package_hash_table = HashTable()

# Load package data into the hash table
load_package(package_hash_table)

# Load packages onto trucks
truck1, truck2, truck3 = truck_load_packages(package_hash_table)

# Deliver packages using each truck and return them to the hub
truck_deliver_packages(truck1, package_hash_table)
truck_deliver_packages(truck3, package_hash_table)
return_to_hub(truck1)
return_to_hub(truck3)

# Special case for truck2's timing and package 9
if truck2.time == datetime.timedelta(hours=10, minutes=20):
    package9 = package_hash_table.search(9)
    package9.street = "410 S State St"

truck_deliver_packages(truck2, package_hash_table)
return_to_hub(truck2)

# Welcome message for the program
print("Welcome to the Package Routing Program.")

# Loop to continuously display the menu and execute user commands
while True:
    print_menu()
    user_input = input("Input a number to proceed. ")
    match user_input:
        case "1":
            print_all_package_status_and_total_mileage(package_hash_table, truck1, truck2, truck3)
        case "2":
            get_single_package_status_with_time(package_hash_table)
        case "3":
            get_all_package_status_with_time(package_hash_table)
        case "4":
            print("Bye!")
            break
