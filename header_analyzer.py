import email
from nicegui import ui

def analyze_header():

    msg = email.message_from_string(header_text.value)

    # Sender info
    SENDER_NOTES = {
        "from_header": "What the user sees in their email client",
        "reply-to": "Where replies go",
        "return-path": "SMTP Envelope From",
        "sender": "If present"
    }

    from_header = msg.get('from')
    return_path = msg.get('return-path')
    reply_to = msg.get('reply-to')
    sender = msg.get('sender')

    columns = [
        {'name': 'addr_type', 'label': 'Address Type', 'field': 'addr_type', 'align': 'left'},
        {'name': 'address', 'label': 'Address', 'field': 'address', 'align': 'left'},
        {'name': 'notes', 'label': 'Notes', 'field': 'notes', 'align': 'left'}
    ]

    rows = [
        {'addr_type': 'From (P2)', 'address': from_header, 'notes': SENDER_NOTES['from_header']},
        {'addr_type': 'Return-Path (P1)', 'address': return_path, 'notes': SENDER_NOTES['return-path']},
        {'addr_type': 'Reply-To', 'address': reply_to, 'notes': SENDER_NOTES['reply-to']},
        {'addr_type': 'Sender', 'address': sender, 'notes': SENDER_NOTES['sender']}
    ]

    ui.label("Sender Display")
    ui.table(columns=columns, rows=rows, row_key='field')

    # Email routing info
    hops = list(reversed(msg.get_all('received') or []))


    columns = [
        {'name': 'hop', 'label': 'Hop', 'field': 'hop', 'required': True, 'align': 'left'},
        {'name': 'data', 'label': 'Data', 'field': 'data', 'required': True, 'align': 'left'},
    ]

    rows = []
    hop_number = 1

    for hop in hops:
        row = {'hop': hop_number, 'data': hop}
        rows.append(row)
        hop_number += 1

    ui.label("Message Routing")
    ui.table(columns=columns, rows=rows, row_key='name')

    auth_results_header = msg.get('authentication-results').split(';')
    # auth_server = auth_results_header[0]
    auth_results = auth_results_header[1:]
    
    columns = [
        {'name': 'method', 'label': 'Method', 'field': 'method', 'align': 'left'},
        {'name': 'result', 'label': 'Result', 'field': 'result', 'align': 'left'},
        {'name': 'detail', 'label': 'Detail', 'field': 'detail', 'align': 'left'},
    ]

    rows = []

    for auth_result in auth_results:
        results = auth_result.split()
        method, result = results[0].split('=')

        row = {'method': method, 'result': result, 'detail': auth_result}
        rows.append(row)

    ui.label("Message Results")
    ui.table(columns=columns, rows=rows, row_key='method')

header_text = ui.textarea(label='Paste Header here', placeholder="paste headers here...")
ui.button('Analyze Header', on_click=analyze_header)

header_processed = ui.label()


ui.run()