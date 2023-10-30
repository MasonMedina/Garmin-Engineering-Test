import getopt
import requests
import smtplib
import sys
import time
from requests.exceptions import HTTPError


def main():
    # Args
    support = ''
    argv = sys.argv[1:]
    trigger = True
    error_count = 0
    total_error = 0
    success_count = 0
    total_success = 0
    outage_timer = Timer()
    monitor_timer = Timer()
    uptime_timer = Timer()
    monitor_timer.start()
    uptime_list = []
    outage_list = []

    # Grab Support Email args
    try:
        options, args = getopt.getopt(argv, 's:', ['support='])
    except:
        print('Invalid Args')

    for input, value in options:
        if input in ['-s', '--support']:
            support = value

    print(f'Support Member Email {support}')

    # Api Checking Loop

    while trigger:
        try:
            try:
                response_json, code = call_api('https://api.qa.fitpay.ninja/health')

                if not uptime_timer.running:
                    uptime_timer.start()

                # Successful API Check
                if 200 <= code < 300:
                    success_count += 1
                    if error_count >= 2:
                        uptime_timer.start()
                        total_success += 1
                        print(' API Outage Restored')
                        send_error_mail(support,
                                        f'API Service Restored, Total Outage duration: {outage_timer.stop():0.1f} seconds')
                    error_count = 0
                    print(f'API check successful, the status is: {response_json['status']}')

                # Unsuccessful API Check
                if 400 <= code < 600:
                    error_count += 1
                    success_count = 0
                    t = time.localtime()
                    current_time = time.strftime("%H:%M:%S", t)
                    outage = (response_json['status'], current_time)
                    outage_list.append(outage)

                    if error_count > 2:
                        print(f'The API check has reported that the outage is ongoing, '
                              f'the status is: {response_json['status']}')
                    if error_count == 2:
                        total_error += 1
                        print(f'An Outage in the API has occurred, the status is: {response_json['status']}')
                        uptime_list.append(uptime_timer.stop())
                        outage_timer.start()
                        match code:
                            case 400:
                                send_error_mail(support,
                                                'Error 400: API receiving multiple bad requests.')
                            case 401:
                                send_error_mail(support,
                                                'Error 401: API receiving multiple requests without valid API key.')
                            case 402:
                                send_error_mail(support,
                                                'Error 402: API receiving multiple requests with valid Parameters but '
                                                'requests failed.')
                            case 404:
                                send_error_mail(support,
                                                'Error 404: API receiving multiple requests for an item that does not '
                                                'exist.')
                            case 500:
                                send_error_mail(support, 'Error 500: FitPay server error registered.')
                            case 502:
                                send_error_mail(support, 'Error 502: FitPay server error registered.')
                            case 503:
                                send_error_mail(support, 'Error 503:FitPay server error registered.')
                            case 504:
                                send_error_mail(support, 'Error 504: FitPay server error registered.')
                            case _:
                                send_error_mail(support, 'Error Unknown: Unknown Error Codes on API.')

            except HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
            except requests.ConnectionError as err:
                print(f'Connection error occurred: {err}')
            except Exception as err:
                print(f'Other error occurred: {err}')

            # Wait 5 seconds for reasonable delay
            time.sleep(5)

        except:
            trigger = False

    if len(uptime_list) >= 2:
        average_uptime = sum(uptime_list) / len(uptime_list)
    else:
        average_uptime = sum(uptime_list) / 1

    send_error_mail(support,
                    f'During the monitors {monitor_timer.stop():0.1f} seconds of uptime there were {total_error} outages '
                    f'and {total_success} restorations of '
                    f'service. With an average uptime between outages of {average_uptime:0.1f} seconds\n'
                    f'Here is a list of all reported outages during the monitoring and their status codes {outage_list}')
    print('Ending Monitoring')


def call_api(url):
    response = requests.get(url)
    response_json = response.json()
    code = response.status_code
    return response_json, code


def send_error_mail(to_email, body):
    # Email Server Info
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'garminhealthmonitor@gmail.com'
    smtp_password = 'cibc ctnt kqfz qcio'
    from_email = 'garminhealthmonitor@gmail.com'

    # Failure Message
    subject = 'Health API Monitor'
    message = f'Subject: {subject}\n\n{body}'

    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.sendmail(from_email, to_email, message)

    print(f'Support Email sent to: {to_email}')


class Timer:
    def __init__(self):
        self._start_time = None
        self.running = False

    def start(self):
        self._start_time = time.perf_counter()
        self.running = True

    def stop(self):
        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
        self.running = False
        return elapsed_time


if __name__ == '__main__':
    main()

