#!/usr/bin/fish

begin
    set -l dir data
    set -l interval 5m

    echo "writing snapshots every $interval"
    echo

    while "true"
        set -l tgz $dir/snapshots/(date '+%Y.%m.%d_%H.%M.%S').tgz
        echo "writing $tgz"
        tar czf $tgz $dir/changes.log $dir/rui.log
        sleep $interval
    end
end
