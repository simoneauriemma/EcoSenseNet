import json
import os
import telebot
import boto3
from dotenv import dotenv_values, load_dotenv
from botocore.exceptions import NoCredentialsError
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot import types
import subprocess


# Load variables from .env file
env_vars = dotenv_values(".env")

# Extra commands
# /clean - clear all table
# /test - call lambda activeMonitoring
# /end - delete all tables

load_dotenv()

TOKEN = env_vars["BOT_TOKEN"]
CHAT_ID = env_vars["CHAT_ID"]
url = "http://localhost:4566"

bot = telebot.TeleBot(TOKEN)
dynamoDb = boto3.resource("dynamodb", endpoint_url=url)


def query_data_dynamodb(table):
    measurementTable = dynamoDb.Table(table)
    response = measurementTable.scan()
    return response["Items"]


def format_message(result):
    formatted_message = ""
    for item in result:
        zone = item["zone"]
        pm10 = item["pm10"]
        pm2_5 = item["pm2_5"]
        daytime = item["dayTime"].split(",")[0]  # Extracting only the date portion

        formatted_message += (
            f"- {zone}: pm10: {pm10}, pm2_5: {pm2_5}, daytime: {daytime}\n"
        )

    return formatted_message


def retrievePM10Average(result):
    formatted_message = ""
    for item in result:
        zone = item["zone"]
        pm10 = item["pm10"]
        daytime = item["dayTime"].split(",")[0]  # Extracting only the date portion

        formatted_message += f"- {zone}: pm10: {pm10}, daytime: {daytime}\n"

    return formatted_message


def retrievePM2_5Average(result):
    formatted_message = ""
    for item in result:
        zone = item["zone"]
        pm2_5 = item["pm2_5"]
        daytime = item["dayTime"].split(",")[0]  # Extracting only the date portion

        formatted_message += f"- {zone}: pm2_5: {pm2_5}, daytime: {daytime}\n"

    return formatted_message


