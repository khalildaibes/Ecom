#!/usr/bin/expect

sanity login

# Look for the exact prompt text or part of it
expect {
    "Login type" {
        # Send the number corresponding to your choice
        send "1\r"  # Replace "1" with the appropriate option number (e.g., "Google" is "1")
    }
}

expect eof
