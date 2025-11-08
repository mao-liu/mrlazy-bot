# Data Model

## Slack

- Only care about messages in slack that starts with the text `!mrlazy`
- Messages follow the structure `!mrlazy <command> <arg> [<arg> ...]`
- Accept only simple messages, no need to handle images/media/reactions or any advanced features

## Server

- Each command maps to a shell script
- Commands are allow-listed by the user

# Components

## AWS Lambda listener

- Minimalistic python Lambda function
- Filters for messages with the correct prefix
- Do not check commands for correctness
- Sends the message to SQS

## Local server

- Minimalistic python function
- Polls SQS for messages
- Checks command against allow-list
- If command matches, add a reply to the message in a thread that processing has began
- Run the command in a background thread, with timeout of 30 minutes
- When command finishes on success/error/timeout, reply to the thread in a new message that processing has completed
- Assume processing steps are idempotent, and safe to retry