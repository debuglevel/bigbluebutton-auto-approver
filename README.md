# BigBlueButton auto approver

This tool is for greenlight instances, which are set to manual approval of registrations. This tool looks into a MySQL table to check which mail addresses should be approved automatically. It looks into the `users_roles` table of greenlight to find all `pending` users and removes this role if the mail address is found in MySQL. Nasty database integration, but should work.

## Configuration

There is a sample `docker-compose.yml`. MySQL should probably better use SSL as the port is open (so that another system can update the mail addresses).

## Python development cheat sheet

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## TODO
Fix the whole lot for Greenlight 2.6 because there only one role is allowd and maintained in users table directly. (And that's why you do not want database integration)