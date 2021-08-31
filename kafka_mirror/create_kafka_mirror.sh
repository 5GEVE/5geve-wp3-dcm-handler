#!/usr/bin/env bash

SITE=$1

/opt/kafka/bin/kafka-run-class.sh \
  kafka.tools.MirrorMaker \
    --abort.on.send.failure "true" \
    --consumer.config "./${SITE}_consumer.config" \
    --num.streams 4 \
    --producer.config ./producer.config \
    --whitelist '^.*\.application_metric\..*$,^.*\.infrastructure_metric\..*$'
