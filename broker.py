import graphene
import graphql
import requests

import auth
import config
import report
import brokerAccount


class Broker(graphene.ObjectType):
    _id = graphene.ID()
    name = graphene.String()
    default = graphene.Boolean()
    userId = graphene.String()
    userToken = graphene.String()
    accounts = graphene.List(brokerAccount.BrokerAccount)


def serializeBroker(broker):
    accounts = [
        brokerAccount.serializeBrokerAccount(b)
        for b in brokerAccount.getBrokerAccounts(broker.get("user_id"), broker.get("user_token"))]

    print(accounts)

    return Broker(
        _id=broker.get("_id"),
        name=broker.get("name"),
        default=broker.get("default"),
        userId=broker.get("user_id"),
        userToken=broker.get("user_token"),
        accounts=accounts
    )


def resolveBroker(root, info, _id, token):
    try:
        # decode token
        auth.decodeToken(token)

        response = requests.get(
            "{}/brokers/{}".format(config.HARAMBE_DATA_SERVICE_ENDPOINT, _id))
        assert (response.status_code == 200), "Could not retrieve broker"

        data = response.json()

        broker = serializeBroker(data)
        return broker
    except AssertionError as e:
        raise graphql.GraphQLError(e)


class CreateBrokerLoginUrl(graphene.Mutation):
    class Arguments:
        brokerName = graphene.NonNull(graphene.String)

    url = graphene.String()

    def mutate(self, info, brokerName):
        response = requests.post(
            "{}/user/getOAuthLoginPopupUrlForWebApp".format(config.TRADE_IT_API_ENDPOINT),
            json={
                "apiKey": config.TRADE_IT_API_KEY,
                "broker": brokerName
            }
        )

        assert(response.status_code == 200), "Error getting popup url"

        data = response.json()

        assert(data.get("status") == "SUCCESS"), "Unsuccessful response getting popup url"

        return CreateBrokerLoginUrl(url=data.get("oAuthURL"))


class CreateBrokerAccount(graphene.Mutation):
    class Arguments:
        token = graphene.NonNull(graphene.String)
        brokerName = graphene.NonNull(graphene.String)
        oAuthVerifier = graphene.NonNull(graphene.String)

    broker = graphene.Field(Broker)

    def mutate(self, info, token, brokerName, oAuthVerifier):
        try:
            decoded = auth.decodeToken(token)

            # get broker info
            brokerResponse = requests.post(
                "{}/user/getOAuthAccessToken".format(config.TRADE_IT_API_ENDPOINT),
                json={
                    "apiKey": config.TRADE_IT_API_KEY,
                    "oAuthVerifier": oAuthVerifier
                }
            )

            brokerData = brokerResponse.json()

            assert (brokerData.get("status") == "SUCCESS"), "Unsuccessful response getting user access token"

            # add broker to database
            dbResponse = requests.post(
                "{}/brokers".format(config.HARAMBE_DATA_SERVICE_ENDPOINT),
                json={
                    "name": brokerName,
                    "user_id": brokerData.get("userId"),
                    "user_token": brokerData.get("userToken"),
                    "user": decoded.get("user_id"),
                    "default": False
                }
            )

            assert (dbResponse.status_code == 200), "Error adding broker to db"

            # serialize broker
            data = dbResponse.json()

            broker = serializeBroker(data)
            return CreateBrokerAccount(broker=broker)
        except AssertionError as e:
            raise graphql.GraphQLError(e)


class SetBrokerAccountDefault(graphene.Mutation):
    class Arguments:
        token = graphene.NonNull(graphene.String)
        _id = graphene.NonNull(graphene.ID)
        default = graphene.NonNull(graphene.Boolean)

    broker = graphene.Field(Broker)

    def mutate(self, info, token, _id, default):
        try:
            auth.decodeToken(token)

            response = requests.patch(
                "{}/brokers/{}".format(config.HARAMBE_DATA_SERVICE_ENDPOINT, _id),
                json={
                    "default": default
                }
            )

            assert (response.status_code == 200), "Error updating broker in db"

            data = response.json()

            broker = serializeBroker(data)
            return SetBrokerAccountDefault(broker=broker)
        except AssertionError as e:
            raise graphql.GraphQLError(e)


class RemoveBrokerAccount(graphene.Mutation):
    class Arguments:
        token = graphene.NonNull(graphene.String)
        _id = graphene.NonNull(graphene.ID)

    result = graphene.Boolean()

    def mutate(self, info, token, _id):
        try:
            auth.decodeToken(token)

            response = requests.delete(
                "{}/brokers/{}".format(config.HARAMBE_DATA_SERVICE_ENDPOINT, _id))

            assert (response.status_code == 200), "Error removing broker"

            return RemoveBrokerAccount(True)
        except AssertionError as e:
            raise graphql.GraphQLError(e)