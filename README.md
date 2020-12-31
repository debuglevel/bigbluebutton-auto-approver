# bigbluebutton-auto-approver

This tool is for Greenlight instances, which are set to manual approval of registrations. This tool looks into a MariaDB table to check which mail addresses should be approved automatically. It looks into the `users` table of Greenlight to find all users with a `pending` role and changes this role to `user` if the mail address is found in MariaDB. Nasty database integration, but should work.

## Configuration

- There is a sample `docker-compose.yml`.
- It is strongly recommended to set up a TLS configuration for MariaDB as its port is open (so that another system can update the mail addresses).
- Another way could be to keep MariaDB bound to localhost only but provide another interface which fills the MariaDB table (e.g. a small REST service).

## Python development cheat sheet

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
