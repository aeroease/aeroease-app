import qrcode
import random
from datetime import datetime, timedelta
import heapq
import gradio as gr
import io
from PIL import Image
from openai import OpenAI
import os
from models.airportapp import AirportApp

app = AirportApp()

def create_user_interface(user_id, name):
    result = app.create_user(user_id, name)
    qr_code = Image.open(io.BytesIO(app.users[user_id]["qr_code"])) if user_id in app.users else None
    return result, qr_code

def create_ticket_interface(user_id, flight_number):
    return app.create_ticket(user_id, flight_number)

def update_flight_interface(flight_number, status, departure_time):
    return app.update_flight_schedule(flight_number, status, departure_time)

def get_flight_info_interface(flight_number):
    return app.get_flight_info(flight_number)

def add_to_queue_interface(user_id, flight_number):
    return app.add_to_check_in_queue(user_id, flight_number)

def process_queue_interface(num_to_process):
    return app.process_check_in_queue(int(num_to_process))

def chatbot_interface(message, history):
    history = history or []
    bot_response = app.genai_bot(message)
    history.append((message, bot_response))
    return history

with gr.Blocks() as interface:
    gr.Markdown("# Airport Productivity App")
    
    with gr.Tab("User Management"):
        gr.Markdown("## Create User")
        user_id_input = gr.Textbox(label="User ID")
        name_input = gr.Textbox(label="Name")
        create_user_button = gr.Button("Create User")
        user_output = gr.Textbox(label="Result")
        qr_output = gr.Image(label="QR Code")
        create_user_button.click(create_user_interface, inputs=[user_id_input, name_input], outputs=[user_output, qr_output])

    with gr.Tab("Ticket Management"):
        gr.Markdown("## Create Ticket")
        ticket_user_id = gr.Textbox(label="User ID")
        ticket_flight_number = gr.Textbox(label="Flight Number")
        create_ticket_button = gr.Button("Create Ticket")
        ticket_output = gr.Textbox(label="Result")
        create_ticket_button.click(create_ticket_interface, inputs=[ticket_user_id, ticket_flight_number], outputs=ticket_output)

    with gr.Tab("Flight Management"):
        gr.Markdown("## Update Flight Schedule")
        flight_number = gr.Textbox(label="Flight Number")
        flight_status = gr.Textbox(label="Status")
        departure_time = gr.Textbox(label="Departure Time (YYYY-MM-DD HH:MM:SS)")
        update_flight_button = gr.Button("Update Flight")
        flight_output = gr.Textbox(label="Result")
        update_flight_button.click(update_flight_interface, inputs=[flight_number, flight_status, departure_time], outputs=flight_output)

        gr.Markdown("## Get Flight Info")
        info_flight_number = gr.Textbox(label="Flight Number")
        get_info_button = gr.Button("Get Info")
        info_output = gr.Textbox(label="Flight Information")
        get_info_button.click(get_flight_info_interface, inputs=info_flight_number, outputs=info_output)

    with gr.Tab("Check-in Queue"):
        gr.Markdown("## Add to Check-in Queue")
        queue_user_id = gr.Textbox(label="User ID")
        queue_flight_number = gr.Textbox(label="Flight Number")
        add_to_queue_button = gr.Button("Add to Queue")
        queue_add_output = gr.Textbox(label="Result")
        add_to_queue_button.click(add_to_queue_interface, inputs=[queue_user_id, queue_flight_number], outputs=queue_add_output)

        gr.Markdown("## Process Check-in Queue")
        num_to_process = gr.Slider(minimum=1, maximum=10, step=1, label="Number of Users to Process")
        process_queue_button = gr.Button("Process Queue")
        queue_process_output = gr.Textbox(label="Processed Users")
        process_queue_button.click(process_queue_interface, inputs=num_to_process, outputs=queue_process_output)

    with gr.Tab("Airport Assistant"):
        gr.Markdown("## Chat with Airport Assistant")
        chatbot = gr.Chatbot()
        msg = gr.Textbox()
        clear = gr.Button("Clear")

        msg.submit(chatbot_interface, inputs=[msg, chatbot], outputs=chatbot)
        clear.click(lambda: [], None, chatbot, queue=False)

if __name__ == "__main__":
    interface.launch(server_name="0.0.0.0", server_port=7860, share=True)