@bot.message_handler(commands=["start"])
def first_start(message):
    cid = message.chat.id
    bot.send_message(
        cid,
        f"Welcome {message.from_user.username}, press /help to get the list of commands",
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["help"])
def send_help(message):
    cid = message.chat.id

    # Create the inline buttons
    button_active_sensors = types.InlineKeyboardButton(
        "Active Sensors", callback_data="activeSensorsValues"
    )
    button_generate_data = types.InlineKeyboardButton(
        "Generate Data", callback_data="generateData"
    )
    button_average_pm10 = types.InlineKeyboardButton(
        "Average PM10", callback_data="averagePM10"
    )
    button_average_pm2_5 = types.InlineKeyboardButton(
        "Average PM2.5", callback_data="averagePM2_5"
    )
    button_send_email = types.InlineKeyboardButton(
        "Send Email", callback_data="sendEmail"
    )
    button_switch_sensor_on = types.InlineKeyboardButton(
        "Switch Sensor On", callback_data="switchSensorOn"
    )
    button_switch_sensor_off = types.InlineKeyboardButton(
        "Switch Sensor Off", callback_data="switchSensorOff"
    )
    button_activate_sensors = types.InlineKeyboardButton(
        "Activate Sensors", callback_data="ONsensors"
    )
    button_deactivate_sensors = types.InlineKeyboardButton(
        "Deactivate Sensors", callback_data="OFFsensors"
    )

    # Create the inline keyboard markup
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        button_active_sensors,
        button_generate_data,
        button_average_pm10,
        button_average_pm2_5,
        button_send_email,
        button_switch_sensor_on,
        button_switch_sensor_off,
        button_activate_sensors,
        button_deactivate_sensors,
    )

    # Send the message with inline buttons
    bot.send_message(cid, "Choose a command:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    if call.data == "activeSensorsValues":
        activeSensorsValues(call.message)
    elif call.data == "generateData":
        generate_data(call.message)
    elif call.data == "averagePM10":
        averagePM10(call.message)
    elif call.data == "averagePM2_5":
        averagePM2_5(call.message)
    elif call.data == "sendEmail":
        sendEmail(call.message)
    elif call.data == "switchSensorOn":
        switchSensorOn(call.message)
    elif call.data == "switchSensorOff":
        switchSensorOff(call.message)
    elif call.data == "ONsensors":
        ONsensors(call.message)
    elif call.data == "OFFsensors":
        OFFsensors(call.message)


@bot.message_handler(commands=["generateData"])
def generate_data(message):
    cid = message.chat.id
    # command = ["node", "..\\dist\\device.js"]
    command = ["node", f"{os.getcwd()}\\dist\\device.js"]
    try:
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        output, error = process.communicate()
    except Exception as e:
        print(e)
    output = output.decode("utf-8")
    error = error.decode("utf-8")
    if process.returncode != 0:
        print(f"Error executing Node.js script: {error}")
        bot.send_message(cid, "error generating data")
    else:
        print(f"Output:\n{output}")
        bot.send_message(cid, "Processing....")
        lambda_client = boto3.client("lambda", endpoint_url=url)
        response = lambda_client.invoke(
            FunctionName="average",
            InvocationType="RequestResponse",
            Payload=json.dumps({"cid": cid}),
        )
        bot.send_message(cid, "Done!")


@bot.message_handler(commands=["activeSensorsValues"])
def activeSensorsValues(message):
    cid = message.chat.id
    try:
        result = query_data_dynamodb("Pollution")
    except Exception as e:
        print(e)
    bot.send_message(cid, format_message(result))


@bot.message_handler(commands=["averagePM10"])
def averagePM10(message):
    cid = message.chat.id
    try:
        result = query_data_dynamodb("Pollution")
    except Exception as e:
        print(e)
    bot.send_message(cid, retrievePM10Average(result))


@bot.message_handler(commands=["averagePM2_5"])
def averagePM2_5(message):
    cid = message.chat.id
    try:
        result = query_data_dynamodb("Pollution")
    except Exception as e:
        print(e)
    bot.send_message(cid, retrievePM2_5Average(result))


@bot.message_handler(commands=["sendEmail"])
def sendEmail(message):
    cid = message.chat.id
    try:
        bot.send_message(cid, "Please insert your email")
        bot.register_next_step_handler(message, process_email)
    except Exception as e:
        bot.send_message(cid, f"Error sending email: {str(e)}")
        # TODO vedere se abbiamo voglia di recuperare la mail nella root del container


def process_email(message):
    cid = message.chat.id
    recipient = message.text

    try:
        subject = f"Email from {bot.get_me().username}"
        body = format_message(query_data_dynamodb("Pollution"))
        sender = env_vars["SENDER_EMAIL"]

        send_email(subject, body, sender, recipient)
        bot.send_message(cid, "Email sent successfully!")
    except Exception as e:
        bot.send_message(cid, f"Error sending email: {str(e)}")


def send_email(subject, body, sender, recipient):
    aws_access_key_id = env_vars["AWS_ACCESS_KEY_ID"]
    aws_secret_access_key = env_vars["AWS_SECRET_ACCESS_KEY"]
    aws_region = env_vars["REGION"]

    # Configure Boto3 client for SES
    ses_client = boto3.client(
        "ses",
        region_name=aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        endpoint_url=env_vars["ENDPOINT"],
    )

    try:
        response = ses_client.send_email(
            Source=sender,
            Destination={"ToAddresses": [recipient]},
            Message={"Subject": {"Data": subject}, "Body": {"Text": {"Data": body}}},
        )
        print("Email sent! Message ID:", response["MessageId"])
    except NoCredentialsError:
        print("Failed to send email: AWS credentials not found.")


@bot.message_handler(commands=["OFFsensors"])
def OFFsensors(message):
    cid = message.chat.id

    try:
        lambda_client = boto3.client("lambda", endpoint_url=url)
        response = lambda_client.invoke(
            FunctionName="offsensors",
            InvocationType="RequestResponse",
            Payload=json.dumps({"cid": cid}),
        )
        bot.send_message(cid, "Active status updated successfully!")

    except Exception as e:
        bot.send_message(cid, f"Error updating active status: {str(e)}")


@bot.message_handler(commands=["ONsensors"])
def ONsensors(message):
    cid = message.chat.id

    try:
        lambda_client = boto3.client("lambda", endpoint_url=url)
        response = lambda_client.invoke(
            FunctionName="onsensors",
            InvocationType="RequestResponse",
            Payload=json.dumps({"cid": cid}),
        )

        bot.send_message(cid, "Active status updated successfully!")

    except Exception as e:
        bot.send_message(cid, f"Error updating active status: {str(e)}")


@bot.message_handler(commands=["switchSensorOn"])
def switchSensorOn(message):
    cid = message.chat.id

    try:
        table = dynamoDb.Table("Pollution")  # Replace "Pollution" with your table name
        response = table.scan()
        items = response["Items"]

        # Extract the unique zones from the items
        zones = list(set(item["zone"] for item in items))

        if not zones:
            bot.send_message(cid, "No zones found in the table.")
            return

        # Create the reply keyboard markup with buttons for each zone
        keyboard = ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
        buttons = [KeyboardButton(zone) for zone in zones]
        keyboard.add(*buttons)

        # Send the zone selection prompt with buttons
        bot.send_message(cid, "Select a zone:", reply_markup=keyboard)

        # Register the next step handler to capture the selected zone
        bot.register_next_step_handler(message, process_zone_selection_on)

    except Exception as e:
        bot.send_message(cid, f"Error toggling active status: {str(e)}")

@bot.message_handler(commands=["switchSensorOff"])
def switchSensorOff(message):
    cid = message.chat.id

    try:
        table = dynamoDb.Table("Pollution")  # Replace "Pollution" with your table name
        response = table.scan()
        items = response["Items"]

        # Extract the unique zones from the items
        zones = list(set(item["zone"] for item in items))

        if not zones:
            bot.send_message(cid, "No zones found in the table.")
            return

        # Create the reply keyboard markup with buttons for each zone
        keyboard = ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
        buttons = [KeyboardButton(zone) for zone in zones]
        keyboard.add(*buttons)

        # Send the zone selection prompt with buttons
        bot.send_message(cid, "Select a zone:", reply_markup=keyboard)

        # Register the next step handler to capture the selected zone
        bot.register_next_step_handler(message, process_zone_selection_off)

    except Exception as e:
        bot.send_message(cid, f"Error toggling active status: {str(e)}")


def process_zone_selection_on(message):
    cid = message.chat.id
    zone = message.text

    lambda_client = boto3.client("lambda", endpoint_url=url)
    response = lambda_client.invoke(
            FunctionName="onsensorzone",
            InvocationType="RequestResponse",
            Payload=json.dumps({"table": "Pollution","zone": zone}),
        )
    bot.send_message(cid, "Done!")

def process_zone_selection_off(message):
    cid = message.chat.id
    zone = message.text

    lambda_client = boto3.client("lambda", endpoint_url=url)
    response = lambda_client.invoke(
            FunctionName="offsensorzone",
            InvocationType="RequestResponse",
            Payload=json.dumps({"table": "Pollution","zone": zone}),
        )
    bot.send_message(cid, "Done!")

bot.polling()
