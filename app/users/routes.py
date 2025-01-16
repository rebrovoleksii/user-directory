import csv
import io

from flask import Blueprint, jsonify, Response, request, g
from app.config import Config
from app.database import db
import logging

from app.models.user import User

users_bp = Blueprint('users', __name__)
logger = logging.getLogger(__name__)


#TODO: add pagination
@users_bp.route('/users', methods=['GET'])
def get_users():
    """

    :return:
    """
    organization_id = request.headers.get('X-Organization-Id')
    if not organization_id:
        logger.warning('Organization ID not provided')
        return jsonify('Organization ID not provided'), 400

    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    email = request.args.get('email')

    query = db.select(User).filter_by(organization_id=organization_id)

    if first_name:
        query = query.filter(User.first_name.ilike(f'%{first_name}%'))
    if last_name:
        query = query.filter(User.last_name.ilike(f'%{last_name}%'))
    if email:
        query = query.filter(User.email.ilike(f'%{email}%'))

    users = db.session.execute(query).scalars().all()
    return jsonify([user.serialize() for user in users])


@users_bp.route('/users', methods=['POST'])
def create_user():
    """
    Create a new user. User uniquest is based on email.

    :return: 200 OK if user is created successfully
             400 Bad Request if organization ID is not correct
             409 Conflict if user with given email already exists
    """
    organization_id = request.headers.get('X-Organization-Id')
    # for simplicity keep list of organizations in Config. If new organizations are added, Config should be updated
    #TODO: add mechanism to sync organizations with WorkOS and keep them in the DB
    if not organization_id or organization_id not in Config.ORGANIZATIONS.keys():
        logger.warning('Organization ID is empty or not correct')
        return jsonify('Organization ID is not correct'), 400

    data = request.get_json()
    #TODO: validate all data inputs
    if data['role'] not in Config.ROLES:
        # for simplicity keep list of roles in Config. If new roles are added, Config should be updated
        # TODO: add mechanism to sync roles with WorkOS and keep them in the DB
        return jsonify('Role is not correct'), 400

    user = db.session.query(User).filter_by(email=data['email']).first()
    if user:
        return jsonify('User with this email already exists'), 409

    # data consistency between WorkOS and DB achieved via webhook for user.updated event.
    # that's why we need to have a reference_id in the DB which is the same as WorkOS user ID
    # TODO: to have transaction like behaviour, need to add exception handling and user deletion from WorkOS in case of DB error
    workos_id = g.workos_service.create_user(data['email'], data['first_name'], data['last_name'], organization_id, data['role'])

    new_user = User(
        reference_id=workos_id,
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        organization_id=organization_id,
        organization_name=Config.ORGANIZATIONS[organization_id],
        role=data['role']
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201


@users_bp.route('/users/import', methods=['POST'])
def import_users():
    """
    Import users from CSV file. CSV file should have the following columns:
    - first_name, last_name, email, role
    - delimiter is comma
    - no header expected
    :return:
    201 Created with list of users created and failed. For failed users, error message is provided.
    400 Bad Request if organization ID is not correct
    """
    organization_id = request.headers.get('X-Organization-Id')
    if not organization_id or organization_id not in Config.ORGANIZATIONS.keys():
        logger.warning('Organization ID not provided')
        return Response(jsonify('Organization ID is not correct', status=400))

    csv_file = request.files.get('file')

    stream = io.StringIO(csv_file.stream.read().decode("UTF8"), newline=None)
    csv_reader = csv.reader(stream)
    users_created = []
    users_failed = []
    for data in csv_reader:
        try:
            if data[3] not in Config.ROLES:
                raise Exception('Role is not correct')

            workos_id = g.workos_service.create_user(first_name=data[0],last_name= data[1],email=data[2], organization_id=organization_id,role= data[3])
            new_user = User(
                reference_id=workos_id,
                first_name=data[0],
                last_name=data[1],
                email=data[2],
                organization_id=organization_id,
                organization_name=Config.ORGANIZATIONS[organization_id],
                role=data[3]
            )
            db.session.add(new_user)
            users_created.append(data)
        except Exception as e:
            logger.warning(f"Error creating user: {e}")
            #TODO: need to use different exception to handle properly various cases and propagate detailed error message
            #TODO: e.g. when user failed to create in WorkOS no cleanup is needed, but when user failed to create in DB, need to cleanup in WorkOS
            users_failed.append({'data': data, 'error': str(e.message)})

    db.session.commit()
    return jsonify({'users_created': users_created, 'users_failed': users_failed}), 201
