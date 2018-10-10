import requests
import time
import datetime

import graphene
import graphql

import auth
import config

class Report(graphene.ObjectType):
    _id = graphene.ID()
    description = graphene.String()
    date = graphene.DateTime()
    value = graphene.Float()
    cash = graphene.Float()
    buyingPower = graphene.Float()
    broker = graphene.ID()
    brokerAccountNumber = graphene.String()


def serializeReport(data):
    return Report(
        _id=data.get("_id"),
        description=data.get("description"),
        date=datetime.datetime.fromtimestamp(data.get("date")),
        value=data.get("value"),
        cash=data.get("cash"),
        buyingPower=data.get("buying_power"),
        broker=data.get("broker"),
        brokerAccountNumber=data.get("broker_account_number")
    )


def resolveReport(root, info, token, brokerId, accountNumber):
    try:
        auth.decodeToken(token)

        report = makeReport(brokerId, accountNumber, "Current Report")
        return serializeReport(report)
    except AssertionError as e:
        raise graphql.GraphQLError(e)


def resolveReports(root, info, token, accountNumber):
    try:
        response = requests.get(
            "{}/reports?broker_account_number__$eq={}".format(
                config.HARAMBE_DATA_SERVICE_ENDPOINT, accountNumber))

        assert (response.status_code == 200), "Could not retrieve list of reports"

        data = response.json()
        reports = [serializeReport(r) for r in data]

        return reports
    except AssertionError as e:
        raise graphql.GraphQLError(e)


def makeReport(brokerId, accountNumber, description):
    brokerResponse = requests.get("{}/brokers/{}".format(
        config.HARAMBE_DATA_SERVICE_ENDPOINT, brokerId))

    assert (brokerResponse.status_code == 200), "Could not retrieve broker"

    broker = brokerResponse.json()

    accountResponse = requests.post("{}/getAccount".format(
        config.HARAMBE_TRADING_SERVICE_ENDPOINT), json={
            "user_id": broker.get("user_id"),
            "user_token": broker.get("user_token"),
            "account_number": accountNumber
        }
    )

    assert (accountResponse.status_code == 200), "Could not retrieve broker sub account"

    account = accountResponse.json()

    report = {
        "description": description,
        "date": int(time.time()),
        "value": account.get("totalValue"),
        "cash": account.get("availableCash"),
        "buyingPower": account.get("buyingPower"),
        "broker": brokerId,
        "broker_account_number": accountNumber
    }

    return report


class SaveReport(graphene.Mutation):
    class Arguments:
        token = graphene.NonNull(graphene.String)
        brokerId = graphene.NonNull(graphene.ID)
        accountNumber = graphene.NonNull(graphene.String)
        description = graphene.String()

    report = graphene.Field(Report)

    def mutate(self, info, token, brokerId, accountNumber, description):
        try:
            auth.decodeToken(token)

            report = makeReport(brokerId, accountNumber, description)

            response = requests.post(
                "{}/reports".format(config.HARAMBE_DATA_SERVICE_ENDPOINT), json=report
            )

            assert (response.status_code == 200), "Could not create report"

            return serializeReport(report)
        except AssertionError as e:
            raise graphql.GraphQLError(e)
