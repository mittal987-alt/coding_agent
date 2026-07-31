async def console_logger(event):

    print(

        f"[{event.timestamp}] "

        f"{event.event} "

        f"{event.message}"

    )