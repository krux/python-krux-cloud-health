python-krux-cloud-health
===============

Python library to access information from Krux Cloud Health API.

Application quick start
===============
The most common use case is to build a CLI script using `krux_cloud_health.cli.Application`. Here's how to do that:

```python
import krux.cli
from krux_cloud_health.cloud_health import CloudHealth, NAME, add_cloud_health_cli_arguments, get_cloud_health

class Application(krux.cli.Application):
    def __init__(self, name=NAME):
        self.cloud_health = get_cloud_health(args=self.args, logger=self.logger, stats=self.stats)

	def run(self):
	    costHistory = self.cloud_health.costHistory()

def main():
    app = Application()
    with app.context():
        app.run()

# Run the application stand alone
if __name__ == '__main__':
    main()
```

