import graphene
import requests

from flask import Flask
from flask_graphql import GraphQLView
from flask_cors import CORS

import config
import user
import broker
import availableBroker
import report

# TODO: create identity service
# TODO: flask middleware to go through identity service
class Queries(graphene.ObjectType):
    user = graphene.Field(
        user.User, token=graphene.String(), resolver=user.resolveUser)

    broker = graphene.Field(
        broker.Broker,
        token=graphene.String(),
        _id=graphene.ID(),
        resolver=broker.resolveBroker)

    availableBrokers = graphene.Field(
        graphene.List(availableBroker.AvailableBroker),
        resolver=availableBroker.resolveAvailableBrokers)

    reports = graphene.Field(
        graphene.List(report.Report),
        token=graphene.String(),
        accountNumber=graphene.ID(),
        resolver=report.resolveReports)

    report = graphene.Field(
        report.Report,
        token=graphene.String(),
        brokerId=graphene.String(),
        accountNumber=graphene.String(),
        resolver=report.resolveReport)


class Mutations(graphene.ObjectType):
    # user
    registerUser = user.RegisterUser.Field()
    loginUser = user.LoginUser.Field()
    setNotification = user.SetNotification.Field()

    # broker
    createBrokerLoginUrl = broker.CreateBrokerLoginUrl.Field()
    createBrokerAccount = broker.CreateBrokerAccount.Field()
    setBrokerAccountDefault = broker.SetBrokerAccountDefault.Field()
    removeBrokerAccount = broker.RemoveBrokerAccount.Field()


schema = graphene.Schema(query=Queries, mutation=Mutations)

app = Flask(__name__)
CORS(app)
app.add_url_rule('/graphql', view_func=GraphQLView.as_view(
    'graphql', schema=schema, graphiql=True))


@app.route('/up')
def mrHappy():
    return 'Happy'