# User Directory Service
The service is a simple API application that's integrates with WorkOS. 
It provides endpoints for managing creating/retrieving users 
and webhooks to keep user data in sync with WorkOS. 

Implemented features and trade-offs
------------------------------------
### Design decisions
WorkOS organization membership and roles assignment specifics impacts the implementation of the service.
Those specifics are:
- membership in the organization along with is created via separate API call
- there are "environment roles" and organization level roles. It is possible to provision default environment role.
- data synchronization is possible either via webhooks or via Events API

### Implementation decisions and trade-offs
- For simplicity email is used as a unique identifier for users and membership only in one organization allowed
- User Directory DB is primary source for retrieving user data to minimize dependency on WorkOS API
- Since creating a user in organization with role means 2 API calls to WorkOS - user first created in WorkOS and then stored in DB.
Implementation is naive because it's hard to achieve transactional consistency between DB and WorkOS API.
- User data syncronization is done via webhooks to eliminate the need for polling WorkOS API.
Although email is unique WorkOS ID (stored during creation process as reference_id) is used to identify users.
This will allow in future have users with same email in different organization and avoid potential issues with email change.
- Roles and organization syncronization with WorkOS is not implemented. Allowed roles and organization are stored in the config file
to allow validation and ease of update in case of changes (code rebuild isn't required)
- Certain features which might be required for production use are out of scope (see below)
- Bulk user import is tricky feature due to 2-step user creation process in WorkOS and DB. 
Current implementation tries to create users for all rows. Response contains information about created and failed users.

Features that are out of scope
------------------------------------
* Authorization
* Full-fledged DB (e.g. PostgreSQL)
* Observability (metrics, tracing)
* OpenAPI spec
* CI/CD
* Sophisticated health check
* Put Flask app behind the proxy (Nginx)
* Reconciliation of the data between the DB and WorkOS
* Seeding of Roles/Permissions in WorkOS


Running app locally in Docker with docker compose
----------
1. Prerequisites: 
   - Docker, Docker Compose
   - Register in WorkOS and get the API key
   - Register at ngrok and install it locally
2. Run ngrok:
```shell
ngrok http http://127.0.0.1:5000
```
3. Go back to WorkOS and add the ngrok URL to the webhook of user.updated event
4. Rename `.env.local` to `.env` and fill in the values
    - Workos API key, Client ID and Webhook secret from WorkOS
    - Database URL - sqllite url, for example: `sqlite:///app.db`
    - Organization ID - the organization ID of default Organization from WorkOS Staging env
    - Roles - the roles that are available in the WorkOS organization
5. Run docker-compose:
```shell
docker-compose up
```

Run unit tests
----------
Navigate to the root of the project and run:
```shell
pytest
```