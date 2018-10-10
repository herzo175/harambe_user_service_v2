import graphene
import requests

import config

class AvailableBroker(graphene.ObjectType):
    shortName = graphene.String()


def serializeAvailableBroker(broker):
    return AvailableBroker(
        shortName=broker.get("shortName")
    )


def resolveAvailableBrokers(root, info):
    response = requests.post(
        "{}/preference/getBrokerList".format(config.TRADE_IT_API_ENDPOINT),
        json={"apiKey": config.TRADE_IT_API_KEY})

    assert(response.status_code == 200), "Unable to fetch broker list"

    data = response.json()

    return [serializeAvailableBroker(broker) for broker in data.get("brokerList")]