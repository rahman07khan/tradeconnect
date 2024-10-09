import graphene
from orders.views import * 

class Mutation(graphene.ObjectType):
    create_fe = FeedbackMasterCreate.Field()
    update_feedback = UpdateFeedbackMaster.Field()
    create_feedback = FeedbackCreate.Field()


class Query(FeedbackMasterQuery,FeedbackQuery,graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
