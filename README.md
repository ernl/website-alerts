# Website Alerts
This script written in Python allows users to receive alerts whenever a website is updated or it has changed.

These alerts are sent through the Pushover API which has got both Desktop and Mobile apps.
Check out the Pushover's website for more information: [pushover.net](https://pushover.net/)

## Dependencies
* Python 3.6+
* Selenium
* ChromeDriverManager (install with `pip install chromedriver-manager`)

## Usage
0. Install the dependencies and set a path to store internal files from the script, you will need to change line 23 of the script with your own path. By default, the path is set to './'

1. First, you will need to create an account on the [Pushover website](https://pushover.net/) so you can get your user key and an application token.
Run the following command to set your user key and application token:
```
python3 website_alerts.py pushover <user_key> <api_key>
```
2. Next up, set your desired time interval between checks by running:
```
python3 website_alerts.py frequency <frequency>
```
3. Now, add your desired website to check by running:
```
python3 website_alerts.py add <website_url>
```
4. Finally, start the website alert script by running:
```
python3 website_alerts.py start
```

Note that the script must be running in order to receive alerts. If you are using Windows, this can be achieved by adding the script to your start-up folder (or as scheduled task).

On the other hand, if you are using Linux, you can run the script daily using Linux's cron.

## More commands
If you wish to learn more about the commands, run the following command:
```
python3 website_alerts.py help
```

## Performance
My original idea was to use Selenium with multithreading but I found out that WebDriver is not thread safe. Therefore, this script uses a single process to check websites.

## Caveats
This script is not guaranteed to work on all websites. If you find any bugs, please report them on this GitHub repo.

Additionally, this script will send an alert if there is the smallest change in the page's content, so it is possible that you might receive a false positive alert.

I hope this script will help you in your daily tasks and if you have any questions, feel free to contact me.