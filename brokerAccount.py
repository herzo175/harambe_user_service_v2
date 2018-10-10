import requests
import graphene
import graphql

import config
import report


class BrokerAccount(graphene.ObjectType):
    accountNumber = graphene.String()
    name = graphene.String()


def serializeBrokerAccount(brokerAccount):
    return BrokerAccount(
        accountNumber=brokerAccount.get("accountNumber"),
        name=brokerAccount.get("name")
    )


def getBrokerAccounts(user_id, user_token):
    try:
        accountResponse = requests.post(
            "{}/getAccounts".format(config.HARAMBE_TRADING_SERVICE_ENDPOINT),
            json={"user_id": user_id, "user_token": user_token}
        )

        assert (accountResponse.status_code == 200), "Could not retrieve list of broker accounts"

        accountData = accountResponse.json()
        return accountData.get("accounts")
    except AssertionError as e:
        raise graphql.GraphQLError(e)