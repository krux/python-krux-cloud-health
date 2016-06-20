python-krux-cloud-health
===============

Python library to access information from Krux Cloud Health API.

Application quick start
===============
The most common use case is to build a CLI script using `krux_cloud_health.cli.Application`. Here's how to do that:

```python
import krux.cli
from krux_cloud_health.cloud_health import CloudHealth, NAME, add_cloud_health_cli_arguments, get_cloud_health

def run(self):
    try:
        costHistory = self.cloud_health.costHistory()
    except ValueError as e:
        self.logger.error(e.message)
        self.exit(1)

    month_index = month_index = [item.keys()[0] for item in costHistory].index(self.args.month)

    for item, data in costHistory[month_index][self.args.month].iteritems():
        self.stats.incr(item, data)

def main():
    app = Application()
    with app.context():
        app.run()

# Run the application stand alone
if __name__ == '__main__':
    main()
```
