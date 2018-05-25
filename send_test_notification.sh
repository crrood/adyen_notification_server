#!/bin/bash

http post localhost:80/notification_server/notifications/ < test_notification.json
