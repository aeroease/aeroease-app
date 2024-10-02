class AirportApp:
    def __init__(self):
        self.users = {}
        self.tickets = {}
        self.flight_schedules = {}
        self.check_in_queue = []
        
        # Set up OpenAI client
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not self.client.api_key:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

    def create_user(self, user_id, name):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(user_id)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        img_byte_arr = io.BytesIO()
        qr_img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        self.users[user_id] = {
            "name": name,
            "qr_code": img_byte_arr
        }
        return f"User {name} created with ID {user_id}"

    def create_ticket(self, user_id, flight_number):
        if user_id not in self.users:
            return f"User {user_id} not found"
        if flight_number not in self.flight_schedules:
            return f"Flight {flight_number} not found"
        
        ticket_number = f"T{random.randint(1000, 9999)}"
        self.tickets[ticket_number] = {
            "user_id": user_id,
            "flight_number": flight_number,
            "status": "Check-in"
        }
        return f"Ticket {ticket_number} created for user {user_id} on flight {flight_number}"

    def update_flight_schedule(self, flight_number, status, departure_time):
        self.flight_schedules[flight_number] = {
            "status": status,
            "departure_time": departure_time
        }
        return f"Flight {flight_number} updated: {status}, departure at {departure_time}"

    def get_flight_info(self, flight_number):
        if flight_number in self.flight_schedules:
            info = self.flight_schedules[flight_number]
            return f"Flight {flight_number}: {info['status']}, departure at {info['departure_time']}"
        return f"Flight {flight_number} not found"

    def add_to_check_in_queue(self, user_id, flight_number):
        if flight_number not in self.flight_schedules:
            return f"Flight {flight_number} not found"
        
        departure_time = datetime.strptime(self.flight_schedules[flight_number]['departure_time'], "%Y-%m-%d %H:%M:%S")
        current_time = datetime.now()
        # departure_time = datetime.strptime(departure_time, "%Y-%m-%d %H:%M:%S")

        time_until_departure = (departure_time - current_time).total_seconds() / 60  # in minutes
        
        heapq.heappush(self.check_in_queue, (time_until_departure, user_id, flight_number))
        return f"User {user_id} added to check-in queue for flight {flight_number}"

    def process_check_in_queue(self, num_to_process=5):
        processed = []
        for _ in range(min(num_to_process, len(self.check_in_queue))):
            if self.check_in_queue:
                time_until_departure, user_id, flight_number = heapq.heappop(self.check_in_queue)
                processed.append(f"User {user_id} for flight {flight_number} (Departure in {time_until_departure:.2f} minutes)")
        return "\n".join(processed) if processed else "No users in the queue"

    def genai_bot(self, query):
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant for an airport. Provide helpful information about the airport and its services."},
                    {"role": "user", "content": query}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"An error occurred while calling the OpenAI API: {str(e)}")
            return "I'm sorry, but I'm having trouble connecting to my knowledge base right now. Please try again later."
