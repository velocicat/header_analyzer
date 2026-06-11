from nicegui import ui
from parser import EmailHeader, SenderInfo

# re_get_text_in_parents = r'(\(.*?\))'

def show_analyzed_header():

    header = EmailHeader(header_text.value)

    # Display user view

    columns = [
        {'name': 'header', 'label': 'Header', 'field': 'header', 'align': 'left'},
        {'name': 'value', 'label': 'Value', 'field': 'value', 'align': 'left'},
    ]

    rows = [
        {'header': 'From', 'value': header.sender_info.from_header},
        {'header': 'Subject', 'value': header.get_header_value('subject')},
        {'header': 'To', 'value': header.get_header_value('to')},
        {'header': 'CC', 'value': header.get_header_value('cc')},
        {'header': 'Date', 'value': header.get_header_value('date')}
    ]

    ui.label("User's view")
    ui.table(columns=columns, rows=rows, row_key='header')

    # Full Sender view

    columns = [
        {'name': 'addr_type', 'label': 'Address Type', 'field': 'addr_type', 'align': 'left'},
        {'name': 'address', 'label': 'Address', 'field': 'address', 'align': 'left'},
        {'name': 'notes', 'label': 'Notes', 'field': 'notes', 'align': 'left'}
    ]

    rows = [
        {'addr_type': 'From (P2)', 'address': header.sender_info.from_header, 'notes': SenderInfo.NOTES['from']},
        {'addr_type': 'Return-Path (P1)', 'address': header.sender_info.return_path, 'notes': SenderInfo.NOTES['return-path']},
        {'addr_type': 'Reply-To', 'address': header.sender_info.reply_to, 'notes': SenderInfo.NOTES['reply-to']},
        {'addr_type': 'Sender', 'address': header.sender_info.sender, 'notes': SenderInfo.NOTES['sender']}
    ]

    ui.label("Full Sender View")
    ui.table(columns=columns, rows=rows, row_key='addr_type')

    # Authentication results

    columns = [
        {'name': 'method', 'label': 'Method', 'field': 'method', 'align': 'left'},
        {'name': 'result', 'label': 'Result', 'field': 'result', 'align': 'left'},
        {'name': 'detail', 'label': 'Detail', 'field': 'detail', 'align': 'left'},
    ]

    rows = []

    if header.authentication_info.spf is not None:
        rows.append(
            {'method': 'SPF', 'result': header.authentication_info.spf.verdict, 'detail': header.authentication_info.spf.raw},
        )

    if header.authentication_info.dkim is not None:
        rows.append(
            {'method': 'DKIM', 'result': header.authentication_info.dkim.verdict, 'detail': header.authentication_info.dkim.raw},
        )

    if header.authentication_info.dmarc is not None:
        rows.append(
            {'method': 'DMARC', 'result': header.authentication_info.dmarc.verdict, 'detail': header.authentication_info.dmarc.raw}
        )

    ui.label("Authentication Results")
    ui.table(columns=columns, rows=rows, row_key='method')

    # Message routing

    columns = [
        {'name': 'hop', 'label': 'Hop', 'field': 'hop', 'required': True, 'align': 'left'},
        {'name': 'data', 'label': 'Data', 'field': 'data', 'required': True, 'align': 'left'},
    ]

    rows = []
    hop_number = 1

    for hop in header.routing_info:
        row = {'hop': hop_number, 'data': hop.raw}
        rows.append(row)
        hop_number += 1

    ui.label("Message Routing")
    ui.table(columns=columns, rows=rows, row_key='name')

    # Display all headers

    columns = [
        {'name': 'name', 'label': 'Header Name', 'field': 'name', 'align': 'left'},
        {'name': 'value', 'label': 'Header Value', 'field': 'value', 'align': 'left'}
    ]

    rows = []
    for header in header.get_all_headers():
        row = {'name': header[0], 'value': header[1]}
        rows.append(row)

    ui.label("All Message Headers")
    ui.table(columns=columns, rows=rows, row_key='name')


header_text = ui.textarea(label='Paste Header here', placeholder="paste headers here...")

ui.button('Analyze Header', on_click=show_analyzed_header)


ui.run(title='Header Analyzer')