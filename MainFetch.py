# Firebase Section
from FirebaseHandler import FirebaseHandler
# Blockchain Section
from Blockchain import Blockchain
# Telegram Bot Section
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
# Additional Section
import os
from datetime import datetime
import csv
import time

# Logging Config
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Hyper Parameters
ref_1 = None
ref_2 = None
bucket_1 = None
bucket_2 = None

# Millis
def current_milli_time():
    return round(time.time() * 1000)

# --- Telegram Bot Code --- #
def start(update: Update, context: CallbackContext) -> None:
    start_mil = current_milli_time()
    message = ">> ======================\n"
    message += ">> Bot : Motion Detection Bot Ready\n"
    message += ">> Bot : Available Commands:\n"
    message += ">> ======================\n"
    message += "1. /verify_databases | Crosscheck Blockchain Validity\n"
    message += "2. /verify_blockchains | Verify Data\n"
    message += "3. /verify_data | Verify Data\n"
    message += "4. /get_data | Fetch Data From A Block\n"
    message += "5. /get_benchmark | Retrieve Telemetries\n"
    message += ">> ======================\n"
    end_mil = current_milli_time()
    message += f">> Bot : Selesai ({(end_mil-start_mil)/1000}s)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def botVerifyDatabases(update: Update, context: CallbackContext) -> None:
    start_mil = current_milli_time()
    message = f">> Bot : Crosschecking Blockchain Validity"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    # Fetch Machine per DB
    db_1 = ref_1.get()
    db_2 = ref_2.get()
    # Status Database
    status_1 = False
    status_2 = False
    # Start Iterative
    if(db_1 is None):
        status_1 = True
    if(db_2 is None):
        status_2 = True
    if(status_1 == True and status_2 == True):
        message = f">> Bot : Nothing Found"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        if(db_1 == db_2):
            message = f">> Bot : Database Perfectly Mirrored"
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        else:
            message = f">> Bot : Database Contains Dirty Block"
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    end_mil = current_milli_time()
    message = f">> Bot : Selesai ({(end_mil-start_mil)/1000}s)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def botVerifyBlockchains(update: Update, context: CallbackContext) -> None:
    start_mil = current_milli_time()
    message = f">> Bot : Verifying Blockchain Validity"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    # Fetch Machine per DB
    db_1 = ref_1.get()
    db_2 = ref_2.get()

    # Blockchain 1
    message = f">> Bot : Verifying Blockchain #1"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    total_blocks = 0
    invalid_blocks = []
    valid = 0
    invalid = 0
    curHash = None
    # Start Iterative
    if (db_1 is not None):
        # Iterate per Machine
        for machine in db_1.keys():
            blocks = ref_1.child(machine).get()
            # Iterate per Block
            for block in blocks.keys():
                total_blocks += 1
                block_data = ref_1.child(machine).child(block).get()
                if (block_data["01 Previous"] == "None" and block == "B_0001"):
                    valid += 1
                else:
                    if (curHash == block_data["01 Previous"]):
                        valid += 1
                    else:
                        invalid += 1
                        invalid_blocks.append(machine + ":" + block)
                curHash = block_data["03 Hash"]

        message = f">> Bot : Found {total_blocks} blocks\n"
        message += f"==>> Valid Blocks : {valid}\n"
        message += f"==>> Invalid Blocks : {invalid}\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        message = "==>> List of Blocks :\n"
        for list in invalid_blocks:
            message += f"====>> {list}\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        message = f">> Bot : Nothing Found"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)

    # Blockchain 2
    message = f">> Bot : Verifying Blockchain #2"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    total_blocks = 0
    invalid_blocks = []
    valid = 0
    invalid = 0
    curHash = None
    # Start Iterative
    if (db_2 is not None):
        # Iterate per Machine
        for machine in db_2.keys():
            blocks = ref_2.child(machine).get()
            # Iterate per Block
            for block in blocks.keys():
                total_blocks += 1
                block_data = ref_2.child(machine).child(block).get()
                if (block_data["01 Previous"] == "None" and block == "B_0001"):
                    valid += 1
                else:
                    if (curHash == block_data["01 Previous"]):
                        valid += 1
                    else:
                        invalid += 1
                        invalid_blocks.append(machine + ":" + block)
                curHash = block_data["03 Hash"]

        message = f">> Bot : Found {total_blocks} blocks\n"
        message += f"==>> Valid Blocks : {valid}\n"
        message += f"==>> Invalid Blocks : {invalid}\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        message = "==>> List of Blocks :\n"
        for list in invalid_blocks:
            message += f"====>> {list}\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        message = f">> Bot : Nothing Found"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)

    end_mil = current_milli_time()
    message = f">> Bot : Selesai ({(end_mil-start_mil)/1000}s)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def botVerifyData(update: Update, context: CallbackContext) -> None:
    start_mil = current_milli_time()
    message = f">> Bot : Verifying Blockchains Data"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    # Fetch Machine per DB
    db_1 = ref_1.get()
    db_2 = ref_2.get()

    if(db_1 is not None and db_2 is not None):
        # Iterate per Machine
        for machine in db_1.keys():
            total_data = 0
            missing = []
            data_exist = 0
            data_missing = 0
            message = f">> Bot : Memeriksa data di mesin '{machine}' (Tunggu)"
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            blocks = ref_1.child(machine).get()
            # Iterate per Block
            for block in blocks.keys():
                print(f"==>> Verifying Block : {block}", end="", flush=True)
                total_data += 1
                block_data = ref_1.child(machine).child(block).get()
                video_id = block_data['02 Data']['0-0 Data']['VidId']
                image_id = block_data['02 Data']['0-0 Data']['ImgId']
                # Check Data
                statusvid = FirebaseHandler.checkData(bucket_1,bucket_2,Blockchain.decryptMessage(str(video_id)))
                statusimg = FirebaseHandler.checkData(bucket_1,bucket_2,Blockchain.decryptMessage(str(image_id)))
                if(statusvid == True and statusimg == True):
                    data_exist += 1
                    print(" > [FOUND]")
                else:
                    data_missing += 1
                    missing.append(machine+":"+block)
                    print(" > [MISSING]")
            message = f">> Bot : Menemukan {total_data} data di '{machine}'\n"
            message += f"==>> Data ada : {data_exist}\n"
            message += f"==>> Data hilang : {data_missing}\n"
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            message = "==>> Daftar data :\n"
            for list in missing:
                message += f"====>> {missing}\n"
                context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        message = f">> Bot : Not Found"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)

    end_mil = current_milli_time()
    message = f">> Bot : Selesai ({(end_mil-start_mil)/1000}s)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def botGetData(update: Update, context: CallbackContext) -> None:
    start_mil = current_milli_time()
    args_len = len(context.args)
    args = context.args
    if(args_len == 0):
        message = f">> Bot : Format Perintah /data [nama mesin] [nama blok]"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    elif(args_len>2 or args_len==1):
        message = f">> Bot : Memerlukan 2 argumen, {args_len} ditemukan"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        if(args[0].isnumeric() or args[1].isnumeric()):
            message = f">> Bot : Memerlukan teks sebagai argumen"
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        else:
            machine = args[0]
            block = args[1]
            message = f">> Bot : Fetching Data From '{block}' in '{machine}'"
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            block_data = ref_1.child(machine).child(block).get()
            if(block_data is not None):
                # Retrieve Data
                video_id = block_data['02 Data']['0-0 Data']['VidId']
                image_id = block_data['02 Data']['0-0 Data']['ImgId']
                # Download Data
                message = f">> Bot : Mengunduh Image dari '{block}' (Tunggu)"
                context.bot.send_message(chat_id=update.effective_chat.id, text=message)
                image_data, statusimg = FirebaseHandler.downloadData(bucket_1,bucket_2, Blockchain.decryptMessage(str(image_id)))
                message = f">> Bot : Mengunduh Video dari '{block}' (Tunggu)"
                context.bot.send_message(chat_id=update.effective_chat.id, text=message)
                video_data,statusvid = FirebaseHandler.downloadData(bucket_1,bucket_2,Blockchain.decryptMessage(str(video_id)))
                # Sending Video
                message = f">> Bot : Mengirim Data ke User (Tunggu)"
                context.bot.send_message(chat_id=update.effective_chat.id, text=message)
                # Get Date Time
                block_telemetry = block_data['02 Data']['0-1 Telemetry']
                block_datetime = block_telemetry['2-00 Datetime']
                block_date = block_datetime['2-02 Date']
                block_time = block_datetime['2-03 Time']
                block_date = Blockchain.decryptMessage(block_date)
                block_time = Blockchain.decryptMessage(block_time)
                message = f"==>> Preview '{block}' at {block_time} {block_date}"
                context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_data, timeout=1000)
                message = f"==>> Video '{block}' at {block_time} {block_date}"
                context.bot.send_video(chat_id=update.effective_chat.id, video=video_data, supports_streaming=False, timeout=1000)
            else:
                message = f">> Bot : Tidak menemukan data di blok {block} - mesin '{machine}'"
                context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    end_mil = current_milli_time()
    message = f">> Bot : Selesai ({(end_mil-start_mil)/1000}s)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def botGetBenchmark(update: Update, context: CallbackContext) -> None:
    counter = 1
    start_mil = current_milli_time()
    message = f">> Bot: Generating Benchmark File"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    db = ref_1.get()
    if(db is not None):
        data_rows = []
        # Iterate per Machine
        for machine in db.keys():
            message = f">> Bot : Fetching Telemetry in '{machine}'"
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            blocks = ref_1.child(machine).get()
            # Iterate per Block
            for block in blocks.keys():
                print(f"==>> Fetching Block : {block}")
                block_data = ref_1.child(machine).child(block).get()
                # Get Telemetry
                block_telemetry = block_data['02 Data']['0-1 Telemetry']
                # Get Timestamp
                block_datetime = block_telemetry['2-00 Datetime']
                block_date = block_datetime['2-02 Date']
                block_time = block_datetime['2-03 Time']
                # Decrypt Data and Set Datetime
                block_date = Blockchain.decryptMessage(block_date)
                block_time = Blockchain.decryptMessage(block_time)
                block_datetime = block_date + " " +block_time
                block_datetime = datetime.strptime(block_datetime,"%d-%B-%Y %H.%M.%S.%f")
                benchmark_timestamp = block_datetime.timestamp()*1000
                # Telemetry Section
                block_benchmark = block_telemetry['1-00 Benchmark']
                block_benchmark_cpu = block_benchmark['1-01 CPU Percent']
                block_benchmark_memory = block_benchmark['1-02 Memory Percent']
                block_benchmark_text = block_benchmark['1-03 Text Usage']
                block_benchmark_data = block_benchmark['1-04 Data Usage']
                block_benchmark_temp = block_benchmark['1-05 CPU Temp']
                block_benchmark_millis = block_benchmark['1-06 Time Milli']
                block_benchmark_diff = block_benchmark['1-07 Difference']
                block_benchmark_mode = block_benchmark['1-08 Mode']
                block_benchmark_confidence = block_benchmark['1-09 Confidence']
                block_benchmark_processing = block_benchmark['1-10 YOLO Processing']
                # Decrypt Data
                benchmark_cpu = Blockchain.decryptMessage(block_benchmark_cpu)
                benchmark_memory = Blockchain.decryptMessage(block_benchmark_memory)
                benchmark_text = Blockchain.decryptMessage(block_benchmark_text)
                benchmark_data = Blockchain.decryptMessage(block_benchmark_data)
                benchmark_temp = Blockchain.decryptMessage(block_benchmark_temp)
                benchmark_millis = Blockchain.decryptMessage(block_benchmark_millis)
                benchmark_diff = Blockchain.decryptMessage(block_benchmark_diff)
                benchmark_mode = Blockchain.decryptMessage(block_benchmark_mode)
                benchmark_confidence = Blockchain.decryptMessage(block_benchmark_confidence)
                benchmark_processing = Blockchain.decryptMessage(block_benchmark_processing)
                # Insert into Row
                row = []
                row.append(counter)
                row.append(machine)
                row.append(block)
                row.append(benchmark_timestamp)
                row.append(benchmark_cpu)
                row.append(benchmark_memory)
                row.append(benchmark_text)
                row.append(benchmark_data)
                row.append(benchmark_temp)
                row.append(benchmark_millis)
                row.append(benchmark_diff)
                row.append(benchmark_mode)
                row.append(benchmark_confidence)
                row.append(benchmark_processing)
                data_rows.append(row)
                counter += 1

        # Write to CSV
        message = f">> Bot : Storing Telemetry to file"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        filename = "benchmark.csv"
        if os.path.isfile(filename):
            os.remove(filename)
        # Set Header CSV
        header = ["No","Machine","Block","Timestamp","CPU","Memory","Text","Data","Temp","Estimate","Diff","Label","Confidence","ProcTime"]
        with open(filename,"w") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for input_row in data_rows:
                writer.writerow(input_row)
        message = f">> Bot : File Telemetry Stored"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        message = f">> Bot : Not Found"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    end_mil = current_milli_time()
    message = f">> Bot : Selesai ({(end_mil-start_mil)/1000}s)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

# --- Main Code --- #
def main():
    global ref_1,ref_2,bucket_1,bucket_2
    ref_1,ref_2 = FirebaseHandler.connectDB()
    bucket_1,bucket_2 = FirebaseHandler.connectBucket()
    # Bot
    updater = Updater(token="1901469256:AAHz0864vwPsAS6HWu68GZ4uoQ8k_FS0YU8",request_kwargs={'read_timeout': 1000, 'connect_timeout': 1000})
    dispatcher = updater.dispatcher
    jq = updater.job_queue
    # Perintah
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("verify_databases", botVerifyDatabases))
    dispatcher.add_handler(CommandHandler("verify_blockchains", botVerifyBlockchains))
    dispatcher.add_handler(CommandHandler("verify_data", botVerifyData))
    dispatcher.add_handler(CommandHandler("get_data", botGetData))
    dispatcher.add_handler(CommandHandler("get_benchmark", botGetBenchmark))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
