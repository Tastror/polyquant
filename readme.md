# polyquant

a quantitative analysis for polymarket

## prerequisities

- python ~= 3.12
- selenium ~= 4.29.0
- chromedriver_autoinstaller ~= 0.6.4

the versions above have been tested and are confirmed to work in Windows 11 24H2 26100.3194, Google Chrome 133.0.6998.36, resolution 2560x1440 (125%)

example of environment creation

```shell
conda create -n polyquant python=3.12
conda activate polyquant
pip install selenium chromedriver_autoinstaller
```

## data collection

```shell
python collect.py {event-name} {scroll-time}
```

- `event-name`: see `url`
- `url`: `https://polymarket.com/event/{event-name}`
- `scroll-time`: default 100

## data analysis

```shell
python analyse.py {filename}
```

- `filename`: `data-{time}.txt` generated in data collection
