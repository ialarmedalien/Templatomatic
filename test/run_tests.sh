#!/bin/bash
echo "Running $0 with args $@"
if [ -L $0 ] ; then
script_dir=$(cd "$(dirname "$(readlink $0)")"; pwd -P) # for symbolic link
else
script_dir=$(cd "$(dirname "$0")"; pwd -P) # for normal file
fi
base_dir=$(cd $script_dir && cd .. && pwd);
export KB_DEPLOYMENT_CONFIG=$script_dir/../deploy.cfg
export KB_AUTH_TOKEN=`cat /kb/module/work/token`
export APPDIR=/kb/module
echo "Removing temp files..."
rm -rf /kb/module/work/tmp/*
echo "Finished removing temp files."
cd /kb/module
python -m compileall lib/ test/
export PYTHONPATH=/kb/module/lib:$PYTHONPATH
PYTHONPATH=/kb/module/lib/:/kb/module/test/:$PYTHONPATH coverage run --source=/kb/module/lib/Templatomatic -m unittest -v Templatomatic_server_test
echo 'Finished testing. Getting coverage data...'
coverage report
env
coveralls
