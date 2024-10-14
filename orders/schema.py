import graphene
from orders.views import * 

class Mutation(graphene.ObjectType):
    create_fe = FeedbackMasterCreate.Field()
    update_feedback = UpdateFeedbackMaster.Field()
    create_feedback = FeedbackCreate.Field()
    update_likes=UpdateLikes.Field()
    create_comment=CreateComment.Field()
    delete_comment=deleteComment.Field()
    update_wish=UpdateWishlist.Field()



class Query(FeedbackMasterQuery,FeedbackQuery,LikesQuery,CommentQuery,WishQuery,ProductQuery,SubCategoryQuery,graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
