import sys
import getopt
import requests


# python monitor.py --support {masonmedina29@gmail.com}

def main():
    api_url = "https://api.qa.fitpay.ninja/health"
    response = requests.get(api_url)
    print(response)
    print(response.json())
    support = ""
    argv = sys.argv[1:]

    try:
        options, args = getopt.getopt(argv, "s:", ["support="])
    except:
        print("Error Message ")

    for input, value in options:
        if input in ['-s', '--support']:
            support = value

    print(support)


if __name__ == '__main__':
    main()
