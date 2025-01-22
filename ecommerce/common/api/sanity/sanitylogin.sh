#!/usr/bin/expect

sanity login

expect "Login type"
send "1\r"  # Replace 1 with the corresponding number of the desired option
expect eof