#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 [-u <username>] [-p <postgres_password>] [-s <sudo_password>] [-d <database>]" 1>&2
    echo "Options:" 1>&2
    echo "  -u <username>           PostgreSQL username" 1>&2
    echo "  -p <postgres_password>  PostgreSQL password" 1>&2
    echo "  -s <sudo_password>      Sudo password" 1>&2
    echo "  -d <database>           PostgreSQL database name" 1>&2
    exit 1
}

# Parse command-line arguments
while getopts ":u:p:s:d:" opt; do
    case ${opt} in
        u )
            username=$OPTARG
            ;;
        p )
            postgres_password=$OPTARG
            ;;
        s )
            sudo_password=$OPTARG
            ;;
        d )
            database=$OPTARG
            ;;
        \? )
            echo "Invalid option: $OPTARG" 1>&2
            usage
            ;;
        : )
            echo "Invalid option: $OPTARG requires an argument" 1>&2
            usage
            ;;
    esac
done
shift $((OPTIND -1))

# Check if all required options are provided
if [ -z "$username" ] || [ -z "$postgres_password" ] || [ -z "$sudo_password" ] || [ -z "$database" ]; then
    echo "Error: All options (-u, -p, -s, -d) are required" 1>&2
    usage
fi

# Update package lists and install PostgreSQL
echo "$sudo_password" | sudo -S apt update
echo "$sudo_password" | sudo -S apt install -y postgresql postgresql-contrib

# Set up PostgreSQL
echo "$sudo_password" | sudo -S -u postgres createuser $username
echo "$sudo_password" | sudo -S -u postgres psql -c "alter user $username password '$postgres_password';"
echo "$sudo_password" | sudo -S -u postgres createdb $database

# Connect to the database as the new role
sudo -u postgres psql -U $username $database

# Additional notes:
# 1. This script assumes you have a non-root user with sudo privileges.
# 2. You can run this script with the desired username, PostgreSQL password, sudo password, and database name using command-line arguments.
# For example: scripts/setup_postgres.sh -u your_username -p your_postgres_password -s your_sudo_password -d your_database
