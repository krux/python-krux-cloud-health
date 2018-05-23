krux-cloud-health
===============

Python library to access information from Cloud Health.

Application quick start
===============
The most common use case is to build a CLI script using `krux_cloud_health.cli.Application`. Here's how to do that:

```python
import krux.cli
import krux_cloud_health.cli.Application

class Application(krux_cloud_health.cli.Application):

	def run(self):
	    print self.cloud_health.costHistory()

def main():
    app = Application()
    with app.context():
        app.run()

# Run the application stand alone
if __name__ == '__main__':
    main()
```