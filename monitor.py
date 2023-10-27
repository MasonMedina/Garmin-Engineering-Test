import getopt
import requests
import smtplib
import sys
import time
from requests.exceptions import HTTPError


def main():
    # Args
    support = ""
    argv = sys.argv[1:]

    # API
    api_url = "https://api.qa.fitpay.ninja/health"

    # Grab Support Email args
    try:
        options, args = getopt.getopt(argv, "s:", ["support="])
    except:
        print("Invalid Args")

    for input, value in options:
        if input in ['-s', '--support']:
            support = value

    support = str(support).replace('{', '').replace('}', '')
    print("Support Member Email " + support)

    # Api Checking Loop
    trigger = True
    error_count = 0
    success_count = 0
    while trigger:

        try:
            try:

                response = requests.get(api_url)
                # response_json = response.json()
                code = 400  # response.status_code

                if 200 <= code < 300:
                    success_count += 1
                    if success_count >= 2:
                        error_count = 0

                if 400 <= code < 600:
                    error_count += 1
                    if error_count >= 2:
                        success_count = 0
                        match code:
                            case 400:
                                send_error_mail(support, "API receiving multiple bad requests.")
                            case 401:
                                send_error_mail(support, "API receiving multiple requests without valid API key.")
                            case 402:
                                send_error_mail(support, "API receiving multiple requests with valid Parameters but "
                                                         "requests failed.")
                            case 404:
                                send_error_mail(support, "API receiving multiple requests for an item that does not "
                                                         "exist.")
                            case 500:
                                send_error_mail(support, "FitPay server error registered.")
                            case 502:
                                send_error_mail(support, "FitPay server error registered.")
                            case 503:
                                send_error_mail(support, "FitPay server error registered.")
                            case 504:
                                send_error_mail(support, "FitPay server error registered.")
                            case _:
                                send_error_mail(support, "Unknown Error Codes on API")

            except HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
            except Exception as err:
                print(f'Other error occurred: {err}')

            time.sleep(5)
        except:
            trigger = False

    print('Ending Monitoring')


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

    print("Support Email sent to " + to_email)


if __name__ == '__main__':
    main()
