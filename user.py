import graphene
import graphql
import requests
import time

import config
import auth
import broker


class Topic(graphene.ObjectType):
    announcements = graphene.Boolean()
    account = graphene.Boolean()


class Method(graphene.ObjectType):
    email = graphene.Boolean()
    sms = graphene.Boolean()


class Notification(graphene.ObjectType):
    topics = graphene.Field(Topic)
    methods = graphene.Field(Method)


class User(graphene.ObjectType):
    _id = graphene.ID()
    first_name = graphene.String()
    last_name = graphene.String()
    email_address = graphene.String()
    password = graphene.String()
    notifications = graphene.Field(Notification)
    brokers = graphene.List(broker.Broker)


def serializeUser(userData):
    brokers = getBrokers(userData.get("_id"))

    return User(
        _id=userData.get("_id"),
        first_name=userData.get("first_name"),
        last_name=userData.get("last_name"),
        email_address=userData.get("email_address"),
        password=userData.get("password"),
        notifications=Notification(
            topics=Topic(
                account=userData.get("notifications").get("topics").get("account"),
                announcements=userData.get("notifications").get("topics").get("announcements")
            ),
            methods=Method(
                sms=userData.get("notifications").get("methods").get("sms"),
                email=userData.get("notifications").get("methods").get("email")
            )
        ),
        brokers=brokers
    )


def getBrokers(_id):
    response = requests.get(
        "{}/brokers?user__$eq={}".format(config.HARAMBE_DATA_SERVICE_ENDPOINT, _id))

    assert (response.status_code == 200), "Could not retrieve brokers"

    data = response.json()

    brokers = [broker.serializeBroker(b) for b in data]
    return brokers


def resolveUser(root, info, token):
    try:
        decoded = auth.decodeToken(token)

        response = requests.get("{}/users/{}".format(config.HARAMBE_DATA_SERVICE_ENDPOINT, decoded.get("user_id")))

        assert(response.status_code == 200), "Could not retrieve user"

        data = response.json()
        return serializeUser(data)
    except AssertionError as e:
        raise graphql.GraphQLError(e)


class RegisterUser(graphene.Mutation):
    class Arguments:
        firstName = graphene.NonNull(graphene.String)
        lastName = graphene.NonNull(graphene.String)
        email_address = graphene.NonNull(graphene.String)
        password = graphene.NonNull(graphene.String)

    token = graphene.String()

    def mutate(self, info, firstName, lastName, email_address, password):
        try:
            passwordHash = auth.generatePassword(password)

            # TODO: validate info
            response = requests.post("{}/users".format(config.HARAMBE_DATA_SERVICE_ENDPOINT), json={
                "firstName": firstName,
                "lastName": lastName,
                "email_address": email_address,
                "password": passwordHash
            })

            assert(response.status_code == 200), "Could not create user"

            # get token
            tokenString = auth.getToken(email_address, password)
            return RegisterUser(token=tokenString)
        except AssertionError as e:
            raise graphql.GraphQLError(e)


class LoginUser(graphene.Mutation):
    class Arguments:
        email_address = graphene.NonNull(graphene.String)
        password = graphene.NonNull(graphene.String)

    token = graphene.String()

    def mutate(self, info, email_address, password):
        try:
            tokenString = auth.getToken(email_address, password)
            return LoginUser(token=tokenString)
        except AssertionError as e:
            raise graphql.GraphQLError(e)


class SetNotification(graphene.Mutation):
    class Arguments:
        token = graphene.NonNull(graphene.String)
        type = graphene.NonNull(graphene.String)
        method = graphene.NonNull(graphene.String)
        allow = graphene.NonNull(graphene.Boolean)

    success = graphene.Boolean()

    def mutate(self, info, token, type, method, allow):
        try:
            tokenData = auth.decodeToken(token)

            updateBody = {
                "notifications": {
                    type: {
                        method: allow
                    }
                }
            }

            updateResponse = requests.patch(
                "{}/users/{}".format(config.HARAMBE_DATA_SERVICE_ENDPOINT, tokenData.get("user_id")),
                json=updateBody
            )

            assert (updateResponse.status_code == 200), "Could not update notification info"

            return SetNotification(success=True)
        except AssertionError as e:
            raise graphql.GraphQLError(e)
