from threadedcomments.models import ThreadedComment

"""some model related stuff for the timeline"""
class TimeLineItem(object):
    """
    A wrapping class over a content to be displayed in the timeline
    
    TODO : it is not saved in database. In a future release, timeline items
    will be created at content creation time  
    """    
    def __init__(self, item, date, user, template):
        """
        
        @param item: an object to be displayed in the timeline (tweet, 
            image, comment, post, track ...)
        @param date: the datetime of the item
        @param user: original poster
        @param template:  
        """        
        self.item = item
        self.date = date
        self.user = user
        self.template = template           

def group_comments(items):
    """create groups for comments"""
    comments = {}
    # first pass : find all the comment about the same subject
    for tlitem in items:
        item = tlitem.item
        if isinstance(item, ThreadedComment):
            key = (item.content_type_id, item.object_id)
            if not key in comments: 
                comments[key] = []
            comments[key].append(tlitem)       
    
    # create groups
    groups = []
    for group in [ comments[key] for key in comments if len(comments[key]) > 1 ]:        
        firstcomment =  group[0]
        firstitem = firstcomment.item
        group_item = TimeLineItem(firstitem, firstitem.date_submitted, firstitem.user, "timeline/_comment_group.html")
        group_item.firstcomment = firstitem
        group_item.comments  = [ firstcomment ]
        for comment in group[1:]:
            group_item.comments.append(comment)
        groups.append(group_item)
   
    # patch the item list
    grouped = items[:]
    for group_item in groups:
        # insert the group
        index = grouped.index(group_item.comments[0])
        grouped[index] = group_item
        # remove contained comments from the timeline
        for comment in group_item.comments:
            if comment in grouped:
                grouped.remove(comment)

    # done !        
    return grouped 