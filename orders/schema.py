import graphene
from orders.views import * 

class Mutation(graphene.ObjectType):
    create_fe = FeedbackMasterCreate.Field()
    update_feedback = UpdateFeedbackMaster.Field()
    create_feedback = FeedbackCreate.Field()


class Query(FeedbackMasterQuery,FeedbackQuery,graphene.ObjectType):
    #  feedbackmaster_list = graphene.List(
    #     FeedbackMasterType, 
    #     is_active=graphene.Boolean(), 
    #     resolver=FeedbackMasterQuery.resolve_feedbackmaster_list
    # )
    #  feedbackmaster_by_id = graphene.Field(
    #     FeedbackMasterType, 
    #     id=graphene.ID(required=True), 
    #     resolver=FeedbackMasterQuery.resolve_feedbackmaster_by_id
    # )
    #  feedbackmaster_by_reports = graphene.List(
    #     FeedbackMasterType, 
    #     is_report=graphene.Boolean(), 
    #     is_active=graphene.Boolean(), 
    #     resolver=FeedbackMasterQuery.resolve_feedbackmaster_by_reports
    # )
    #  feedback_list = graphene.List(
    #     FeedbackType, 
    #     is_active=graphene.Boolean(), 
    #     resolver=FeedbackQuery.resolve_feedback_list
    # )
    #  feedback_product_feedback = graphene.List(
    #     UserType, 
    #     product_id=graphene.ID(required=True), 
    #     resolver=FeedbackQuery.resolve_users_who_gave_feedback
    # )
    #  feedback_user_feedback = graphene.List(
    #     FeedbackType, 
    #     user_id=graphene.ID(required=True), 
    #     is_active=graphene.Boolean(), 
    #     resolver=FeedbackQuery.resolve_user_feedback
    # )
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
