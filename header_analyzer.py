import email
import re
from nicegui import ui

re_get_text_in_parents = r'(\(.*?\))'
def analyze_header():

    msg = email.message_from_string(header_text.value)
    all_headers = msg.items()

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

    # Authentication Results display (no ARC handling yet)
    # TODO: Add ARC result handling

    # auth_server = auth_results_header[0]
    auth_results_header = msg.get('authentication-results').split(';')
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

    ui.label("Authentication Results")
    ui.table(columns=columns, rows=rows, row_key='method')

    arc_results = msg.get_all('arc-authentication-results') or []

    columns = [
            {'name': 'hop', 'label': 'ARC Hop Counter', 'field': 'hop', 'align': 'left'},
            {'name': 'server', 'label': 'Authenticating Server', 'field':'server', 'align': 'left'},
            {'name': 'spf', 'label': 'SPF', 'field': 'spf', 'align': 'left'},
            {'name': 'dkim', 'label': 'DKIM', 'field': 'dkim', 'align': 'left'},
            {'name': 'dmarc', 'label': 'DMARC', 'field': 'dmarc', 'align': 'left'},
            {'name': 'result', 'label': 'ARC Results', 'field': 'result', 'align': 'left'}
    ]

    rows = []
    for r in arc_results:
        result = dict()
        fields = r.split(';')

        for field in fields:
            if field.startswith("i"):
                result["i"] = field.split('=')[-1]
            if field.find('=') == -1:
                result["server"] = field.strip()
            if field.count('=') > 1:
                match = re.search(re_get_text_in_parents, field)
                comment = match.group(1) if match else None
                cleaned_result = re.sub(re_get_text_in_parents, '', field)

                result.update({k: v for item in cleaned_result.split() for k, v in [item.split('=')]})

        row = {
            'hop': result['i'],
            'server': result['server'],
            'spf': result['spf'],
            'dkim': result['dkim'],
            'dmarc': result['dmarc'],
            'result': r
        }

        rows.append(row)

    ui.label("ARC-Authentication Results")
    ui.table(columns=columns, rows=rows, row_key='hop')

    # Display all headers

    columns = [
        {'name': 'name', 'label': 'Header Name', 'field': 'name', 'align': 'left'},
        {'name': 'value', 'label': 'Header Value', 'field': 'value', 'align': 'left'}
    ]

    rows = []
    for header in all_headers:
        row = {'name': header[0], 'value': header[1]}
        rows.append(row)

    ui.label("All Message Headers")
    ui.table(columns=columns, rows=rows, row_key='name')

header_text = ui.textarea(label='Paste Header here', placeholder="paste headers here...")
ui.button('Analyze Header', on_click=analyze_header)

header_processed = ui.label()

ui.run()