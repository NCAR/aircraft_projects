# How to run tests within this /test directory.

In order to run these tests, you will need to change the path in the
__init__.py file from
```
sys.path.append('/scr/tmp/taylort/aircraft_projects/scripts/')
```
to wherever your local checkout is. Then, from the data_flow directory run

```
./run_tests.sh
```
